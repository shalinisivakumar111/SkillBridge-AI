import pandas as pd
import os
import re


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

JOBS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_jobs.csv"
)


def normalize(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()

    replacements = {
        "ms-excel": "excel",
        "ms office": "office",
        "microsoft excel": "excel",
        "microsoft office": "office",
        "english proficiency spoken": "english",
        "english proficiency written": "english",
        "effective communication": "communication",
        "customer service": "customer service",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9+#.\- ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):

    text = normalize(text)

    # Important skills/phrases that can appear
    # without separators in the local dataset.
    known_skills = [
        "excel",
        "office",
        "data entry",
        "communication",
        "english",
        "sales",
        "marketing",
        "digital marketing",
        "accounting",
        "tally",
        "gst",
        "bookkeeping",
        "customer service",
        "problem solving",
        "graphic design",
        "photoshop",
        "illustrator",
        "creativity",
        "networking",
        "troubleshooting",
        "windows",
        "seo",
        "social media",
        "content writing",
        "python",
        "sql",
        "javascript",
        "react",
        "html",
        "css",
        "statistics",
        "data analysis",
        "communication",
        "negotiation",
        "ms office",
        "ms excel",
        "accounting",
        "classroom management",
        "teaching",
        "mobile repair",
        "electronics",
        "computer hardware"
    ]

    found = []

    for skill in known_skills:

        skill_normalized = normalize(skill)

        if skill_normalized in text:
            found.append(skill_normalized)

    return set(found)


def calculate_match(
    candidate_skills,
    job_skills
):

    job_skill_set = extract_skills(
        job_skills
    )

    matched = []

    for candidate_skill in candidate_skills:

        candidate_skill = normalize(
            candidate_skill
        )

        if not candidate_skill:
            continue

        # Direct match
        if candidate_skill in job_skill_set:
            matched.append(candidate_skill)
            continue

        # Partial/related matching
        for job_skill in job_skill_set:

            if (
                candidate_skill in job_skill
                or job_skill in candidate_skill
            ):
                matched.append(
                    candidate_skill
                )
                break

    matched = sorted(
        set(matched)
    )

    if len(candidate_skills) == 0:
        return 0, matched

    score = (
        len(matched)
        / len(candidate_skills)
    ) * 100

    return round(score, 2), matched


def infer_job_title(job):

    existing_title = job.get(
        "job_title",
        ""
    )

    if (
        pd.notna(existing_title)
        and str(existing_title).strip()
        and str(existing_title).lower()
        != "nan"
    ):
        return str(existing_title)

    skills = normalize(
        job.get("skills", "")
    )

    # Infer a useful local job title
    # from the job's skills.

    if "data analysis" in skills:
        return "Data Analyst"

    if "python" in skills and "sql" in skills:
        return "Python / Data Analyst"

    if "digital marketing" in skills:
        return "Digital Marketing Executive"

    if "graphic design" in skills:
        return "Graphic Designer"

    if "photoshop" in skills:
        return "Graphic Designer"

    if "accounting" in skills:
        return "Accounts Assistant"

    if "tally" in skills:
        return "Accounts Assistant"

    if "bookkeeping" in skills:
        return "Bookkeeping Assistant"

    if "sales" in skills:
        return "Sales Executive"

    if "customer service" in skills:
        return "Customer Service Executive"

    if "data entry" in skills:
        return "Data Entry Operator"

    if "excel" in skills:
        return "Computer / Office Assistant"

    if "networking" in skills:
        return "Network Support Technician"

    if "mobile repair" in skills:
        return "Mobile Repair Technician"

    if "electronics" in skills:
        return "Electronics Technician"

    if "teaching" in skills:
        return "Teaching Assistant"

    if "content writing" in skills:
        return "Content Writer"

    if "marketing" in skills:
        return "Marketing Assistant"

    if "computer hardware" in skills:
        return "Computer Hardware Technician"

    return "Local Employment Opportunity"


def find_matches(
    candidate_skills,
    candidate_location,
    top_n=10
):

    jobs = pd.read_csv(
        JOBS_FILE
    )

    candidate_skills = set(
        extract_skills(
            candidate_skills
        )
    )

    results = []

    for _, job in jobs.iterrows():

        score, matched = calculate_match(
            candidate_skills,
            job.get("skills", "")
        )

        # --------------------------------------
        # Location bonus
        # --------------------------------------

        location_bonus = 0

        candidate_location_clean = normalize(
            candidate_location
        )

        job_location = normalize(
            job.get("location", "")
        )

        if (
            candidate_location_clean
            and candidate_location_clean
            in job_location
        ):
            location_bonus = 10

        final_score = min(
            score + location_bonus,
            100
        )

        title = infer_job_title(
            job
        )

        results.append({

            "job_id":
                job.get("job_id", ""),

            "job_title":
                title,

            "company":
                job.get("company", ""),

            "location":
                job.get("location", ""),

            "skills":
                job.get("skills", ""),

            "skill_score":
                score,

            "location_bonus":
                location_bonus,

            "final_score":
                final_score,

            "matched_skills":
                ", ".join(matched),

            "community_need":
                job.get(
                    "community_need",
                    ""
                )
        })

    results = pd.DataFrame(
        results
    )

    results = results.sort_values(
        by="final_score",
        ascending=False
    )

    return results.head(
        top_n
    )


def main():

    print("=" * 70)

    print(
        "              SKILLBRIDGE AI"
    )

    print(
        "       LOCAL AI SKILL MATCHING"
    )

    print("=" * 70)

    if not os.path.exists(
        JOBS_FILE
    ):

        print(
            "\n❌ final_jobs.csv not found."
        )

        print(
            "Run:"
        )

        print(
            "python scripts/07_build_final_dataset.py"
        )

        return

    jobs = pd.read_csv(
        JOBS_FILE
    )

    print(
        f"\n✅ Jobs loaded: {len(jobs):,}"
    )

    print("\n" + "-" * 70)

    candidate_name = input(
        "Candidate name: "
    )

    candidate_location = input(
        "Candidate location: "
    )

    candidate_skills = input(
        "Candidate skills "
        "(comma separated): "
    )

    print(
        "\n🔎 Matching candidate skills "
        "with local employment..."
    )

    matches = find_matches(
        candidate_skills,
        candidate_location,
        top_n=10
    )

    print("\n" + "=" * 70)

    print(
        "             TOP LOCAL JOB MATCHES"
    )

    print("=" * 70)

    for index, (_, job) in enumerate(
        matches.iterrows(),
        start=1
    ):

        print(
            f"\n{index}. {job['job_title']}"
        )

        print(
            f"   Company: "
            f"{job['company']}"
        )

        print(
            f"   Location: "
            f"{job['location']}"
        )

        print(
            f"   Skill Match: "
            f"{job['skill_score']}%"
        )

        print(
            f"   Local Bonus: "
            f"+{job['location_bonus']}%"
        )

        print(
            f"   Final Score: "
            f"{job['final_score']}%"
        )

        print(
            f"   Matched Skills: "
            f"{job['matched_skills']}"
        )

        print(
            f"   Community Need: "
            f"{job['community_need']}"
        )

    print("\n" + "=" * 70)

    print(
        f"Candidate: {candidate_name}"
    )

    print(
        "✅ LOCAL RECOMMENDATION COMPLETE"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()