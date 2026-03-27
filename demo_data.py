# This runs on first launch of the live app to seed demo data
import sqlite3

def seed_demo_data(conn):
    cursor = conn.cursor()
    
    # Check if demo data already exists
    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]
    if count > 0:
        return  # Already has data, skip
    
    players = [
        ("Marcus Silva", "2008-03-14", "U16", "Striker", "Right", "Riverside FC Academy", "Brazilian"),
        ("James Okafor", "2007-09-22", "U17", "Central Midfielder", "Right", "Riverside FC Academy", "Nigerian"),
        ("Luca Ferretti", "2008-11-05", "U16", "Right Winger", "Right", "Riverside FC Academy", "Italian"),
        ("Antoine Dubois", "2007-06-18", "U17", "Centre Back", "Left", "Northgate United Academy", "French"),
        ("Hamza Al-Rashid", "2009-01-30", "U15", "Goalkeeper", "Right", "Northgate United Academy", "Moroccan"),
        ("Diego Vargas", "2008-07-12", "U16", "Left Back", "Left", "Northgate United Academy", "Colombian"),
        ("Theo Williams", "2007-04-25", "U17", "Attacking Midfielder", "Right", "Eastside Youth FC", "English"),
        ("Kai Nakamura", "2009-08-09", "U15", "Defensive Midfielder", "Right", "Eastside Youth FC", "Japanese"),
        ("Emre Yilmaz", "2008-02-17", "U16", "Left Winger", "Left", "Eastside Youth FC", "Turkish"),
        ("Samuel Asante", "2007-12-03", "U17", "Right Back", "Right", "Riverside FC Academy", "Ghanaian"),
    ]
    
    player_ids = []
    for p in players:
        cursor.execute("""INSERT INTO players 
            (name, date_of_birth, age_group, position, dominant_foot, club, nationality)
            VALUES (?,?,?,?,?,?,?)""", p)
        conn.commit()
        player_ids.append(cursor.lastrowid)
    
    import random
    random.seed(42)
    
    session_templates = [
        ("2024-09-07", "match"), ("2024-09-14", "training"), ("2024-09-21", "match"),
        ("2024-09-28", "training"), ("2024-10-05", "match"), ("2024-10-12", "training"),
        ("2024-10-19", "match"), ("2024-10-26", "training"),
    ]
    
    position_profiles = {
        "Striker":              dict(dist=(8.5,10.5), spr=(18,28), spd=(28,34), pc=(15,25), pa=(20,32), drib=(4,8), def_a=(2,5), goals=(0,2), ast=(0,1), chances=(1,3), tack=(1,3)),
        "Central Midfielder":   dict(dist=(10,12.5), spr=(14,22), spd=(25,30), pc=(40,60), pa=(48,72), drib=(2,5), def_a=(5,10), goals=(0,1), ast=(0,2), chances=(1,4), tack=(3,7)),
        "Right Winger":         dict(dist=(9,11.5), spr=(20,30), spd=(29,35), pc=(22,35), pa=(28,44), drib=(5,10), def_a=(2,5), goals=(0,1), ast=(0,2), chances=(1,4), tack=(1,3)),
        "Centre Back":          dict(dist=(9,11), spr=(10,18), spd=(24,29), pc=(35,55), pa=(42,65), drib=(1,3), def_a=(8,16), goals=(0,1), ast=(0,1), chances=(0,2), tack=(4,9)),
        "Goalkeeper":           dict(dist=(4,6), spr=(4,8), spd=(20,26), pc=(20,35), pa=(26,44), drib=(0,1), def_a=(2,5), goals=(0,0), ast=(0,0), chances=(0,0), tack=(0,1)),
        "Left Back":            dict(dist=(9.5,12), spr=(14,22), spd=(26,31), pc=(30,48), pa=(38,58), drib=(2,5), def_a=(6,12), goals=(0,1), ast=(0,1), chances=(0,2), tack=(3,7)),
        "Attacking Midfielder": dict(dist=(9,11.5), spr=(14,22), spd=(26,32), pc=(30,48), pa=(38,58), drib=(4,8), def_a=(3,7), goals=(0,1), ast=(0,2), chances=(2,5), tack=(2,5)),
        "Defensive Midfielder": dict(dist=(10,12.5), spr=(12,20), spd=(24,29), pc=(38,58), pa=(46,70), drib=(2,4), def_a=(7,14), goals=(0,1), ast=(0,1), chances=(0,2), tack=(4,9)),
        "Left Winger":          dict(dist=(9,11.5), spr=(20,30), spd=(29,35), pc=(20,34), pa=(26,42), drib=(5,10), def_a=(2,5), goals=(0,1), ast=(0,2), chances=(1,4), tack=(1,3)),
        "Right Back":           dict(dist=(9.5,12), spr=(14,22), spd=(26,31), pc=(30,48), pa=(38,58), drib=(2,5), def_a=(6,12), goals=(0,1), ast=(0,1), chances=(0,2), tack=(3,7)),
    }
    
    def r(lo, hi): return round(random.uniform(lo, hi), 1)
    def ri(lo, hi): return random.randint(lo, hi)
    
    for i, pid in enumerate(player_ids):
        pos = players[i][3]
        prof = position_profiles.get(pos, position_profiles["Central Midfielder"])
        base_coach = random.randint(6, 9)
        base_att = random.randint(6, 9)
        
        for j, (date, stype) in enumerate(session_templates):
            mins = 90 if stype == "match" else ri(60, 75)
            trend = j * 0.05
            cursor.execute("""INSERT INTO sessions 
                (player_id, session_date, session_type, minutes_played,
                distance_covered_km, sprint_count, top_speed_kmh,
                passes_completed, passes_attempted, dribbles_completed,
                defensive_actions, goals, assists, chances_created,
                tackles_won, coachability_rating, attitude_score,
                consistency_rating, coach_notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (pid, date, stype, mins,
                 r(prof['dist'][0], prof['dist'][1]),
                 ri(prof['spr'][0], prof['spr'][1]),
                 r(prof['spd'][0], prof['spd'][1]),
                 ri(prof['pc'][0], prof['pc'][1]),
                 ri(prof['pa'][0], prof['pa'][1]),
                 ri(prof['drib'][0], prof['drib'][1]),
                 ri(prof['def_a'][0], prof['def_a'][1]),
                 ri(prof['goals'][0], prof['goals'][1]),
                 ri(prof['ast'][0], prof['ast'][1]),
                 ri(prof['chances'][0], prof['chances'][1]),
                 ri(prof['tack'][0], prof['tack'][1]),
                 min(10, base_coach + ri(0,1)),
                 min(10, base_att + ri(0,1)),
                 min(10, ri(6,9)),
                 "Good session." if stype == "training" else "Solid match performance."))
            conn.commit()
    
    print(f"Demo data seeded: {len(players)} players, {len(players)*len(session_templates)} sessions")

