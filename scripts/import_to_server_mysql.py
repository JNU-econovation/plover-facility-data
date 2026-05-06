import csv
from pathlib import Path

import pymysql

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "data" / "cleaned"

TRASH_CSV = CLEANED_DIR / "cleaned_trash_bins.csv"
TOILET_CSV = CLEANED_DIR / "cleaned_toilets.csv"


def normalize(value):
    if value is None:
        return None

    value = value.strip()
    if value == "":
        return None

    return value


def insert_csv(cursor, csv_path, table_name, columns, batch_size=1000):
    sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(columns))})
    """

    total_count = 0
    batch = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            values = [normalize(row.get(column)) for column in columns]
            batch.append(values)

            if len(batch) >= batch_size:
                cursor.executemany(sql, batch)
                total_count += len(batch)
                batch.clear()

        if batch:
            cursor.executemany(sql, batch)
            total_count += len(batch)

    print(f"{table_name} insert 완료: {total_count}건")


def main():
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=False,
    )

    try:
        with connection.cursor() as cursor:
            print("기존 데이터 삭제 중...")
            cursor.execute("TRUNCATE TABLE trash_bins")
            cursor.execute("TRUNCATE TABLE toilets")

            print("CSV import 시작...")

            insert_csv(
                cursor,
                TRASH_CSV,
                "trash_bins",
                ["name", "road_address", "latitude", "longitude", "trash_type"],
            )

            insert_csv(
                cursor,
                TOILET_CSV,
                "toilets",
                ["name", "road_address", "latitude", "longitude", "toilet_type", "open_time_type"],
            )

        connection.commit()
        print("전체 import 완료")

    except Exception as e:
        connection.rollback()
        print("import 실패. rollback 처리됨.")
        raise e

    finally:
        connection.close()


if __name__ == "__main__":
    main()
