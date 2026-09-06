import os
import json
import re
import time
import requests
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "data",
    "config",
    "job_api_config.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dynamic_real_jobs.csv"
)


# ============================================================
# UNIVERSAL JOB SEARCH CATEGORIES
# ============================================================

PROFESSION_SEARCHES = {

    "Healthcare": [
        "doctor",
        "medical officer",
        "general physician",
        "physician",
        "MBBS doctor",
        "resident doctor",
        "clinical",
        "healthcare",
        "medical representative",
        "medical coder"
    ],

    "IT & Software": [
        "software developer",
        "software engineer",
        "python developer",
        "java developer",
        "web developer",
        "frontend developer",
        "backend developer",
        "full stack developer",
        "data analyst",
        "data scientist",
        "machine learning",
        "AI engineer",
        "IT support",
        "cloud engineer"
    ],

    "Education": [
        "teacher",
        "school teacher",
        "primary teacher",
        "secondary teacher",
        "lecturer",
        "professor",
        "tutor",
        "academic",
        "trainer"
    ],

    "Finance & Accounting": [
        "accountant",
        "junior accountant",
        "accounts assistant",
        "account assistant",
        "finance executive",
        "financial analyst",
        "bookkeeper",
        "auditor",
        "tax assistant"
    ],

    "Sales & Retail": [
        "sales executive",
        "sales representative",
        "business development",
        "retail",
        "store manager",
        "sales manager",
        "customer service",
        "customer support",
        "cashier"
    ],

    "Marketing": [
        "digital marketing",
        "marketing executive",
        "marketing manager",
        "SEO",
        "social media",
        "content writer",
        "content marketing",
        "brand manager"
    ],

    "Design & Creative": [
        "graphic designer",
        "UI designer",
        "UX designer",
        "web designer",
        "visual designer",
        "video editor",
        "photographer",
        "creative designer"
    ],

    "Engineering & Technical": [
        "engineer",
        "mechanical engineer",
        "electrical engineer",
        "electronics engineer",
        "civil engineer",
        "technician",
        "maintenance technician",
        "machine operator",
        "quality engineer"
    ],

    "Skilled Trades": [
        "electrician",
        "plumber",
        "carpenter",
        "welder",
        "mechanic",
        "repair technician",
        "tailor",
        "beautician"
    ],

    "Logistics & Transport": [
        "driver",
        "delivery executive",
        "delivery driver",
        "logistics",
        "warehouse associate",
        "warehouse executive",
        "inventory executive",
        "transport"
    ],

    "Hospitality": [
        "chef",
        "cook",
        "hotel staff",
        "restaurant staff",
        "front office executive",
        "receptionist",
        "housekeeping",
        "hospitality"
    ],

    "Administration": [
        "office assistant",
        "office administrator",
        "administrative assistant",
        "data entry operator",
        "computer operator",
        "receptionist",
        "admin executive"
    ],

    "Manufacturing": [
        "production operator",
        "machine operator",
        "production executive",
        "quality inspector",
        "quality control",
        "factory worker",
        "manufacturing"
    ],

    "Agriculture": [
        "farm worker",
        "agriculture officer",
        "agricultural technician",
        "farm manager",
        "horticulture",
        "dairy worker"
    ]
}


# ============================================================
# CITY SEARCH LOCATIONS
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
    "Kollam"
]
def normalize_search_location(value):
    """
    Clean the user's preferred job location.
    Returns an empty string when no usable location was provided.
    """
    location = clean_text(value)

    if not location:
        return ""

    return location


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):

    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


def load_config():

    if not os.path.exists(CONFIG_FILE):

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
        config.get("app_id", "")
    )

    app_key = clean_text(
        config.get("app_key", "")
    )

    country = clean_text(
        config.get("country", "in")
    )

    if not app_id or not app_key:

        raise ValueError(
            "Adzuna app_id/app_key are missing."
        )

    return (
        app_id,
        app_key,
        country
    )


# ============================================================
# ADZUNA REQUEST
# ============================================================

def fetch_jobs(
    app_id,
    app_key,
    country,
    location,
    search_term,
    page=1,
    results_per_page=50
):

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{country}/search/{page}"
    )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": search_term,
        "where": location,
        "content-type": "application/json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "results",
        []
    )


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(
    job,
    searched_location,
    profession,
    search_term
):

    location = job.get(
        "location",
        {}
    )

    company = job.get(
        "company",
        {}
    )

    salary_min = job.get(
        "salary_min"
    )

    salary_max = job.get(
        "salary_max"
    )

    return {

        "source": "Adzuna",

        "source_job_id": job.get(
            "id"
        ),

        "job_title": clean_text(
            job.get("title")
        ),

        "company": clean_text(
            company.get("display_name")
            if isinstance(company, dict)
            else company
        ),

        "location": clean_text(
            location.get("display_name")
            if isinstance(location, dict)
            else location
        ),

        "location_area": clean_text(
            location.get("area")
            if isinstance(location, dict)
            else ""
        ),

        "searched_location":
            searched_location,

        "latitude": (
            job.get("latitude")
            or job.get("location", {}).get(
                "latitude"
            )
            if isinstance(
                job.get("location"),
                dict
            )
            else job.get("latitude")
        ),

        "longitude": (
            job.get("longitude")
            or job.get("location", {}).get(
                "longitude"
            )
            if isinstance(
                job.get("location"),
                dict
            )
            else job.get("longitude")
        ),

        "salary_min": salary_min,

        "salary_max": salary_max,

        "salary_is_predicted":
            job.get(
                "salary_is_predicted"
            ),

        "contract_type":
            clean_text(
                job.get("contract_type")
            ),

        "contract_time":
            clean_text(
                job.get("contract_time")
            ),

        "category":
            clean_text(
                job.get(
                    "category",
                    {}
                ).get("label")
                if isinstance(
                    job.get("category"),
                    dict
                )
                else job.get("category")
            ),

        "description":
            clean_text(
                job.get("description")
            ),

        "created":
            job.get("created"),

        "redirect_url":
            clean_text(
                job.get("redirect_url")
            ),

        "profession_category":
            profession,

        "search_term":
            search_term
    }


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def deduplicate_jobs(df):

    if df.empty:
        return df

    df = df.copy()

    df["dedupe_key"] = (
        df["source"].fillna("").astype(str)
        + "|"
        + df["source_job_id"].fillna("").astype(str)
    )

    df = df.drop_duplicates(
        subset=["dedupe_key"]
    )

    df = df.drop(
        columns=["dedupe_key"]
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main(preferred_location=None):

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       DYNAMIC REAL-WORLD JOB SEARCH")
    print("=" * 70)

    # --------------------------------------------------------
    # Adzuna configuration
    # --------------------------------------------------------

    try:

        print()
        print(
            "Loading Adzuna configuration..."
        )

        app_id, app_key, country = load_config()

        print(
            "Adzuna credentials loaded successfully."
        )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        return

    # --------------------------------------------------------
    # Preferred job location
    # --------------------------------------------------------

    preferred_location = normalize_search_location(
        preferred_location
    )

    if preferred_location:

        search_locations = [
            preferred_location
        ]

        print()
        print(
            f"Searching specifically for jobs in: "
            f"{preferred_location}"
        )

    else:

        search_locations = LOCATIONS

        print()
        print(
            "No preferred job location supplied."
        )

        print(
            "Using the default city search list."
        )

    # --------------------------------------------------------
    # Candidate skills
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("CANDIDATE PROFILE")
    print("=" * 70)

    raw_skills = input(
        "\nEnter candidate skills separated by commas:\n> "
    ).strip()

    if not raw_skills:

        print(
            "ERROR: Candidate skills are required."
        )

        return

    candidate_skills = [
        skill.strip().lower()
        for skill in raw_skills.split(",")
        if skill.strip()
    ]

    print()
    print("Candidate skills:")

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Detect profession using the same logic from Stage 21A
    # --------------------------------------------------------

    profession_scores = {}

    for profession, searches in (
        PROFESSION_SEARCHES.items()
    ):

        score = 0

        # Match candidate skill against search concepts.
        for skill in candidate_skills:

            skill_text = skill.lower()

            for term in searches:

                term_text = (
                    term.lower()
                )

                if (
                    skill_text == term_text
                    or term_text in skill_text
                    or skill_text in term_text
                ):

                    score += 1
                    break

        if score > 0:

            profession_scores[
                profession
            ] = score

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not profession_scores:

        print()
        print(
            "No specific profession detected."
        )

        print(
            "Using broad employment search."
        )

        selected_professions = [
            "Administration",
            "Sales & Retail",
            "Customer Support"
        ]

    else:

        selected_professions = [
            profession
            for profession, score
            in sorted(
                profession_scores.items(),
                key=lambda item:
                    item[1],
                reverse=True
            )
            if score >= 1
        ]

    print()
    print("=" * 70)
    print("SEARCH CATEGORIES")
    print("=" * 70)

    for profession in selected_professions:

        score = profession_scores.get(
            profession,
            0
        )

        print(
            f"✓ {profession}"
            f"  (profile score: {score})"
        )

    # --------------------------------------------------------
    # Build search terms
    # --------------------------------------------------------

    search_terms = []

    for profession in selected_professions:

        for term in PROFESSION_SEARCHES.get(
            profession,
            []
        ):

            if term not in search_terms:

                search_terms.append(
                    term
                )

    # Limit requests for a lightweight system.
    search_terms = search_terms[:12]

    print()
    print(
        f"Dynamic searches selected: "
        f"{len(search_terms)}"
    )

    print()

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    collected = []

    total_requests = (
        len(search_locations)
        * len(search_terms)
    )

    request_number = 0

    for location in search_locations:

        print(
            f"\nSearching {location}..."
        )

        for search_term in search_terms:

            request_number += 1

            print(
                f"  [{request_number}/{total_requests}] "
                f"{search_term}"
            )

            try:

                jobs = fetch_jobs(
                    app_id=app_id,
                    app_key=app_key,
                    country=country,
                    location=location,
                    search_term=search_term,
                    page=1,
                    results_per_page=50
                )

                print(
                    f"       received "
                    f"{len(jobs)} jobs"
                )

                for job in jobs:

                    collected.append(
                        normalize_job(
                            job,
                            location,
                            (
                                selected_professions[0]
                                if selected_professions
                                else "General"
                            ),
                            search_term
                        )
                    )

            except requests.RequestException as error:

                print(
                    f"       request failed: "
                    f"{error}"
                )

            except Exception as error:

                print(
                    f"       processing failed: "
                    f"{error}"
                )

            time.sleep(0.15)

    # --------------------------------------------------------
    # Create dataframe
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PROCESSING DYNAMIC JOB DATA")
    print("=" * 70)

    if not collected:

        print()
        print(
            "No jobs were collected."
        )

        return

    df = pd.DataFrame(
        collected
    )

    before = len(df)

    df = deduplicate_jobs(
        df
    )

    after = len(df)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print(
        "DYNAMIC REAL JOB DATASET CREATED"
    )

    print()
    print(
        f"Raw jobs collected: {before}"
    )

    print(
        f"Unique jobs: {after}"
    )

    print(
        f"Locations searched: "
        f"{len(search_locations)}"
    )

    print()
    print(
        "Jobs by location:"
    )

    print(
        df[
            "searched_location"
        ].value_counts().to_string()
    )

    print()
    print(
        "Jobs by profession:"
    )

    print(
        df[
            "profession_category"
        ].value_counts().to_string()
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
    print(
        "DYNAMIC JOB SEARCH COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":

    user_location = input(
        "\nEnter preferred job location "
        "(for example Chennai):\n> "
    ).strip()

    main(
        preferred_location=user_location
    )