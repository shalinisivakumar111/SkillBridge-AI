import os
import re
import sys
import pandas as pd

# PDF library
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SKILL_DICTIONARY = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "skill_dictionary.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "candidate_skills.csv"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for skill matching.
    """

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Replace common separators with spaces
    text = text.replace("/", " ")
    text = text.replace("\\", " ")
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    # Remove unusual characters
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill(text):
    """
    Normalize an individual skill.
    """

    text = normalize_text(text)

    # Common abbreviations
    replacements = {
        "microsoft excel": "excel",
        "ms excel": "excel",
        "microsoft office": "office",
        "ms office": "office",
        "microsoft word": "word",
        "ms word": "word",
        "structured query language": "sql",
        "python programming": "python",
        "javascript programming": "javascript",
    }

    return replacements.get(text, text)


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_path):

    if not os.path.exists(pdf_path):
        print("\n❌ Resume file not found:")
        print(pdf_path)
        return ""

    try:

        document = pymupdf.open(pdf_path)

        pages = []

        for page in document:
            text = page.get_text()

            if text:
                pages.append(text)

        document.close()

        full_text = "\n".join(pages)

        return full_text

    except Exception as error:

        print("\n❌ Could not read PDF.")
        print(f"Error: {error}")

        return ""


# ============================================================
# LOAD ESCO SKILL DICTIONARY
# ============================================================

def load_skill_dictionary():

    print("\nLoading ESCO skill dictionary...")

    if not os.path.exists(SKILL_DICTIONARY):

        print("\n❌ Skill dictionary not found:")
        print(SKILL_DICTIONARY)

        return None

    try:

        df = pd.read_csv(
            SKILL_DICTIONARY,
            keep_default_na=False
        )

    except Exception as error:

        print("\n❌ Could not load skill dictionary.")
        print(f"Error: {error}")

        return None

    print(
        f"ESCO skills available: {len(df):,}"
    )

    return df


# ============================================================
# BUILD SKILL INDEX
# ============================================================

def build_skill_index(skill_df):

    skill_index = {}

    for _, row in skill_df.iterrows():

        skill_id = str(
            row.get("skill_id", "")
        ).strip()

        skill = str(
            row.get("skill", "")
        ).strip()

        aliases = str(
            row.get("aliases", "")
        ).strip()

        if not skill:
            continue

        # ----------------------------------------------------
        # Preferred skill name
        # ----------------------------------------------------

        preferred = normalize_skill(skill)

        if preferred:
            skill_index.setdefault(
                preferred,
                {
                    "skill_id": skill_id,
                    "skill": skill,
                    "source": "preferred"
                }
            )

        # ----------------------------------------------------
        # Aliases
        # ----------------------------------------------------

        if aliases:

            # ESCO aliases can be separated by newlines
            alias_list = re.split(
                r"[\n;,|]+",
                aliases
            )

            for alias in alias_list:

                alias = alias.strip()

                if not alias:
                    continue

                normalized_alias = normalize_skill(alias)

                if not normalized_alias:
                    continue

                # Do not overwrite preferred skill
                if normalized_alias not in skill_index:

                    skill_index[
                        normalized_alias
                    ] = {
                        "skill_id": skill_id,
                        "skill": skill,
                        "source": "alias"
                    }

    return skill_index


# ============================================================
# FIND SKILLS IN RESUME
# ============================================================

def find_skills(resume_text, skill_index):

    normalized_resume = normalize_text(
        resume_text
    )

    found = {}

    # --------------------------------------------------------
    # Sort longest skills first.
    #
    # This prevents:
    #
    # "data analysis"
    #
    # being detected after:
    #
    # "data"
    # --------------------------------------------------------

    skills_to_check = sorted(
        skill_index.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for normalized_skill, info in skills_to_check:

        if len(normalized_skill) < 2:
            continue

        # ----------------------------------------------------
        # Word-boundary matching
        # ----------------------------------------------------

        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(normalized_skill)
            + r"(?![a-z0-9+#])"
        )

        if re.search(
            pattern,
            normalized_resume
        ):

            skill_name = info["skill"]

            key = normalize_skill(
                skill_name
            )

            if key not in found:

                found[key] = {
                    "skill_id": info["skill_id"],
                    "skill": skill_name,
                    "matched_as": normalized_skill,
                    "source": info["source"]
                }

    return list(found.values())


# ============================================================
# REMOVE WEAK / DUPLICATE SKILLS
# ============================================================

def clean_detected_skills(skills):

    cleaned = []

    seen = set()

    # Skills that are too generic to be useful
    generic_skills = {
        "data",
        "work",
        "management",
        "business",
        "service",
        "communication",
        "english",
        "language",
        "information",
        "technology",
        "skills",
        "operations",
        "support"
    }

    for item in skills:

        skill = item["skill"].strip()

        normalized = normalize_skill(
            skill
        )

        if not normalized:
            continue

        # Keep generic skills only when they
        # are part of a more specific phrase
        if normalized in generic_skills:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        cleaned.append(item)

    return cleaned


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    candidate_skills,
    resume_path
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    rows = []

    for item in candidate_skills:

        rows.append(
            {
                "resume_file": os.path.basename(
                    resume_path
                ),
                "skill_id": item["skill_id"],
                "skill": item["skill"],
                "matched_as": item["matched_as"],
                "source": item["source"]
            }
        )

    df = pd.DataFrame(
        rows,
        columns=[
            "resume_file",
            "skill_id",
            "skill",
            "matched_as",
            "source"
        ]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("          RESUME SKILL EXTRACTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Check command line argument
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print("\n❌ Please provide a resume PDF.")

        print(
            "\nExample:"
        )

        print(
            "python scripts/11_resume_skill_extractor.py "
            "uploads/resumes/test_resume.pdf"
        )

        return

    resume_path = sys.argv[1]

    # --------------------------------------------------------
    # Convert relative path to project path
    # --------------------------------------------------------

    if not os.path.isabs(resume_path):

        resume_path = os.path.join(
            BASE_DIR,
            resume_path
        )

    print("\nResume:")
    print(resume_path)

    # --------------------------------------------------------
    # Check resume
    # --------------------------------------------------------

    if not os.path.exists(resume_path):

        print("\n❌ Resume file not found:")
        print(resume_path)

        return

    print("\n✅ Resume file found")

    # --------------------------------------------------------
    # Extract PDF
    # --------------------------------------------------------

    print("\nExtracting resume text...")

    resume_text = extract_pdf_text(
        resume_path
    )

    if not resume_text.strip():

        print(
            "\n❌ No readable text found in the PDF."
        )

        print(
            "The PDF may be image/scanned only."
        )

        return

    print(
        f"Resume text extracted: "
        f"{len(resume_text):,} characters"
    )

    # --------------------------------------------------------
    # Load ESCO dictionary
    # --------------------------------------------------------

    skill_df = load_skill_dictionary()

    if skill_df is None:
        return

    # --------------------------------------------------------
    # Build index
    # --------------------------------------------------------

    print("\nBuilding offline skill index...")

    skill_index = build_skill_index(
        skill_df
    )

    print(
        f"Searchable skill terms: "
        f"{len(skill_index):,}"
    )

    # --------------------------------------------------------
    # Find skills
    # --------------------------------------------------------

    print("\nSearching resume for matching skills...")

    detected_skills = find_skills(
        resume_text,
        skill_index
    )

    # --------------------------------------------------------
    # Clean results
    # --------------------------------------------------------

    detected_skills = clean_detected_skills(
        detected_skills
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    result_df = save_results(
        detected_skills,
        resume_path
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("           DETECTED CANDIDATE SKILLS")
    print("=" * 70)

    if len(result_df) == 0:

        print(
            "\n⚠️ No ESCO skills were detected."
        )

        print(
            "\nTry using a resume containing skills such as:"
        )

        print(
            "Excel, Python, SQL, communication, "
            "data entry, accounting, etc."
        )

    else:

        for number, skill in enumerate(
            result_df["skill"].tolist(),
            start=1
        ):

            print(
                f"{number:2}. {skill}"
            )

    print(
        f"\nTotal candidate skills: "
        f"{len(result_df)}"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("        RESUME SKILL EXTRACTION COMPLETE")
    print("=" * 70)

    print("\nSaved candidate skills to:")

    print(OUTPUT_FILE)

    print("\nNext stage:")

    print(
        "Candidate skills → Local job matching"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()