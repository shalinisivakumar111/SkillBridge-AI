import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESCO_SKILLS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "esco_skills.csv"
)

ESCO_RELATIONS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "occupation_skills.csv"
)

OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "skill_dictionary.csv"
)


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("             SKILL DICTIONARY")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Load ESCO skills
    # --------------------------------------------------

    print("\nLoading ESCO skills...")

    if not os.path.exists(ESCO_SKILLS):
        print("❌ esco_skills.csv not found")
        print(f"Expected location: {ESCO_SKILLS}")
        return

    skills = pd.read_csv(ESCO_SKILLS)

    print(f"ESCO skills loaded: {len(skills):,}")

    # --------------------------------------------------
    # 2. Select useful columns
    # --------------------------------------------------

    columns = [
        "conceptUri",
        "preferredLabel",
        "altLabels",
        "skillType",
        "reuseLevel",
        "description"
    ]

    available = [c for c in columns if c in skills.columns]

    skills = skills[available].copy()

    # --------------------------------------------------
    # 3. Rename columns
    # --------------------------------------------------

    rename_map = {
        "conceptUri": "skill_id",
        "preferredLabel": "skill",
        "altLabels": "aliases",
        "skillType": "skill_type",
        "reuseLevel": "reuse_level",
        "description": "description"
    }

    skills.rename(columns=rename_map, inplace=True)

    # --------------------------------------------------
    # 4. Clean text
    # --------------------------------------------------

    for column in ["skill", "aliases", "description"]:

        if column in skills.columns:
            skills[column] = skills[column].fillna("").astype(str)

    skills["skill"] = skills["skill"].apply(clean_text)

    skills["aliases"] = skills["aliases"].apply(clean_text)

    # --------------------------------------------------
    # 5. Remove empty skills
    # --------------------------------------------------

    skills = skills[
        skills["skill"].str.len() > 0
    ].copy()

    # --------------------------------------------------
    # 6. Remove duplicates
    # --------------------------------------------------

    skills.drop_duplicates(
        subset=["skill_id"],
        inplace=True
    )

    # --------------------------------------------------
    # 7. Create searchable text
    # --------------------------------------------------

    skills["search_text"] = (
        skills["skill"] + " " +
        skills["aliases"] + " " +
        skills["description"]
    ).str.strip()

    # --------------------------------------------------
    # 8. Create normalized skill name
    # --------------------------------------------------

    skills["normalized_skill"] = (
        skills["skill"]
        .str.lower()
        .str.replace(r"[^a-z0-9+#.\- ]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # --------------------------------------------------
    # 9. Save
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    skills.to_csv(
        OUTPUT,
        index=False
    )

    # --------------------------------------------------
    # 10. Display result
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("          SKILL DICTIONARY COMPLETE")
    print("=" * 70)

    print(f"\nTotal skills: {len(skills):,}")

    print(f"\nSaved to:")
    print(OUTPUT)

    print("\nColumns:")

    for column in skills.columns:
        print(f"  ✓ {column}")

    print("\nFirst 10 skills:")

    print(
        skills[
            ["skill_id", "skill", "normalized_skill"]
        ].head(10).to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("✅ SKILL DICTIONARY READY")
    print("=" * 70)


if __name__ == "__main__":
    main()