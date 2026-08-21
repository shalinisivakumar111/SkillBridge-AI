import os
import re
from collections import defaultdict

import pandas as pd


# ============================================================
# SKILLBRIDGE AI
# STAGE 21I - PRECISE ROLE MATCHING
# ============================================================

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
    "precise_role_matches.csv"
)


# ============================================================
# ROLE DEFINITIONS
# IMPORTANT:
# JOB TITLE HAS THE HIGHEST PRIORITY.
# DESCRIPTION IS NOT USED TO OVERRIDE THE JOB TITLE.
# ============================================================

ROLE_KEYWORDS = {
    "Doctor / Physician": [
        "doctor",
        "physician",
        "medical officer",
        "general practitioner",
        "general physician",
        "medical consultant",
        "consultant physician",
        "consultant -",
        "mbbs doctor",
        "md doctor",
        "mbbs,md",
        "mbbs/md",
        "resident doctor",
        "senior resident",
        "junior resident",
        "cardiologist",
        "dermatologist",
        "ophthalmologist",
        "psychiatrist",
        "paediatrician",
        "pediatrician",
        "gynaecologist",
        "gynecologist",
        "surgeon",
        "anaesthetist",
        "anesthetist",
        "radiologist",
        "oncologist",
        "neurologist",
        "dentist",
        "pathologist",
    ],

    "Nurse": [
        "nurse",
        "staff nurse",
        "registered nurse",
        "nursing officer",
        "nursing staff",
    ],

    "Physiotherapist": [
        "physiotherapist",
        "physio therapist",
        "physio",
        "physical therapist",
    ],

    "Medical Coder": [
        "medical coder",
        "medical coding",
        "medical coding specialist",
        "coding specialist",
    ],

    "Healthcare Professional": [
        "healthcare",
        "health care",
        "clinical",
        "hospital",
        "medical",
    ],

    "Software Developer": [
        "software developer",
        "software engineer",
        "python developer",
        "java developer",
        "full stack developer",
        "backend developer",
        "back end developer",
        "frontend developer",
        "front end developer",
        "web developer",
        "application developer",
    ],

    "Data Professional": [
        "data analyst",
        "data scientist",
        "data engineer",
        "business analyst",
        "data manager",
    ],

    "IT Support": [
        "it support",
        "technical support",
        "desktop support",
        "help desk",
        "helpdesk",
        "system administrator",
        "network administrator",
        "network engineer",
    ],

    "Teacher / Educator": [
        "teacher",
        "school teacher",
        "subject teacher",
        "lecturer",
        "professor",
        "trainer",
        "tutor",
        "faculty",
        "educator",
        "academic",
    ],

    "Sales Professional": [
        "sales executive",
        "sales representative",
        "sales officer",
        "sales manager",
        "business development executive",
        "business development manager",
        "business development",
        "account executive",
        "territory sales",
    ],

    "Marketing Professional": [
        "marketing executive",
        "marketing manager",
        "digital marketing",
        "marketing specialist",
        "seo",
        "social media manager",
        "brand manager",
    ],

    "Finance / Accounting": [
        "accountant",
        "account assistant",
        "accounts assistant",
        "accounts executive",
        "finance executive",
        "financial analyst",
        "accounts payable",
        "accounts receivable",
        "bookkeeper",
    ],

    "HR Professional": [
        "human resources",
        "hr executive",
        "hr manager",
        "hrbp",
        "recruiter",
        "recruitment",
        "talent acquisition",
    ],

    "Administration": [
        "office assistant",
        "office administrator",
        "administrative assistant",
        "administration executive",
        "executive assistant",
        "office executive",
        "computer operator",
        "data entry",
    ],

    "Customer Support": [
        "customer support",
        "customer service",
        "customer care",
        "support executive",
        "call center",
        "call centre",
    ],

    "Graphic Designer": [
        "graphic designer",
        "graphic design",
        "ui designer",
        "ux designer",
        "visual designer",
    ],

    "Hospitality Professional": [
        "hotel",
        "chef",
        "cook",
        "restaurant",
        "hospitality",
        "housekeeping",
        "front office",
    ],

    "Logistics Professional": [
        "logistics",
        "warehouse",
        "supply chain",
        "delivery executive",
        "fleet",
        "operations executive",
    ],

    "Engineer": [
        "engineer",
        "engineering",
        "electrical engineer",
        "mechanical engineer",
        "civil engineer",
        "electronics engineer",
    ],
}


# ============================================================
# SKILLS
# ============================================================

SKILL_ALIASES = {
    "mbbs": ["mbbs"],
    "md": ["md"],
    "general medicine": ["general medicine", "general physician"],
    "doctor": ["doctor", "physician"],
    "patient assessment": ["patient assessment"],
    "diagnosis": ["diagnosis", "diagnostic"],
    "emergency care": ["emergency care", "emergency medicine"],
    "bls": ["bls"],
    "acls": ["acls"],
    "clinical documentation": [
        "clinical documentation",
        "medical documentation"
    ],
    "patient counselling": [
        "patient counselling",
        "patient counseling"
    ],
    "patient care": ["patient care"],
    "medical coding": [
        "medical coding",
        "medical coder"
    ],
    "medical records": [
        "medical records",
        "medical record"
    ],
    "nursing": ["nursing", "nurse"],
    "communication": ["communication"],
    "sales": ["sales"],
    "excel": ["excel", "microsoft excel"],
    "git": ["git", "github"],
    "physiotherapy": [
        "physiotherapy",
        "physiotherapist"
    ],
    "radiology": ["radiology", "radiologist"],
    "healthcare management": [
        "healthcare management",
        "health care management"
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):
    if pd.isna(value):
        return ""

    value = str(value).lower().strip()
    value = re.sub(r"\s+", " ", value)

    return value


def contains_keyword(text, keyword):
    text = normalize(text)
    keyword = normalize(keyword)

    if not keyword:
        return False

    # Word boundary for short/simple keywords
    if len(keyword) <= 4 and " " not in keyword:
        return bool(
            re.search(
                rf"\b{re.escape(keyword)}\b",
                text
            )
        )

    return keyword in text


# ============================================================
# CANDIDATE ROLE
# ============================================================

def detect_candidate_role(skills):
    text = " ".join(normalize(x) for x in skills)

    doctor_signals = [
        "mbbs",
        "md",
        "doctor",
        "physician",
        "general medicine",
        "diagnosis",
        "patient assessment",
        "emergency care",
        "bls",
        "acls",
    ]

    nurse_signals = [
        "nurse",
        "nursing",
        "patient care",
    ]

    developer_signals = [
        "python",
        "java",
        "javascript",
        "software development",
        "programming",
        "react",
        "django",
        "flask",
    ]

    teacher_signals = [
        "teaching",
        "teacher",
        "education",
        "lesson planning",
        "classroom",
    ]

    sales_signals = [
        "sales",
        "business development",
        "lead generation",
    ]

    scores = {
        "Doctor / Physician": sum(
            contains_keyword(text, x)
            for x in doctor_signals
        ),
        "Nurse": sum(
            contains_keyword(text, x)
            for x in nurse_signals
        ),
        "Software Developer": sum(
            contains_keyword(text, x)
            for x in developer_signals
        ),
        "Teacher / Educator": sum(
            contains_keyword(text, x)
            for x in teacher_signals
        ),
        "Sales Professional": sum(
            contains_keyword(text, x)
            for x in sales_signals
        ),
    }

    best_role = max(scores, key=scores.get)

    if scores[best_role] == 0:
        return "Other"

    return best_role


# ============================================================
# JOB ROLE DETECTION
#
# VERY IMPORTANT:
# 1. JOB TITLE decides the role.
# 2. Category can support the decision.
# 3. Description cannot turn an unrelated title into a doctor.
# ============================================================

def detect_job_role(job_title, category=""):
    title = normalize(job_title)
    category = normalize(category)

    # --------------------------------------------------------
    # Doctor-specific TITLE matching
    # --------------------------------------------------------

    doctor_title_patterns = [
        r"\bdoctor\b",
        r"\bphysician\b",
        r"\bmedical officer\b",
        r"\bgeneral practitioner\b",
        r"\bgeneral physician\b",
        r"\bmbbs doctor\b",
        r"\bmd doctor\b",
        r"\bconsultant physician\b",
        r"\bresident doctor\b",
        r"\bsenior resident\b",
        r"\bjunior resident\b",
        r"\bcardiologist\b",
        r"\bdermatologist\b",
        r"\bophthalmologist\b",
        r"\bpsychiatrist\b",
        r"\bpaediatrician\b",
        r"\bpediatrician\b",
        r"\bgynaecologist\b",
        r"\bgynecologist\b",
        r"\bsurgeon\b",
        r"\bradiologist\b",
        r"\boncologist\b",
        r"\bneurologist\b",
        r"\bdentist\b",
        r"\bpathologist\b",
        r"\bmedical consultant\b",
        r"\bconsultant - ophthalmologist\b",
    ]

    for pattern in doctor_title_patterns:
        if re.search(pattern, title):
            return "Doctor / Physician"

    # --------------------------------------------------------
    # Nurse
    # --------------------------------------------------------

    nurse_patterns = [
        r"\bnurse\b",
        r"\bstaff nurse\b",
        r"\bregistered nurse\b",
        r"\bnursing officer\b",
    ]

    for pattern in nurse_patterns:
        if re.search(pattern, title):
            return "Nurse"

    # --------------------------------------------------------
    # Physiotherapist
    # --------------------------------------------------------

    if (
        "physiotherapist" in title
        or "physical therapist" in title
    ):
        return "Physiotherapist"

    # --------------------------------------------------------
    # Medical Coding
    # --------------------------------------------------------

    if (
        "medical coder" in title
        or "medical coding" in title
    ):
        return "Medical Coder"

    # --------------------------------------------------------
    # Software
    # --------------------------------------------------------

    software_patterns = [
        "software developer",
        "software engineer",
        "python developer",
        "java developer",
        "full stack developer",
        "backend developer",
        "frontend developer",
        "web developer",
        "application developer",
    ]

    for keyword in software_patterns:
        if keyword in title:
            return "Software Developer"

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    data_patterns = [
        "data analyst",
        "data scientist",
        "data engineer",
        "business analyst",
        "data manager",
    ]

    for keyword in data_patterns:
        if keyword in title:
            return "Data Professional"

    # --------------------------------------------------------
    # IT Support
    # --------------------------------------------------------

    it_patterns = [
        "it support",
        "technical support",
        "desktop support",
        "help desk",
        "helpdesk",
        "system administrator",
        "network administrator",
        "network engineer",
    ]

    for keyword in it_patterns:
        if keyword in title:
            return "IT Support"

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education_patterns = [
        "teacher",
        "lecturer",
        "professor",
        "tutor",
        "faculty",
        "educator",
        "academic",
    ]

    for keyword in education_patterns:
        if keyword in title:
            return "Teacher / Educator"

    # --------------------------------------------------------
    # Sales
    # --------------------------------------------------------

    sales_patterns = [
        "sales executive",
        "sales representative",
        "sales officer",
        "sales manager",
        "business development executive",
        "business development manager",
        "business development",
        "account executive",
        "territory sales",
    ]

    for keyword in sales_patterns:
        if keyword in title:
            return "Sales Professional"

    # --------------------------------------------------------
    # Marketing
    # --------------------------------------------------------

    marketing_patterns = [
        "marketing executive",
        "marketing manager",
        "digital marketing",
        "marketing specialist",
        "seo",
        "social media manager",
        "brand manager",
    ]

    for keyword in marketing_patterns:
        if keyword in title:
            return "Marketing Professional"

    # --------------------------------------------------------
    # Finance
    # --------------------------------------------------------

    finance_patterns = [
        "accountant",
        "account assistant",
        "accounts assistant",
        "accounts executive",
        "finance executive",
        "financial analyst",
        "accounts payable",
        "accounts receivable",
        "bookkeeper",
    ]

    for keyword in finance_patterns:
        if keyword in title:
            return "Finance / Accounting"

    # --------------------------------------------------------
    # HR
    # --------------------------------------------------------

    hr_patterns = [
        "human resources",
        "hr executive",
        "hr manager",
        "hrbp",
        "recruiter",
        "recruitment",
        "talent acquisition",
    ]

    for keyword in hr_patterns:
        if keyword in title:
            return "HR Professional"

    # --------------------------------------------------------
    # Administration
    # --------------------------------------------------------

    admin_patterns = [
        "office assistant",
        "office administrator",
        "administrative assistant",
        "administration executive",
        "executive assistant",
        "office executive",
        "computer operator",
        "data entry",
    ]

    for keyword in admin_patterns:
        if keyword in title:
            return "Administration"

    # --------------------------------------------------------
    # Customer Support
    # --------------------------------------------------------

    support_patterns = [
        "customer support",
        "customer service",
        "customer care",
        "support executive",
        "call center",
        "call centre",
    ]

    for keyword in support_patterns:
        if keyword in title:
            return "Customer Support"

    # --------------------------------------------------------
    # Graphic Design
    # --------------------------------------------------------

    if (
        "graphic designer" in title
        or "graphic design" in title
        or "ui designer" in title
        or "ux designer" in title
    ):
        return "Graphic Designer"

    # --------------------------------------------------------
    # Hospitality
    # --------------------------------------------------------

    hospitality_patterns = [
        "chef",
        "cook",
        "hospitality",
        "housekeeping",
        "front office",
        "hotel",
        "restaurant",
    ]

    for keyword in hospitality_patterns:
        if keyword in title:
            return "Hospitality Professional"

    # --------------------------------------------------------
    # Logistics
    # --------------------------------------------------------

    logistics_patterns = [
        "logistics",
        "warehouse",
        "supply chain",
        "delivery executive",
        "fleet",
    ]

    for keyword in logistics_patterns:
        if keyword in title:
            return "Logistics Professional"

    # --------------------------------------------------------
    # Engineering
    # --------------------------------------------------------

    if (
        "engineer" in title
        or "engineering" in title
    ):
        return "Engineer"

    return "Other"


# ============================================================
# SKILL EXTRACTION FROM JOB
# ============================================================

def extract_job_skills(row):
    title = normalize(row.get("job_title", ""))
    description = normalize(row.get("description", ""))
    category = normalize(row.get("category", ""))

    # Use title + description for SKILLS,
    # but NOT for role classification.
    text = f"{title} {description} {category}"

    found = []

    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if contains_keyword(text, alias):
                found.append(canonical)
                break

    return found


# ============================================================
# MATCH SKILLS
# ============================================================

def calculate_skill_match(candidate_skills, job_skills):
    candidate = set(
        normalize(x)
        for x in candidate_skills
    )

    job = set(
        normalize(x)
        for x in job_skills
    )

    if not job:
        return 0.0, []

    matched = sorted(candidate.intersection(job))

    percentage = (
        len(matched) / len(candidate) * 100
        if candidate
        else 0
    )

    return round(percentage, 2), matched


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("         PRECISE ROLE MATCHING")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):
        print()
        print("ERROR: Input file not found:")
        print(INPUT_FILE)
        return

    df = pd.read_csv(INPUT_FILE)

    print()
    print(f"Real jobs loaded: {len(df)}")

    print()
    print("=" * 70)
    print("CANDIDATE")
    print("=" * 70)

    raw = input(
        "\nEnter candidate skills separated by commas:\n> "
    )

    candidate_skills = [
        x.strip()
        for x in raw.split(",")
        if x.strip()
    ]

    print("\nCandidate skills:")

    for skill in candidate_skills:
        print(f"  ✓ {skill}")

    candidate_role = detect_candidate_role(candidate_skills)

    print()
    print("Detected candidate role:")
    print(f"  ✓ {candidate_role}")

    results = []

    for _, row in df.iterrows():

        title = row.get("job_title", "")
        category = row.get("category", "")

        job_role = detect_job_role(
            title,
            category
        )

        job_skills = extract_job_skills(row)

        skill_percentage, matched = calculate_skill_match(
            candidate_skills,
            job_skills
        )

        # ----------------------------------------------------
        # ROLE MATCH
        # ----------------------------------------------------

        exact_role = (
            candidate_role != "Other"
            and job_role == candidate_role
        )

        # Strong role bonus
        if exact_role:
            role_score = 50
        elif job_role == "Other":
            role_score = 5
        else:
            role_score = 0

        # Skill contribution
        skill_score = skill_percentage * 0.5

        final_score = round(
            role_score + skill_score,
            2
        )

        # ----------------------------------------------------
        # ROLE-SPECIFIC GAPS
        # ----------------------------------------------------

        role_skill_requirements = {
            "Doctor / Physician": [
                "patient care",
                "medical records",
                "medical coding",
                "clinical documentation",
            ],

            "Nurse": [
                "patient care",
                "nursing",
                "communication",
                "clinical documentation",
            ],

            "Software Developer": [
                "git",
                "python",
                "javascript",
                "testing",
            ],

            "Teacher / Educator": [
                "communication",
                "training",
                "assessment",
            ],

            "Sales Professional": [
                "sales",
                "communication",
                "business development",
            ],

            "Finance / Accounting": [
                "excel",
                "accounting",
                "documentation",
            ],
        }

        required = role_skill_requirements.get(
            job_role,
            []
        )

        candidate_normalized = set(
            normalize(x)
            for x in candidate_skills
        )

        gaps = [
            skill
            for skill in required
            if skill not in candidate_normalized
        ]

        results.append({
            "job_title": title,
            "company": row.get("company", ""),
            "location": row.get("location", ""),
            "detected_job_role": job_role,
            "skill_match_percentage": skill_percentage,
            "matched_skills": ", ".join(matched),
            "role_skill_gaps": ", ".join(gaps),
            "exact_role_match": exact_role,
            "final_precise_score": final_score,
            "redirect_url": row.get("redirect_url", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "company_address": row.get("company_address", ""),
        })

    result_df = pd.DataFrame(results)

    # ========================================================
    # IMPORTANT:
    # EXACT ROLE JOBS FIRST.
    # UNRELATED ROLES MUST NOT FLOOD TOP RESULTS.
    # ========================================================

    result_df = result_df.sort_values(
        by=[
            "exact_role_match",
            "final_precise_score",
            "skill_match_percentage",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    )

    # Save everything
    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    exact_count = int(
        result_df["exact_role_match"].sum()
    )

    print()
    print("=" * 70)
    print("PRECISE ROLE MATCHING COMPLETE")
    print("=" * 70)

    print()
    print(f"Candidate role: {candidate_role}")
    print(f"Exact-role jobs: {exact_count}")
    print(f"Other jobs retained: {len(result_df) - exact_count}")

    # ========================================================
    # DISPLAY ONLY RELEVANT JOBS
    # ========================================================

    exact_jobs = result_df[
        result_df["exact_role_match"] == True
    ]

    if len(exact_jobs) == 0:

        # Fallback:
        # show jobs with meaningful skill matches
        display_df = result_df[
            result_df["skill_match_percentage"] > 0
        ].head(20)

    else:

        display_df = exact_jobs.head(20)

    print()
    print("TOP RELEVANT JOBS")
    print("-" * 70)

    if len(display_df) == 0:

        print("No relevant jobs found.")

    else:

        print(
            display_df[
                [
                    "job_title",
                    "company",
                    "location",
                    "detected_job_role",
                    "skill_match_percentage",
                    "matched_skills",
                    "role_skill_gaps",
                    "final_precise_score",
                ]
            ].to_string(index=False)
        )

    print()
    print("Saved to:")
    print(OUTPUT_FILE)

    print()
    print("=" * 70)
    print("STAGE 21I COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
