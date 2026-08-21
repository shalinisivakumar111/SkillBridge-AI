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
    "universal_skill_matches.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "role_aware_matches.csv"
)


# ============================================================
# ROLE DEFINITIONS
# ============================================================

ROLES = {

    "Doctor / Physician": [
        "doctor",
        "physician",
        "medical officer",
        "general practitioner",
        "general physician",
        "medical consultant",
        "consultant physician",
        "mbbs doctor",
        "md doctor",
        "resident doctor",
        "senior resident",
        "junior resident",
        "clinical physician"
    ],

    "Nurse": [
        "nurse",
        "staff nurse",
        "registered nurse",
        "nursing officer",
        "clinical nurse"
    ],

    "Pharmacist": [
        "pharmacist",
        "pharmacy",
        "pharmacy officer"
    ],

    "Physiotherapist": [
        "physiotherapist",
        "physiotherapy",
        "physical therapist"
    ],

    "Medical Coder": [
        "medical coder",
        "medical coding",
        "coding specialist",
        "medical billing"
    ],

    "Medical Research": [
        "clinical research",
        "research associate",
        "clinical research associate",
        "medical research"
    ],

    "Healthcare Administration": [
        "hospital administrator",
        "healthcare administrator",
        "hospital administration",
        "healthcare management",
        "medical administrator"
    ],

    "Dentist": [
        "dentist",
        "dental surgeon",
        "dental doctor"
    ],

    "Radiologist": [
        "radiologist",
        "radiology",
        "radiology consultant"
    ],

    "Laboratory": [
        "lab technician",
        "laboratory technician",
        "medical laboratory",
        "pathology technician"
    ],

    "IT Developer": [
        "software developer",
        "software engineer",
        "python developer",
        "java developer",
        "web developer",
        "full stack developer",
        "frontend developer",
        "backend developer"
    ],

    "Data Analyst": [
        "data analyst",
        "business analyst",
        "data scientist",
        "analytics"
    ],

    "Teacher": [
        "teacher",
        "school teacher",
        "subject teacher",
        "lecturer",
        "professor",
        "tutor",
        "faculty"
    ],

    "Accountant": [
        "accountant",
        "accounts executive",
        "accounts assistant",
        "finance executive",
        "auditor"
    ],

    "Sales Executive": [
        "sales executive",
        "sales representative",
        "sales officer",
        "business development executive",
        "business development manager"
    ],

    "Customer Support": [
        "customer support",
        "customer service",
        "customer care",
        "support executive"
    ],

    "Graphic Designer": [
        "graphic designer",
        "visual designer",
        "ui designer",
        "ux designer"
    ],

    "Electrician": [
        "electrician",
        "electrical technician"
    ],

    "Mechanic": [
        "mechanic",
        "automobile mechanic",
        "vehicle technician"
    ],

    "Driver": [
        "driver",
        "delivery driver",
        "chauffeur"
    ]
}


# ============================================================
# ROLE-SPECIFIC SKILLS
# ============================================================

ROLE_SKILLS = {

    "Doctor / Physician": [
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
        "Medical Records",
        "Clinical Research",
        "Pharmacology",
        "Healthcare Management"
    ],

    "Nurse": [
        "Nursing",
        "Patient Care",
        "Patient Assessment",
        "BLS",
        "ACLS",
        "Medication Administration",
        "Clinical Documentation",
        "Vital Signs",
        "Emergency Care"
    ],

    "Pharmacist": [
        "Pharmacy",
        "Pharmacology",
        "Medication",
        "Prescription",
        "Drug Safety",
        "Patient Counselling",
        "Inventory Management"
    ],

    "Physiotherapist": [
        "Physiotherapy",
        "Physical Therapy",
        "Rehabilitation",
        "Patient Assessment",
        "Exercise Therapy",
        "Pain Management"
    ],

    "Medical Coder": [
        "Medical Coding",
        "Medical Records",
        "ICD",
        "CPT",
        "Healthcare Documentation",
        "Medical Billing"
    ],

    "Medical Research": [
        "Clinical Research",
        "Research",
        "Clinical Trials",
        "Data Analysis",
        "Medical Documentation",
        "Research Methodology"
    ],

    "Healthcare Administration": [
        "Healthcare Management",
        "Hospital Administration",
        "Hospital Management",
        "Medical Records",
        "Communication",
        "MS Office"
    ],

    "Dentist": [
        "Dentistry",
        "Dental Surgery",
        "Patient Care",
        "Diagnosis",
        "Oral Surgery",
        "Dental Treatment"
    ],

    "Radiologist": [
        "Radiology",
        "Medical Imaging",
        "CT",
        "MRI",
        "Ultrasound",
        "Diagnosis"
    ],

    "Laboratory": [
        "Laboratory",
        "Pathology",
        "Blood Testing",
        "Sample Collection",
        "Medical Laboratory"
    ],

    "IT Developer": [
        "Python",
        "Java",
        "JavaScript",
        "SQL",
        "Git",
        "React",
        "Node.js",
        "AWS",
        "Docker"
    ],

    "Data Analyst": [
        "SQL",
        "Python",
        "Excel",
        "Data Analysis",
        "Statistics",
        "Power BI",
        "Tableau"
    ],

    "Teacher": [
        "Teaching",
        "Lesson Planning",
        "Classroom Management",
        "Communication",
        "Assessment",
        "Curriculum Development"
    ],

    "Accountant": [
        "Accounting",
        "Tally",
        "GST",
        "Excel",
        "Bookkeeping",
        "Auditing",
        "Taxation"
    ],

    "Sales Executive": [
        "Sales",
        "Communication",
        "Negotiation",
        "Customer Service",
        "Business Development",
        "CRM"
    ],

    "Customer Support": [
        "Customer Service",
        "Communication",
        "Customer Support",
        "Problem Solving",
        "CRM"
    ],

    "Graphic Designer": [
        "Graphic Design",
        "Photoshop",
        "Illustrator",
        "Figma",
        "UI Design",
        "UX Design"
    ],

    "Electrician": [
        "Electrical",
        "Wiring",
        "Electrical Maintenance",
        "Troubleshooting",
        "Safety"
    ],

    "Mechanic": [
        "Automobile",
        "Repair",
        "Maintenance",
        "Troubleshooting",
        "Mechanical"
    ],

    "Driver": [
        "Driving",
        "Road Safety",
        "Navigation",
        "Vehicle Maintenance"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

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
# DETECT ROLE FROM JOB
# ============================================================

def detect_role(row):

    title = normalize(
        row.get("job_title", "")
    )

    description = normalize(
        row.get("description", "")
    )

    category = normalize(
        row.get("category", "")
    )

    category_tag = normalize(
        row.get("category_tag", "")
    )

    # Title gets much higher importance
    title_scores = {}

    for role, keywords in ROLES.items():

        score = 0

        for keyword in keywords:

            keyword = normalize(keyword)

            if keyword in title:
                score += 10

            elif keyword in description:
                score += 2

            elif keyword in category:
                score += 2

            elif keyword in category_tag:
                score += 2

        title_scores[role] = score

    best_role = max(
        title_scores,
        key=title_scores.get
    )

    best_score = title_scores[
        best_role
    ]

    if best_score == 0:
        return "Other"

    return best_role


# ============================================================
# CANDIDATE ROLE DETECTION
# ============================================================

def detect_candidate_role(
    candidate_skills
):

    candidate_text = " ".join(
        normalize(skill)
        for skill in candidate_skills
    )

    scores = {}

    for role, keywords in ROLES.items():

        score = 0

        role_skills = ROLE_SKILLS.get(
            role,
            []
        )

        for keyword in keywords:

            if normalize(keyword) in candidate_text:
                score += 5

        for skill in role_skills:

            if normalize(skill) in candidate_text:
                score += 3

        scores[role] = score

    best_role = max(
        scores,
        key=scores.get
    )

    if scores[best_role] == 0:
        return "Other"

    return best_role


# ============================================================
# SKILL MATCH
# ============================================================

def skill_exists(
    skill,
    text
):

    skill = normalize(skill)

    if skill in text:
        return True

    aliases = {

        "patient counselling": [
            "patient counselling",
            "patient counseling"
        ],

        "medical records": [
            "medical records",
            "medical record"
        ],

        "medical coding": [
            "medical coding",
            "medical coder"
        ],

        "general medicine": [
            "general medicine",
            "general physician"
        ],

        "clinical research": [
            "clinical research"
        ],

        "patient care": [
            "patient care"
        ],

        "bls": [
            "bls",
            "basic life support"
        ],

        "acls": [
            "acls",
            "advanced cardiac life support"
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
    print("          ROLE-AWARE JOB MATCHING")
    print("=" * 70)

    if not os.path.exists(
        INPUT_FILE
    ):

        print()
        print(
            "ERROR: Input file not found:"
        )

        print(INPUT_FILE)

        return

    df = pd.read_csv(
        INPUT_FILE
    )

    print()
    print(
        f"Jobs loaded: {len(df)}"
    )

    print()
    print("=" * 70)
    print("CANDIDATE")
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
        x.strip()
        for x in raw_skills.split(",")
        if x.strip()
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
    # Detect candidate role
    # --------------------------------------------------------

    candidate_role = detect_candidate_role(
        candidate_skills
    )

    print()
    print(
        "Detected candidate role:"
    )

    print(
        f"  ✓ {candidate_role}"
    )

    # --------------------------------------------------------
    # Score jobs
    # --------------------------------------------------------

    results = []

    role_skills = ROLE_SKILLS.get(
        candidate_role,
        []
    )

    candidate_normalized = {
        normalize(skill)
        for skill in candidate_skills
    }

    for _, row in df.iterrows():

        job_role = detect_role(
            row
        )

        # Strong preference for same role
        role_score = 0

        if job_role == candidate_role:
            role_score = 50

        elif (
            candidate_role == "Doctor / Physician"
            and job_role in [
                "Medical Research",
                "Healthcare Administration",
                "Radiologist"
            ]
        ):
            role_score = 15

        elif (
            candidate_role == "Other"
        ):
            role_score = 0

        else:
            role_score = -20

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

        matched = []

        for skill in candidate_skills:

            if skill_exists(
                skill,
                job_text
            ):

                matched.append(
                    skill
                )

        skill_percentage = (
            len(matched)
            / len(candidate_skills)
            * 100
            if candidate_skills
            else 0
        )

        # Additional role-specific skills
        required_role_skills = []

        for skill in role_skills:

            if skill_exists(
                skill,
                job_text
            ):

                required_role_skills.append(
                    skill
                )

        missing_role_skills = []

        for skill in required_role_skills:

            if normalize(skill) not in candidate_normalized:

                missing_role_skills.append(
                    skill
                )

        final_score = (
            skill_percentage * 0.65
            + role_score
        )

        result = row.to_dict()

        result[
            "candidate_role"
        ] = candidate_role

        result[
            "job_role"
        ] = job_role

        result[
            "role_score"
        ] = role_score

        result[
            "skill_match_percentage"
        ] = round(
            skill_percentage,
            2
        )

        result[
            "matched_skills"
        ] = ", ".join(
            matched
        )

        result[
            "role_skill_gaps"
        ] = ", ".join(
            missing_role_skills
        )

        result[
            "final_role_aware_score"
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
    # Only keep sensible roles
    # --------------------------------------------------------

    if candidate_role != "Other":

        result_df = result_df[
            (
                result_df["job_role"]
                == candidate_role
            )
            |
            (
                result_df["role_score"]
                > 0
            )
        ].copy()

    result_df = result_df.sort_values(
        [
            "final_role_aware_score",
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
    print("ROLE-AWARE MATCHING COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Candidate role: {candidate_role}"
    )

    print(
        f"Relevant jobs: {len(result_df)}"
    )

    print()
    print(
        "TOP 20 ROLE-AWARE JOBS"
    )

    print("-" * 70)

    columns = [
        "job_title",
        "company",
        "location",
        "job_role",
        "skill_match_percentage",
        "matched_skills",
        "role_skill_gaps",
        "final_role_aware_score"
    ]

    available = [
        c
        for c in columns
        if c in result_df.columns
    ]

    if result_df.empty:

        print(
            "No role-relevant jobs found."
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
        "STAGE 21F COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
