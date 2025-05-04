import json
import os
import sqlite3
from datetime import datetime

DB_FILE = "tournaments2.db"
TOURNAMENT_DIR = "data"
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
    cursor = conn.cursor()
    try:
        tournaments = """
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                lake TEXT,
                region TEXT,
                tournament TEXT,
                tournament_trail TEXT
            )
            """
        results = """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER,
            place INTEGER,
            skeeter_boat BOOL,
            angler1 TEXT,
            angler1_hometown TEXT,
            angler2 TEXT,
            angler2_hometown TEXT,
            fish INTEGER,
            big_bass REAL,
            weight REAL,
            prize TEXT,
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
        )
        """
        # for q in [tournaments, results]:
        #     cursor.execute(q)

        for filename in os.listdir(TOURNAMENT_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(TOURNAMENT_DIR, filename)) as f:
                    data = json.load(f)

                metadata = data.get("metadata", {})
                results = data.get("results", [])
                dt = datetime.strptime(metadata.get("Date"), "%B %d, %Y")
                lake = None
                for ident, l in LAKES.items():
                    if ident in metadata.get("Tournament", "").lower():
                        lake = l
                        break
                if not lake:
                    print(f"date = {dt.date().isoformat()}")
                    print(f"metadata = {metadata}")

                # cursor.execute(
                #     """
                #     INSERT INTO tournaments (
                #         date, lake, region, tournament, tournament_trail
                #     ) VALUES (?, ?, ?, ?, ?)
                #     """,
                #     (
                #         dt.strftime("%Y-%m-%d"),
                #         lake,
                #         metadata.get("Region"),
                #         metadata.get("Tournament"),
                #         metadata.get("Tournament Trail"),
                #     ),
                # )
                # tournament_id = cursor.lastrowid
                # for r in results:
                #     cursor.execute(
                #         """
                #         INSERT INTO results (
                #             tournament_id, place, skeeter_boat, angler1, angler1_hometown,
                #             angler2, angler2_hometown, fish, big_bass, weight, prize
                #         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                #     """,
                #         (
                #             tournament_id,
                #             r.get("place"),
                #             r.get("skeeter_boat"),
                #             r.get("angler1"),
                #             r.get("angler1_hometown"),
                #             r.get("angler2"),
                #             r.get("angler2_hometown"),
                #             r.get("fish"),
                #             r.get("big bass"),
                #             r.get("Wt."),
                #             r.get("prize"),
                #         ),
                #     )
    finally:
        if conn:
            conn.commit()
            conn.close()
    print("✅ All tournament data saved to:", DB_FILE)
