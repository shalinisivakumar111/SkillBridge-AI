from pathlib import Path
import math
import time
import requests
import pandas as pd


# ============================================================
# SKILLBRIDGE AI
# JOB LOCATION ENRICHMENT
#
# Purpose:
# - Keep real Adzuna job data
# - Fill missing coordinates when the source location
#   can be geocoded
# - NEVER invent an employer address
# - Preserve the original location information
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "real_jobs.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "enriched_real_jobs.csv"
)


# OpenStreetMap Nominatim
GEOCODING_URL = (
    "https://nominatim.openstreetmap.org/search"
)

REQUEST_TIMEOUT = 10

REQUEST_DELAY = 1.0

USER_AGENT = (
    "SkillBridgeAI/1.0 "
    "(local employment hackathon project)"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_jobs():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    return df


# ============================================================
# CLEAN TEXT
# ============================================================

def clean(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# CHECK COORDINATES
# ============================================================

def has_coordinates(row):

    latitude = row.get("latitude")
    longitude = row.get("longitude")

    if pd.isna(latitude) or pd.isna(longitude):
        return False

    try:

        lat = float(latitude)
        lon = float(longitude)

        return (
            -90 <= lat <= 90
            and
            -180 <= lon <= 180
        )

    except (ValueError, TypeError):

        return False


# ============================================================
# GEOCODE LOCATION
# ============================================================

def geocode_location(location):

    location = clean(location)

    if not location:
        return None

    params = {
        "q": location,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    try:

        response = requests.get(
            GEOCODING_URL,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]

        latitude = result.get("lat")
        longitude = result.get("lon")

        if latitude is None or longitude is None:
            return None

        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "geocoded_display_name": clean(
                result.get("display_name")
            ),
        }

    except Exception:

        return None


# ============================================================
# BUILD GEOCODING QUERY
# ============================================================

def build_query(row):

    location = clean(
        row.get("location")
    )

    searched_location = clean(
        row.get("searched_location")
    )

    location_area = clean(
        row.get("location_area")
    )

    # Prefer the actual location supplied by Adzuna.
    if location:
        return location

    if location_area:
        return location_area

    if searched_location:
        return searched_location

    return ""


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("        JOB LOCATION ENRICHMENT")
    print("=" * 70)
    print()

    print(
        "Loading real Adzuna jobs..."
    )

    df = load_jobs()

    print(
        f"Jobs loaded: {len(df)}"
    )

    print()

    # --------------------------------------------------------
    # ADD ENRICHMENT COLUMNS
    # --------------------------------------------------------

    df["coordinates_source"] = ""

    df["geocoded_display_name"] = ""

    # --------------------------------------------------------
    # MARK EXISTING COORDINATES
    # --------------------------------------------------------

    existing_count = 0

    for index, row in df.iterrows():

        if has_coordinates(row):

            df.at[
                index,
                "coordinates_source"
            ] = "Adzuna"

            existing_count += 1

    missing_before = (
        len(df) - existing_count
    )

    print(
        f"Existing coordinates: {existing_count}"
    )

    print(
        f"Missing coordinates: {missing_before}"
    )

    print()

    # --------------------------------------------------------
    # GEOCODE ONLY MISSING JOBS
    # --------------------------------------------------------

    missing_indexes = []

    for index, row in df.iterrows():

        if not has_coordinates(row):

            missing_indexes.append(
                index
            )

    print(
        "Attempting to geocode missing locations..."
    )

    print()

    success_count = 0

    failed_count = 0

    attempted_queries = set()

    for number, index in enumerate(
        missing_indexes,
        start=1
    ):

        row = df.loc[index]

        query = build_query(
            row
        )

        print(
            f"[{number}/{len(missing_indexes)}] "
            f"{query}"
        )

        if not query:

            print(
                "   No location text available."
            )

            failed_count += 1

            continue

        # ----------------------------------------------------
        # CACHE IDENTICAL LOCATION QUERIES
        # ----------------------------------------------------

        if query in attempted_queries:

            print(
                "   Same location already attempted."
            )

            failed_count += 1

            continue

        attempted_queries.add(
            query
        )

        result = geocode_location(
            query
        )

        if result:

            df.at[
                index,
                "latitude"
            ] = result["latitude"]

            df.at[
                index,
                "longitude"
            ] = result["longitude"]

            df.at[
                index,
                "coordinates_source"
            ] = "OpenStreetMap geocoding"

            df.at[
                index,
                "geocoded_display_name"
            ] = result[
                "geocoded_display_name"
            ]

            success_count += 1

            print(
                "   ✓ Coordinates found:"
            )

            print(
                f"     "
                f"{result['latitude']:.6f}, "
                f"{result['longitude']:.6f}"
            )

        else:

            failed_count += 1

            print(
                "   ✗ Could not geocode."
            )

        time.sleep(
            REQUEST_DELAY
        )

    # --------------------------------------------------------
    # FINAL COORDINATE COUNTS
    # --------------------------------------------------------

    final_coordinates = 0

    final_missing = 0

    for _, row in df.iterrows():

        if has_coordinates(row):

            final_coordinates += 1

        else:

            final_missing += 1

    # --------------------------------------------------------
    # LOCATION QUALITY
    # --------------------------------------------------------

    def location_status(row):

        if has_coordinates(row):

            source = clean(
                row.get(
                    "coordinates_source"
                )
            )

            if source == "Adzuna":

                return "Coordinates from Adzuna"

            if source == "OpenStreetMap geocoding":

                return "Coordinates geocoded from job location"

            return "Coordinates available"

        return "Location available; coordinates unavailable"

    df["location_status"] = df.apply(
        location_status,
        axis=1
    )

    # --------------------------------------------------------
    # ADDRESS SAFETY
    # --------------------------------------------------------
    #
    # We preserve the source address/location.
    # We do NOT create an invented street address.
    # --------------------------------------------------------

    if "company_address" not in df.columns:

        df["company_address"] = ""

    df["company_address"] = (
        df["company_address"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["company_address"] = df[
        "company_address"
    ].replace(
        "",
        pd.NA
    )

    df["company_address"] = (
        df["company_address"]
        .fillna(
            df["location"]
        )
    )

    # --------------------------------------------------------
    # DISTANCE READY
    # --------------------------------------------------------

    df["distance_available"] = df.apply(
        has_coordinates,
        axis=1
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("LOCATION ENRICHMENT COMPLETE")
    print("=" * 70)
    print()

    print(
        f"Total jobs: {len(df)}"
    )

    print(
        f"Coordinates before: {existing_count}"
    )

    print(
        f"Missing before: {missing_before}"
    )

    print(
        f"New coordinates found: {success_count}"
    )

    print(
        f"Geocoding failures: {failed_count}"
    )

    print(
        f"Final jobs with coordinates: "
        f"{final_coordinates}"
    )

    print(
        f"Final jobs without coordinates: "
        f"{final_missing}"
    )

    print()

    print(
        "Location status:"
    )

    print(
        df["location_status"]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Coordinates added by geocoding represent "
        "the job location text, not a verified "
        "employer building entrance."
    )

    print(
        "The application must continue to show "
        "source-provided addresses honestly."
    )


if __name__ == "__main__":

    main()
