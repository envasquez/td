import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


DB_FILE = Path(__file__).resolve().parent.parent / "tournaments.db"
TOURNAMENT_DIR = Path(__file__).resolve().parent.parent / "data"
LAKES = {
    "amistad": "Lake Amistad",
    "belton": "Lake Belton",
    "cedar creek": "Cedar Creek Reservoir",
    "choke": "Choke Canyon Reservoir",
    "buchanan": "Lake Buchanan",
    "falcon": "Lake Falcon",
    "fork": "Lake Fork",
    "lbj": "Lake LBJ",
    "lewisville": "Lake Lewisville",
    "ivie": "O.H. Ivie Reservoir",
    "ray roberts": "Lake Ray Roberts",
    "sam rayburn": "Sam Rayburn Reservoir",
    "tawakoni": "Lake Tawakoni",
    "travis": "Lake Travis",
    "toledo": "Toledo Bend Reservoir",
    "whitney": "Lake Whitney",
    "red river": "The Red River",
    "arbuckle": "Lake Arbuckle",
    "texoma": "Lake Texoma",
    "richland": "Richland-Chambers Reservoir",
    "sabine": "The Sabine River",
    "eagle": "Eagle Mountain Lake",
    "limestone": "Lake Limestone",
    "squaw": "Squaw Creek",
}


if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()
    try:
        for filename in os.listdir(TOURNAMENT_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(TOURNAMENT_DIR, filename)) as f:
                    data = json.load(f)
                metadata = data.get("metadata", {})
                results = data.get("results", [])
                dt = datetime.strptime(metadata.get("Date"), "%B %d, %Y")
                date_str = dt.date().isoformat()

                lake = None
                for ident, l in LAKES.items():
                    if ident in metadata.get("Tournament", "").lower():
                        lake = l
                        break

                tournament_name = metadata.get("Tournament")
                region = metadata.get("Region")
                trail = metadata.get("Tournament Trail")
                cursor.execute(
                    "SELECT id FROM tournaments WHERE date = ? AND tournament = ?",
                    (date_str, tournament_name),
                )
                exists = cursor.fetchone()
                if exists:
                    continue

                cursor.execute(
                    """
                    INSERT INTO tournaments (date, lake, region, tournament, tournament_trail)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (date_str, lake, region, tournament_name, trail),
                )
                tournament_id = cursor.lastrowid
                print(f"✅ Inserted: id - {tournament_id} - {tournament_name} on {date_str}")
                for r in results:
                    cursor.execute(
                        """
                        INSERT INTO results (
                            tournament_id, place, skeeter_boat , angler1, angler1_hometown,
                            angler2, angler2_hometown, fish, big_bass, weight, prize
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            tournament_id,
                            r.get("place"),
                            r.get("skeeter_boat"),
                            r.get("angler1"),
                            r.get("angler1_hometown"),
                            r.get("angler2"),
                            r.get("angler2_hometown"),
                            r.get("fish"),
                            r.get("big bass"),
                            r.get("Wt."),
                            r.get("prize"),
                        ),
                    )
    finally:
        conn.commit()
        conn.close()

    print("🏁 Done loading all tournaments into:", DB_FILE)
