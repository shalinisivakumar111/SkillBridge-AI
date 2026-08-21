from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "esco"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# Input files
SKILLS_FILE = RAW_DIR / "skills_en.csv"
OCCUPATIONS_FILE = RAW_DIR / "occupations_en.csv"
RELATIONS_FILE = RAW_DIR / "occupationSkillRelations_en.csv"
HIERARCHY_FILE = RAW_DIR / "skillsHierarchy_en.csv"


# Output files
SKILLS_OUTPUT = PROCESSED_DIR / "esco_skills.csv"
OCCUPATIONS_OUTPUT = PROCESSED_DIR / "esco_occupations.csv"
RELATIONS_OUTPUT = PROCESSED_DIR / "occupation_skills.csv"
HIERARCHY_OUTPUT = PROCESSED_DIR / "skill_hierarchy.csv"


# ============================================================
# LOAD CSV
# ============================================================

def load_csv(path):

    if not path.exists():

        print(f"❌ File not found: {path}")

        return None

    try:

        return pd.read_csv(
            path,
            encoding="utf-8",
            low_memory=False
        )

    except UnicodeDecodeError:

        return pd.read_csv(
            path,
            encoding="latin-1",
            low_memory=False
        )


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# PROCESS SKILLS
# ============================================================

def process_skills():

    print("\n" + "-" * 70)
    print("PROCESSING ESCO SKILLS")
    print("-" * 70)

    df = load_csv(SKILLS_FILE)

    if df is None:
        return None

    print(f"Original skills: {len(df):,}")

    # Keep useful fields only
    columns = [
        "conceptUri",
        "skillType",
        "reuseLevel",
        "preferredLabel",
        "altLabels",
        "description"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df[available].copy()

    # Clean text
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .apply(clean_text)
            )

    # Remove duplicate skill URIs
    if "conceptUri" in df.columns:

        df = df.drop_duplicates(
            subset=["conceptUri"]
        )

    # Remove rows without skill name
    if "preferredLabel" in df.columns:

        df = df[
            df["preferredLabel"].str.strip() != ""
        ]

    df.to_csv(
        SKILLS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Clean skills: {len(df):,}"
    )

    print(
        f"Saved: {SKILLS_OUTPUT}"
    )

    return df


# ============================================================
# PROCESS OCCUPATIONS
# ============================================================

def process_occupations():

    print("\n" + "-" * 70)
    print("PROCESSING ESCO OCCUPATIONS")
    print("-" * 70)

    df = load_csv(OCCUPATIONS_FILE)

    if df is None:
        return None

    print(
        f"Original occupations: {len(df):,}"
    )

    columns = [
        "conceptUri",
        "iscoGroup",
        "preferredLabel",
        "altLabels",
        "description",
        "code"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df[available].copy()

    # Clean text
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .apply(clean_text)
            )

    # Remove duplicate occupations
    if "conceptUri" in df.columns:

        df = df.drop_duplicates(
            subset=["conceptUri"]
        )

    # Remove empty occupation names
    if "preferredLabel" in df.columns:

        df = df[
            df["preferredLabel"].str.strip() != ""
        ]

    df.to_csv(
        OCCUPATIONS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Clean occupations: {len(df):,}"
    )

    print(
        f"Saved: {OCCUPATIONS_OUTPUT}"
    )

    return df


# ============================================================
# PROCESS OCCUPATION-SKILL RELATIONS
# ============================================================

def process_relations():

    print("\n" + "-" * 70)
    print("PROCESSING OCCUPATION-SKILL RELATIONS")
    print("-" * 70)

    df = load_csv(RELATIONS_FILE)

    if df is None:
        return None

    print(
        f"Original relations: {len(df):,}"
    )

    columns = [
        "occupationUri",
        "occupationLabel",
        "relationType",
        "skillType",
        "skillUri",
        "skillLabel"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df[available].copy()

    # Clean text
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .apply(clean_text)
            )

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Remove relations without occupation
    df = df[
        df["occupationUri"].str.strip() != ""
    ]

    # Remove relations without skill
    df = df[
        df["skillUri"].str.strip() != ""
    ]

    df.to_csv(
        RELATIONS_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Clean relations: {len(df):,}"
    )

    print(
        f"Saved: {RELATIONS_OUTPUT}"
    )

    return df


# ============================================================
# PROCESS SKILL HIERARCHY
# ============================================================

def process_hierarchy():

    print("\n" + "-" * 70)
    print("PROCESSING SKILL HIERARCHY")
    print("-" * 70)

    df = load_csv(HIERARCHY_FILE)

    if df is None:
        return None

    print(
        f"Original hierarchy rows: {len(df):,}"
    )

    useful_columns = [
        "Level 0 URI",
        "Level 0 preferred term",
        "Level 1 URI",
        "Level 1 preferred term",
        "Level 2 URI",
        "Level 2 preferred term",
        "Level 3 URI",
        "Level 3 preferred term",
        "Description",
        "Scope note",
        "Level 0 code",
        "Level 1 code",
        "Level 2 code",
        "Level 3 code"
    ]

    available = [
        column
        for column in useful_columns
        if column in df.columns
    ]

    df = df[available].copy()

    # Clean string fields
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .apply(clean_text)
            )

    df = df.drop_duplicates()

    df.to_csv(
        HIERARCHY_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Clean hierarchy rows: {len(df):,}"
    )

    print(
        f"Saved: {HIERARCHY_OUTPUT}"
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("                 SKILLBRIDGE AI")
    print("               ESCO PROCESSING")
    print("=" * 70)

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Process all four datasets

    skills = process_skills()

    occupations = process_occupations()

    relations = process_relations()

    hierarchy = process_hierarchy()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("              ESCO PROCESSING COMPLETE")
    print("=" * 70)

    print("\nGenerated files:")

    if skills is not None:
        print(
            f"  ✅ esco_skills.csv "
            f"({len(skills):,} rows)"
        )

    if occupations is not None:
        print(
            f"  ✅ esco_occupations.csv "
            f"({len(occupations):,} rows)"
        )

    if relations is not None:
        print(
            f"  ✅ occupation_skills.csv "
            f"({len(relations):,} rows)"
        )

    if hierarchy is not None:
        print(
            f"  ✅ skill_hierarchy.csv "
            f"({len(hierarchy):,} rows)"
        )

    print("\n" + "=" * 70)
    print("✅ ESCO DATA IS READY FOR SKILL MATCHING")
    print("=" * 70)


if __name__ == "__main__":
    main()