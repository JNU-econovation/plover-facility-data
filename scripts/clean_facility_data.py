# Usage: python scripts/clean_facility_data.py

import zipfile
import io
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = DATA_DIR / "cleaned"

TRASH_SRC = DATA_DIR / "전국휴지통표준데이터.csv"
TOILET_SRC = DATA_DIR / "공중화장실정보.csv"

TRASH_COLUMNS = {
    "설치장소명": "name",
    "소재지도로명주소": "road_address",
    "위도": "latitude",
    "경도": "longitude",
    "휴지통종류": "trash_type",
}

TOILET_COLUMNS = {
    "화장실명": "name",
    "소재지도로명주소": "road_address",
    "WGS84위도": "latitude",
    "WGS84경도": "longitude",
    "구분명": "toilet_type",
    "개방시간": "open_time_type",
}

# 고정 시설이 아니므로 제외 (임시·이동식)
TOILET_EXCLUDE_TYPES = {"간이화장실", "이동화장실"}


def read_csv_or_zip(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                raise FileNotFoundError(f"zip 안에 CSV 파일이 없습니다: {path}")
            with zf.open(csv_names[0]) as f:
                return pd.read_csv(io.TextIOWrapper(f, encoding="cp949"))
    return pd.read_csv(path, encoding="cp949")


def clean_coords(df: pd.DataFrame) -> pd.DataFrame:
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["latitude", "longitude"])
    dropped_null = before - len(df)

    before = len(df)
    df = df[
        df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)
    ]
    dropped_range = before - len(df)

    return df, dropped_null, dropped_range


def clean(src: Path, col_map: dict, label: str, exclude_closed: bool = False) -> pd.DataFrame:
    print(f"\n[{label}]")
    raw = read_csv_or_zip(src)
    total = len(raw)
    print(f"  원본 행 수: {total:,}")

    df = raw[list(col_map.keys())].copy()
    df = df.rename(columns=col_map)

    dropped_closed = 0
    if exclude_closed and "open_time_type" in df.columns:
        before = len(df)
        df = df[df["open_time_type"] != "미개방"]
        dropped_closed = before - len(df)

    dropped_type = 0
    if "toilet_type" in df.columns:
        before = len(df)
        df = df[~df["toilet_type"].isin(TOILET_EXCLUDE_TYPES)]
        dropped_type = before - len(df)

    df, dropped_null, dropped_range = clean_coords(df)

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["name", "latitude", "longitude"])
    dropped_dedup = before_dedup - len(df)

    final = len(df)
    if dropped_closed:
        print(f"  미개방 제거: {dropped_closed:,}행")
    if dropped_type:
        print(f"  임시·이동식 제거: {dropped_type:,}행")
    print(f"  좌표 없음 제거: {dropped_null:,}행")
    print(f"  좌표 범위 초과 제거: {dropped_range:,}행")
    print(f"  중복 제거: {dropped_dedup:,}행")
    print(f"  정제 후 행 수: {final:,}")
    print(f"  총 제거 행 수: {total - final:,}")

    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    trash = clean(TRASH_SRC, TRASH_COLUMNS, "휴지통")
    trash.to_csv(OUT_DIR / "cleaned_trash_bins.csv", index=False, encoding="utf-8-sig")

    toilet = clean(TOILET_SRC, TOILET_COLUMNS, "화장실", exclude_closed=True)
    toilet.to_csv(OUT_DIR / "cleaned_toilets.csv", index=False, encoding="utf-8-sig")

    print(f"\n출력 경로: {OUT_DIR}")


if __name__ == "__main__":
    main()
