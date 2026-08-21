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
    "enriched_real_jobs.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "universal_matched_jobs.csv"
)


# ============================================================
# SKILL / PROFESSION KNOWLEDGE
# ============================================================

PROFESSION_RULES = {

    "Healthcare": {
        "skills": [
            "doctor",
            "medical",
            "medicine",
            "mbbs",
            "md",
            "ms",
            "general medicine",
            "physician",
            "nursing",
            "nurse",
            "pharmacist",
            "pharmacy",
            "clinical",
            "patient care",
            "diagnosis",
            "surgery",
            "surgical",
            "emergency care",
            "healthcare",
            "hospital",
            "laboratory",
            "lab technician",
            "radiology",
            "physiotherapy",
            "physiotherapist"
        ],
        "jobs": [
            "doctor",
            "medical officer",
            "physician",
            "general physician",
            "resident doctor",
            "medical",
            "nurse",
            "staff nurse",
            "pharmacist",
            "clinical",
            "healthcare",
            "lab technician",
            "radiology technician",
            "physiotherapist"
        ]
    },

    "IT & Software": {
        "skills": [
            "python",
            "java",
            "javascript",
            "typescript",
            "react",
            "angular",
            "node",
            "sql",
            "flask",
            "django",
            "git",
            "software",
            "programming",
            "coding",
            "machine learning",
            "artificial intelligence",
            "ai",
            "data science",
            "data analyst",
            "cloud",
            "aws",
            "azure",
            "devops",
            "cybersecurity",
            "networking",
            "computer science",
            "web development"
        ],
        "jobs": [
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
            "ai engineer",
            "devops",
            "cloud engineer",
            "cybersecurity",
            "it support",
            "system administrator"
        ]
    },

    "Education": {
        "skills": [
            "teaching",
            "teacher",
            "education",
            "lesson planning",
            "classroom management",
            "mathematics",
            "physics",
            "chemistry",
            "biology",
            "english teaching",
            "tutor",
            "training",
            "academic"
        ],
        "jobs": [
            "teacher",
            "school teacher",
            "primary teacher",
            "secondary teacher",
            "lecturer",
            "professor",
            "tutor",
            "academic",
            "trainer",
            "teaching"
        ]
    },

    "Finance & Accounting": {
        "skills": [
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
        "jobs": [
            "accountant",
            "junior accountant",
            "accounts assistant",
            "account assistant",
            "finance executive",
            "financial analyst",
            "bookkeeper",
            "auditor",
            "tax assistant",
            "payroll"
        ]
    },

    "Sales & Retail": {
        "skills": [
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
        "jobs": [
            "sales executive",
            "sales representative",
            "business development",
            "retail",
            "store manager",
            "sales manager",
            "customer service",
            "customer support",
            "cashier"
        ]
    },

    "Marketing": {
        "skills": [
            "digital marketing",
            "marketing",
            "seo",
            "sem",
            "social media",
            "content writing",
            "content marketing",
            "advertising",
            "branding",
            "email marketing",
            "google ads"
        ],
        "jobs": [
            "digital marketing",
            "marketing executive",
            "marketing manager",
            "seo",
            "social media",
            "content writer",
            "content marketing",
            "brand manager"
        ]
    },

    "Design & Creative": {
        "skills": [
            "graphic design",
            "graphic designer",
            "photoshop",
            "illustrator",
            "figma",
            "ui design",
            "ux design",
            "video editing",
            "photography",
            "creativity"
        ],
        "jobs": [
            "graphic designer",
            "ui designer",
            "ux designer",
            "web designer",
            "visual designer",
            "video editor",
            "photographer",
            "creative designer"
        ]
    },

    "Engineering & Technical": {
        "skills": [
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
        "jobs": [
            "engineer",
            "mechanical engineer",
            "electrical engineer",
            "electronics engineer",
            "civil engineer",
            "technician",
            "maintenance technician",
            "machine operator",
            "quality engineer"
        ]
    },

    "Skilled Trades": {
        "skills": [
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
        "jobs": [
            "electrician",
            "plumber",
            "carpenter",
            "welder",
            "mechanic",
            "technician",
            "repair technician",
            "tailor",
            "beautician"
        ]
    },

    "Logistics & Transport": {
        "skills": [
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
        "jobs": [
            "driver",
            "delivery executive",
            "delivery driver",
            "logistics",
            "warehouse associate",
            "warehouse executive",
            "inventory executive",
            "transport"
        ]
    },

    "Hospitality": {
        "skills": [
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
        "jobs": [
            "chef",
            "cook",
            "hotel staff",
            "restaurant staff",
            "front office executive",
            "receptionist",
            "housekeeping",
            "hospitality"
        ]
    },

    "Administration": {
        "skills": [
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
        "jobs": [
            "office assistant",
            "office administrator",
            "administrative assistant",
            "data entry operator",
            "computer operator",
            "receptionist",
            "admin executive"
        ]
    },

    "Manufacturing": {
        "skills": [
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
        "jobs": [
            "production operator",
            "machine operator",
            "production executive",
            "quality inspector",
            "quality control",
            "factory worker",
            "manufacturing"
        ]
    },

    "Agriculture": {
        "skills": [
            "agriculture",
            "farming",
            "agricultural",
            "horticulture",
            "irrigation",
            "crop",
            "livestock",
            "dairy",
            "farm management"
        ],
        "jobs": [
            "farm worker",
            "agriculture officer",
            "agricultural technician",
            "farm manager",
            "horticulture",
            "dairy worker"
        ]
    }
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9+#.\-/ ]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    return value


def normalize_skill(value):
    value = normalize_text(value)

    replacements = {
        "ms office": "ms office",
        "microsoft office": "ms office",
        "general physician": "general physician",
        "general medicine": "general medicine",
        "machine learning": "machine learning",
        "artificial intelligence": "artificial intelligence",
        "data science": "data science",
        "customer support": "customer support",
        "customer service": "customer service"
    }

    return replacements.get(value, value)


# ============================================================
# CANDIDATE PROFESSION DETECTION
# ============================================================

def detect_professions(candidate_skills):

    normalized_skills = [
        normalize_skill(skill)
        for skill in candidate_skills
        if str(skill).strip()
    ]

    detected = []

    for profession, rule in PROFESSION_RULES.items():

        score = 0
        matched = []

        for skill in normalized_skills:

            for rule_skill in rule["skills"]:

                rule_skill_normalized = normalize_text(
                    rule_skill
                )

                if (
                    skill == rule_skill_normalized
                    or rule_skill_normalized in skill
                    or skill in rule_skill_normalized
                ):
                    score += 1
                    matched.append(skill)
                    break

        if score > 0:

            detected.append({
                "profession": profession,
                "score": score,
                "matched_skills": sorted(
                    set(matched)
                )
            })

    detected.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return detected


# ============================================================
# JOB RELEVANCE
# ============================================================

def calculate_job_relevance(row, detected_professions):

    job_text = " ".join([
        normalize_text(row.get("job_title", "")),
        normalize_text(row.get("description", "")),
        normalize_text(row.get("category", "")),
        normalize_text(row.get("category_tag", ""))
    ])

    score = 0
    matched_professions = []

    for item in detected_professions:

        profession = item["profession"]

        rule = PROFESSION_RULES.get(
            profession,
            {}
        )

        for job_keyword in rule.get("jobs", []):

            keyword = normalize_text(
                job_keyword
            )

            if keyword and keyword in job_text:

                score += 1

                if profession not in matched_professions:
                    matched_professions.append(
                        profession
                    )

    return score, matched_professions


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       UNIVERSAL JOB MATCHING ENGINE")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print()
        print("ERROR: Real job dataset not found.")
        print()
        print(INPUT_FILE)
        return

    print()
    print("Loading real-world jobs...")

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Jobs loaded: {len(df)}"
    )

    print()
    print("=" * 70)
    print("ENTER CANDIDATE SKILLS")
    print("=" * 70)

    raw_skills = input(
        "\nEnter candidate skills separated by commas:\n> "
    ).strip()

    if not raw_skills:

        print()
        print("ERROR: No skills entered.")
        return

    candidate_skills = [
        skill.strip()
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
    # Detect professions
    # --------------------------------------------------------

    detected = detect_professions(
        candidate_skills
    )

    print()
    print("=" * 70)
    print("DETECTED JOB CATEGORIES")
    print("=" * 70)

    if not detected:

        print()
        print(
            "No specific profession detected."
        )

        print(
            "Using General/All Jobs mode."
        )

        df["job_relevance_score"] = 0
        df["matched_professions"] = ""

        result = df.copy()

    else:

        for number, item in enumerate(
            detected,
            start=1
        ):

            print()
            print(
                f"{number}. "
                f"{item['profession']}"
            )

            print(
                f"   Evidence score: "
                f"{item['score']}"
            )

            print(
                "   Matched skills: "
                + ", ".join(
                    item["matched_skills"]
                )
            )

        # ----------------------------------------------------
        # Score jobs
        # ----------------------------------------------------

        relevance_scores = []
        matched_professions = []

        for _, row in df.iterrows():

            score, professions = (
                calculate_job_relevance(
                    row,
                    detected
                )
            )

            relevance_scores.append(
                score
            )

            matched_professions.append(
                ", ".join(professions)
            )

        result = df.copy()

        result[
            "job_relevance_score"
        ] = relevance_scores

        result[
            "matched_professions"
        ] = matched_professions

        # Keep relevant jobs first
        result = result.sort_values(
            [
                "job_relevance_score"
            ],
            ascending=False
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("UNIVERSAL JOB MATCHING COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Candidate skills: "
        f"{len(candidate_skills)}"
    )

    print(
        f"Jobs evaluated: "
        f"{len(result)}"
    )

    if detected:

        print(
            f"Detected categories: "
            f"{len(detected)}"
        )

    print()
    print("Top relevant jobs:")

    preview_columns = [
        "job_title",
        "company",
        "location",
        "job_relevance_score",
        "matched_professions"
    ]

    available_columns = [
        column
        for column in preview_columns
        if column in result.columns
    ]

    print()

    print(
        result[
            available_columns
        ].head(15).to_string(
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


if __name__ == "__main__":
    main()
