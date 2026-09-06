"""
SkillBridge AI
Precise Job Location Enrichment

Purpose:
- Preserve source job information.
- Use detailed job location/address when available.
- Geocode detailed locations using OpenStreetMap.
- Preserve source-provided coordinates when no better
  location information is available.
- Never invent an employer street address.
"""

from pathlib import Path
import time

import pandas as pd
import requests


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "real_jobs.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "enriched_real_jobs.csv"
)


# ============================================================
# SETTINGS
# ============================================================

NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/search"
)

USER_AGENT = "SkillBridgeAI/1.0"

REQUEST_DELAY = 1.1


# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


def valid_coordinates(latitude, longitude):

    try:
        lat = float(latitude)
        lon = float(longitude)

        if not (-90 <= lat <= 90):
            return False

        if not (-180 <= lon <= 180):
            return False

        return True

    except (TypeError, ValueError):
        return False


# ============================================================
# GEOCODING
# ============================================================

def geocode_location(location):

    location = clean(location)

    if not location:
        return None

    try:

        query = location

        if "india" not in query.lower():
            query = f"{query}, India"

        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "in",
            },
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=10,
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]

        latitude = result.get("lat")
        longitude = result.get("lon")

        if not valid_coordinates(
            latitude,
            longitude
        ):
            return None

        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "geocoded_display_name": clean(
                result.get("display_name")
            ),
        }

    except Exception as exc:

        print(
            f"   Geocoding error: {exc}"
        )

        return None


# ============================================================
# BUILD BEST LOCATION TEXT
# ============================================================

def best_location_text(row):

    company_address = clean(
        row.get("company_address")
    )

    location_area = clean(
        row.get("location_area")
    )

    location = clean(
        row.get("location")
    )

    searched_location = clean(
        row.get("searched_location")
    )

    # --------------------------------------------------------
    # Most precise available text first.
    # --------------------------------------------------------

    if company_address:
        return company_address

    if location_area:
        return location_area

    if location:
        return location

    if searched_location:
        return searched_location

    return ""


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("        PRECISE JOB LOCATION ENRICHMENT")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print()
    print(
        f"Jobs loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    for column in [
        "latitude",
        "longitude",
    ]:

        if column not in df.columns:
            df[column] = pd.NA

    for column in [
        "company_address",
        "location_area",
        "location",
        "searched_location",
    ]:

        if column not in df.columns:
            df[column] = ""

    # --------------------------------------------------------
    # Output metadata columns
    # --------------------------------------------------------

    df["geocoded_display_name"] = ""

    df["coordinates_source"] = (
        df.get(
            "coordinates_source",
            pd.Series(
                "",
                index=df.index
            )
        )
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # Cache repeated locations
    # --------------------------------------------------------

    geocode_cache = {}

    successful = 0
    failed = 0
    existing_kept = 0

    print()
    print(
        "Checking job locations..."
    )

    # --------------------------------------------------------
    # Process every job
    # --------------------------------------------------------

    for index, row in df.iterrows():

        location_text = best_location_text(
            row
        )

        if not location_text:

            failed += 1

            continue

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # We attempt geocoding even when coordinates already
        # exist, because existing Adzuna coordinates may only
        # represent the city.
        # ----------------------------------------------------

        cache_key = location_text.lower()

        if cache_key in geocode_cache:

            result = geocode_cache[
                cache_key
            ]

        else:

            print(
                f"[{index + 1}/{len(df)}] "
                f"{location_text}"
            )

            result = geocode_location(
                location_text
            )

            geocode_cache[
                cache_key
            ] = result

            time.sleep(
                REQUEST_DELAY
            )

        # ----------------------------------------------------
        # Geocoding succeeded
        # ----------------------------------------------------

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
                "geocoded_display_name"
            ] = result[
                "geocoded_display_name"
            ]

            df.at[
                index,
                "coordinates_source"
            ] = "OpenStreetMap geocoding"

            successful += 1

            print(
                "   ✓ Precise coordinates:"
            )

            print(
                f"     "
                f"{result['latitude']:.6f}, "
                f"{result['longitude']:.6f}"
            )

        # ----------------------------------------------------
        # Geocoding failed
        # ----------------------------------------------------

        else:

            if valid_coordinates(
                row.get("latitude"),
                row.get("longitude")
            ):

                existing_kept += 1

                print(
                    "   → Keeping source coordinates"
                )

            else:

                failed += 1

                print(
                    "   ✗ No coordinates available"
                )

    # ========================================================
    # LOCATION STATUS
    # ========================================================

    def location_status(row):

        latitude = row.get(
            "latitude"
        )

        longitude = row.get(
            "longitude"
        )

        source = clean(
            row.get(
                "coordinates_source"
            )
        )

        if not valid_coordinates(
            latitude,
            longitude
        ):

            return (
                "Location available; "
                "coordinates unavailable"
            )

        if source == (
            "OpenStreetMap geocoding"
        ):

            return (
                "Coordinates geocoded "
                "from detailed job location"
            )

        if source:

            return (
                f"Coordinates from {source}"
            )

        return (
            "Coordinates available"
        )

    df["location_status"] = df.apply(
        location_status,
        axis=1
    )

    # --------------------------------------------------------
    # Distance availability
    # --------------------------------------------------------

    df["distance_available"] = (
        df.apply(
            lambda row:
            valid_coordinates(
                row.get("latitude"),
                row.get("longitude")
            ),
            axis=1
        )
    )

    # --------------------------------------------------------
    # Preserve source address honestly
    # --------------------------------------------------------

    df["company_address"] = (
        df["company_address"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # If company_address is empty, use location text.
    empty_address = (
        df["company_address"] == ""
    )

    df.loc[
        empty_address,
        "company_address"
    ] = (
        df.loc[
            empty_address,
            "location"
        ]
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("LOCATION ENRICHMENT COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Total jobs: {len(df)}"
    )

    print(
        f"Precise geocoding successful: "
        f"{successful}"
    )

    print(
        f"Existing coordinates retained: "
        f"{existing_kept}"
    )

    print(
        f"Jobs without coordinates: "
        f"{int((~df['distance_available']).sum())}"
    )

    print()
    print(
        "Location status:"
    )

    print(
        df[
            "location_status"
        ]
        .value_counts()
        .to_string()
    )

    print()
    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Geocoded coordinates represent "
        "the supplied job location text."
    )

    print(
        "They are not guaranteed to represent "
        "the exact employer building entrance."
    )


if __name__ == "__main__":
    main()