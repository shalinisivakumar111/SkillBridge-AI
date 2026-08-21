import pandas as pd
import os
import re
from collections import defaultdict


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

JOBS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "local_jobs_clean.csv"
)

RELATIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "occupation_skills.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "local_jobs_with_titles.csv"
)


def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9+#.\- ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text):

    text = clean_text(text)

    # These are the common skills found
    # in your local job dataset.

    known_skills = [
        "ms excel",
        "excel",
        "ms office",
        "office",
        "data entry",
        "english",
        "communication",
        "effective communication",
        "digital marketing",
        "marketing",
        "market research",
        "marketing strategies",
        "negotiation",
        "presentation skills",
        "accounting",
        "tally",
        "gst",
        "bookkeeping",
        "legal research",
        "company law",
        "legal drafting",
        "contract management",
        "python",
        "sql",
        "flask",
        "git",
        "javascript",
        "html",
        "css",
        "react",
        "customer service",
        "sales",
        "problem solving",
        "graphic design",
        "photoshop",
        "illustrator",
        "seo",
        "social media",
        "content writing",
        "statistics",
        "power bi",
        "networking",
        "troubleshooting",
        "windows",
        "computer hardware",
        "electronics",
        "teaching",
        "mathematics",
        "classroom management",
        "mobile repair"
    ]

    found = []

    for skill in known_skills:

        if clean_text(skill) in text:

            found.append(
                clean_text(skill)
            )

    return set(found)


def build_occupation_index(relations):

    print(
        "\nBuilding ESCO occupation index..."
    )

    occupation_skills = defaultdict(set)

    for _, row in relations.iterrows():

        occupation = clean_text(
            row.get(
                "occupationLabel",
                ""
            )
        )

        skill = clean_text(
            row.get(
                "skillLabel",
                ""
            )
        )

        if not occupation or not skill:
            continue

        occupation_skills[
            occupation
        ].add(skill)

    print(
        f"ESCO occupations indexed: "
        f"{len(occupation_skills):,}"
    )

    return occupation_skills


def find_best_occupation(
    job_skills,
    occupation_skills
):

    if not job_skills:

        return (
            "Local Employment Opportunity",
            0,
            []
        )

    best_occupation = (
        "Local Employment Opportunity"
    )

    best_score = 0

    best_matches = []

    for occupation, required_skills in (
        occupation_skills.items()
    ):

        matched = []

        for job_skill in job_skills:

            for esco_skill in required_skills:

                if (
                    job_skill in esco_skill
                    or esco_skill in job_skill
                ):

                    matched.append(
                        job_skill
                    )

                    break

        matched = sorted(
            set(matched)
        )

        if not matched:
            continue

        score = (
            len(matched)
            /
            len(job_skills)
        ) * 100

        if score > best_score:

            best_score = score

            best_occupation = (
                occupation.title()
            )

            best_matches = matched

    return (
        best_occupation,
        round(best_score, 2),
        best_matches
    )


def main():

    print("=" * 70)

    print(
        "              SKILLBRIDGE AI"
    )

    print(
        "          ESCO JOB TITLE INFERENCE"
    )

    print("=" * 70)


    # --------------------------------------------------
    # Check files
    # --------------------------------------------------

    if not os.path.exists(
        JOBS_FILE
    ):

        print(
            "\n❌ Local jobs file not found:"
        )

        print(
            JOBS_FILE
        )

        return


    if not os.path.exists(
        RELATIONS_FILE
    ):

        print(
            "\n❌ ESCO occupation-skill relations "
            "file not found:"
        )

        print(
            RELATIONS_FILE
        )

        return


    # --------------------------------------------------
    # Load data
    # --------------------------------------------------

    print(
        "\nLoading local jobs..."
    )

    jobs = pd.read_csv(
        JOBS_FILE
    )

    print(
        f"Local jobs: {len(jobs):,}"
    )


    print(
        "\nLoading ESCO occupation-skill relations..."
    )

    relations = pd.read_csv(
        RELATIONS_FILE
    )

    print(
        f"ESCO relations: "
        f"{len(relations):,}"
    )


    # --------------------------------------------------
    # Build ESCO index
    # --------------------------------------------------

    occupation_skills = (
        build_occupation_index(
            relations
        )
    )


    # --------------------------------------------------
    # Infer titles
    # --------------------------------------------------

    inferred_titles = []

    inference_scores = []

    matched_skill_lists = []


    print(
        "\nInferring job titles..."
    )


    for _, job in jobs.iterrows():

        skills_text = job.get(
            "skills",
            ""
        )

        job_skills = extract_skills(
            skills_text
        )

        title, score, matched = (
            find_best_occupation(
                job_skills,
                occupation_skills
            )
        )

        inferred_titles.append(
            title
        )

        inference_scores.append(
            score
        )

        matched_skill_lists.append(
            ", ".join(matched)
        )


    # --------------------------------------------------
    # Add results
    # --------------------------------------------------

    jobs["job_title"] = (
        inferred_titles
    )

    jobs["title_inference_score"] = (
        inference_scores
    )

    jobs["title_matched_skills"] = (
        matched_skill_lists
    )


    # --------------------------------------------------
    # Save
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
    # Display
    # --------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "       JOB TITLE INFERENCE COMPLETE"
    )

    print("=" * 70)

    print(
        f"\nJobs processed: "
        f"{len(jobs):,}"
    )

    print(
        f"Titles inferred: "
        f"{len(inferred_titles):,}"
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nSample inferred titles:"
    )

    print(
        jobs[
            [
                "job_id",
                "company",
                "location",
                "job_title",
                "title_inference_score",
                "title_matched_skills"
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    print("\n" + "=" * 70)

    print(
        "✅ ESCO JOB TITLES READY"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()