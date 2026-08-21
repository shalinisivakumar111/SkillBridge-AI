import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_recommendations.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "multilingual_recommendations.csv"
)


# ============================================================
# TRANSLATION DICTIONARIES
# ============================================================

TRANSLATIONS = {

    "te": {
        "Recommended": "సిఫార్సు చేయబడింది",
        "Possible Match": "సాధ్యమైన సరిపోలిక",
        "Low Match": "తక్కువ సరిపోలిక",

        "Strong skill match": "నైపుణ్య సరిపోలిక బాగుంది",
        "Moderate skill match": "మధ్యస్థ నైపుణ్య సరిపోలిక",
        "Partial skill match": "పాక్షిక నైపుణ్య సరిపోలిక",

        "matches": "సరిపోలుతోంది",
        "Local opportunity": "స్థానిక ఉద్యోగ అవకాశం",
        "near the candidate's area": "అభ్యర్థి ప్రాంతానికి సమీపంలో ఉంది",
        "Overall recommendation score": "మొత్తం సిఫార్సు స్కోర్",

        "office administration": "ఆఫీస్ అడ్మినిస్ట్రేషన్",
        "customer service": "కస్టమర్ సర్వీస్",
        "excel": "Excel",
        "ms office": "MS Office",
        "data entry": "డేటా ఎంట్రీ",
        "communication": "కమ్యూనికేషన్",
        "sales": "సేల్స్",
        "problem solving": "సమస్య పరిష్కారం",
        "python": "Python",
        "sql": "SQL",
        "git": "Git",
        "digital marketing": "డిజిటల్ మార్కెటింగ్",
        "teaching": "బోధన",
        "accounting": "అకౌంటింగ్",
    },

    "hi": {
        "Recommended": "अनुशंसित",
        "Possible Match": "संभावित मिलान",
        "Low Match": "कम मिलान",

        "Strong skill match": "कौशल का अच्छा मिलान है",
        "Moderate skill match": "मध्यम कौशल मिलान है",
        "Partial skill match": "आंशिक कौशल मिलान है",

        "matches": "से मेल खाता है",
        "Local opportunity": "स्थानीय नौकरी का अवसर",
        "near the candidate's area": "उम्मीदवार के क्षेत्र के पास है",
        "Overall recommendation score": "कुल अनुशंसा स्कोर",

        "office administration": "ऑफिस एडमिनिस्ट्रेशन",
        "customer service": "कस्टमर सर्विस",
        "excel": "Excel",
        "ms office": "MS Office",
        "data entry": "डेटा एंट्री",
        "communication": "कम्युनिकेशन",
        "sales": "सेल्स",
        "problem solving": "समस्या समाधान",
        "python": "Python",
        "sql": "SQL",
        "git": "Git",
        "digital marketing": "डिजिटल मार्केटिंग",
        "teaching": "शिक्षण",
        "accounting": "अकाउंटिंग",
    },

    "ta": {
        "Recommended": "பரிந்துரைக்கப்படுகிறது",
        "Possible Match": "சாத்தியமான பொருத்தம்",
        "Low Match": "குறைந்த பொருத்தம்",

        "Strong skill match": "திறன் பொருத்தம் சிறப்பாக உள்ளது",
        "Moderate skill match": "மிதமான திறன் பொருத்தம் உள்ளது",
        "Partial skill match": "பகுதியளவு திறன் பொருத்தம் உள்ளது",

        "matches": "பொருந்துகிறது",
        "Local opportunity": "உள்ளூர் வேலை வாய்ப்பு",
        "near the candidate's area": "விண்ணப்பதாரரின் பகுதியின் அருகில் உள்ளது",
        "Overall recommendation score": "மொத்த பரிந்துரை மதிப்பெண்",

        "office administration": "அலுவலக நிர்வாகம்",
        "customer service": "வாடிக்கையாளர் சேவை",
        "excel": "Excel",
        "ms office": "MS Office",
        "data entry": "தரவு உள்ளீடு",
        "communication": "தொடர்பு",
        "sales": "விற்பனை",
        "problem solving": "சிக்கல் தீர்வு",
        "python": "Python",
        "sql": "SQL",
        "git": "Git",
        "digital marketing": "டிஜிட்டல் மார்க்கெட்டிங்",
        "teaching": "கற்பித்தல்",
        "accounting": "கணக்கியல்",
    }
}


# ============================================================
# TRANSLATION FUNCTION
# ============================================================

def translate_text(text, language):

    if pd.isna(text):
        return ""

    text = str(text)

    dictionary = TRANSLATIONS.get(language, {})

    # Long phrases first
    phrases = sorted(
        dictionary.keys(),
        key=len,
        reverse=True
    )

    for phrase in phrases:

        replacement = dictionary[phrase]

        pattern = re.compile(
            re.escape(phrase),
            re.IGNORECASE
        )

        text = pattern.sub(
            replacement,
            text
        )

    return text


# ============================================================
# GENERATE BETTER MULTILINGUAL EXPLANATION
# ============================================================

def create_explanation(row, language):

    recommendation = str(row.get("recommendation", ""))
    score = float(row.get("final_score", 0))

    matched = row.get("matched_skills", "")

    if pd.isna(matched):
        matched = ""

    matched = str(matched)

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    if language == "en":

        if score >= 50:
            strength = "Strong skill match."
        elif score >= 30:
            strength = "Moderate skill match."
        else:
            strength = "Partial skill match."

        if matched:
            skills = []

            for item in matched.split(";"):

                item = item.strip()

                if "→" in item:
                    candidate_skill, job_skill = item.split(
                        "→",
                        1
                    )

                    skills.append(
                        f"{candidate_skill.strip()} matches {job_skill.strip()}"
                    )

            skill_text = ". ".join(skills)

            if skill_text:
                strength += " " + skill_text + "."

        location = str(row.get("location", ""))

        if location:
            strength += (
                f" Local opportunity in or near the candidate's "
                f"area ({location})."
            )

        strength += (
            f" Overall recommendation score: {score:.1f}%."
        )

        return strength

    # --------------------------------------------------------
    # Telugu
    # --------------------------------------------------------

    if language == "te":

        if score >= 50:
            strength = "నైపుణ్య సరిపోలిక బాగుంది."
        elif score >= 30:
            strength = "మధ్యస్థ నైపుణ్య సరిపోలిక ఉంది."
        else:
            strength = "పాక్షిక నైపుణ్య సరిపోలిక ఉంది."

        if matched:

            skills = []

            for item in matched.split(";"):

                item = item.strip()

                if "→" in item:

                    candidate_skill, job_skill = item.split(
                        "→",
                        1
                    )

                    candidate_skill = translate_text(
                        candidate_skill.strip(),
                        "te"
                    )

                    job_skill = translate_text(
                        job_skill.strip(),
                        "te"
                    )

                    skills.append(
                        f"{candidate_skill} {job_skill}తో సరిపోలుతోంది"
                    )

            if skills:
                strength += " " + ". ".join(skills) + "."

        location = str(row.get("location", ""))

        if location:
            strength += (
                f" ఈ స్థానిక ఉద్యోగ అవకాశం "
                f"({location}) అభ్యర్థి ప్రాంతానికి సమీపంలో ఉంది."
            )

        strength += (
            f" మొత్తం సిఫార్సు స్కోర్: {score:.1f}%."
        )

        return strength

    # --------------------------------------------------------
    # Hindi
    # --------------------------------------------------------

    if language == "hi":

        if score >= 50:
            strength = "कौशल का अच्छा मिलान है।"
        elif score >= 30:
            strength = "मध्यम कौशल मिलान है।"
        else:
            strength = "आंशिक कौशल मिलान है।"

        if matched:

            skills = []

            for item in matched.split(";"):

                item = item.strip()

                if "→" in item:

                    candidate_skill, job_skill = item.split(
                        "→",
                        1
                    )

                    candidate_skill = translate_text(
                        candidate_skill.strip(),
                        "hi"
                    )

                    job_skill = translate_text(
                        job_skill.strip(),
                        "hi"
                    )

                    skills.append(
                        f"{candidate_skill} {job_skill} से मेल खाता है"
                    )

            if skills:
                strength += " " + ". ".join(skills) + "."

        location = str(row.get("location", ""))

        if location:
            strength += (
                f" यह स्थानीय नौकरी ({location}) "
                f"उम्मीदवार के क्षेत्र के पास है।"
            )

        strength += (
            f" कुल अनुशंसा स्कोर: {score:.1f}%."
        )

        return strength

    # --------------------------------------------------------
    # Tamil
    # --------------------------------------------------------

    if language == "ta":

        if score >= 50:
            strength = "திறன் பொருத்தம் சிறப்பாக உள்ளது."
        elif score >= 30:
            strength = "மிதமான திறன் பொருத்தம் உள்ளது."
        else:
            strength = "பகுதியளவு திறன் பொருத்தம் உள்ளது."

        if matched:

            skills = []

            for item in matched.split(";"):

                item = item.strip()

                if "→" in item:

                    candidate_skill, job_skill = item.split(
                        "→",
                        1
                    )

                    candidate_skill = translate_text(
                        candidate_skill.strip(),
                        "ta"
                    )

                    job_skill = translate_text(
                        job_skill.strip(),
                        "ta"
                    )

                    skills.append(
                        f"{candidate_skill} {job_skill} உடன் பொருந்துகிறது"
                    )

            if skills:
                strength += " " + ". ".join(skills) + "."

        location = str(row.get("location", ""))

        if location:
            strength += (
                f" இந்த உள்ளூர் வேலை வாய்ப்பு ({location}) "
                f"விண்ணப்பதாரரின் பகுதிக்கு அருகில் உள்ளது."
            )

        strength += (
            f" மொத்த பரிந்துரை மதிப்பெண்: {score:.1f}%."
        )

        return strength

    return ""


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       MULTILINGUAL EXPLANATION ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # Load recommendations
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print("\n❌ Input file not found:")
        print(INPUT_FILE)
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"\nRecommendations loaded: {len(df)}")

    # --------------------------------------------------------
    # Generate four language versions
    # --------------------------------------------------------

    print("\nGenerating multilingual explanations...")

    df["explanation_en"] = df.apply(
        lambda row: create_explanation(row, "en"),
        axis=1
    )

    df["explanation_te"] = df.apply(
        lambda row: create_explanation(row, "te"),
        axis=1
    )

    df["explanation_hi"] = df.apply(
        lambda row: create_explanation(row, "hi"),
        axis=1
    )

    df["explanation_ta"] = df.apply(
        lambda row: create_explanation(row, "ta"),
        axis=1
    )

    # --------------------------------------------------------
    # Save
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
    # Display
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("     MULTILINGUAL EXPLANATIONS COMPLETE")
    print("=" * 70)

    print(f"\nSaved to:")
    print(OUTPUT_FILE)

    print("\nLanguages:")
    print("  ✓ English")
    print("  ✓ Telugu")
    print("  ✓ Hindi")
    print("  ✓ Tamil")

    print("\nNew columns:")

    print("  ✓ explanation_en")
    print("  ✓ explanation_te")
    print("  ✓ explanation_hi")
    print("  ✓ explanation_ta")

    print("\nSample:")

    if len(df) > 0:

        row = df.iloc[0]

        print("\nEnglish:")
        print(row["explanation_en"])

        print("\nTelugu:")
        print(row["explanation_te"])

        print("\nHindi:")
        print(row["explanation_hi"])

        print("\nTamil:")
        print(row["explanation_ta"])

    print("\n" + "=" * 70)
    print("✅ MULTILINGUAL EXPLANATIONS READY")
    print("=" * 70)


if __name__ == "__main__":
    main()
