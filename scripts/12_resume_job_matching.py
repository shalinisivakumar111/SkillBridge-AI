import os
import re
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

JOBS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_local_jobs.csv"
)

CANDIDATE_SKILLS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "candidate_skills.csv"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = text.replace("/", " ")
    text = text.replace("\\", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"[^a-z0-9+#.\s]",
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
# SKILL NORMALIZATION
# ============================================================

def normalize_skill(skill):

    skill = normalize_text(skill)

    replacements = {
        "microsoft excel": "excel",
        "ms excel": "excel",
        "microsoft office": "office",
        "ms office": "office",
        "microsoft word": "word",
        "ms word": "word",
        "data entry": "data entry",
        "office administration": "office administration",
    }

    return replacements.get(
        skill,
        skill
    )


# ============================================================
# LOAD CANDIDATE SKILLS
# ============================================================

def load_candidate_skills():

    print("\nLoading candidate skills...")

    if not os.path.exists(
        CANDIDATE_SKILLS_FILE
    ):

        print("\n❌ candidate_skills.csv not found.")

        print(
            "Run Step 11 first:"
        )

        print(
            "python scripts/11_resume_skill_extractor.py "
            "uploads/resumes/test_resume.pdf"
        )

        return []

    df = pd.read_csv(
        CANDIDATE_SKILLS_FILE,
        keep_default_na=False
    )

    if "skill" not in df.columns:

        print(
            "\n❌ 'skill' column not found."
        )

        return []

    skills = []

    for skill in df["skill"]:

        normalized = normalize_skill(
            skill
        )

        if normalized and normalized not in skills:

            skills.append(
                normalized
            )

    return skills


# ============================================================
# LOAD LOCAL JOBS
# ============================================================

def load_jobs():

    print("\nLoading local jobs...")

    if not os.path.exists(
        JOBS_FILE
    ):

        print("\n❌ Local job dataset not found:")
        print(JOBS_FILE)

        return None

    jobs = pd.read_csv(
        JOBS_FILE,
        keep_default_na=False
    )

    print(
        f"Local jobs loaded: {len(jobs)}"
    )

    return jobs


# ============================================================
# EXTRACT JOB SKILLS
# ============================================================

def extract_job_skills(job):

    skills_text = str(
        job.get(
            "skills",
            ""
        )
    )

    if not skills_text:

        return []

    # Handle common separators
    parts = re.split(
        r"[,;\n|]+",
        skills_text
    )

    skills = []

    for part in parts:

        skill = normalize_skill(
            part
        )

        if skill:

            skills.append(
                skill
            )

    return list(
        dict.fromkeys(skills)
    )


# ============================================================
# LOCATION MATCH
# ============================================================

def calculate_location_bonus(
    candidate_location,
    job_location
):

    candidate = normalize_text(
        candidate_location
    )

    job = normalize_text(
        job_location
    )

    if not candidate or not job:

        return 0

    if candidate in job:

        return 10

    # Hyderabad / Secunderabad are treated
    # as the same local employment area
    hyderabad_area = {
        "hyderabad",
        "secunderabad"
    }

    if (
        candidate in hyderabad_area
        and any(
            city in job
            for city in hyderabad_area
        )
    ):

        return 10

    return 0


# ============================================================
# MATCH ONE JOB
# ============================================================

def match_job(
    job,
    candidate_skills,
    candidate_location
):

    job_skills = extract_job_skills(
        job
    )

    if not job_skills:

        return {
            "skill_match": 0,
            "local_bonus": 0,
            "final_score": 0,
            "matched_skills": []
        }

    matched = []

    for candidate_skill in candidate_skills:

        # Exact skill match
        if candidate_skill in job_skills:

            matched.append(
                candidate_skill
            )

            continue

        # Partial phrase matching
        for job_skill in job_skills:

            if (
                candidate_skill in job_skill
                or job_skill in candidate_skill
            ):

                matched.append(
                    candidate_skill
                )

                break

    matched = list(
        dict.fromkeys(matched)
    )

    skill_score = (
        len(matched)
        / len(candidate_skills)
        * 100
        if candidate_skills
        else 0
    )

    local_bonus = calculate_location_bonus(
        candidate_location,
        job.get("location", "")
    )

    final_score = min(
        skill_score + local_bonus,
        100
    )

    return {
        "skill_match": skill_score,
        "local_bonus": local_bonus,
        "final_score": final_score,
        "matched_skills": matched
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       RESUME → LOCAL JOB MATCHING")
    print("=" * 70)

    # --------------------------------------------------------
    # Candidate name
    # --------------------------------------------------------

    candidate_name = input(
        "\nCandidate name: "
    ).strip()

    if not candidate_name:

        candidate_name = "Candidate"

    # --------------------------------------------------------
    # Candidate location
    # --------------------------------------------------------

    candidate_location = input(
        "Candidate location: "
    ).strip()

    # --------------------------------------------------------
    # Candidate skills
    # --------------------------------------------------------

    candidate_skills = load_candidate_skills()

    if not candidate_skills:

        print(
            "\n❌ No candidate skills available."
        )

        return

    print(
        "\nCandidate skills detected:"
    )

    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )

    # --------------------------------------------------------
    # Load jobs
    # --------------------------------------------------------

    jobs = load_jobs()

    if jobs is None:

        return

    # --------------------------------------------------------
    # Match jobs
    # --------------------------------------------------------

    print(
        "\n🔎 Matching resume skills with "
        "local employment..."
    )

    results = []

    for _, job in jobs.iterrows():

        match = match_job(
            job,
            candidate_skills,
            candidate_location
        )

        result = {
            "job_id": job.get(
                "job_id",
                ""
            ),

            "job_title": job.get(
                "job_title",
                "Local Employment Opportunity"
            ),

            "company": job.get(
                "company",
                ""
            ),

            "location": job.get(
                "location",
                ""
            ),

            "skill_match": match[
                "skill_match"
            ],

            "local_bonus": match[
                "local_bonus"
            ],

            "final_score": match[
                "final_score"
            ],

            "matched_skills": ", ".join(
                match["matched_skills"]
            )
        }

        results.append(
            result
        )

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort by final score
    # --------------------------------------------------------

    results_df = results_df.sort_values(
        by=[
            "final_score",
            "skill_match"
        ],
        ascending=False
    )

    # --------------------------------------------------------
    # Top 10
    # --------------------------------------------------------

    top_jobs = results_df.head(
        10
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("             TOP LOCAL JOB MATCHES")
    print("=" * 70)

    for number, (_, row) in enumerate(
        top_jobs.iterrows(),
        start=1
    ):

        print(
            f"\n{number}. "
            f"{row['job_title']}"
        )

        print(
            f"   Company: "
            f"{row['company']}"
        )

        print(
            f"   Location: "
            f"{row['location']}"
        )

        print(
            f"   Skill Match: "
            f"{row['skill_match']:.1f}%"
        )

        print(
            f"   Local Bonus: "
            f"+{row['local_bonus']:.0f}%"
        )

        print(
            f"   Final Score: "
            f"{row['final_score']:.1f}%"
        )

        print(
            f"   Matched Skills: "
            f"{row['matched_skills']}"
        )

    # --------------------------------------------------------
    # Save recommendation results
    # --------------------------------------------------------

    output_file = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "resume_job_recommendations.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        f"Candidate: {candidate_name}"
    )

    print(
        f"Location: {candidate_location}"
    )

    print(
        "✅ RESUME-BASED LOCAL "
        "RECOMMENDATION COMPLETE"
    )

    print("=" * 70)

    print(
        "\nRecommendations saved to:"
    )

    print(output_file)


if __name__ == "__main__":
    main()