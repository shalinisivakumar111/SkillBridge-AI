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
    "profession_skill_gap.csv"
)


# ============================================================
# PROFESSION-SPECIFIC SKILLS
# ============================================================

PROFESSION_SKILLS = {

    "Healthcare": [
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
        "Medical Records",
        "Clinical Research",
        "Pharmacology",
        "Radiology",
        "Healthcare Management",
        "Nursing",
        "Physiotherapy"
    ],

    "IT & Software": [
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
        "AWS",
        "Azure",
        "DevOps",
        "Cybersecurity",
        "Networking",
        "Docker"
    ],

    "Education": [
        "Teaching",
        "Lesson Planning",
        "Classroom Management",
        "Curriculum Development",
        "Assessment",
        "Tutoring",
        "Communication",
        "Training",
        "Educational Technology"
    ],

    "Finance & Accounting": [
        "Accounting",
        "Tally",
        "GST",
        "Bookkeeping",
        "Financial Analysis",
        "Auditing",
        "Taxation",
        "Payroll",
        "Excel",
        "Financial Reporting"
    ],

    "Sales & Retail": [
        "Sales",
        "Customer Service",
        "Customer Support",
        "Negotiation",
        "Business Development",
        "Lead Generation",
        "CRM",
        "Retail",
        "Merchandising"
    ],

    "Marketing": [
        "Digital Marketing",
        "SEO",
        "SEM",
        "Social Media Marketing",
        "Content Writing",
        "Content Marketing",
        "Email Marketing",
        "Google Ads",
        "Brand Management"
    ],

    "Design & Creative": [
        "Graphic Design",
        "Photoshop",
        "Illustrator",
        "Figma",
        "UI Design",
        "UX Design",
        "Video Editing",
        "Photography"
    ],

    "Engineering & Technical": [
        "Mechanical Engineering",
        "Electrical Engineering",
        "Electronics",
        "Civil Engineering",
        "AutoCAD",
        "CAD",
        "Maintenance",
        "Troubleshooting",
        "Quality Control",
        "Machine Operation"
    ],

    "Skilled Trades": [
        "Electrician",
        "Plumbing",
        "Carpentry",
        "Welding",
        "Mechanic",
        "Repair",
        "Tailoring"
    ],

    "Logistics & Transport": [
        "Driving",
        "Delivery",
        "Logistics",
        "Warehouse Management",
        "Inventory Management",
        "Supply Chain",
        "Dispatch"
    ],

    "Hospitality": [
        "Cooking",
        "Chef",
        "Food Service",
        "Hotel Management",
        "Housekeeping",
        "Front Office",
        "Restaurant Operations"
    ],

    "Administration": [
        "MS Office",
        "Excel",
        "Data Entry",
        "Office Administration",
        "Documentation",
        "Communication",
        "Office Management"
    ],

    "Manufacturing": [
        "Production",
        "Manufacturing",
        "Quality Inspection",
        "Assembly",
        "Production Planning",
        "Machine Operation"
    ],

    "Agriculture": [
        "Agriculture",
        "Farming",
        "Horticulture",
        "Irrigation",
        "Crop Management",
        "Livestock",
        "Dairy"
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
# ALIASES
# ============================================================

ALIASES = {

    "mbbs": [
        "mbbs"
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

    "patient care": [
        "patient care",
        "patient-care"
    ],

    "medical records": [
        "medical records",
        "medical record"
    ],

    "medical coding": [
        "medical coding",
        "medical coder"
    ],

    "clinical research": [
        "clinical research"
    ],

    "healthcare management": [
        "healthcare management",
        "hospital management"
    ],

    "bls": [
        "bls",
        "basic life support"
    ],

    "acls": [
        "acls",
        "advanced cardiac life support"
    ],

    "python": [
        "python"
    ],

    "javascript": [
        "javascript"
    ],

    "machine learning": [
        "machine learning"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "data analysis": [
        "data analysis",
        "data analyst"
    ],

    "digital marketing": [
        "digital marketing"
    ],

    "customer service": [
        "customer service",
        "customer support"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ]
}


# ============================================================
# SKILL DETECTION
# ============================================================

def contains_skill(
    skill,
    text
):

    normalized_skill = normalize(skill)

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
# DETECT CANDIDATE PROFESSION
# ============================================================

def detect_profession(
    candidate_skills
):

    scores = {}

    normalized_candidate = [
        normalize(skill)
        for skill in candidate_skills
    ]

    for profession, skills in (
        PROFESSION_SKILLS.items()
    ):

        score = 0

        for skill in skills:

            normalized_skill = normalize(
                skill
            )

            if normalized_skill in normalized_candidate:

                score += 1

        scores[profession] = score

    best_profession = max(
        scores,
        key=scores.get
    )

    best_score = scores[
        best_profession
    ]

    if best_score == 0:

        return "General"

    return best_profession


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       PROFESSION-AWARE SKILL GAP")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print()
        print(
            "ERROR: Input dataset not found:"
        )

        print(INPUT_FILE)

        return

    print()
    print(
        "Loading universal skill matches..."
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
            "ERROR: Candidate skills required."
        )

        return

    candidate_skills = [
        skill.strip()
        for skill in raw_skills.split(",")
        if skill.strip()
    ]

    print()
    print(
        "Candidate skills:"
    )

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Detect profession
    # --------------------------------------------------------

    profession = detect_profession(
        candidate_skills
    )

    print()
    print(
        "Detected profession:"
    )

    print(
        f"  ✓ {profession}"
    )

    # --------------------------------------------------------
    # Select profession-specific vocabulary
    # --------------------------------------------------------

    profession_skills = PROFESSION_SKILLS.get(
        profession,
        []
    )

    if not profession_skills:

        profession_skills = [
            skill
            for skills in PROFESSION_SKILLS.values()
            for skill in skills
        ]

    # --------------------------------------------------------
    # Analyze jobs
    # --------------------------------------------------------

    frequency = Counter()

    profession_jobs = 0

    for _, row in df.iterrows():

        row_profession = str(
            row.get(
                "detected_job_profession",
                ""
            )
        )

        row_profession = row_profession.strip()

        # Prefer same profession
        if (
            profession != "General"
            and row_profession != profession
        ):
            continue

        profession_jobs += 1

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

        for skill in profession_skills:

            if contains_skill(
                skill,
                job_text
            ):

                frequency[skill] += 1

    # --------------------------------------------------------
    # Candidate normalized skills
    # --------------------------------------------------------

    candidate_normalized = {
        normalize(skill)
        for skill in candidate_skills
    }

    # --------------------------------------------------------
    # Build results
    # --------------------------------------------------------

    records = []

    for skill, count in frequency.most_common():

        normalized_skill = normalize(
            skill
        )

        if normalized_skill in candidate_normalized:

            status = "Already Have"

        else:

            status = "Skill Gap"

        coverage = (
            count
            / profession_jobs
            * 100
            if profession_jobs
            else 0
        )

        if coverage >= 30:

            priority = "High"

        elif coverage >= 10:

            priority = "Medium"

        else:

            priority = "Low"

        records.append({

            "profession":
                profession,

            "skill":
                skill,

            "jobs_requiring_skill":
                count,

            "job_coverage_percentage":
                round(
                    coverage,
                    2
                ),

            "status":
                status,

            "priority":
                priority
        })

    result_df = pd.DataFrame(
        records
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
    print("PROFESSION-AWARE SKILL GAP ANALYSIS")
    print("=" * 70)

    print()
    print(
        f"Profession: {profession}"
    )

    print(
        f"Profession-relevant jobs: {profession_jobs}"
    )

    print()
    print(
        "SKILLS ALREADY HAVE:"
    )

    existing = result_df[
        result_df["status"]
        == "Already Have"
    ]

    if existing.empty:

        print(
            "  None detected"
        )

    else:

        for _, row in existing.iterrows():

            print(
                f"  ✓ {row['skill']}"
            )

    print()
    print(
        "RECOMMENDED SKILLS:"
    )

    gaps = result_df[
        result_df["status"]
        == "Skill Gap"
    ].copy()

    if gaps.empty:

        print(
            "  No profession-specific skill gaps detected."
        )

    else:

        gaps = gaps.sort_values(
            [
                "priority",
                "jobs_requiring_skill"
            ],
            ascending=[
                True,
                False
            ]
        )

        # High / Medium / Low order
        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2
        }

        gaps["_priority"] = gaps[
            "priority"
        ].map(
            priority_order
        )

        gaps = gaps.sort_values(
            [
                "_priority",
                "jobs_requiring_skill"
            ],
            ascending=[
                True,
                False
            ]
        )

        for number, (_, row) in enumerate(
            gaps.head(15).iterrows(),
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
                "     Coverage: "
                f"{row['job_coverage_percentage']:.1f}%"
            )

            print(
                "     Priority: "
                f"{row['priority']}"
            )

    print()
    print("=" * 70)
    print(
        "PROFESSION-AWARE ANALYSIS COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        "Saved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
