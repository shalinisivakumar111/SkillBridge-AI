from pathlib import Path
import json
import time
import requests
import pandas as pd


# ============================================================
# SKILLBRIDGE AI
# REAL-WORLD JOB COLLECTOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = (
    BASE_DIR
    / "data"
    / "config"
    / "job_api_config.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "real_jobs.csv"
)


# ============================================================
# SETTINGS
# ============================================================

COUNTRY = "in"

# IMPORTANT:
# Only ONE API page per location.
# This keeps the collector fast and avoids hundreds of requests.
RESULTS_PER_PAGE = 50
MAX_PAGES = 1

REQUEST_TIMEOUT = 15

REQUEST_DELAY = 0.5


# ============================================================
# LOCATIONS
# ============================================================

LOCATIONS = [
    "Chennai",
    "Madurai",
    "Coimbatore",
    "Salem",
    "Tiruchirappalli",
    "Tirunelveli",
    "Vellore",
    "Bengaluru",
    "Hyderabad",
    "Kochi",
    "Thiruvananthapuram",
    "Kozhikode",
    "Kollam",
]


# ============================================================
# BROAD SEARCH
# ============================================================

SEARCH_TERM = "jobs"


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def load_config():

    if not CONFIG_FILE.exists():

        raise FileNotFoundError(
            f"Configuration file not found:\n{CONFIG_FILE}"
        )

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(file)

    app_id = clean_text(
        config.get("app_id")
    )

    app_key = clean_text(
        config.get("app_key")
    )

    if not app_id or not app_key:

        raise ValueError(
            "Adzuna app_id or app_key is empty."
        )

    return app_id, app_key


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(job):

    location = job.get("location", {})

    if not isinstance(location, dict):
        location = {}

    display_name = clean_text(
        location.get("display_name")
    )

    area = location.get("area", [])

    if isinstance(area, list):

        area_text = ", ".join(
            clean_text(x)
            for x in area
            if clean_text(x)
        )

    else:

        area_text = clean_text(area)

    return display_name, area_text


# ============================================================
# EXTRACT COMPANY
# ============================================================

def extract_company(job):

    company = job.get("company", {})

    if isinstance(company, dict):

        return clean_text(
            company.get("display_name")
        )

    return clean_text(company)


# ============================================================
# FETCH ONE PAGE
# ============================================================

def fetch_jobs(
    app_id,
    app_key,
    location,
    page=1
):

    url = (
        f"https://api.adzuna.com/v1/api/"
        f"jobs/{COUNTRY}/search/{page}"
    )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": RESULTS_PER_PAGE,
        "what": SEARCH_TERM,
        "where": location,
        "content-type": "application/json",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    except requests.exceptions.Timeout:

        print(
            f"     WARNING: timeout while searching {location}"
        )

        return []

    except requests.exceptions.RequestException as error:

        print(
            f"     WARNING: API request failed: {error}"
        )

        return []

    except ValueError:

        print(
            f"     WARNING: invalid JSON returned for {location}"
        )

        return []


# ============================================================
# CONVERT JOB
# ============================================================

def convert_job(
    job,
    requested_location
):

    location_name, location_area = (
        extract_location(job)
    )

    company = extract_company(job)

    latitude = job.get("latitude")
    longitude = job.get("longitude")

    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    salary_is_predicted = job.get(
        "salary_is_predicted"
    )

    contract_type = clean_text(
        job.get("contract_type")
    )

    contract_time = clean_text(
        job.get("contract_time")
    )

    category = job.get("category", {})

    if isinstance(category, dict):

        category_name = clean_text(
            category.get("label")
        )

        category_tag = clean_text(
            category.get("tag")
        )

    else:

        category_name = ""
        category_tag = ""

    return {

        "source": "Adzuna",

        "source_job_id": clean_text(
            job.get("id")
        ),

        "job_title": clean_text(
            job.get("title")
        ),

        "company": company,

        "location": location_name,

        "location_area": location_area,

        "searched_location": requested_location,

        "latitude": latitude,

        "longitude": longitude,

        "salary_min": salary_min,

        "salary_max": salary_max,

        "salary_is_predicted": salary_is_predicted,

        "contract_type": contract_type,

        "contract_time": contract_time,

        "category": category_name,

        "category_tag": category_tag,

        "description": clean_text(
            job.get("description")
        ),

        "created": clean_text(
            job.get("created")
        ),

        "redirect_url": clean_text(
            job.get("redirect_url")
        ),

    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("          REAL-WORLD JOB COLLECTOR")
    print("=" * 70)
    print()

    print(
        "Loading Adzuna configuration..."
    )

    try:

        app_id, app_key = load_config()

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        return

    print(
        "Adzuna credentials loaded successfully."
    )

    print()

    print(
        f"Locations: {len(LOCATIONS)}"
    )

    print(
        f"Pages per location: {MAX_PAGES}"
    )

    print(
        f"Maximum results per page: {RESULTS_PER_PAGE}"
    )

    print()

    print(
        "Using ONE broad real-job search per location."
    )

    print(
        "This replaces the previous 300+ request process."
    )

    print()

    all_jobs = []

    # --------------------------------------------------------
    # LOCATION LOOP
    # --------------------------------------------------------

    for index, location in enumerate(
        LOCATIONS,
        start=1
    ):

        print(
            f"[{index}/{len(LOCATIONS)}] "
            f"Searching jobs in {location}..."
        )

        location_jobs = []

        for page in range(
            1,
            MAX_PAGES + 1
        ):

            print(
                f"   page {page}..."
            )

            jobs = fetch_jobs(
                app_id=app_id,
                app_key=app_key,
                location=location,
                page=page
            )

            print(
                f"   received {len(jobs)} jobs"
            )

            for job in jobs:

                converted = convert_job(
                    job,
                    requested_location=location
                )

                location_jobs.append(
                    converted
                )

            if len(jobs) < RESULTS_PER_PAGE:

                break

            time.sleep(
                REQUEST_DELAY
            )

        print(
            f"   total collected for {location}: "
            f"{len(location_jobs)}"
        )

        print()

        all_jobs.extend(
            location_jobs
        )

        time.sleep(
            REQUEST_DELAY
        )

    # ========================================================
    # DATAFRAME
    # ========================================================

    print("=" * 70)
    print("PROCESSING REAL JOB DATA")
    print("=" * 70)
    print()

    if not all_jobs:

        print(
            "No jobs were returned by Adzuna."
        )

        return

    df = pd.DataFrame(
        all_jobs
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    if "source_job_id" in df.columns:

        df = df.drop_duplicates(
            subset=["source_job_id"],
            keep="first"
        )

    # --------------------------------------------------------
    # CLEAN TEXT
    # --------------------------------------------------------

    text_columns = [
        "job_title",
        "company",
        "location",
        "location_area",
        "searched_location",
        "description",
        "redirect_url",
        "category",
        "category_tag",
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # --------------------------------------------------------
    # ADDRESS
    #
    # IMPORTANT:
    # Do NOT invent an employer street address.
    #
    # We use the actual location information supplied
    # by the API.
    # --------------------------------------------------------

    df["company_address"] = df[
        "location_area"
    ]

    df.loc[
        df["company_address"] == "",
        "company_address"
    ] = df["location"]

    # --------------------------------------------------------
    # LOCATION DISPLAY
    # --------------------------------------------------------

    df["location_display"] = (
        df["location"]
        .replace("", "Location not specified")
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "searched_location",
            "job_title"
        ],
        ascending=[
            True,
            True
        ]
    )

    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "REAL JOB DATASET CREATED"
    )

    print()

    print(
        f"Total unique jobs: {len(df)}"
    )

    print(
        f"Locations with jobs: "
        f"{df['searched_location'].nunique()}"
    )

    print()

    print(
        "Jobs by searched location:"
    )

    counts = (
        df["searched_location"]
        .value_counts()
    )

    for location, count in counts.items():

        print(
            f"  ✓ {location}: {count}"
        )

    print()

    print(
        "Columns:"
    )

    for column in df.columns:

        print(
            f"  ✓ {column}"
        )

    print()

    print(
        "Saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print("=" * 70)
    print("REAL-WORLD JOB COLLECTION COMPLETE")
    print("=" * 70)

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "The address shown by SkillBridge comes from "
        "the real job-source data."
    )

    print(
        "If Adzuna does not provide a floor, building, "
        "landmark or street address, SkillBridge will "
        "not invent one."
    )


if __name__ == "__main__":

    main()
