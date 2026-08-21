import pandas as pd
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOCAL_JOBS = os.path.join(
    BASE_DIR,
    "data",
    "local",
    "local_jobs.csv"
)

ESCO_RESULTS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "local_jobs_with_titles.csv"
)

OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_local_jobs.csv"
)


def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("          FINAL LOCAL JOB DATA")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Check local dataset
    # --------------------------------------------------

    print("\nChecking local job dataset...")

    if not os.path.exists(LOCAL_JOBS):

        print("❌ local_jobs.csv not found")

        print(
            f"Expected location:\n{LOCAL_JOBS}"
        )

        return

    print("✅ Local job dataset found")


    # --------------------------------------------------
    # 2. Load local jobs
    # --------------------------------------------------

    jobs = pd.read_csv(
        LOCAL_JOBS
    )

    print(
        f"\nLocal jobs loaded: {len(jobs):,}"
    )

    print("\nLocal dataset columns:")

    for column in jobs.columns:

        print(
            f"  ✓ {column}"
        )


    # --------------------------------------------------
    # 3. Check required columns
    # --------------------------------------------------

    required_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "skills"
    ]

    missing = [
        column
        for column in required_columns
        if column not in jobs.columns
    ]

    if missing:

        print(
            "\n❌ Missing required columns:"
        )

        for column in missing:

            print(
                f"  • {column}"
            )

        print(
            "\nPlease check data/local/local_jobs.csv"
        )

        return


    # --------------------------------------------------
    # 4. Clean job titles
    # --------------------------------------------------

    jobs["job_title"] = (
        jobs["job_title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    jobs["company"] = (
        jobs["company"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    jobs["location"] = (
        jobs["location"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    jobs["skills"] = (
        jobs["skills"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------
    # 5. Remove duplicate job IDs
    # --------------------------------------------------

    before = len(jobs)

    jobs = jobs.drop_duplicates(
        subset=["job_id"]
    )

    after = len(jobs)

    print(
        f"\nDuplicate jobs removed: "
        f"{before - after}"
    )


    # --------------------------------------------------
    # 6. Load ESCO information
    # --------------------------------------------------

    if os.path.exists(
        ESCO_RESULTS
    ):

        print(
            "\nLoading ESCO information..."
        )

        esco = pd.read_csv(
            ESCO_RESULTS
        )

        print(
            f"ESCO records loaded: "
            f"{len(esco):,}"
        )

        # We DO NOT take job_title
        # from ESCO.

        useful_columns = [
            "job_id",
            "title_inference_score",
            "title_matched_skills"
        ]

        available = [
            column
            for column in useful_columns
            if column in esco.columns
        ]

        esco = esco[
            available
        ]

        # Remove duplicate job IDs
        esco = esco.drop_duplicates(
            subset=["job_id"]
        )

        # Merge ESCO information
        jobs = jobs.merge(
            esco,
            on="job_id",
            how="left"
        )

        print(
            "✅ ESCO information attached"
        )

    else:

        print(
            "\n⚠️ ESCO results not found."
        )

        print(
            "Continuing with local data only."
        )

        jobs[
            "title_inference_score"
        ] = 0

        jobs[
            "title_matched_skills"
        ] = ""


    # --------------------------------------------------
    # 7. Mark local employment
    # --------------------------------------------------

    jobs["local_job"] = True


    # --------------------------------------------------
    # 8. Create searchable text
    # --------------------------------------------------

    jobs["search_text"] = (
        jobs["job_title"]
        + " "
        + jobs["company"]
        + " "
        + jobs["location"]
        + " "
        + jobs["skills"]
    )


    # --------------------------------------------------
    # 9. Reorder columns
    # --------------------------------------------------

    preferred_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "skills",
        "salary",
        "employment_type",
        "experience_years",
        "community_need",
        "title_inference_score",
        "title_matched_skills",
        "local_job",
        "search_text"
    ]

    final_columns = [
        column
        for column in preferred_columns
        if column in jobs.columns
    ]

    # Include anything else that exists
    remaining_columns = [
        column
        for column in jobs.columns
        if column not in final_columns
    ]

    jobs = jobs[
        final_columns + remaining_columns
    ]


    # --------------------------------------------------
    # 10. Save final local dataset
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    jobs.to_csv(
        OUTPUT,
        index=False
    )


    # --------------------------------------------------
    # 11. Display result
    # --------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "       FINAL LOCAL JOB DATA READY"
    )

    print("=" * 70)

    print(
        f"\nFinal jobs: {len(jobs):,}"
    )

    print(
        f"\nSaved to:\n{OUTPUT}"
    )


    print(
        "\nFINAL JOB TITLES:"
    )

    print(
        jobs[
            [
                "job_id",
                "job_title",
                "company",
                "location"
            ]
        ].to_string(
            index=False
        )
    )


    print("\n" + "=" * 70)

    print(
        "✅ CORRECT LOCAL TITLES PRESERVED"
    )

    print(
        "✅ ESCO INFORMATION RETAINED"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()