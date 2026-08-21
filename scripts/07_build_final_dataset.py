import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

JOBS_FILE = os.path.join(
    BASE_DIR, "data", "processed", "jobs_clean.csv"
)

SKILLS_FILE = os.path.join(
    BASE_DIR, "data", "processed", "skill_dictionary.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "data", "processed", "final_jobs.csv"
)


def clean_text(value):
    if pd.isna(value):
        return ""

    value = str(value).lower()
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def main():

    print("=" * 70)
    print("                 SKILLBRIDGE AI")
    print("             FINAL DATASET BUILD")
    print("=" * 70)

    # --------------------------------------------------
    # LOAD JOBS
    # --------------------------------------------------

    print("\nLoading cleaned jobs...")

    if not os.path.exists(JOBS_FILE):
        print("❌ jobs_clean.csv not found")
        return

    jobs = pd.read_csv(JOBS_FILE)

    print(f"Jobs loaded: {len(jobs):,}")

    # --------------------------------------------------
    # LOAD SKILL DICTIONARY
    # --------------------------------------------------

    print("\nLoading skill dictionary...")

    if not os.path.exists(SKILLS_FILE):
        print("❌ skill_dictionary.csv not found")
        return

    skills = pd.read_csv(SKILLS_FILE)

    print(f"Skills loaded: {len(skills):,}")

    # --------------------------------------------------
    # CLEAN JOB SKILLS
    # --------------------------------------------------

    jobs["skills"] = (
        jobs["skills"]
        .fillna("")
        .astype(str)
    )

    jobs["skills_clean"] = (
        jobs["skills"]
        .apply(clean_text)
    )

    jobs["job_text"] = (
        jobs["job_text"]
        .fillna("")
        .astype(str)
    )

    jobs["job_text_clean"] = (
        jobs["job_text"]
        .apply(clean_text)
    )

    # --------------------------------------------------
    # PREPARE ESCO SKILLS
    # --------------------------------------------------

    skills["normalized_skill"] = (
        skills["normalized_skill"]
        .fillna("")
        .astype(str)
        .apply(clean_text)
    )

    skill_lookup = {}

    for _, row in skills.iterrows():

        skill = row["normalized_skill"]

        if skill:

            skill_lookup[skill] = {
                "skill_id": row["skill_id"],
                "skill": row["skill"]
            }

    print(
        f"Skill lookup created: {len(skill_lookup):,}"
    )

    # --------------------------------------------------
    # MATCH JOB SKILLS
    # --------------------------------------------------

    print("\nMatching jobs with ESCO skills...")

    matched_names = []
    matched_ids = []

    for job_text in jobs["skills_clean"]:

        names = []
        ids = []

        for normalized, info in skill_lookup.items():

            if normalized in job_text:

                names.append(info["skill"])
                ids.append(info["skill_id"])

        names = sorted(set(names))
        ids = sorted(set(ids))

        matched_names.append(
            "; ".join(names)
        )

        matched_ids.append(
            "; ".join(ids)
        )

    jobs["esco_skills"] = matched_names
    jobs["esco_skill_ids"] = matched_ids

    # --------------------------------------------------
    # COUNT MATCHED SKILLS
    # --------------------------------------------------

    jobs["matched_skill_count"] = (
        jobs["esco_skill_ids"]
        .apply(
            lambda x:
            len(
                [i for i in str(x).split(";") if i.strip()]
            )
        )
    )

    # --------------------------------------------------
    # ORIGINAL SKILL COUNT
    # --------------------------------------------------

    jobs["original_skill_count"] = (
        jobs["skills_clean"]
        .apply(
            lambda x:
            len(
                [
                    s for s in re.split(
                        r"[,;]",
                        x
                    )
                    if s.strip()
                ]
            )
        )
    )

    # --------------------------------------------------
    # MATCH PERCENTAGE
    # --------------------------------------------------

    def calculate_percentage(row):

        original = row["original_skill_count"]
        matched = row["matched_skill_count"]

        if original == 0:
            return 0

        return round(
            matched / original * 100,
            2
        )

    jobs["skill_match_percentage"] = (
        jobs.apply(
            calculate_percentage,
            axis=1
        )
    )

    # --------------------------------------------------
    # MATCHING TEXT
    # --------------------------------------------------

    jobs["matching_text"] = (
        jobs["job_title"].fillna("").astype(str)
        + " "
        + jobs["company"].fillna("").astype(str)
        + " "
        + jobs["location"].fillna("").astype(str)
        + " "
        + jobs["skills"].fillna("").astype(str)
        + " "
        + jobs["esco_skills"].fillna("").astype(str)
    )

    jobs["matching_text"] = (
        jobs["matching_text"]
        .apply(clean_text)
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    jobs.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("             FINAL DATASET COMPLETE")
    print("=" * 70)

    print(f"\nFinal jobs: {len(jobs):,}")

    print(
        "Jobs with ESCO skills: "
        f"{(jobs['matched_skill_count'] > 0).sum():,}"
    )

    print(
        "Total matched skills: "
        f"{jobs['matched_skill_count'].sum():,}"
    )

    print(f"\nSaved to:")
    print(OUTPUT_FILE)

    print("\nFirst 5 jobs:")

    print(
        jobs[
            [
                "job_id",
                "job_title",
                "company",
                "location",
                "skills",
                "esco_skills",
                "matched_skill_count",
                "skill_match_percentage"
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("✅ FINAL JOB DATASET READY")
    print("=" * 70)


if __name__ == "__main__":
    main()