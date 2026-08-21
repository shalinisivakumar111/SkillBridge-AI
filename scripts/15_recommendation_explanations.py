import pandas as pd
import os
import math


# ============================================================
# SKILLBRIDGE AI
# RECOMMENDATION EXPLANATION ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "smart_job_recommendations.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_recommendations.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """Convert NaN/empty values into a safe string."""

    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    return str(value).strip()


def create_explanation(row):
    """
    Create a human-readable explanation for a job recommendation.
    """

    job_title = clean_value(row.get("job_title"))
    location = clean_value(row.get("location"))

    skill_match = float(row.get("skill_match", 0))
    local_bonus = float(row.get("local_bonus", 0))
    final_score = float(row.get("final_score", 0))

    matched_skills = clean_value(
        row.get("matched_skills")
    )

    match_types = clean_value(
        row.get("match_types")
    )

    reasons = []

    # --------------------------------------------------------
    # Skill matching explanation
    # --------------------------------------------------------

    if matched_skills:

        matches = matched_skills.split(";")

        for match in matches:

            match = match.strip()

            if not match:
                continue

            if "→" in match:

                candidate_skill, job_skill = match.split(
                    "→",
                    1
                )

                candidate_skill = candidate_skill.strip()
                job_skill = job_skill.strip()

                reasons.append(
                    f"{candidate_skill} matches "
                    f"{job_skill}"
                )

            else:

                reasons.append(
                    f"Candidate skill matches {match}"
                )

    # --------------------------------------------------------
    # Match quality
    # --------------------------------------------------------

    if skill_match >= 70:
        match_quality = "Excellent skill match"

    elif skill_match >= 50:
        match_quality = "Strong skill match"

    elif skill_match >= 30:
        match_quality = "Moderate skill match"

    elif skill_match > 0:
        match_quality = "Partial skill match"

    else:
        match_quality = "No direct skill match"

    # --------------------------------------------------------
    # Locality explanation
    # --------------------------------------------------------

    if local_bonus > 0:

        local_reason = (
            f"Local opportunity in or near "
            f"the candidate's area ({location})"
        )

    else:

        local_reason = (
            f"Location is outside the candidate's "
            f"preferred local area ({location})"
        )

    # --------------------------------------------------------
    # Overall recommendation
    # --------------------------------------------------------

    if final_score >= 70:

        recommendation = "Highly Recommended"

    elif final_score >= 50:

        recommendation = "Recommended"

    elif final_score >= 30:

        recommendation = "Possible Match"

    else:

        recommendation = "Low Match"

    # --------------------------------------------------------
    # Build explanation
    # --------------------------------------------------------

    explanation_parts = []

    explanation_parts.append(
        match_quality
    )

    if reasons:

        explanation_parts.extend(
            reasons[:5]
        )

    explanation_parts.append(
        local_reason
    )

    explanation_parts.append(
        f"Overall recommendation score: "
        f"{final_score:.1f}%"
    )

    explanation = ". ".join(
        explanation_parts
    )

    if not explanation.endswith("."):
        explanation += "."

    return (
        recommendation,
        explanation
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       RECOMMENDATION EXPLANATION ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Check input
    # --------------------------------------------------------

    print("\nLoading smart recommendations...")

    if not os.path.exists(INPUT_FILE):

        print("❌ Smart recommendations file not found.")

        print(
            f"Expected location:\n{INPUT_FILE}"
        )

        print(
            "\nRun this first:"
        )

        print(
            "python scripts/14_smart_skill_matching.py"
        )

        return

    # --------------------------------------------------------
    # 2. Load recommendations
    # --------------------------------------------------------

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Recommendations loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # 3. Validate required columns
    # --------------------------------------------------------

    required_columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "skill_match",
        "local_bonus",
        "final_score",
        "matched_skills",
        "match_types"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print(
            "\n❌ Missing columns:"
        )

        for column in missing:
            print(
                f"  • {column}"
            )

        return

    # --------------------------------------------------------
    # 4. Create explanations
    # --------------------------------------------------------

    print(
        "\nGenerating recommendation explanations..."
    )

    recommendations = []
    explanations = []

    for _, row in df.iterrows():

        recommendation, explanation = (
            create_explanation(row)
        )

        recommendations.append(
            recommendation
        )

        explanations.append(
            explanation
        )

    df[
        "recommendation"
    ] = recommendations

    df[
        "explanation"
    ] = explanations

    # --------------------------------------------------------
    # 5. Add skill summary
    # --------------------------------------------------------

    def skill_summary(value):

        value = clean_value(value)

        if not value:
            return "No matching skills detected"

        matches = [
            item.strip()
            for item in value.split(";")
            if item.strip()
        ]

        return (
            f"{len(matches)} relevant skill "
            f"connection(s) found"
        )

    df[
        "skill_summary"
    ] = df[
        "matched_skills"
    ].apply(skill_summary)

    # --------------------------------------------------------
    # 6. Save final recommendations
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # 7. Display results
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("          FINAL JOB RECOMMENDATIONS")
    print("=" * 70)

    for index, row in df.head(10).iterrows():

        print(
            f"\n{index + 1}. "
            f"{row['job_title']}"
        )

        print(
            f"   Company: "
            f"{row['company']}"
        )

        print(
            f"   Location: "
            f"{row['location']}"
        )

        print(
            f"   Skill Match: "
            f"{float(row['skill_match']):.1f}%"
        )

        print(
            f"   Local Bonus: "
            f"+{float(row['local_bonus']):.1f}%"
        )

        print(
            f"   Final Score: "
            f"{float(row['final_score']):.1f}%"
        )

        print(
            f"   Recommendation: "
            f"{row['recommendation']}"
        )

        print(
            f"   Why recommended:"
        )

        print(
            f"   {row['explanation']}"
        )

    # --------------------------------------------------------
    # 8. Completion message
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("      RECOMMENDATION EXPLANATIONS READY")
    print("=" * 70)

    print(
        f"\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nNew columns:"
    )

    print(
        "  ✓ recommendation"
    )

    print(
        "  ✓ explanation"
    )

    print(
        "  ✓ skill_summary"
    )

    print(
        "\nNext stage:"
    )

    print(
        "Final recommendations → Multilingual interface"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()