import os
import re
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dynamic_real_jobs.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "universal_skill_matches.csv"
)


# ============================================================
# PROFESSION-SPECIFIC SKILLS
# ============================================================

PROFESSION_SKILLS = {

    "Healthcare": [
        "mbbs",
        "md",
        "doctor",
        "physician",
        "general medicine",
        "diagnosis",
        "patient care",
        "patient assessment",
        "clinical",
        "emergency care",
        "bls",
        "acls",
        "nursing",
        "nurse",
        "pharmacist",
        "pharmacy",
        "medical",
        "healthcare",
        "hospital",
        "clinical documentation",
        "patient counselling",
        "radiology",
        "physiotherapy",
        "medical coding"
    ],

    "IT & Software": [
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "angular",
        "node",
        "sql",
        "django",
        "flask",
        "git",
        "programming",
        "coding",
        "machine learning",
        "artificial intelligence",
        "data science",
        "data analyst",
        "aws",
        "azure",
        "cloud",
        "devops",
        "cybersecurity",
        "networking"
    ],

    "Education": [
        "teaching",
        "teacher",
        "education",
        "lesson planning",
        "classroom management",
        "mathematics",
        "physics",
        "chemistry",
        "biology",
        "english",
        "tutor",
        "training",
        "academic"
    ],

    "Finance & Accounting": [
        "accounting",
        "accountant",
        "tally",
        "gst",
        "bookkeeping",
        "finance",
        "financial analysis",
        "accounts",
        "audit",
        "tax",
        "excel",
        "payroll"
    ],

    "Sales & Retail": [
        "sales",
        "retail",
        "customer service",
        "customer support",
        "negotiation",
        "business development",
        "merchandising",
        "store management",
        "cashier"
    ],

    "Marketing": [
        "digital marketing",
        "marketing",
        "seo",
        "sem",
        "social media",
        "content writing",
        "content marketing",
        "advertising",
        "branding",
        "email marketing"
    ],

    "Design & Creative": [
        "graphic design",
        "graphic designer",
        "photoshop",
        "illustrator",
        "figma",
        "ui design",
        "ux design",
        "video editing",
        "photography",
        "creative"
    ],

    "Engineering & Technical": [
        "engineering",
        "mechanical",
        "electrical",
        "electronics",
        "civil",
        "automobile",
        "cad",
        "autocad",
        "maintenance",
        "technician",
        "troubleshooting",
        "machine operator"
    ],

    "Skilled Trades": [
        "electrician",
        "plumbing",
        "plumber",
        "carpentry",
        "carpenter",
        "welding",
        "welder",
        "mechanic",
        "repair",
        "technician",
        "tailoring",
        "tailor",
        "beautician"
    ],

    "Logistics & Transport": [
        "driving",
        "driver",
        "delivery",
        "logistics",
        "warehouse",
        "inventory",
        "transport",
        "supply chain",
        "dispatch"
    ],

    "Hospitality": [
        "hotel",
        "hospitality",
        "cooking",
        "chef",
        "cook",
        "food service",
        "restaurant",
        "front office",
        "housekeeping",
        "hotel management"
    ],

    "Administration": [
        "office administration",
        "office management",
        "ms office",
        "excel",
        "data entry",
        "communication",
        "documentation",
        "administration",
        "administrative"
    ],

    "Manufacturing": [
        "manufacturing",
        "production",
        "machine operation",
        "machine operator",
        "quality control",
        "quality inspection",
        "assembly",
        "factory",
        "production planning"
    ],

    "Agriculture": [
        "agriculture",
        "farming",
        "agricultural",
        "horticulture",
        "irrigation",
        "crop",
        "livestock",
        "dairy",
        "farm management"
    ]
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):

    if pd.isna(value):
        return ""

    text = str(value).lower()

    text = re.sub(
        r"[^a-z0-9+#./ -]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# FIND SKILL IN JOB
# ============================================================

def skill_in_job(skill, job_text):

    skill = normalize_text(skill)

    if not skill:
        return False

    # Exact phrase first
    if skill in job_text:
        return True

    # Handle common abbreviations
    aliases = {

        "mbbs": [
            "mbbs",
            "bachelor of medicine"
        ],

        "md": [
            " md ",
            "doctor of medicine"
        ],

        "bls": [
            "bls",
            "basic life support"
        ],

        "acls": [
            "acls",
            "advanced cardiac life support"
        ],

        "patient counselling": [
            "patient counselling",
            "patient counseling"
        ],

        "general medicine": [
            "general medicine",
            "general physician"
        ]
    }

    for alias in aliases.get(
        skill,
        []
    ):

        if alias in job_text:
            return True

    return False


# ============================================================
# DETERMINE JOB PROFESSION
# ============================================================

def detect_job_profession(row):

    title = normalize_text(
        row.get("job_title", "")
    )

    description = normalize_text(
        row.get("description", "")
    )

    category = normalize_text(
        row.get("category", "")
    )

    job_text = (
        title
        + " "
        + description
        + " "
        + category
    )

    scores = {}

    for profession, skills in (
        PROFESSION_SKILLS.items()
    ):

        score = 0

        for skill in skills:

            if skill_in_job(
                skill,
                job_text
            ):

                score += 1

        if score > 0:
            scores[profession] = score

    if not scores:
        return "General"

    return max(
        scores,
        key=scores.get
    )


# ============================================================
# SKILL MATCHING
# ============================================================

def calculate_match(
    candidate_skills,
    row
):

    title = normalize_text(
        row.get("job_title", "")
    )

    description = normalize_text(
        row.get("description", "")
    )

    category = normalize_text(
        row.get("category", "")
    )

    job_text = (
        title
        + " "
        + description
        + " "
        + category
    )

    matched = []
    missing = []

    for skill in candidate_skills:

        normalized_skill = normalize_text(
            skill
        )

        if skill_in_job(
            normalized_skill,
            job_text
        ):

            matched.append(
                skill
            )

        else:

            missing.append(
                skill
            )

    if not candidate_skills:

        return (
            0.0,
            matched,
            missing
        )

    percentage = (
        len(matched)
        / len(candidate_skills)
        * 100
    )

    return (
        percentage,
        matched,
        missing
    )


# ============================================================
# JOB TITLE RELEVANCE
# ============================================================

def title_relevance(
    candidate_skills,
    row
):

    title = normalize_text(
        row.get("job_title", "")
    )

    score = 0

    for skill in candidate_skills:

        skill = normalize_text(
            skill
        )

        if not skill:
            continue

        if skill in title:
            score += 2

    return score


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("        UNIVERSAL SKILL MATCHING")
    print("=" * 70)

    if not os.path.exists(
        INPUT_FILE
    ):

        print()
        print(
            "ERROR: Dynamic job dataset not found:"
        )

        print(
            INPUT_FILE
        )

        return

    print()
    print(
        "Loading dynamic real-world jobs..."
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Jobs loaded: {len(df)}"
    )

    print()
    print("=" * 70)
    print("CANDIDATE SKILLS")
    print("=" * 70)

    raw_skills = input(
        "\nEnter candidate skills separated by commas:\n> "
    ).strip()

    if not raw_skills:

        print(
            "ERROR: Skills are required."
        )

        return

    candidate_skills = [
        skill.strip()
        for skill in raw_skills.split(",")
        if skill.strip()
    ]

    print()
    print("Skills received:")

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Calculate matches
    # --------------------------------------------------------

    results = []

    print()
    print(
        "Calculating skill matches..."
    )

    for _, row in df.iterrows():

        match_percentage, matched, missing = (
            calculate_match(
                candidate_skills,
                row
            )
        )

        title_score = title_relevance(
            candidate_skills,
            row
        )

        profession = detect_job_profession(
            row
        )

        # ----------------------------------------------------
        # Final score
        # ----------------------------------------------------

        final_score = (
            match_percentage * 0.85
            + min(title_score * 5, 15)
        )

        result = row.to_dict()

        result[
            "detected_job_profession"
        ] = profession

        result[
            "skill_match_percentage"
        ] = round(
            match_percentage,
            2
        )

        result[
            "matched_skills"
        ] = ", ".join(
            matched
        )

        result[
            "missing_candidate_skills"
        ] = ", ".join(
            missing
        )

        result[
            "matched_skill_count"
        ] = len(matched)

        result[
            "missing_skill_count"
        ] = len(missing)

        result[
            "final_match_score"
        ] = round(
            final_score,
            2
        )

        results.append(
            result
        )

    result_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Remove clearly irrelevant jobs
    # --------------------------------------------------------

    result_df = result_df[
        result_df[
            "skill_match_percentage"
        ] > 0
    ].copy()

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    result_df = result_df.sort_values(
        [
            "final_match_score",
            "skill_match_percentage"
        ],
        ascending=False
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("UNIVERSAL SKILL MATCHING COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Original jobs: {len(df)}"
    )

    print(
        f"Relevant jobs: {len(result_df)}"
    )

    print()
    print("TOP 20 MATCHES")
    print("-" * 70)

    columns = [
        "job_title",
        "company",
        "location",
        "detected_job_profession",
        "skill_match_percentage",
        "matched_skills",
        "final_match_score"
    ]

    available = [
        column
        for column in columns
        if column in result_df.columns
    ]

    if result_df.empty:

        print(
            "No jobs matched the candidate skills."
        )

    else:

        print(
            result_df[
                available
            ].head(20).to_string(
                index=False
            )
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
        "STAGE 21C COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
