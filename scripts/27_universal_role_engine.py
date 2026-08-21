import os
import re
from collections import defaultdict

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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
    "universal_role_matches.csv"
)


# ============================================================
# UNIVERSAL JOB FAMILIES
# ============================================================

JOB_FAMILIES = {

    "Healthcare": [
        "healthcare",
        "medical",
        "doctor",
        "physician",
        "nurse",
        "nursing",
        "pharmacist",
        "pharmacy",
        "dentist",
        "dental",
        "physiotherapist",
        "physiotherapy",
        "medical coder",
        "medical coding",
        "hospital",
        "clinical",
        "healthcare"
    ],

    "IT & Software": [
        "software",
        "developer",
        "programmer",
        "engineering",
        "technology",
        "it ",
        "information technology",
        "cloud",
        "devops",
        "cyber",
        "database",
        "network",
        "web developer",
        "python",
        "java",
        "javascript",
        "data engineer"
    ],

    "Data & Analytics": [
        "data analyst",
        "data scientist",
        "analytics",
        "business analyst",
        "machine learning",
        "artificial intelligence",
        "data science",
        "bi analyst"
    ],

    "Finance & Accounting": [
        "accounting",
        "accountant",
        "accounts",
        "finance",
        "financial",
        "audit",
        "auditor",
        "tax",
        "payroll",
        "bookkeeping"
    ],

    "Sales & Business": [
        "sales",
        "business development",
        "account executive",
        "sales executive",
        "sales manager",
        "business development manager",
        "account manager",
        "key account"
    ],

    "Customer Service": [
        "customer service",
        "customer support",
        "customer care",
        "support executive",
        "call center",
        "contact center"
    ],

    "Marketing": [
        "marketing",
        "digital marketing",
        "seo",
        "sem",
        "advertising",
        "content marketing",
        "social media",
        "brand"
    ],

    "Education": [
        "teacher",
        "teaching",
        "lecturer",
        "professor",
        "faculty",
        "tutor",
        "education",
        "school",
        "academic"
    ],

    "Engineering": [
        "engineer",
        "engineering",
        "civil",
        "mechanical",
        "electrical",
        "electronics",
        "structural",
        "design engineer",
        "project engineer"
    ],

    "Administration": [
        "admin",
        "administration",
        "office assistant",
        "executive assistant",
        "office administrator",
        "office manager",
        "data entry"
    ],

    "Human Resources": [
        "hr ",
        "human resources",
        "recruitment",
        "recruiter",
        "talent acquisition",
        "hrbp",
        "people operations"
    ],

    "Retail": [
        "retail",
        "store",
        "shop",
        "retail operations",
        "store manager",
        "cashier",
        "merchandising"
    ],

    "Creative & Design": [
        "graphic designer",
        "graphic design",
        "designer",
        "ui designer",
        "ux designer",
        "creative",
        "interior designer",
        "visual designer"
    ],

    "Manufacturing": [
        "manufacturing",
        "production",
        "factory",
        "assembly",
        "production manager",
        "quality control",
        "quality assurance",
        "machine operator"
    ],

    "Logistics & Supply Chain": [
        "logistics",
        "supply chain",
        "warehouse",
        "inventory",
        "procurement",
        "dispatch",
        "transport"
    ],

    "Hospitality & Food": [
        "hotel",
        "hospitality",
        "restaurant",
        "chef",
        "cook",
        "food service",
        "housekeeping",
        "front office"
    ],

    "Construction": [
        "construction",
        "site engineer",
        "site supervisor",
        "civil works",
        "building",
        "contractor"
    ],

    "Legal": [
        "lawyer",
        "legal",
        "attorney",
        "advocate",
        "legal counsel",
        "paralegal"
    ],

    "Agriculture": [
        "agriculture",
        "farmer",
        "farming",
        "horticulture",
        "agri",
        "livestock",
        "dairy"
    ],

    "Transport & Delivery": [
        "driver",
        "delivery",
        "chauffeur",
        "transport",
        "fleet",
        "rider"
    ],

    "Skilled Trades": [
        "electrician",
        "plumber",
        "carpenter",
        "welder",
        "mechanic",
        "technician",
        "repair",
        "maintenance"
    ]
}


# ============================================================
# ROLE-SPECIFIC SKILLS
# ============================================================

FAMILY_SKILLS = {

    "Healthcare": [
        "MBBS",
        "MD",
        "Diagnosis",
        "Patient Assessment",
        "Patient Care",
        "Emergency Care",
        "BLS",
        "ACLS",
        "Clinical Documentation",
        "Patient Counselling",
        "Medical Coding",
        "Medical Records",
        "Clinical Research",
        "Pharmacology",
        "Healthcare Management"
    ],

    "IT & Software": [
        "Python",
        "Java",
        "JavaScript",
        "SQL",
        "Git",
        "React",
        "Node.js",
        "AWS",
        "Azure",
        "Docker",
        "Linux",
        "Networking"
    ],

    "Data & Analytics": [
        "Python",
        "SQL",
        "Excel",
        "Statistics",
        "Data Analysis",
        "Power BI",
        "Tableau",
        "Machine Learning"
    ],

    "Finance & Accounting": [
        "Accounting",
        "Excel",
        "Tally",
        "GST",
        "Bookkeeping",
        "Auditing",
        "Taxation",
        "Payroll",
        "Financial Analysis"
    ],

    "Sales & Business": [
        "Sales",
        "Communication",
        "Negotiation",
        "Business Development",
        "Customer Service",
        "CRM",
        "Lead Generation"
    ],

    "Customer Service": [
        "Communication",
        "Customer Service",
        "Customer Support",
        "Problem Solving",
        "CRM",
        "Email Support"
    ],

    "Marketing": [
        "Digital Marketing",
        "SEO",
        "SEM",
        "Social Media Marketing",
        "Content Writing",
        "Google Ads",
        "Email Marketing"
    ],

    "Education": [
        "Teaching",
        "Communication",
        "Lesson Planning",
        "Classroom Management",
        "Assessment",
        "Training",
        "Curriculum Development"
    ],

    "Engineering": [
        "CAD",
        "AutoCAD",
        "Engineering",
        "Project Management",
        "Quality Control",
        "Troubleshooting",
        "Design"
    ],

    "Administration": [
        "MS Office",
        "Excel",
        "Data Entry",
        "Documentation",
        "Communication",
        "Office Management"
    ],

    "Human Resources": [
        "Recruitment",
        "Talent Acquisition",
        "HR",
        "Communication",
        "Payroll",
        "Employee Relations"
    ],

    "Retail": [
        "Customer Service",
        "Sales",
        "Inventory",
        "Merchandising",
        "Cash Handling",
        "Retail Operations"
    ],

    "Creative & Design": [
        "Graphic Design",
        "Photoshop",
        "Illustrator",
        "Figma",
        "UI Design",
        "UX Design",
        "Video Editing"
    ],

    "Manufacturing": [
        "Production",
        "Manufacturing",
        "Quality Control",
        "Machine Operation",
        "Maintenance",
        "Safety"
    ],

    "Logistics & Supply Chain": [
        "Logistics",
        "Supply Chain",
        "Inventory Management",
        "Warehouse Management",
        "Procurement",
        "Dispatch"
    ],

    "Hospitality & Food": [
        "Cooking",
        "Food Service",
        "Hotel Management",
        "Housekeeping",
        "Customer Service",
        "Front Office"
    ],

    "Construction": [
        "Construction",
        "Civil Engineering",
        "Site Management",
        "Safety",
        "AutoCAD",
        "Project Management"
    ],

    "Legal": [
        "Law",
        "Legal Research",
        "Contract Management",
        "Legal Documentation",
        "Compliance"
    ],

    "Agriculture": [
        "Agriculture",
        "Farming",
        "Crop Management",
        "Irrigation",
        "Horticulture"
    ],

    "Transport & Delivery": [
        "Driving",
        "Navigation",
        "Road Safety",
        "Vehicle Maintenance",
        "Delivery"
    ],

    "Skilled Trades": [
        "Electrical",
        "Plumbing",
        "Welding",
        "Carpentry",
        "Mechanical",
        "Maintenance",
        "Troubleshooting"
    ]
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):

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
# DETECT FAMILY FROM JOB
# ============================================================

def detect_job_family(row):

    title = normalize(
        row.get("job_title", "")
    )

    category = normalize(
        row.get("category", "")
    )

    category_tag = normalize(
        row.get("category_tag", "")
    )

    description = normalize(
        row.get("description", "")
    )

    # Title is strongest signal
    scores = defaultdict(int)

    for family, keywords in JOB_FAMILIES.items():

        for keyword in keywords:

            keyword = normalize(keyword)

            if not keyword:
                continue

            if keyword in title:
                scores[family] += 10

            elif keyword in category:
                scores[family] += 6

            elif keyword in category_tag:
                scores[family] += 6

            elif keyword in description:
                scores[family] += 1

    if not scores:
        return "Other"

    best_family = max(
        scores,
        key=scores.get
    )

    if scores[best_family] <= 0:
        return "Other"

    return best_family


# ============================================================
# DETECT CANDIDATE FAMILY
# ============================================================

def detect_candidate_family(
    candidate_skills
):

    text = " ".join(
        normalize(x)
        for x in candidate_skills
    )

    scores = {}

    for family, keywords in JOB_FAMILIES.items():

        score = 0

        for keyword in keywords:

            keyword = normalize(keyword)

            if keyword in text:
                score += 5

        for skill in FAMILY_SKILLS.get(
            family,
            []
        ):

            if normalize(skill) in text:
                score += 3

        scores[family] = score

    if not scores:
        return "Other"

    best = max(
        scores,
        key=scores.get
    )

    if scores[best] == 0:
        return "Other"

    return best


# ============================================================
# SKILL MATCH
# ============================================================

def skill_in_text(
    skill,
    text
):

    skill = normalize(skill)

    if not skill:
        return False

    if skill in text:
        return True

    aliases = {

        "patient counselling": [
            "patient counselling",
            "patient counseling"
        ],

        "medical coding": [
            "medical coding",
            "medical coder"
        ],

        "medical records": [
            "medical records",
            "medical record"
        ],

        "general medicine": [
            "general medicine",
            "general physician"
        ],

        "clinical documentation": [
            "clinical documentation"
        ],

        "customer service": [
            "customer service",
            "customer support"
        ],

        "digital marketing": [
            "digital marketing"
        ],

        "data analysis": [
            "data analysis",
            "data analyst"
        ],

        "machine learning": [
            "machine learning"
        ],

        "artificial intelligence": [
            "artificial intelligence",
            "ai"
        ]
    }

    for alias in aliases.get(
        skill,
        []
    ):

        if alias in text:
            return True

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("        UNIVERSAL ROLE ENGINE")
    print("=" * 70)

    if not os.path.exists(
        INPUT_FILE
    ):

        print()
        print(
            "ERROR: Dataset not found:"
        )

        print(INPUT_FILE)

        return

    df = pd.read_csv(
        INPUT_FILE
    )

    print()
    print(
        f"Real jobs loaded: {len(df)}"
    )

    print()
    print("=" * 70)
    print("CANDIDATE SKILLS")
    print("=" * 70)

    raw = input(
        "\nEnter candidate skills separated by commas:\n> "
    ).strip()

    if not raw:

        print(
            "ERROR: Candidate skills required."
        )

        return

    candidate_skills = [
        x.strip()
        for x in raw.split(",")
        if x.strip()
    ]

    print()
    print(
        "Skills received:"
    )

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Candidate family
    # --------------------------------------------------------

    candidate_family = detect_candidate_family(
        candidate_skills
    )

    print()
    print(
        "Detected candidate job family:"
    )

    print(
        f"  ✓ {candidate_family}"
    )

    # --------------------------------------------------------
    # Normalize candidate skills
    # --------------------------------------------------------

    candidate_normalized = {
        normalize(x)
        for x in candidate_skills
    }

    # --------------------------------------------------------
    # Match every real job
    # --------------------------------------------------------

    output = []

    for _, row in df.iterrows():

        job_family = detect_job_family(
            row
        )

        title = normalize(
            row.get(
                "job_title",
                ""
            )
        )

        description = normalize(
            row.get(
                "description",
                ""
            )
        )

        category = normalize(
            row.get(
                "category",
                ""
            )
        )

        job_text = (
            title
            + " "
            + description
            + " "
            + category
        )

        # ----------------------------------------------------
        # Family score
        # ----------------------------------------------------

        if job_family == candidate_family:

            family_score = 40

        elif candidate_family == "Other":

            family_score = 0

        else:

            family_score = 0

        # ----------------------------------------------------
        # Candidate skill matching
        # ----------------------------------------------------

        matched_skills = []

        for skill in candidate_skills:

            if skill_in_text(
                skill,
                job_text
            ):

                matched_skills.append(
                    skill
                )

        skill_percentage = (
            len(matched_skills)
            / len(candidate_skills)
            * 100
            if candidate_skills
            else 0
        )

        # ----------------------------------------------------
        # Recommended skills for this job family
        # ----------------------------------------------------

        family_skills = FAMILY_SKILLS.get(
            job_family,
            []
        )

        gaps = []

        for skill in family_skills:

            if (
                normalize(skill)
                not in candidate_normalized
            ):

                if skill_in_text(
                    skill,
                    job_text
                ):

                    gaps.append(
                        skill
                    )

        # ----------------------------------------------------
        # Final score
        # ----------------------------------------------------

        final_score = (
            family_score
            + skill_percentage * 0.60
        )

        record = row.to_dict()

        record[
            "candidate_job_family"
        ] = candidate_family

        record[
            "detected_job_family"
        ] = job_family

        record[
            "family_score"
        ] = family_score

        record[
            "skill_match_percentage"
        ] = round(
            skill_percentage,
            2
        )

        record[
            "matched_skills"
        ] = ", ".join(
            matched_skills
        )

        record[
            "skill_gaps"
        ] = ", ".join(
            gaps
        )

        record[
            "final_universal_score"
        ] = round(
            final_score,
            2
        )

        output.append(
            record
        )

    result = pd.DataFrame(
        output
    )

    # --------------------------------------------------------
    # Keep relevant family jobs
    # --------------------------------------------------------

    if candidate_family != "Other":

        relevant = result[
            result[
                "detected_job_family"
            ]
            == candidate_family
        ].copy()

    else:

        relevant = result.copy()

    relevant = relevant.sort_values(
        [
            "final_universal_score",
            "skill_match_percentage"
        ],
        ascending=False
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    relevant.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "UNIVERSAL ROLE MATCHING COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Candidate family: {candidate_family}"
    )

    print(
        f"Relevant jobs: {len(relevant)}"
    )

    print()
    print(
        "TOP JOBS"
    )

    print("-" * 70)

    columns = [
        "job_title",
        "company",
        "location",
        "detected_job_family",
        "skill_match_percentage",
        "matched_skills",
        "skill_gaps",
        "final_universal_score"
    ]

    available = [
        c
        for c in columns
        if c in relevant.columns
    ]

    if relevant.empty:

        print(
            "No relevant jobs found."
        )

    else:

        print(
            relevant[
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
        "STAGE 21G COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
