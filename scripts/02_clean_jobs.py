from pathlib import Path
import pandas as pd
import re


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "jobs"
    / "Job_dataset.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = OUTPUT_DIR / "jobs_clean.csv"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    value = str(value)

    # Remove multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# SALARY CLEANING
# ============================================================

def clean_salary(value):

    value = clean_text(value)

    if not value:
        return ""

    return value


# ============================================================
# EXPERIENCE CLEANING
# ============================================================

def extract_experience(value):

    value = clean_text(value)

    if not value:
        return 0.0

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        value
    )

    if match:
        return float(match.group(1))

    return 0.0


# ============================================================
# SKILL CLEANING
# ============================================================

def clean_skills(value):

    value = clean_text(value)

    if not value:
        return ""

    # Add spaces between common concatenated skill patterns.
    # We keep the original skill text rather than aggressively
    # changing it because the ESCO matching stage will normalize it.

    replacements = {
        "MS-OfficeMS-Excel": "MS-Office, MS-Excel",
        "English Proficiency": "English Proficiency",
        "MS-ExcelEnglish": "MS-Excel, English",
        "Digital MarketingMarket": "Digital Marketing, Market",
        "Marketing Strategies": "Marketing Strategies",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("             SKILLBRIDGE AI")
    print("          JOB DATA CLEANING")
    print("=" * 70)

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print("\n❌ Job dataset not found:")
        print(INPUT_FILE)

        return

    print("\n✅ Job dataset found")

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="utf-8",
            low_memory=False
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="latin-1",
            low_memory=False
        )

    print(f"\nOriginal rows: {len(df):,}")
    print(f"Original columns: {len(df.columns)}")

    print("\nOriginal columns:")

    for column in df.columns:
        print(f"  • {column}")

    # --------------------------------------------------------
    # Rename columns according to ACTUAL dataset
    # --------------------------------------------------------

    df = df.rename(
        columns={
            "Company Name": "company",
            "Locations": "location",
            "Salary": "salary",
            "Experience": "experience",
            "Skills": "skills"
        }
    )

    # --------------------------------------------------------
    # Verify expected columns
    # --------------------------------------------------------

    required_columns = [
        "company",
        "location",
        "salary",
        "experience",
        "skills"
    ]

    print("\nChecking columns:")

    for column in required_columns:

        if column in df.columns:
            print(f"  ✅ {column}")

        else:
            print(f"  ❌ {column} missing")

    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    df["company"] = df["company"].apply(clean_text)

    df["location"] = df["location"].apply(clean_text)

    df["salary"] = df["salary"].apply(clean_salary)

    df["skills"] = df["skills"].apply(clean_skills)

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    df["experience_text"] = (
        df["experience"]
        .apply(clean_text)
    )

    df["experience_years"] = (
        df["experience"]
        .apply(extract_experience)
    )

    # --------------------------------------------------------
    # Remove duplicate records
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=[
            "company",
            "location",
            "salary",
            "experience",
            "skills"
        ]
    )

    after = len(df)

    print(
        f"\nDuplicate records removed: "
        f"{before - after:,}"
    )

    print(
        f"Unique job records remaining: "
        f"{after:,}"
    )

    # --------------------------------------------------------
    # Remove records without skills
    # --------------------------------------------------------

    before = len(df)

    df = df[
        df["skills"].str.strip() != ""
    ]

    after = len(df)

    print(
        f"Records removed without skills: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # Job title
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # The original dataset does NOT contain job titles.
    #
    # We therefore do NOT invent a job title.
    #
    # Later, ESCO will be used to infer the most appropriate
    # occupation from the required skills.
    #

    df["job_title"] = ""

    # --------------------------------------------------------
    # Employment type
    # --------------------------------------------------------
    #
    # Original dataset does not contain employment type.
    #

    df["employment_type"] = ""

    # --------------------------------------------------------
    # Create searchable job text
    # --------------------------------------------------------

    df["job_text"] = (
        df["company"]
        + " "
        + df["location"]
        + " "
        + df["skills"]
        + " "
        + df["experience_text"]
    ).str.strip()

    # --------------------------------------------------------
    # Create unique job ID
    # --------------------------------------------------------

    df.insert(
        0,
        "job_id",
        range(1, len(df) + 1)
    )

    # --------------------------------------------------------
    # Arrange columns
    # --------------------------------------------------------

    final_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "skills",
        "salary",
        "employment_type",
        "experience_text",
        "experience_years",
        "job_text"
    ]

    df = df[final_columns]

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("             CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"\nFinal jobs: {len(df):,}"
    )

    print("\nSaved to:")

    print(OUTPUT_FILE)

    print("\nFinal columns:")

    for column in final_columns:
        print(f"  ✓ {column}")

    print("\nFirst 5 cleaned jobs:")

    print(
        df.head(5).to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)

    print(
        "✅ JOB DATASET READY"
    )

    print("=" * 70)

    print("\nNOTE:")
    print(
        "Job titles will be inferred later using ESCO "
        "occupation-skill relationships."
    )


if __name__ == "__main__":
    main()