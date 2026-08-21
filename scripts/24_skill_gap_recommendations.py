import os
import re
from collections import Counter

import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "universal_skill_matches.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "skill_gap_analysis.csv"
)


# ============================================================
# UNIVERSAL SKILL VOCABULARY
# ============================================================

SKILL_VOCABULARY = [
    # Healthcare
    "MBBS",
    "MD",
    "General Medicine",
    "Diagnosis",
    "Patient Assessment",
    "Patient Care",
    "Emergency Care",
    "BLS",
    "ACLS",
    "Clinical Documentation",
    "Patient Counselling",
    "Medical Coding",
    "Radiology",
    "Physiotherapy",
    "Nursing",
    "Pharmacology",
    "Clinical Research",
    "Medical Records",
    "Healthcare Management",

    # IT
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "SQL",
    "React",
    "Angular",
    "Node.js",
    "Django",
    "Flask",
    "Git",
    "Machine Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analysis",
    "Cloud Computing",
    "AWS",
    "Azure",
    "DevOps",
    "Cybersecurity",
    "Networking",

    # Education
    "Teaching",
    "Lesson Planning",
    "Classroom Management",
    "Curriculum Development",
    "Assessment",
    "Tutoring",
    "Communication",
    "Training",
    "Educational Technology",

    # Finance
    "Accounting",
    "Tally",
    "GST",
    "Bookkeeping",
    "Financial Analysis",
    "Auditing",
    "Taxation",
    "Payroll",
    "Excel",
    "Financial Reporting",

    # Sales
    "Sales",
    "Customer Service",
    "Customer Support",
    "Negotiation",
    "Business Development",
    "Lead Generation",
    "CRM",
    "Retail",
    "Merchandising",

    # Marketing
    "Digital Marketing",
    "SEO",
    "SEM",
    "Social Media Marketing",
    "Content Writing",
    "Content Marketing",
    "Email Marketing",
    "Google Ads",
    "Brand Management",

    # Design
    "Graphic Design",
    "Photoshop",
    "Illustrator",
    "Figma",
    "UI Design",
    "UX Design",
    "Video Editing",
    "Photography",

    # Engineering
    "Mechanical Engineering",
    "Electrical Engineering",
    "Electronics",
    "Civil Engineering",
    "AutoCAD",
    "CAD",
    "Maintenance",
    "Troubleshooting",
    "Quality Control",
    "Machine Operation",

    # Skilled trades
    "Electrician",
    "Plumbing",
    "Carpentry",
    "Welding",
    "Mechanic",
    "Repair",
    "Tailoring",

    # Logistics
    "Driving",
    "Delivery",
    "Logistics",
    "Warehouse Management",
    "Inventory Management",
    "Supply Chain",
    "Dispatch",

    # Hospitality
    "Cooking",
    "Chef",
    "Food Service",
    "Hotel Management",
    "Housekeeping",
    "Front Office",
    "Restaurant Operations",

    # Administration
    "MS Office",
    "Excel",
    "Data Entry",
    "Office Administration",
    "Documentation",
    "Communication",
    "Office Management",

    # Manufacturing
    "Production",
    "Manufacturing",
    "Quality Inspection",
    "Assembly",
    "Production Planning",
    "Machine Operation",

    # Agriculture
    "Agriculture",
    "Farming",
    "Horticulture",
    "Irrigation",
    "Crop Management",
    "Livestock",
    "Dairy"
]


# ============================================================
# NORMALIZATION
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
# SKILL ALIASES
# ============================================================

ALIASES = {

    "mbbs": [
        "mbbs",
        "bachelor of medicine"
    ],

    "md": [
        " md ",
        "doctor of medicine"
    ],

    "general medicine": [
        "general medicine",
        "general physician"
    ],

    "patient counselling": [
        "patient counselling",
        "patient counseling"
    ],

    "clinical documentation": [
        "clinical documentation",
        "clinical records",
        "medical documentation"
    ],

    "bls": [
        "bls",
        "basic life support"
    ],

    "acls": [
        "acls",
        "advanced cardiac life support"
    ],

    "medical coding": [
        "medical coding",
        "medical coder"
    ],

    "data analysis": [
        "data analysis",
        "data analyst"
    ],

    "machine learning": [
        "machine learning"
    ],

    "artificial intelligence": [
        "artificial intelligence"
    ],

    "digital marketing": [
        "digital marketing"
    ],

    "customer service": [
        "customer service",
        "customer support"
    ],

    "office administration": [
        "office administration",
        "administration"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ],

    "python": [
        "python"
    ],

    "sql": [
        "sql"
    ]
}


# ============================================================
# CHECK SKILL
# ============================================================

def skill_present(skill, text):

    normalized_skill = normalize_text(skill)

    if not normalized_skill:
        return False

    if normalized_skill in text:
        return True

    aliases = ALIASES.get(
        normalized_skill,
        []
    )

    for alias in aliases:

        if alias in text:
            return True

    return False


# ============================================================
# EXTRACT SKILLS FROM JOB
# ============================================================

def extract_job_skills(job_text):

    found = []

    for skill in SKILL_VOCABULARY:

        if skill_present(
            skill,
            job_text
        ):

            found.append(skill)

    return found


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       SKILL GAP & RECOMMENDATION ENGINE")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print()
        print(
            "ERROR: Input file not found:"
        )
        print(INPUT_FILE)
        return

    print()
    print("Loading matched jobs...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Matched jobs loaded: {len(df)}"
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

    candidate_normalized = {
        normalize_text(skill)
        for skill in candidate_skills
    }

    print()
    print("Candidate skills:")

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Analyze jobs
    # --------------------------------------------------------

    skill_frequency = Counter()

    print()
    print(
        "Analyzing required skills across matched jobs..."
    )

    for _, row in df.iterrows():

        title = normalize_text(
            row.get(
                "job_title",
                ""
            )
        )

        description = normalize_text(
            row.get(
                "description",
                ""
            )
        )

        category = normalize_text(
            row.get(
                "category",
                ""
            )
        )

        profession = normalize_text(
            row.get(
                "detected_job_profession",
                ""
            )
        )

        job_text = (
            title
            + " "
            + description
            + " "
            + category
            + " "
            + profession
        )

        required_skills = extract_job_skills(
            job_text
        )

        for skill in required_skills:

            skill_frequency[skill] += 1

    # --------------------------------------------------------
    # Build gap analysis
    # --------------------------------------------------------

    records = []

    total_jobs = len(df)

    for skill, frequency in skill_frequency.most_common():

        normalized_skill = normalize_text(skill)

        if normalized_skill in candidate_normalized:

            status = "Already Have"

        else:

            status = "Skill Gap"

        percentage = (
            frequency / total_jobs * 100
            if total_jobs
            else 0
        )

        if percentage >= 20:
            priority = "High"

        elif percentage >= 8:
            priority = "Medium"

        else:
            priority = "Low"

        records.append({

            "skill": skill,

            "jobs_requiring_skill":
                frequency,

            "job_percentage":
                round(
                    percentage,
                    2
                ),

            "status":
                status,

            "priority":
                priority
        })

    gap_df = pd.DataFrame(records)

    # --------------------------------------------------------
    # Recommended skills
    # --------------------------------------------------------

    recommended = gap_df[
        gap_df["status"] == "Skill Gap"
    ].copy()

    recommended = recommended.sort_values(
        [
            "jobs_requiring_skill",
            "job_percentage"
        ],
        ascending=False
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    gap_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SKILL GAP ANALYSIS")
    print("=" * 70)

    print()
    print("Skills already present:")

    existing = gap_df[
        gap_df["status"] == "Already Have"
    ]

    if existing.empty:

        print("  None detected")

    else:

        for _, row in existing.iterrows():

            print(
                f"  ✓ {row['skill']}"
            )

    print()
    print("RECOMMENDED SKILLS TO LEARN:")

    if recommended.empty:

        print(
            "  No major skill gaps detected."
        )

    else:

        for number, (_, row) in enumerate(
            recommended.head(15).iterrows(),
            start=1
        ):

            print(
                f"\n  {number}. {row['skill']}"
            )

            print(
                "     Jobs requiring it: "
                f"{int(row['jobs_requiring_skill'])}"
            )

            print(
                "     Job coverage: "
                f"{row['job_percentage']:.1f}%"
            )

            print(
                "     Priority: "
                f"{row['priority']}"
            )

    print()
    print("=" * 70)
    print("SKILL GAP ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print("Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
