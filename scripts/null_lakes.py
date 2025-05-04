import sqlite3
from pathlib import Path

NULL_LAKE_DATES = {
    "Lake LBJ": ["2012-09-29"],
    "Lake Fork": ["2023-06-25", "2010-08-28"],
    "Squaw Creek": ["2015-12-13"],
    "Lake Belton": ["2011-09-10"],
    "Lake Falcon": ["2012-10-27", "2011-10-08"],
    "Lake Texoma": ["2023-10-14", "2019-10-12", "2024-10-12"],
    "Lake Whitney": [
        "2010-05-30",
        "2011-05-29",
        "2008-05-25",
        "2022-10-08",
        "2012-05-27",
    ],
    "The Red River": ["2015-10-10", "2013-10-05", "2014-10-11", "2020-10-10"],
    "Lake Arbuckle": ["2009-10-23"],
    "Lake Limestone": ["2006-10-07"],
    "Lake Lewisville": ["2012-09-15"],
    "The Sabine River": ["2016-10-08"],
    "O.H. Ivie Reservoir": ["2010-10-02", "2009-10-03", "2021-10-09"],
    "Eagle Mountain Lake": ["2008-10-18"],
    "Toledo Bend Reservoir": ["2010-10-09", "2012-09-08", "2018-02-17"],
    "Sam Rayburn Reservoir": [
        "2015-06-28",
        "2022-06-26",
        "2007-10-27",
        "2011-10-01",
        "2006-05-21",
        "2019-06-22",
        "2020-06-28",
        "2017-06-25",
        "2018-06-23",
        "2016-06-26",
        "2021-09-12",
    ],
    "Cedar Creek Reservoir": ["2011-09-17", "2009-10-10"],
}
DB_FILE = Path(__file__).resolve().parent.parent / "tournaments.db"


def assign_lakes(db_path=DB_FILE):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for lake, dates in NULL_LAKE_DATES.items():
            for date in dates:
                cursor.execute(
                    """
                    UPDATE tournaments
                    SET lake = ?
                    WHERE date = ? AND lake IS NULL
                """,
                    (lake, date),
                )
        conn.commit()


if __name__ == "__main__":
    assign_lakes()
    print("✅ Lake assignments updated where date matched and lake was NULL.")
