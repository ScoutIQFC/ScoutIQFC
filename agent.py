import os
import pandas as pd
from dotenv import load_dotenv
import sqlite3
import anthropic

load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))

conn = sqlite3.connect("scout_agent.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_of_birth TEXT,
    age_group TEXT,
    position TEXT,
    dominant_foot TEXT,
    club TEXT,
    nationality TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id),
    session_date TEXT,
    session_type TEXT,
    minutes_played INTEGER,
    distance_covered_km REAL,
    sprint_count INTEGER,
    top_speed_kmh REAL,
    passes_completed INTEGER,
    passes_attempted INTEGER,
    dribbles_completed INTEGER,
    defensive_actions INTEGER,
    goals INTEGER,
    assists INTEGER,
    chances_created INTEGER,
    tackles_won INTEGER,
    coachability_rating INTEGER,
    attitude_score INTEGER,
    consistency_rating INTEGER,
    coach_notes TEXT
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id),
    report_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()


def import_from_excel(filepath):
    print(f"\nReading file: {filepath}")
    df = pd.read_excel(filepath)

    for _, row in df.iterrows():
        cursor.execute("SELECT id FROM players WHERE name = ?", (str(row["name"]),))
        existing = cursor.fetchone()

        if existing:
            player_id = existing[0]
            print(f"Player exists: {row['name']}")
        else:
            cursor.execute("""
                INSERT INTO players
                (name, date_of_birth, position, club, dominant_foot, age_group, nationality)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row["name"]),
                str(row["date_of_birth"])[:10],
                str(row["position"]),
                str(row["club"]),
                str(row["dominant_foot"]),
                str(row["age_group"]),
                str(row["nationality"])
            ))
            conn.commit()
            player_id = cursor.lastrowid
            print(f"Added player: {row['name']}")

        raw_date = str(row["session_date"])
        clean_date = raw_date[:10].replace('/', '-')

        cursor.execute("""
            INSERT INTO sessions
            (player_id, session_date, session_type, minutes_played,
            distance_covered_km, sprint_count, top_speed_kmh,
            passes_completed, passes_attempted, dribbles_completed,
            defensive_actions, goals, assists, chances_created,
            tackles_won, coachability_rating, attitude_score,
            consistency_rating, coach_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id,
            clean_date,
            str(row["session_type"]),
            int(row["minutes_played"]),
            float(row["distance_covered_km"]),
            int(row["sprint_count"]),
            float(row["top_speed_kmh"]),
            int(row["passes_completed"]),
            int(row["passes_attempted"]),
            int(row["dribbles_completed"]),
            int(row["defensive_actions"]),
            int(row["goals"]),
            int(row["assists"]),
            int(row["chances_created"]),
            int(row["tackles_won"]),
            int(row["coachability_rating"]),
            int(row["attitude_score"]),
            int(row["consistency_rating"]),
            str(row["coach_notes"])
        ))
        conn.commit()
        print(f"Session logged: {row['name']} on {clean_date}")

    print("\nAll data imported successfully.")


def generate_report(player_name):
    cursor.execute("SELECT * FROM players WHERE name = ?", (player_name,))
    player = cursor.fetchone()

    if not player:
        print(f"Player not found: {player_name}")
        return

    player_id = player[0]

    cursor.execute(
        "SELECT * FROM sessions WHERE player_id = ? ORDER BY session_date",
        (player_id,)
    )
    sessions = cursor.fetchall()

    if not sessions:
        print("No sessions found.")
        return

    cursor.execute(
        "SELECT * FROM reports WHERE player_id = ? ORDER BY created_at",
        (player_id,)
    )
    previous_reports = cursor.fetchall()

    sessions_text = "\n".join([
        f"- {s[2]} ({s[3]}): "
        f"{s[4]} mins, {s[5]}km, "
        f"{s[6]} sprints, top speed {s[7]}km/h, "
        f"passes {s[8]}/{s[9]}, "
        f"dribbles {s[10]}, "
        f"defensive actions {s[11]}, "
        f"goals {s[12]}, assists {s[13]}, "
        f"chances created {s[14]}, "
        f"tackles won {s[15]}. "
        f"Coachability {s[16]}/10, "
        f"attitude {s[17]}/10, "
        f"consistency {s[18]}/10. "
        f"Notes: {s[19]}"
        for s in sessions
    ])

    previous_text = ""
    if previous_reports:
        last = previous_reports[-1]
        previous_text = f"""
PREVIOUS REPORT SUMMARY:
{last[2][:400]}
"""

    prompt = f"""
You are a senior youth football scout and player development specialist
with 20 years of experience at academy level across Europe and South America.
You write development reports that serve as a player's professional CV —
read by academy directors, technical coaches and talent ID managers.

Your reports are concise, direct and written in the language coaches use
every day. No academic language. No AI-sounding phrases. No bullet points
or dashes. Full sentences throughout. Maximum 4 pages when printed.

PLAYER PROFILE:
Name: {player[1]}
Position: {player[4]}
Date of birth: {player[2]}
Age group: {player[3]}
Club: {player[6]}
Nationality: {player[7]}
Dominant foot: {player[5]}

SESSION DATA ({len(sessions)} sessions):
{sessions_text}

{previous_text}

Write a youth development scouting report structured exactly as follows.
Every section must be complete. No truncation. No bullet points. No dashes.
Write as a UEFA Pro Licence coach writing for a peer. Confident and direct.

EXECUTIVE SUMMARY

Write 4 sentences maximum. This is the first thing an academy director reads.
Sentence 1: Who this player is and their standout quality backed by one number.
Sentence 2: Their biggest current limitation backed by one number.
Sentence 3: Their development trajectory — are they ahead, on track or behind
for their age group and position.
Sentence 4: Your recommendation in plain language.

1. PERFORMANCE RATING

Give a score out of 10. One sentence justification with two specific data points.
State whether this player is Below Expectation, Meets Expectation,
Above Expectation or Exceptional for their age group and position.

2. TECHNICAL PROFILE

Calculate and state pass completion rate as a percentage from the data.
Calculate and state dribble completion rate as a percentage from the data.
Calculate defensive actions per 90 minutes from the data.
Calculate goal and assist involvement per 90 minutes from the data.
Write two sentences interpreting what these numbers mean about technical
quality relative to what is expected for this position at this age.
Tailor the interpretation to the position — a goalkeeper's passing matters
differently to a striker's, a centre back's defensive actions differ from
a winger's. Make the assessment position-appropriate.

3. PHYSICAL PROFILE

State average distance covered per session, average sprint count per session
and peak recorded top speed from the data.
Write two sentences assessing whether the physical output is elite, adequate
or concerning for this age group and position.
Flag any session where physical output dropped more than 15 percent below the
average and state what this may indicate about load, fatigue or motivation.
If no significant drop exists, state this with the supporting numbers.

4. MENTAL AND ATTITUDE PROFILE

State the average coachability, attitude and consistency scores and identify
the trend direction across sessions — improving, stable or declining.
Write two sentences interpreting what these scores mean for this player's
long term development potential.
Give one specific behavioural recommendation for the coaching staff — how
should they communicate with and challenge this player based on the scores.

5. BEST POSITION NOW AND FUTURE

State the position this player should play right now based on the data.
State one alternative position that the data profile supports and explain
in two sentences why trialling this position would benefit their development.
If the data suggests the player is struggling in their current role, state
this directly and recommend the positional change as a priority action rather
than waiting for further decline.

6. SHORT TERM RECOMMENDATIONS (Next 4 to 8 weeks)

Write three specific actionable training recommendations based directly on
the weakest metrics in the data.
For each recommendation state the current metric value, the target metric
value to aim for and the specific type of training session that would
address it.
Write these as a coach planning a weekly training block would — specific,
position-relevant and immediately implementable.

7. MEDIUM TERM DEVELOPMENT PLAN (This season)

Write three development targets for the remainder of the season.
Each target must include a specific measurable metric so progress can
be tracked objectively over time.
Include one out-of-the-box recommendation — something unconventional
that could unlock a meaningful step change in development. This could be
a position change, specific opposition to expose the player to, a loan
or dual registration consideration, a particular training methodology
or an individual development programme focus.

8. LONG TERM CEILING AND PATHWAY (12 months plus)

State this player's realistic ceiling and choose one level:
local academy standard, regional standard, national standard or
professional pathway. Justify the choice with three specific data points.
Write one paragraph describing what this player's career looks like
at age 21 if current trends continue without significant intervention.
Write one paragraph describing what becomes possible if the development
recommendations in this report are followed consistently and the player
responds well to coaching.

9. INJURY AND LOAD WATCH

Short term (next 4 weeks): identify any immediate physical load concerns
based on recent session data, sprint volumes or distance trends.
Recommend specific recovery or load management actions if needed.
Medium term (next 3 months): identify any patterns that could develop
into injury risk if not addressed. Name the specific physical areas at
risk based on the position demands and the output data shown.
Long term (beyond 3 months): assess whether the current physical
development trajectory is sustainable for a player of this age.
If no concerns exist across any of these timeframes, state this clearly
and provide the data that supports it.

10. MAN MANAGEMENT GUIDE

Short term (next training block): based on the attitude and coachability
scores give specific guidance on how to deliver feedback to this player,
how to frame challenges and what motivational approach is most likely
to work right now.
This season: advise on how to manage this player's minutes, responsibility
and challenge level to maintain development momentum without risk of
disengagement or burnout.
Long term (career pathway): give an honest assessment of this player's
psychological readiness for the next level and state clearly what needs
to happen before a step up should be considered.

11. TRAINING SESSION IDEAS

Suggest two specific training session formats tailored directly to this
player's development needs based on the data.
For each session: name it, describe the setup and structure in two
sentences, state which specific metric from the report it targets and
explain in one sentence why this format suits this player's profile.
These must be practical and position-specific — sessions a coach could
run in their next training week with minimal resource requirements.

12. SCOUTING VERDICT

State your recommendation: Continue Monitoring, Increase Development
Focus, Priority Development Case or Consider Promotion.
Write three sentences justifying the verdict using only data referenced
elsewhere in this report.
Write one final sentence that captures this player the way a scout would
describe them verbally to a colleague — honest, direct and memorable.
This sentence should stick in the mind of anyone who reads it.

Write every section fully and completely without exception.
Maximum length equivalent to 4 printed pages.
No bullet points. No dashes. No markdown formatting. No asterisks.
Write in the language coaches actually use. Direct, clear and actionable.
"""

    print(f"\nGenerating report for {player_name}...")
    print("=" * 50)

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    report_text = response.content[0].text

    cursor.execute("""
        INSERT INTO reports (player_id, report_text)
        VALUES (?, ?)
    """, (player_id, report_text))
    conn.commit()

    print(report_text)
    print("=" * 50)
    print(f"\nReport saved.")
    return report_text


def list_players():
    cursor.execute("SELECT name, position, club, age_group FROM players")
    players = cursor.fetchall()
    print("\nPlayers in database:")
    print("-" * 40)
    for p in players:
        print(f"{p[0]} | {p[1]} | {p[2]} | {p[3]}")
    print("-" * 40)


def generate_all_reports():
    cursor.execute("SELECT name FROM players")
    players = cursor.fetchall()
    for p in players:
        generate_report(p[0])


if __name__ == "__main__":
    import_from_excel("Players.xlsx")
    list_players()
    generate_all_reports()