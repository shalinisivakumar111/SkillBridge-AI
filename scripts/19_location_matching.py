from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import pandas as pd


# ============================================================
# SKILLBRIDGE AI
# LOCATION-AWARE JOB MATCHING ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

JOBS_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "location_enabled_jobs.csv"
)

CANDIDATE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "candidate_skills.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "location_job_recommendations.csv"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("              SKILLBRIDGE AI")
print("       LOCATION-AWARE JOB MATCHING")
print("=" * 70)


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_distance_km(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):
    """
    Calculate distance between two GPS coordinates.

    Returns:
        Distance in kilometres.
    """

    try:
        latitude_1 = float(latitude_1)
        longitude_1 = float(longitude_1)
        latitude_2 = float(latitude_2)
        longitude_2 = float(longitude_2)
    except (TypeError, ValueError):
        return None

    earth_radius_km = 6371.0

    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)

    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


# ============================================================
# DISTANCE CLASSIFICATION
# ============================================================

def classify_distance(distance_km):

    if distance_km is None:
        return "Unknown"

    if distance_km <= 5:
        return "Very Nearby"

    if distance_km <= 15:
        return "Nearby"

    if distance_km <= 30:
        return "Within Area"

    return "Far"


# ============================================================
# LOCATION SCORE
# ============================================================

def calculate_location_score(distance_km):

    if distance_km is None:
        return 0.0

    if distance_km <= 5:
        return 15.0

    if distance_km <= 15:
        return 12.0

    if distance_km <= 30:
        return 8.0

    if distance_km <= 50:
        return 3.0

    return 0.0


# ============================================================
# SKILL MATCHING
# ============================================================

def normalize_skill(skill):

    return (
        str(skill)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def calculate_skill_match(
    candidate_skills,
    job_skills
):

    candidate = [
        normalize_skill(skill)
        for skill in candidate_skills
        if str(skill).strip()
    ]

    job = [
        normalize_skill(skill)
        for skill in job_skills
        if str(skill).strip()
    ]

    if not candidate or not job:
        return 0.0, [], []

    matched = []
    match_types = []

    # --------------------------------------------------------
    # Intelligent relationships
    # --------------------------------------------------------

    related_groups = {
        "office administration": {
            "ms office",
            "microsoft office",
            "excel",
            "ms excel",
            "data entry",
            "computer operations",
            "office administration",
        },

        "customer service": {
            "customer service",
            "communication",
            "sales",
            "problem solving",
            "customer support",
        },

        "communication": {
            "communication",
            "english communication",
            "customer service",
            "customer support",
            "sales",
        },

        "telugu": {
            "telugu",
            "customer service",
            "communication",
        },

        "hindi": {
            "hindi",
            "customer service",
            "communication",
        },

        "tamil": {
            "tamil",
            "customer service",
            "communication",
        }
    }

    # --------------------------------------------------------
    # Find matches
    # --------------------------------------------------------

    for candidate_skill in candidate:

        for job_skill in job:

            # Exact
            if candidate_skill == job_skill:

                matched.append(
                    f"{candidate_skill} → {job_skill}"
                )

                match_types.append("exact")

                continue

            # Related
            related = False

            if candidate_skill in related_groups:

                if job_skill in related_groups[
                    candidate_skill
                ]:

                    related = True

            if related:

                matched.append(
                    f"{candidate_skill} → {job_skill}"
                )

                match_types.append("related")

    # --------------------------------------------------------
    # Remove duplicate matches
    # --------------------------------------------------------

    unique_matches = []
    unique_types = []

    seen = set()

    for match, match_type in zip(
        matched,
        match_types
    ):

        if match not in seen:

            seen.add(match)

            unique_matches.append(match)
            unique_types.append(match_type)

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    if not job:

        return 0.0, [], []

    exact_count = sum(
        1
        for match_type in unique_types
        if match_type == "exact"
    )

    related_count = sum(
        1
        for match_type in unique_types
        if match_type == "related"
    )

    # Each candidate skill should not generate unlimited points.
    candidate_skill_scores = []

    for candidate_skill in candidate:

        candidate_job_matches = []

        for match, match_type in zip(
            unique_matches,
            unique_types
        ):

            source = match.split(" → ")[0]

            if source == candidate_skill:

                if match_type == "exact":
                    candidate_job_matches.append(1.0)

                elif match_type == "related":
                    candidate_job_matches.append(0.65)

        if candidate_job_matches:

            # Best relationship for this candidate skill
            candidate_skill_scores.append(
                max(candidate_job_matches)
            )

    if candidate_skill_scores:

        skill_match = (
            sum(candidate_skill_scores)
            / len(candidate)
        ) * 100

    else:

        skill_match = 0.0

    skill_match = min(
        skill_match,
        100.0
    )

    return (
        round(skill_match, 1),
        unique_matches,
        unique_types
    )


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading location-enabled jobs...")

jobs_df = pd.read_csv(
    JOBS_FILE
)

print(
    f"Jobs available: {len(jobs_df)}"
)


print("\nLoading candidate skills...")

candidate_df = pd.read_csv(
    CANDIDATE_FILE
)

candidate_skills = (
    candidate_df["skill"]
    .dropna()
    .astype(str)
    .tolist()
)

print(
    f"Candidate skills: {len(candidate_skills)}"
)

for skill in candidate_skills:
    print(f"  ✓ {skill}")


# ============================================================
# CANDIDATE LOCATION
# ============================================================

print("\n" + "=" * 70)
print("CANDIDATE LOCATION")
print("=" * 70)

print(
    """
For this test, enter a city:

Examples:
  Chennai
  Madurai
  Coimbatore
  Kochi
  Hyderabad
  Bengaluru
"""
)

candidate_city = input(
    "Enter candidate city: "
).strip()


# ============================================================
# CITY COORDINATES
# ============================================================

city_coordinates = {

    "chennai": (
        13.0827,
        80.2707
    ),

    "madurai": (
        9.9252,
        78.1198
    ),

    "coimbatore": (
        11.0168,
        76.9558
    ),

    "salem": (
        11.6643,
        78.1460
    ),

    "tiruchirappalli": (
        10.7905,
        78.7047
    ),

    "tirunelveli": (
        8.7139,
        77.7567
    ),

    "vellore": (
        12.9165,
        79.1325
    ),

    "bengaluru": (
        12.9716,
        77.5946
    ),

    "hyderabad": (
        17.3850,
        78.4867
    ),

    "kochi": (
        9.9312,
        76.2673
    ),

    "thiruvananthapuram": (
        8.5241,
        76.9366
    ),

    "kozhikode": (
        11.2588,
        75.7804
    ),

    "kollam": (
        8.8932,
        76.6141
    )
}


candidate_key = (
    candidate_city
    .strip()
    .lower()
)


if candidate_key not in city_coordinates:

    print(
        f"\nLocation '{candidate_city}' "
        "is not available in the current demo dataset."
    )

    print("\nAvailable locations:")

    for city in sorted(
        jobs_df["location"].dropna().unique()
    ):

        print(
            f"  ✓ {city}"
        )

    raise SystemExit(1)


candidate_latitude, candidate_longitude = (
    city_coordinates[candidate_key]
)


print(
    f"\nCandidate location: {candidate_city}"
)

print(
    f"Latitude: {candidate_latitude}"
)

print(
    f"Longitude: {candidate_longitude}"
)


# ============================================================
# CALCULATE MATCHES
# ============================================================

print(
    "\nCalculating skill + distance matches..."
)

results = []


for _, job in jobs_df.iterrows():

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    distance_km = calculate_distance_km(
        candidate_latitude,
        candidate_longitude,
        job["latitude"],
        job["longitude"]
    )

    distance_category = classify_distance(
        distance_km
    )

    location_score = calculate_location_score(
        distance_km
    )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    job_skills = str(
        job["skills"]
    ).split(",")

    skill_match, matched_skills, match_types = (
        calculate_skill_match(
            candidate_skills,
            job_skills
        )
    )

    # --------------------------------------------------------
    # Final score
    #
    # Skill = maximum 100
    # Location = maximum 15
    #
    # We cap the final score at 100.
    # --------------------------------------------------------

    final_score = min(
        skill_match + location_score,
        100.0
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if final_score >= 70:

        recommendation = "Recommended"

    elif final_score >= 50:

        recommendation = "Good Match"

    elif final_score >= 30:

        recommendation = "Possible Match"

    else:

        recommendation = "Low Match"

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    results.append({

        "job_id": job["job_id"],

        "job_title": job["job_title"],

        "company": job["company"],

        "location": job["location"],

        "address": job["address"],

        "latitude": job["latitude"],

        "longitude": job["longitude"],

        "distance_km": round(
            distance_km,
            2
        ),

        "distance_category":
            distance_category,

        "skill_match":
            round(
                skill_match,
                1
            ),

        "location_score":
            round(
                location_score,
                1
            ),

        "final_score":
            round(
                final_score,
                1
            ),

        "recommendation":
            recommendation,

        "matched_skills":
            "; ".join(
                matched_skills
            ),

        "match_types":
            "; ".join(
                match_types
            ),

        "salary":
            job.get(
                "salary",
                ""
            ),

        "employment_type":
            job.get(
                "employment_type",
                ""
            ),

        "experience_years":
            job.get(
                "experience_years",
                ""
            )
    })


# ============================================================
# DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)


# ============================================================
# FILTER NEARBY JOBS
# ============================================================

# For the recommendation screen we primarily want jobs
# within 30 km.

nearby_results = results_df[
    results_df["distance_km"] <= 30
].copy()


# If there are fewer than 10 nearby jobs, keep the closest
# available jobs instead of showing unrelated distant jobs.

if len(nearby_results) < 10:

    nearby_results = results_df.sort_values(
        [
            "distance_km",
            "final_score"
        ],
        ascending=[
            True,
            False
        ]
    ).head(10)

else:

    nearby_results = nearby_results.sort_values(
        [
            "final_score",
            "distance_km"
        ],
        ascending=[
            False,
            True
        ]
    ).head(10)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

nearby_results.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 70)
print("             NEARBY JOB RECOMMENDATIONS")
print("=" * 70)


for number, (_, row) in enumerate(
    nearby_results.iterrows(),
    start=1
):

    print(
        f"\n{number}. {row['job_title']}"
    )

    print(
        f"   Company: {row['company']}"
    )

    print(
        f"   Address: {row['address']}"
    )

    print(
        f"   Location: {row['location']}"
    )

    print(
        f"   Distance: "
        f"{row['distance_km']:.2f} km"
    )

    print(
        f"   Location Type: "
        f"{row['distance_category']}"
    )

    print(
        f"   Skill Match: "
        f"{row['skill_match']:.1f}%"
    )

    print(
        f"   Location Score: "
        f"+{row['location_score']:.1f}"
    )

    print(
        f"   Final Score: "
        f"{row['final_score']:.1f}%"
    )

    print(
        f"   Recommendation: "
        f"{row['recommendation']}"
    )

    if pd.notna(
        row["matched_skills"]
    ) and str(
        row["matched_skills"]
    ).strip():

        print(
            f"   Matched Skills: "
            f"{row['matched_skills']}"
        )

    else:

        print(
            "   Matched Skills: None"
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("      LOCATION MATCHING COMPLETE")
print("=" * 70)

print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)

print(
    "\nThe next app stage can use:"
)

print(
    "  ✓ GPS coordinates"
)

print(
    "  ✓ Distance"
)

print(
    "  ✓ Radius filtering"
)

print(
    "  ✓ Skill matching"
)

print(
    "  ✓ Company"
)

print(
    "  ✓ Address"
)

print(
    "  ✓ Recommendation score"
)

print(
    "  ✓ Nearby classification"
)
