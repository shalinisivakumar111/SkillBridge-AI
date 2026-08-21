from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"


DATASETS = {
    "Jobs": DATA_DIR / "jobs" / "Job_dataset.csv",

    "Resumes": DATA_DIR / "resume" / "UpdatedResumeDataSet.csv",

    "O*NET Essential Skills":
        DATA_DIR / "onet" / "essential_skills.csv",

    "O*NET Software Skills":
        DATA_DIR / "onet" / "software_skills.csv",

    "O*NET Transferable Skills":
        DATA_DIR / "onet" / "transferable_skills_to_work_context.csv",

    "O*NET Knowledge":
        DATA_DIR / "onet" / "knowledge.csv",

    "ESCO Occupations":
        DATA_DIR / "esco" / "occupations_en.csv",

    "ESCO Skills":
        DATA_DIR / "esco" / "skills_en.csv",

    "ESCO Skill Hierarchy":
        DATA_DIR / "esco" / "skillsHierarchy_en.csv",

    "ESCO Occupation-Skill Relations":
        DATA_DIR / "esco" / "occupationSkillRelations_en.csv",
}


def inspect_dataset(name, path):

    print("\n" + "=" * 70)
    print(f"DATASET: {name}")
    print("=" * 70)

    print(f"Path: {path}")

    if not path.exists():
        print("❌ FILE NOT FOUND")
        return

    print("✅ FILE FOUND")

    try:
        df = pd.read_csv(
            path,
            encoding="utf-8",
            low_memory=False
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            path,
            encoding="latin-1",
            low_memory=False
        )

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nCOLUMN NAMES:")

    for column in df.columns:
        print(f"  • {column}")

    print("\nMISSING VALUES:")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("  No missing values")
    else:
        for column, count in missing.items():
            percentage = count / len(df) * 100

            print(
                f"  • {column}: "
                f"{count:,} "
                f"({percentage:.2f}%)"
            )

    print("\nDUPLICATES:")

    duplicates = df.duplicated().sum()

    print(f"  {duplicates:,} duplicate rows")

    print("\nFIRST 3 ROWS:")

    print(
        df.head(3).to_string(index=False)
    )


def main():

    print("\n")
    print("=" * 70)
    print("                 SKILLBRIDGE AI")
    print("              DATASET INSPECTION")
    print("=" * 70)

    print(f"\nProject:")
    print(PROJECT_ROOT)

    print(f"\nData:")
    print(DATA_DIR)

    for name, path in DATASETS.items():

        inspect_dataset(
            name,
            path
        )

    print("\n")
    print("=" * 70)
    print("              INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()