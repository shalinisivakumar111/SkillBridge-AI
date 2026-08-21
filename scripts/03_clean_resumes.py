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
    / "resume"
    / "UpdatedResumeDataSet.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = OUTPUT_DIR / "resumes_clean.csv"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    value = str(value)

    # Fix common encoding problems
    replacements = {
        "Ã©️": "é",
        "Ã¯": "ï",
        "Ã±": "ñ",
        "Ã©️": "é",
        "â€™️": "'",
        "â€“": "-",
        "â€œ": '"',
        "â€": '"',
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    # Normalize line breaks
    value = value.replace("\r", "\n")

    # Remove excessive whitespace
    value = re.sub(r"[ \t]+", " ", value)

    # Remove excessive blank lines
    value = re.sub(r"\n\s*\n+", "\n\n", value)

    return value.strip()


# ============================================================
# CATEGORY CLEANING
# ============================================================

def clean_category(value):

    value = clean_text(value)

    if not value:
        return "Unknown"

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("             SKILLBRIDGE AI")
    print("            RESUME CLEANING")
    print("=" * 70)

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print("\n❌ Resume dataset not found:")
        print(INPUT_FILE)

        return

    print("\n✅ Resume dataset found")

    # --------------------------------------------------------
    # Load dataset
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
    # Verify columns
    # --------------------------------------------------------

    required_columns = [
        "Category",
        "Resume"
    ]

    print("\nChecking columns:")

    for column in required_columns:

        if column in df.columns:
            print(f"  ✅ {column}")

        else:
            print(f"  ❌ {column} missing")

    # --------------------------------------------------------
    # Rename columns
    # --------------------------------------------------------

    df = df.rename(
        columns={
            "Category": "category",
            "Resume": "resume_text"
        }
    )

    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    df["category"] = (
        df["category"]
        .apply(clean_category)
    )

    df["resume_text"] = (
        df["resume_text"]
        .apply(clean_text)
    )

    # --------------------------------------------------------
    # Remove duplicate resumes
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["resume_text"]
    )

    removed = before - len(df)

    print(
        f"\nDuplicate resumes removed: "
        f"{removed:,}"
    )

    print(
        f"Unique resumes remaining: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Remove empty resumes
    # --------------------------------------------------------

    before = len(df)

    df = df[
        df["resume_text"].str.strip() != ""
    ]

    removed_empty = before - len(df)

    print(
        f"Empty resumes removed: "
        f"{removed_empty:,}"
    )

    # --------------------------------------------------------
    # Create resume IDs
    # --------------------------------------------------------

    df.insert(
        0,
        "resume_id",
        range(1, len(df) + 1)
    )

    # --------------------------------------------------------
    # Resume length
    # --------------------------------------------------------

    df["resume_length"] = (
        df["resume_text"]
        .str.len()
    )

    # --------------------------------------------------------
    # Word count
    # --------------------------------------------------------

    df["word_count"] = (
        df["resume_text"]
        .str.split()
        .str.len()
    )

    # --------------------------------------------------------
    # Final column order
    # --------------------------------------------------------

    df = df[
        [
            "resume_id",
            "category",
            "resume_text",
            "resume_length",
            "word_count"
        ]
    ]

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
    # Statistics
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("             CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"\nFinal resumes: {len(df):,}"
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("\nFinal columns:")

    for column in df.columns:
        print(f"  ✓ {column}")

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    print("\nResume categories:")

    category_counts = (
        df["category"]
        .value_counts()
    )

    for category, count in category_counts.items():

        print(
            f"  • {category}: {count}"
        )

    # --------------------------------------------------------
    # First 3 resumes
    # --------------------------------------------------------

    print("\nFirst 3 cleaned resumes:")

    preview = df[
        [
            "resume_id",
            "category",
            "word_count"
        ]
    ].head(3)

    print(
        preview.to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("✅ RESUME DATASET READY")
    print("=" * 70)


if __name__ == "__main__":
    main()