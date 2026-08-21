import pandas as pd
import os


# ============================================================
# SKILLBRIDGE AI
# STEP 16 - OFFLINE MULTILINGUAL INTERFACE
# Languages:
# English
# Telugu
# Hindi
# Tamil
# ============================================================


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_recommendations.csv"
)


# ============================================================
# TRANSLATIONS
# ============================================================

TEXT = {

    "en": {
        "language": "English",
        "title": "SKILLBRIDGE AI",
        "subtitle": "AI-Based Skill Matching for Local Employment",
        "select_language": "Select Language",
        "candidate": "Candidate",
        "location": "Location",
        "top_jobs": "TOP LOCAL JOB MATCHES",
        "company": "Company",
        "skill_match": "Skill Match",
        "local_bonus": "Local Bonus",
        "final_score": "Final Score",
        "recommendation": "Recommendation",
        "why": "Why recommended",
        "matched_skills": "Matched Skills",
        "excellent": "Highly Recommended",
        "strong": "Recommended",
        "moderate": "Possible Match",
        "low": "Low Match",
        "exit": "Exit",
        "invalid": "Invalid choice. Please try again.",
        "no_jobs": "No recommendations found.",
        "complete": "MULTILINGUAL RECOMMENDATION COMPLETE"
    },

    "te": {
        "language": "తెలుగు",
        "title": "స్కిల్‌బ్రిడ్జ్ AI",
        "subtitle": "స్థానిక ఉద్యోగాల కోసం AI ఆధారిత నైపుణ్య సరిపోలిక",
        "select_language": "భాషను ఎంచుకోండి",
        "candidate": "అభ్యర్థి",
        "location": "ప్రాంతం",
        "top_jobs": "అత్యుత్తమ స్థానిక ఉద్యోగ సరిపోలికలు",
        "company": "కంపెనీ",
        "skill_match": "నైపుణ్య సరిపోలిక",
        "local_bonus": "స్థానిక బోనస్",
        "final_score": "తుది స్కోర్",
        "recommendation": "సిఫార్సు",
        "why": "ఎందుకు సిఫార్సు చేయబడింది",
        "matched_skills": "సరిపోలిన నైపుణ్యాలు",
        "excellent": "చాలా మంచి సరిపోలిక",
        "strong": "సిఫార్సు చేయబడింది",
        "moderate": "సాధ్యమైన సరిపోలిక",
        "low": "తక్కువ సరిపోలిక",
        "exit": "నిష్క్రమించు",
        "invalid": "చెల్లని ఎంపిక. మళ్లీ ప్రయత్నించండి.",
        "no_jobs": "ఉద్యోగ సిఫార్సులు కనుగొనబడలేదు.",
        "complete": "బహుభాషా ఉద్యోగ సిఫార్సులు పూర్తయ్యాయి"
    },

    "hi": {
        "language": "हिन्दी",
        "title": "स्किलब्रिज AI",
        "subtitle": "स्थानीय रोजगार के लिए AI आधारित कौशल मिलान",
        "select_language": "भाषा चुनें",
        "candidate": "उम्मीदवार",
        "location": "स्थान",
        "top_jobs": "शीर्ष स्थानीय नौकरी मिलान",
        "company": "कंपनी",
        "skill_match": "कौशल मिलान",
        "local_bonus": "स्थानीय बोनस",
        "final_score": "अंतिम स्कोर",
        "recommendation": "सिफारिश",
        "why": "क्यों सुझाया गया",
        "matched_skills": "मिलान किए गए कौशल",
        "excellent": "बहुत अच्छा मिलान",
        "strong": "अनुशंसित",
        "moderate": "संभावित मिलान",
        "low": "कम मिलान",
        "exit": "बाहर निकलें",
        "invalid": "अमान्य विकल्प। कृपया फिर प्रयास करें।",
        "no_jobs": "कोई नौकरी सुझाव नहीं मिला।",
        "complete": "बहुभाषी नौकरी सिफारिश पूरी हुई"
    },

    "ta": {
        "language": "தமிழ்",
        "title": "ஸ்கில்பிரிட்ஜ் AI",
        "subtitle": "உள்ளூர் வேலைவாய்ப்பிற்கான AI அடிப்படையிலான திறன் பொருத்தம்",
        "select_language": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "candidate": "விண்ணப்பதாரர்",
        "location": "இடம்",
        "top_jobs": "சிறந்த உள்ளூர் வேலை பொருத்தங்கள்",
        "company": "நிறுவனம்",
        "skill_match": "திறன் பொருத்தம்",
        "local_bonus": "உள்ளூர் போனஸ்",
        "final_score": "இறுதி மதிப்பெண்",
        "recommendation": "பரிந்துரை",
        "why": "ஏன் பரிந்துரைக்கப்படுகிறது",
        "matched_skills": "பொருந்திய திறன்கள்",
        "excellent": "மிகச் சிறந்த பொருத்தம்",
        "strong": "பரிந்துரைக்கப்படுகிறது",
        "moderate": "சாத்தியமான பொருத்தம்",
        "low": "குறைந்த பொருத்தம்",
        "exit": "வெளியேறு",
        "invalid": "தவறான தேர்வு. மீண்டும் முயற்சிக்கவும்.",
        "no_jobs": "வேலை பரிந்துரைகள் எதுவும் கிடைக்கவில்லை.",
        "complete": "பல்மொழி வேலை பரிந்துரை முடிந்தது"
    }
}


# ============================================================
# LANGUAGE SELECTION
# ============================================================

def choose_language():

    print("\n" + "=" * 70)
    print("              SKILLBRIDGE AI")
    print("             MULTILINGUAL MODE")
    print("=" * 70)

    print("\nSelect Language / భాష / भाषा / மொழி")

    print("1. English")
    print("2. తెలుగు")
    print("3. हिन्दी")
    print("4. தமிழ்")

    while True:

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            return "en"

        if choice == "2":
            return "te"

        if choice == "3":
            return "hi"

        if choice == "4":
            return "ta"

        print("Invalid choice. Please enter 1, 2, 3 or 4.")


# ============================================================
# RECOMMENDATION LABEL
# ============================================================

def get_recommendation(score, lang):

    if score >= 70:
        key = "excellent"

    elif score >= 50:
        key = "strong"

    elif score >= 30:
        key = "moderate"

    else:
        key = "low"

    return TEXT[lang][key]


# ============================================================
# DISPLAY JOB
# ============================================================

def display_job(row, number, lang, candidate_name, candidate_location):

    t = TEXT[lang]

    score = float(row["final_score"])
    skill_match = float(row["skill_match"])
    local_bonus = float(row["local_bonus"])

    print("\n" + "-" * 70)

    print(
        f"{number}. {row['job_title']}"
    )

    print(
        f"   {t['company']}: {row['company']}"
    )

    print(
        f"   {t['location']}: {row['location']}"
    )

    print(
        f"   {t['skill_match']}: {skill_match:.1f}%"
    )

    print(
        f"   {t['local_bonus']}: +{local_bonus:.1f}%"
    )

    print(
        f"   {t['final_score']}: {score:.1f}%"
    )

    print(
        f"   {t['recommendation']}: "
        f"{get_recommendation(score, lang)}"
    )

    # --------------------------------------------------------
    # Matched skills
    # --------------------------------------------------------

    matched = row.get("matched_skills", "")

    if pd.notna(matched) and str(matched).strip():

        print(
            f"   {t['matched_skills']}:"
        )

        matches = str(matched).split(";")

        for item in matches:

            item = item.strip()

            if item:
                print(
                    f"      ✓ {item}"
                )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = row.get(
        "explanation",
        ""
    )

    if pd.notna(explanation) and str(explanation).strip():

        print(
            f"   {t['why']}:"
        )

        print(
            f"      {explanation}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load recommendations
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print(
            "\n❌ final_recommendations.csv not found."
        )

        print(
            "\nRun this first:"
        )

        print(
            "python scripts/15_recommendation_explanations.py"
        )

        return

    df = pd.read_csv(
        INPUT_FILE
    )

    if len(df) == 0:

        print(
            "\n❌ No recommendations available."
        )

        return

    # --------------------------------------------------------
    # Candidate information
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    candidate_name = input(
        "Candidate name: "
    ).strip()

    if not candidate_name:
        candidate_name = "Candidate"

    candidate_location = input(
        "Candidate location: "
    ).strip()

    if not candidate_location:
        candidate_location = "Not specified"

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    lang = choose_language()

    t = TEXT[lang]

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        f"              {t['title']}"
    )

    print(
        f"       {t['subtitle']}"
    )

    print("=" * 70)

    print(
        f"\n{t['candidate']}: "
        f"{candidate_name}"
    )

    print(
        f"{t['location']}: "
        f"{candidate_location}"
    )

    print(
        f"\n{t['top_jobs']}"
    )

    # --------------------------------------------------------
    # Display top 10
    # --------------------------------------------------------

    top_jobs = df.head(10)

    for number, (_, row) in enumerate(
        top_jobs.iterrows(),
        start=1
    ):

        display_job(
            row,
            number,
            lang,
            candidate_name,
            candidate_location
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        f"      {t['complete']}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()