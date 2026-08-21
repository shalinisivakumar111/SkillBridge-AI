import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT = os.path.join(
    BASE_DIR,
    "data",
    "local",
    "local_jobs.csv"
)

OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "local_jobs_clean.csv"
)


def clean_text(value):
    if pd.isna(value):
        return ""

    value = str(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("          LOCAL JOB PROCESSING")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Check input file
    # --------------------------------------------------

    if not os.path.exists(INPUT):
        print("\n❌ local_jobs.csv not found")
        print(f"Expected location:\n{INPUT}")
        return

    print("\n✅ Local job dataset found")

    # --------------------------------------------------
    # 2. Load dataset
    # --------------------------------------------------

    df = pd.read_csv(INPUT)

    print(f"Original jobs: {len(df):,}")

    # --------------------------------------------------
    # 3. Check required columns
    # --------------------------------------------------

    required_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "skills",
        "salary",
        "experience_years",
        "employment_type",
        "community_need"
    ]

    print("\nChecking columns:")

    missing_columns = []

    for column in required_columns:

        if column in df.columns:
            print(f"  ✅ {column}")
        else:
            print(f"  ❌ {column}")
            missing_columns.append(column)

    if missing_columns:

        print("\n❌ Missing required columns:")

        for column in missing_columns:
            print(f"   - {column}")

        return

    # --------------------------------------------------
    # 4. Clean text fields
    # --------------------------------------------------

    text_columns = [
        "job_title",
        "company",
        "location",
        "skills",
        "employment_type",
        "community_need"
    ]

    for column in text_columns:
        df[column] = df[column].apply(clean_text)

    # --------------------------------------------------
    # 5. Remove duplicate jobs
    # --------------------------------------------------

    before = len(df)

    df.drop_duplicates(
        subset=["job_id"],
        inplace=True
    )

    removed = before - len(df)

    print(f"\nDuplicate jobs removed: {removed}")

    # --------------------------------------------------
    # 6. Remove jobs without important information
    # --------------------------------------------------

    before = len(df)

    df = df[
        (df["job_title"] != "") &
        (df["location"] != "") &
        (df["skills"] != "")
    ].copy()

    removed = before - len(df)

    print(f"Jobs removed without title/location/skills: {removed}")

    # --------------------------------------------------
    # 7. Create searchable job text
    # --------------------------------------------------

    df["job_text"] = (
        df["job_title"] + " " +
        df["skills"] + " " +
        df["community_need"]
    ).str.strip()

    # --------------------------------------------------
    # 8. Normalize location
    # --------------------------------------------------

    df["location_normalized"] = (
        df["location"]
        .str.lower()
        .str.strip()
    )

    # --------------------------------------------------
    # 9. Normalize skills
    # --------------------------------------------------

    df["skills_normalized"] = (
        df["skills"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # --------------------------------------------------
    # 10. Save
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT,
        index=False
    )

    # --------------------------------------------------
    # 11. Display results
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("          LOCAL JOB PROCESSING COMPLETE")
    print("=" * 70)

    print(f"\nFinal local jobs: {len(df):,}")

    print("\nSaved to:")
    print(OUTPUT)

    print("\nFinal columns:")

    for column in df.columns:
        print(f"  ✓ {column}")

    print("\nLocal jobs:")

    print(
        df[
            [
                "job_id",
                "job_title",
                "company",
                "location",
                "skills"
            ]
        ].to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("✅ LOCAL JOB DATASET READY")
    print("=" * 70)


if __name__ == "__main__":
    main()