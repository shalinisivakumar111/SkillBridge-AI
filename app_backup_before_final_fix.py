from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
import re
import html

import pandas as pd
import requests
import streamlit as st

try:
    import folium
    from streamlit_folium import st_folium
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

try:
    from streamlit_geolocation import streamlit_geolocation
    GEOLOCATION_AVAILABLE = True
except ImportError:
    GEOLOCATION_AVAILABLE = False


# ============================================================
# SKILLBRIDGE AI
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
REAL_JOBS_FILE = BASE_DIR / "data" / "processed" / "enriched_real_jobs.csv"
FALLBACK_JOBS_FILE = BASE_DIR / "data" / "processed" / "real_jobs.csv"

st.set_page_config(page_title="SkillBridge AI", page_icon="💼", layout="wide")


LANGUAGES = {
    "English": {
        "title": "SKILLBRIDGE AI",
        "subtitle": "AI-Based Skill Matching for Real-World Employment",
        "candidate": "Candidate Information",
        "name": "Candidate Name",
        "location": "Candidate Location",
        "skills": "Candidate Skills",
        "resume": "Resume Upload",
        "upload": "Upload Resume",
        "gps": "Enable My Location",
        "find": "Find Nearby Jobs",
        "matches": "TOP REAL-WORLD JOB MATCHES",
        "company": "Company",
        "address": "Company / Job Location",
        "distance": "Distance",
        "skill_match": "Skill Match",
        "location_score": "Location Score",
        "final_score": "Final Score",
        "recommendation": "Recommendation",
        "matched": "Matched Skills",
        "why": "Why recommended",
        "recommended": "Recommended",
        "good": "Good Match",
        "possible": "Possible Match",
        "low": "Low Match",
    },
    "తెలుగు": {
        "title": "స్కిల్‌బ్రిడ్జ్ AI",
        "subtitle": "నిజమైన ఉద్యోగాల కోసం AI నైపుణ్య సరిపోలిక",
        "candidate": "అభ్యర్థి సమాచారం", "name": "అభ్యర్థి పేరు", "location": "అభ్యర్థి స్థానం",
        "skills": "అభ్యర్థి నైపుణ్యాలు", "resume": "రెజ్యూమ్ అప్‌లోడ్", "upload": "రెజ్యూమ్ అప్‌లోడ్ చేయండి",
        "gps": "నా స్థానాన్ని ప్రారంభించండి", "find": "సమీప ఉద్యోగాలను కనుగొనండి", "matches": "నిజమైన ఉద్యోగ సరిపోలికలు",
        "company": "కంపెనీ", "address": "కంపెనీ / ఉద్యోగ స్థానం", "distance": "దూరం", "skill_match": "నైపుణ్య సరిపోలిక",
        "location_score": "స్థాన స్కోర్", "final_score": "తుది స్కోర్", "recommendation": "సిఫార్సు",
        "matched": "సరిపోలిన నైపుణ్యాలు", "why": "ఎందుకు సిఫార్సు", "recommended": "సిఫార్సు చేయబడింది",
        "good": "మంచి సరిపోలిక", "possible": "సాధ్యమైన సరిపోలిక", "low": "తక్కువ సరిపోలిక",
    },
    "हिन्दी": {
        "title": "स्किलब्रिज AI", "subtitle": "वास्तविक नौकरियों के लिए AI कौशल मिलान", "candidate": "उम्मीदवार जानकारी",
        "name": "उम्मीदवार का नाम", "location": "उम्मीदवार का स्थान", "skills": "उम्मीदवार के कौशल",
        "resume": "रिज्यूमे अपलोड", "upload": "रिज्यूमे अपलोड करें", "gps": "मेरी लोकेशन शुरू करें",
        "find": "पास की नौकरियां खोजें", "matches": "वास्तविक नौकरी मिलान", "company": "कंपनी", "address": "कंपनी / नौकरी स्थान",
        "distance": "दूरी", "skill_match": "कौशल मिलान", "location_score": "स्थान स्कोर", "final_score": "अंतिम स्कोर",
        "recommendation": "अनुशंसा", "matched": "मिलान किए गए कौशल", "why": "क्यों अनुशंसित", "recommended": "अनुशंसित",
        "good": "अच्छा मिलान", "possible": "संभावित मिलान", "low": "कम मिलान",
    },
    "தமிழ்": {
        "title": "ஸ்கில்பிரிட்ஜ் AI", "subtitle": "உண்மையான வேலைகளுக்கான AI திறன் பொருத்தம்", "candidate": "விண்ணப்பதாரர் தகவல்",
        "name": "விண்ணப்பதாரர் பெயர்", "location": "விண்ணப்பதாரர் இருப்பிடம்", "skills": "விண்ணப்பதாரர் திறன்கள்",
        "resume": "ரெஸ்யூம் பதிவேற்றம்", "upload": "ரெஸ்யூமை பதிவேற்றவும்", "gps": "என் இருப்பிடத்தை இயக்கவும்",
        "find": "அருகிலுள்ள வேலைகளை தேடுங்கள்", "matches": "உண்மையான வேலை பொருத்தங்கள்", "company": "நிறுவனம்", "address": "நிறுவனம் / வேலை இடம்",
        "distance": "தூரம்", "skill_match": "திறன் பொருத்தம்", "location_score": "இருப்பிட மதிப்பெண்", "final_score": "இறுதி மதிப்பெண்",
        "recommendation": "பரிந்துரை", "matched": "பொருந்திய திறன்கள்", "why": "ஏன் பரிந்துரை", "recommended": "பரிந்துரைக்கப்படுகிறது",
        "good": "நல்ல பொருத்தம்", "possible": "சாத்தியமான பொருத்தம்", "low": "குறைந்த பொருத்தம்",
    },
}

RELATED_SKILLS = {
    "office administration": {"office administration", "ms office", "microsoft office", "excel", "data entry", "computer operations", "communication"},
    "customer service": {"customer service", "customer support", "communication", "sales", "problem solving"},
    "hindi": {"hindi", "communication", "customer service"},
    "tamil": {"tamil", "communication", "customer service"},
    "telugu": {"telugu", "communication", "customer service"},
    "communication": {"communication", "english communication", "customer service", "customer support", "sales"},
    "excel": {"excel", "ms excel", "ms office", "data entry", "accounting", "statistics"},
    "data entry": {"data entry", "excel", "ms excel", "ms office", "office administration"},
    "python": {"python", "django", "flask", "pandas", "numpy"},
    "javascript": {"javascript", "typescript", "react", "node.js", "node"},
    "web development": {"web development", "html", "css", "javascript", "frontend", "backend"},
}

COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "sql", "mysql", "postgresql",
    "excel", "ms office", "microsoft office", "word", "powerpoint", "data entry", "office administration",
    "customer service", "customer support", "communication", "sales", "marketing", "digital marketing",
    "accounting", "tally", "power bi", "tableau", "data analysis", "data analyst", "pandas", "numpy",
    "machine learning", "deep learning", "html", "css", "react", "node.js", "node", "django", "flask",
    "php", "laravel", "wordpress", "graphic design", "photoshop", "figma", "teaching", "teacher",
    "it support", "networking", "linux", "git", "aws", "azure", "telugu", "tamil", "hindi", "english",
}


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower().replace("-", " ").replace("_", " "))


def clean_value(value):
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def safe_float(value):
    try:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_location(query):
    """Convert a user-entered Indian location into GPS coordinates using OpenStreetMap Nominatim."""
    query = clean_value(query)
    if not query:
        return None

    headers = {
        "User-Agent": "SkillBridgeAI/1.0 local-employment-demo"
    }

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": f"{query}, India",
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "in",
            },
            headers=headers,
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            return None

        result = data[0]
        lat = safe_float(result.get("lat"))
        lon = safe_float(result.get("lon"))
        if lat is None or lon is None:
            return None

        return {
            "latitude": lat,
            "longitude": lon,
            "display_name": clean_value(result.get("display_name")),
        }
    except Exception:
        return None


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return straight-line GPS distance in kilometres."""
    R = 6371.0
    p1 = radians(float(lat1))
    p2 = radians(float(lat2))
    dp = radians(float(lat2) - float(lat1))
    dl = radians(float(lon2) - float(lon1))
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def location_score(distance):
    if distance <= 5:
        return 20.0
    if distance <= 15:
        return 15.0
    if distance <= 30:
        return 10.0
    if distance <= 50:
        return 5.0
    return 0.0


def distance_label(distance):
    if distance <= 5:
        return "Very Nearby"
    if distance <= 15:
        return "Nearby"
    if distance <= 30:
        return "Within Area"
    if distance <= 50:
        return "Far"
    return "Outside 50 km"


def calculate_skill_match(candidate_skills, job_skills):
    candidates = [normalize_text(x) for x in candidate_skills if clean_value(x)]
    jobs = [normalize_text(x) for x in job_skills if clean_value(x)]
    if not candidates or not jobs:
        return 0.0, []

    matches = []
    for candidate_skill in candidates:
        best = (0.0, None, None)
        for job_skill in jobs:
            if candidate_skill == job_skill:
                candidate = (1.0, job_skill, "exact")
            elif candidate_skill in RELATED_SKILLS and job_skill in RELATED_SKILLS[candidate_skill]:
                candidate = (0.65, job_skill, "related")
            else:
                candidate = (0.0, None, None)
            if candidate[0] > best[0]:
                best = candidate
        if best[1]:
            matches.append({"candidate_skill": candidate_skill, "job_skill": best[1], "score": best[0], "type": best[2]})

    if not matches:
        return 0.0, []
    score = sum(x["score"] for x in matches) / max(len(candidates), 1) * 100
    return min(round(score, 1), 100.0), matches


def recommendation_label(score):
    if score >= 70:
        return "Recommended"
    if score >= 50:
        return "Good Match"
    if score >= 30:
        return "Possible Match"
    return "Low Match"



def skill_key(value):
    return normalize_text(value)


def skill_is_related(candidate_skill, required_skill):
    candidate = skill_key(candidate_skill)
    required = skill_key(required_skill)
    if not candidate or not required:
        return False
    if candidate == required:
        return True

    if required in RELATED_SKILLS and candidate in RELATED_SKILLS[required]:
        return True
    if candidate in RELATED_SKILLS and required in RELATED_SKILLS[candidate]:
        return True

    groups = [
        {"excel", "ms excel", "ms office", "microsoft office"},
        {"python", "pandas", "numpy"},
        {"javascript", "typescript", "react", "node", "node.js"},
        {"web development", "html", "css", "javascript", "frontend", "backend"},
        {"customer service", "customer support", "communication"},
        {"data analysis", "data analyst", "statistics", "power bi", "tableau"},
        {"accounting", "tally", "excel", "ms office"},
        {"digital marketing", "marketing", "social media"},
        {"it support", "computer operations", "networking", "windows", "linux"},
    ]
    return any(candidate in group and required in group for group in groups)


def calculate_skill_gap(candidate_skills, required_skills):
    exact = []
    transferable = []
    missing = []
    seen = set()

    for required in required_skills:
        required_text = clean_value(required)
        required_key = skill_key(required_text)
        if not required_key or required_key in seen:
            continue
        seen.add(required_key)

        if any(skill_key(c) == required_key for c in candidate_skills):
            exact.append(required_text)
            continue

        related_source = next(
            (clean_value(c) for c in candidate_skills if skill_is_related(c, required_text)),
            None,
        )
        if related_source:
            transferable.append({
                "required_skill": required_text,
                "candidate_skill": related_source,
            })
        else:
            missing.append(required_text)

    return exact, transferable, missing


def aggregate_skill_gap_recommendations(results_df, candidate_skills, top_n=10):
    """Rank missing/partially covered skills by importance across top jobs."""
    if results_df is None or results_df.empty:
        return []

    candidate_keys = {skill_key(x) for x in candidate_skills if clean_value(x)}
    stats = {}

    for rank, (_, row) in enumerate(results_df.iterrows(), start=1):
        required = job_skills_from_row(row)
        _, transferable, missing = calculate_skill_gap(candidate_skills, required)

        rank_weight = max(0.35, 1.0 - ((rank - 1) / max(len(results_df), 1)) * 0.65)
        job_weight = max(0.25, float(row.get("final_score", 0) or 0) / 100.0)

        for skill in missing:
            key = skill_key(skill)
            if not key or key in candidate_keys:
                continue
            item = stats.setdefault(key, {
                "skill": skill,
                "missing_jobs": 0,
                "partial_jobs": 0,
                "weighted_occurrences": 0.0,
                "best_job_score": 0.0,
                "example_jobs": [],
            })
            item["missing_jobs"] += 1
            item["weighted_occurrences"] += rank_weight * (0.75 + 0.25 * job_weight)
            item["best_job_score"] = max(item["best_job_score"], float(row.get("final_score", 0) or 0))
            if len(item["example_jobs"]) < 3:
                item["example_jobs"].append(
                    f"{clean_value(row.get('job_title')) or 'Job'} at "
                    f"{clean_value(row.get('company')) or 'Company'}"
                )

        for item_transfer in transferable:
            skill = item_transfer["required_skill"]
            key = skill_key(skill)
            if not key or key in candidate_keys:
                continue
            item = stats.setdefault(key, {
                "skill": skill,
                "missing_jobs": 0,
                "partial_jobs": 0,
                "weighted_occurrences": 0.0,
                "best_job_score": 0.0,
                "example_jobs": [],
            })
            item["partial_jobs"] += 1
            item["weighted_occurrences"] += rank_weight * 0.45
            item["best_job_score"] = max(item["best_job_score"], float(row.get("final_score", 0) or 0))

    recommendations = []
    for item in stats.values():
        item["priority_score"] = round(
            item["missing_jobs"] * 12
            + item["partial_jobs"] * 5
            + item["weighted_occurrences"] * 8
            + item["best_job_score"] * 0.08,
            1,
        )

        if item["missing_jobs"] >= 2:
            item["priority"] = "High"
            item["reason"] = f"Missing from your profile and required by {item['missing_jobs']} displayed jobs."
        elif item["missing_jobs"] == 1:
            item["priority"] = "Medium"
            item["reason"] = "Missing from your profile and required by a displayed job."
        else:
            item["priority"] = "Foundation"
            item["reason"] = (
                f"Related to your current skills and useful for {item['partial_jobs']} displayed job(s)."
            )
        recommendations.append(item)

    recommendations.sort(
        key=lambda x: (x["priority_score"], x["missing_jobs"], x["best_job_score"]),
        reverse=True,
    )
    return recommendations[:top_n]


def render_skill_gap_section(results_df, candidate_skills):
    st.markdown("## 🎯 Skill Gap Analysis")
    st.caption(
        "SkillBridge compares your current skills with the requirements detected "
        "from your best real-world job matches."
    )

    recommendations = aggregate_skill_gap_recommendations(
        results_df, candidate_skills, top_n=10
    )

    if not recommendations:
        st.success(
            "🎉 No significant skill gaps were detected in the displayed jobs."
        )
        return

    high = sum(x["priority"] == "High" for x in recommendations)
    medium = sum(x["priority"] == "Medium" for x in recommendations)
    foundation = sum(x["priority"] == "Foundation" for x in recommendations)

    c1, c2, c3 = st.columns(3)
    c1.metric("High-priority gaps", high)
    c2.metric("Other missing skills", medium)
    c3.metric("Skills to strengthen", foundation)

    st.markdown("### 📚 Recommended Skills to Learn")
    st.caption(
        "Recommendations are based on skills detected in the real jobs currently shown, "
        "with higher priority given to gaps appearing in stronger matches."
    )

    for number, item in enumerate(recommendations, start=1):
        icon = {"High": "🔴", "Medium": "🟠", "Foundation": "🟢"}.get(
            item["priority"], "🔵"
        )
        with st.container(border=True):
            a, b = st.columns([3, 1])
            with a:
                st.markdown(f"### {number}. {item['skill'].title()}")
                st.write(item["reason"])
            with b:
                st.metric("Priority", f"{icon} {item['priority']}")
                st.metric("Gap score", f"{item['priority_score']:.1f}")

            if item["example_jobs"]:
                st.caption("Useful for: " + " • ".join(item["example_jobs"]))

    # Compact overall view.
    all_missing = []
    all_transferable = []
    for _, row in results_df.iterrows():
        required = job_skills_from_row(row)
        _, transferable, missing = calculate_skill_gap(candidate_skills, required)
        for skill in missing:
            if skill_key(skill) not in {skill_key(x) for x in all_missing}:
                all_missing.append(skill)
        for item in transferable:
            label = f"{item['required_skill']} ← {item['candidate_skill']}"
            if label not in all_transferable:
                all_transferable.append(label)

    st.markdown("### 🧩 Overall Gap Summary")
    if all_missing:
        st.warning("Missing: " + ", ".join(all_missing[:30]))
    if all_transferable:
        st.info("Transferable/partial: " + ", ".join(all_transferable[:20]))

def extract_resume_text(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if name.endswith(".docx"):
            from docx import Document
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs)
        if name.endswith((".txt", ".md", ".csv")):
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as exc:
        st.warning(f"Resume text extraction failed: {exc}")
    return ""


def extract_skills_from_resume(text, jobs_df):
    normalized = normalize_text(text)
    known = set(COMMON_SKILLS)
    if "skills" in jobs_df.columns:
        for value in jobs_df["skills"].dropna():
            for item in str(value).split(","):
                item = normalize_text(item)
                if item:
                    known.add(item)
    found = []
    for skill in sorted(known, key=len, reverse=True):
        if skill and skill in normalized and skill not in found:
            found.append(skill)
    return found


@st.cache_data
def _load_jobs():
    source = REAL_JOBS_FILE if REAL_JOBS_FILE.exists() else FALLBACK_JOBS_FILE
    if not source.exists():
        return pd.DataFrame()
    df = pd.read_csv(source)

    # Support both the real Adzuna dataset and the earlier demo dataset.
    aliases = {
        "job_id": ["job_id", "source_job_id"],
        "job_title": ["job_title", "title"],
        "company": ["company", "company_name"],
        "location": ["location", "location_display", "searched_location"],
        "address": ["company_address", "address", "location_display", "location"],
        "skills": ["skills", "category", "category_tag"],
        "latitude": ["latitude"],
        "longitude": ["longitude"],
        "redirect_url": ["redirect_url", "url"],
        "description": ["description"],
        "salary": ["salary"],
        "employment_type": ["employment_type", "contract_time", "contract_type"],
        "experience_years": ["experience_years"],
    }
    for target, choices in aliases.items():
        if target not in df.columns:
            for choice in choices:
                if choice in df.columns:
                    df[target] = df[choice]
                    break
            else:
                df[target] = ""
    return df



def infer_job_role(candidate_skills, explicit_role=""):
    """Infer a requested job role from explicit role text or obvious role skills."""
    explicit = normalize_text(explicit_role)
    if explicit:
        return explicit

    keys = {normalize_text(x) for x in candidate_skills if clean_value(x)}
    # Strong role indicators. Qualifications such as MBBS/MD are intentionally
    # treated as Doctor/Physician so entering skills alone still searches the
    # correct profession instead of unrelated nearby jobs.
    if keys & {
        "doctor", "physician", "mbbs", "md", "medical doctor",
        "medical officer", "general medicine", "general physician",
        "patient assessment", "diagnosis", "emergency care", "acls", "bls"
    }:
        return "doctor"
    if keys & {"nurse", "nursing", "staff nurse", "registered nurse", "gnm", "bsc nursing"}:
        return "nurse"
    if keys & {"teacher", "teaching", "educator", "lecturer", "faculty"}:
        return "teacher"
    if keys & {"accountant", "accounting", "accounts"}:
        return "accountant"
    if keys & {"developer", "programmer", "software developer", "software engineer"}:
        return "developer"
    return ""

def role_search_score(search_text, row):
    """Return a role relevance score based primarily on the JOB TITLE.

    The previous version searched the entire description, which caused a
    Doctor search to pick unrelated jobs such as sales/telecaller roles that
    merely mentioned doctors in their description.  A job title is the
    authoritative signal for the requested role; description/skills are only
    used as a limited fallback for neutral titles.
    """
    query = normalize_text(search_text)
    if not query:
        return 0.0

    title = normalize_text(row.get("job_title", ""))
    category = normalize_text(row.get("category", ""))
    category_tag = normalize_text(row.get("category_tag", ""))
    skills = normalize_text(row.get("skills", ""))

    synonyms = {
        "doctor": {
            "doctor", "physician", "medical doctor", "mbbs", "medical officer",
            "general physician", "resident doctor", "medical consultant",
            "ophthalmologist", "cardiologist", "dermatologist", "gynaecologist",
            "gynecologist", "pediatrician", "paediatrician", "surgeon",
            "psychiatrist", "radiologist", "pathologist", "anaesthetist",
            "anesthetist", "intensivist"
        },
        "physician": {
            "doctor", "physician", "medical doctor", "mbbs", "medical officer",
            "general physician", "resident doctor", "medical consultant",
            "ophthalmologist", "cardiologist", "dermatologist", "gynaecologist",
            "gynecologist", "pediatrician", "paediatrician", "surgeon",
            "psychiatrist", "radiologist", "pathologist", "anaesthetist",
            "anesthetist", "intensivist"
        },
        "nurse": {"nurse", "nursing", "staff nurse", "registered nurse", "gnm", "bsc nursing"},
        "dentist": {"dentist", "dental", "dental surgeon", "bds"},
        "pharmacist": {"pharmacist", "pharmacy", "pharmaceutical", "d pharma", "b pharma"},
        "teacher": {"teacher", "teaching", "educator", "school teacher", "faculty", "lecturer"},
        "accountant": {"accountant", "accounting", "accounts"},
        "developer": {"developer", "software developer", "programmer", "software engineer"},
    }

    terms = synonyms.get(query, {query})

    # Strong role/title match.  Do not use company name or description here.
    if any(term in title for term in terms):
        return 100.0

    # Reject obvious competing roles even if the description mentions the
    # requested profession (e.g. "Doctor Onboarding" is a sales job, not a
    # Doctor job).
    unrelated_role_terms = {
        "telecaller", "customer service", "relationship manager", "banker",
        "sales executive", "sales representative", "sales manager",
        "business development", "marketing executive", "content developer",
        "software developer", "programmer", "teacher", "nurse", "accountant",
        "recruiter", "hr executive", "data entry", "office assistant",
    }
    if any(term in title for term in unrelated_role_terms):
        return 0.0

    # Limited fallback: only a neutral/unclear title can inherit a role from
    # the job's category + skills.  Never use the free-form description,
    # because descriptions frequently mention other professions.
    combined = " ".join([category, category_tag, skills])
    if query in {"doctor", "physician"} and "healthcare" in combined:
        medical_skill_terms = {
            "mbbs", "md", "medical", "medicine", "clinical", "patient",
            "diagnosis", "emergency care", "healthcare", "medical coding"
        }
        if any(term in combined for term in medical_skill_terms):
            return 65.0

    if any(term in combined for term in terms):
        return 55.0

    q_tokens = [x for x in query.split() if len(x) > 2]
    if q_tokens:
        hits = sum(token in title for token in q_tokens)
        if hits:
            return min(90.0, 50.0 + 20.0 * hits / len(q_tokens))

    return 0.0


def role_matches(search_text, row):
    """Return True when a job is relevant to the requested role."""
    return role_search_score(search_text, row) > 0


def job_skills_from_row(row):
    text = " ".join(clean_value(row.get(c, "")) for c in ["skills", "category", "category_tag", "job_title", "description"])
    found = []
    normalized = normalize_text(text)
    for skill in sorted(COMMON_SKILLS, key=len, reverse=True):
        if skill in normalized and skill not in found:
            found.append(skill)
    for item in clean_value(row.get("skills", "")).split(","):
        item = normalize_text(item)
        if item and item not in found:
            found.append(item)
    return found


def render_map(candidate_lat, candidate_lon, jobs):
    """Render the results map using candidate origin and each job/company coordinate."""
    if not MAP_AVAILABLE:
        st.warning("Map packages are not installed. Run: pip install folium streamlit-folium")
        return

    m = folium.Map(
        location=[candidate_lat, candidate_lon],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    folium.Marker(
        [candidate_lat, candidate_lon],
        tooltip="Candidate location",
        popup="Candidate location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    bounds = [[candidate_lat, candidate_lon]]
    for _, row in jobs.iterrows():
        lat = safe_float(row.get("latitude"))
        lon = safe_float(row.get("longitude"))
        if lat is None or lon is None:
            continue

        title = html.escape(clean_value(row.get("job_title")) or "Job")
        company = html.escape(clean_value(row.get("company")) or "Company")
        location = html.escape(clean_value(row.get("address")) or clean_value(row.get("location")) or "")
        distance = safe_float(row.get("distance_km"))
        distance_text = f"{distance:.2f} km" if distance is not None else "Distance unavailable"
        popup = folium.Popup(
            f"<b>{title}</b><br>{company}<br>{location}<br>Distance: {distance_text}",
            max_width=380,
        )
        folium.Marker(
            [lat, lon],
            tooltip=f"{clean_value(row.get('job_title'))} • {distance_text}",
            popup=popup,
            icon=folium.Icon(color="red", icon="briefcase", prefix="fa"),
        ).add_to(m)
        bounds.append([lat, lon])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(25, 25))
    st_folium(m, width=None, height=560, returned_objects=[])


def render_company_picker(job_id, default_lat, default_lon, default_label, candidate_lat, candidate_lon):
    """Allow manual address, browser GPS, or Leaflet map-click selection for a company."""
    override = st.session_state.company_location_overrides.get(job_id, {})
    current_lat = safe_float(override.get("latitude")) if override else default_lat
    current_lon = safe_float(override.get("longitude")) if override else default_lon
    current_label = clean_value(override.get("label")) if override else default_label

    method = st.radio(
        "Company location method",
        ["🔎 Manual address", "📍 Browser GPS", "🗺️ Pick on OpenStreetMap"],
        horizontal=True,
        key=f"company_method_{job_id}",
    )

    if method.startswith("🔎"):
        address_input = st.text_input(
            "Exact company address / area / landmark",
            value=current_label if current_label and current_label != "Address unavailable" else "",
            placeholder="Example: 2nd Floor, ABC Towers, Gandhipuram, Coimbatore, Tamil Nadu",
            key=f"company_address_input_{job_id}",
        )
        st.caption("Use the real address when you know it. SkillBridge will geocode it with OpenStreetMap and will not invent missing floor/landmark details.")
        if st.button("🔎 FIND COMPANY LOCATION", key=f"company_find_{job_id}", use_container_width=True):
            if not address_input.strip():
                st.warning("Enter a company address, area, street, or landmark first.")
            else:
                with st.spinner("Finding company location on OpenStreetMap..."):
                    result = geocode_location(address_input.strip())
                if result:
                    st.session_state.company_location_overrides[job_id] = {
                        "latitude": result["latitude"],
                        "longitude": result["longitude"],
                        "label": result["display_name"] or address_input.strip(),
                        "source": "Manual OpenStreetMap geocoding",
                    }
                    st.rerun()
                else:
                    st.error("Company location not found. Include city and state/country for better results.")

    elif method.startswith("📍"):
        if not GEOLOCATION_AVAILABLE:
            st.error("GPS component is not installed. Run: pip install streamlit-geolocation")
        else:
            st.caption("Use this when you are physically at the company location and want your browser GPS to become the company pin.")
            gps = streamlit_geolocation()
            if isinstance(gps, dict):
                lat = safe_float(gps.get("latitude"))
                lon = safe_float(gps.get("longitude"))
                if lat is not None and lon is not None:
                    st.success(f"GPS detected: {lat:.6f}, {lon:.6f}")
                    if st.button("📍 USE THIS GPS AS COMPANY LOCATION", key=f"company_use_gps_{job_id}", use_container_width=True):
                        st.session_state.company_location_overrides[job_id] = {
                            "latitude": lat,
                            "longitude": lon,
                            "label": "Company location from browser GPS",
                            "source": "Browser GPS",
                        }
                        st.rerun()

    else:
        center_lat = current_lat if current_lat is not None else candidate_lat
        center_lon = current_lon if current_lon is not None else candidate_lon
        if center_lat is None or center_lon is None:
            center_lat, center_lon = 20.5937, 78.9629
        st.caption("Click the exact company point on the Leaflet/OpenStreetMap map.")
        picker = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles="OpenStreetMap", control_scale=True)
        folium.Marker([center_lat, center_lon], tooltip="Current company point").add_to(picker)
        map_result = st_folium(
            picker,
            width=None,
            height=420,
            returned_objects=["last_clicked"],
            key=f"company_map_{job_id}",
        )
        clicked = map_result.get("last_clicked") if isinstance(map_result, dict) else None
        if clicked and safe_float(clicked.get("lat")) is not None and safe_float(clicked.get("lng")) is not None:
            lat = safe_float(clicked.get("lat"))
            lon = safe_float(clicked.get("lng"))
            st.info(f"Selected company coordinates: {lat:.6f}, {lon:.6f}")
            if st.button("🗺️ USE SELECTED MAP POINT", key=f"company_use_map_{job_id}", use_container_width=True):
                st.session_state.company_location_overrides[job_id] = {
                    "latitude": lat,
                    "longitude": lon,
                    "label": "Company location selected on OpenStreetMap",
                    "source": "Leaflet/OpenStreetMap map pin",
                }
                st.rerun()

    active = st.session_state.company_location_overrides.get(job_id)
    if active:
        lat = safe_float(active.get("latitude"))
        lon = safe_float(active.get("longitude"))
        label = active.get("label") or "Custom company location"
        if lat is not None and lon is not None:
            d = haversine_distance(candidate_lat, candidate_lon, lat, lon)
            st.success(f"Active company location: {label}")
            st.write(f"Coordinates: `{lat:.6f}, {lon:.6f}`")
            st.metric("Candidate → Company distance", f"{d:.2f} km")
            if st.button("↩️ RESET TO SOURCE JOB LOCATION", key=f"company_reset_{job_id}"):
                st.session_state.company_location_overrides.pop(job_id, None)
                st.rerun()


# ============================================================
# SESSION STATE
# ============================================================
if "gps_location" not in st.session_state:
    st.session_state.gps_location = None
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "gps_enabled" not in st.session_state:
    st.session_state.gps_enabled = False
if "location_method" not in st.session_state:
    st.session_state.location_method = None
if "manual_location" not in st.session_state:
    st.session_state.manual_location = ""
if "manual_location_display" not in st.session_state:
    st.session_state.manual_location_display = ""
if "candidate_lat" not in st.session_state:
    st.session_state.candidate_lat = None
if "candidate_lon" not in st.session_state:
    st.session_state.candidate_lon = None
if "candidate_location_label" not in st.session_state:
    st.session_state.candidate_location_label = ""
if "company_location_overrides" not in st.session_state:
    st.session_state.company_location_overrides = {}
if "last_results" not in st.session_state:
    st.session_state.last_results = pd.DataFrame()
if "last_search_signature" not in st.session_state:
    st.session_state.last_search_signature = ""

language = st.sidebar.selectbox("Language / భాష / भाषा / மொழி", list(LANGUAGES.keys()))
T = LANGUAGES[language]

st.sidebar.markdown("### SkillBridge AI\n\n**Real-world jobs • GPS • Multilingual**\n\nAI-powered skill + location matching.")

st.title(f"💼 {T['title']}")
st.subheader(T["subtitle"])
st.caption("Real Adzuna jobs • Browser GPS • OpenStreetMap • Haversine distance")
st.divider()

jobs_df = _load_jobs()
if jobs_df.empty:
    st.error("No job dataset found. Expected data/processed/enriched_real_jobs.csv")
    st.stop()

# ============================================================
# CANDIDATE
# ============================================================
st.header(f"👤 {T['candidate']}")

col1, col2 = st.columns(2)
with col1:
    candidate_name = st.text_input(
        T["name"],
        value="",
        placeholder="Enter employee / candidate name",
    )

with col2:
    st.caption("You can use either GPS or manual location. Both calculate real distance.")
    st.info("📍 GPS = device location   |   🔎 Manual = any city, area, street or landmark")

st.markdown(f"### 📍 {T['location']}")

# Make the two location choices impossible to miss.
location_method_label = st.radio(
    "SELECT LOCATION METHOD",
    options=[
        "📍 GPS — Use my current location",
        "🔎 MANUAL — Enter any location",
        "🗺️ MAP — Pick exact point on OpenStreetMap",
    ],
    index=(0 if st.session_state.location_method in (None, "GPS") else 1 if st.session_state.location_method == "MANUAL" else 2),
    horizontal=False,
    key="location_method_selector",
    help="Choose GPS for the device's current location or Manual to search any Indian location.",
)

if location_method_label.startswith("📍"):
    selected_method = "GPS"
elif location_method_label.startswith("🔎"):
    selected_method = "MANUAL"
else:
    selected_method = "MAP"

# When switching methods, discard the previous origin.
if (
    st.session_state.location_method is not None
    and selected_method != st.session_state.location_method
):
    st.session_state.candidate_lat = None
    st.session_state.candidate_lon = None
    st.session_state.candidate_location_label = ""
    st.session_state.gps_location = None
    st.session_state.manual_location_display = ""
    st.session_state.last_results = pd.DataFrame()

st.session_state.location_method = selected_method

candidate_lat = None
candidate_lon = None
candidate_location_label = ""

# ------------------------------------------------------------
# GPS MODE
# ------------------------------------------------------------
if selected_method == "GPS":
    st.success("📍 GPS mode selected")

    if not GEOLOCATION_AVAILABLE:
        st.error(
            "GPS component is not installed. Run this in Terminal:\n\n"
            "pip install streamlit-geolocation"
        )
    else:
        st.caption(
            "Click the location button below and choose Allow when your browser asks for location permission."
        )

        gps_result = streamlit_geolocation()

        if isinstance(gps_result, dict):
            lat = safe_float(gps_result.get("latitude"))
            lon = safe_float(gps_result.get("longitude"))
            accuracy = safe_float(gps_result.get("accuracy"))

            if lat is not None and lon is not None:
                st.session_state.gps_location = {
                    "latitude": lat,
                    "longitude": lon,
                }
                st.session_state.gps_enabled = True

                st.success(f"📍 Current GPS detected: {lat:.6f}, {lon:.6f}")

                if accuracy is not None:
                    st.caption(
                        f"Browser-reported GPS accuracy: approximately {accuracy:.0f} metres"
                    )

                if st.button(
                    "📍 USE THIS GPS LOCATION",
                    type="primary",
                    use_container_width=True,
                    key="use_gps_location_button",
                ):
                    st.session_state.candidate_lat = lat
                    st.session_state.candidate_lon = lon
                    st.session_state.candidate_location_label = "Current GPS location"
                    st.rerun()
            else:
                st.info("Click the GPS/location button above to request your current location.")

    if st.session_state.get("candidate_lat") is not None:
        candidate_lat = st.session_state.candidate_lat
        candidate_lon = st.session_state.candidate_lon
        candidate_location_label = (
            st.session_state.candidate_location_label or "Current GPS location"
        )

# ------------------------------------------------------------
# MANUAL MODE
# ------------------------------------------------------------
elif selected_method == "MANUAL":
    st.success("🔎 Manual location mode selected")

    st.markdown("#### Enter any location")
    st.caption(
        "You are NOT limited to the 13 job-search cities. "
        "Enter a city, locality, area, street, neighbourhood or landmark."
    )

    manual_location = st.text_input(
        "📍 Location to search",
        value=st.session_state.manual_location,
        placeholder=(
            "Examples: Gandhipuram, Coimbatore | "
            "Kakkanad, Kochi | T Nagar, Chennai | "
            "Katpadi, Vellore | Anna Nagar, Madurai"
        ),
        key="manual_location_input",
    )
    st.session_state.manual_location = manual_location

    if st.button(
        "🔎 FIND & USE THIS MANUAL LOCATION",
        type="primary",
        use_container_width=True,
        key="find_manual_location_button",
    ):
        query = manual_location.strip()

        if not query:
            st.warning("Please enter a location first.")
        else:
            with st.spinner("Finding the exact searchable location on OpenStreetMap..."):
                result = geocode_location(query)

            if result:
                st.session_state.candidate_lat = result["latitude"]
                st.session_state.candidate_lon = result["longitude"]
                st.session_state.candidate_location_label = (
                    result["display_name"] or query
                )
                st.session_state.manual_location_display = (
                    result["display_name"] or query
                )
                st.success("✅ Manual location found.")
                st.rerun()
            else:
                st.error(
                    "❌ Location was not found. Try including the city and state, "
                    "for example: 'Gandhipuram, Coimbatore, Tamil Nadu'."
                )

    if (
        st.session_state.get("candidate_lat") is not None
        and st.session_state.location_method == "MANUAL"
    ):
        candidate_lat = st.session_state.candidate_lat
        candidate_lon = st.session_state.candidate_lon
        candidate_location_label = (
            st.session_state.candidate_location_label
            or st.session_state.manual_location_display
            or manual_location
        )

# ------------------------------------------------------------
# MAP MODE
# ------------------------------------------------------------
else:
    st.success("🗺️ OpenStreetMap map mode selected")
    if not MAP_AVAILABLE:
        st.error("Map packages are not installed. Run: pip install folium streamlit-folium")
        st.stop()
    st.caption("Click the exact candidate point on the Leaflet/OpenStreetMap map, then use that point as the candidate location.")
    center_lat = st.session_state.candidate_lat or 13.0827
    center_lon = st.session_state.candidate_lon or 80.2707
    candidate_picker = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    folium.Marker([center_lat, center_lon], tooltip="Current candidate point").add_to(candidate_picker)
    candidate_map_result = st_folium(
        candidate_picker,
        width=None,
        height=420,
        returned_objects=["last_clicked"],
        key="candidate_location_map_picker",
    )
    clicked = candidate_map_result.get("last_clicked") if isinstance(candidate_map_result, dict) else None
    if clicked and safe_float(clicked.get("lat")) is not None and safe_float(clicked.get("lng")) is not None:
        clicked_lat = safe_float(clicked.get("lat"))
        clicked_lon = safe_float(clicked.get("lng"))
        st.info(f"Selected candidate coordinates: {clicked_lat:.6f}, {clicked_lon:.6f}")
        if st.button("🗺️ USE SELECTED MAP POINT", type="primary", use_container_width=True, key="use_candidate_map_point"):
            st.session_state.candidate_lat = clicked_lat
            st.session_state.candidate_lon = clicked_lon
            st.session_state.candidate_location_label = "Candidate location selected on OpenStreetMap"
            st.rerun()

    if st.session_state.get("candidate_lat") is not None:
        candidate_lat = st.session_state.candidate_lat
        candidate_lon = st.session_state.candidate_lon
        candidate_location_label = st.session_state.candidate_location_label or "OpenStreetMap selected location"

# ------------------------------------------------------------
# ACTIVE LOCATION
# ------------------------------------------------------------
if candidate_lat is not None and candidate_lon is not None:
    mode_name = {
        "GPS": "GPS",
        "MANUAL": "Manual",
        "MAP": "OpenStreetMap Map",
    }.get(selected_method, selected_method)

    st.success(
        f"📍 Active location ({mode_name}): {candidate_location_label}"
    )
    st.write(
        f"Coordinates: `{candidate_lat:.6f}, {candidate_lon:.6f}`"
    )

    if selected_method == "MANUAL":
        st.caption(
            "These coordinates came from OpenStreetMap geocoding of the location you entered."
        )
else:
    st.warning(
        "⚠️ No active location yet. Choose GPS or Manual, then set your location."
    )

# ============================================================
# RESUME
# ============================================================
st.header(f"📄 {T['resume']}")
uploaded_resume = st.file_uploader(
    T["upload"],
    type=["pdf", "docx", "txt", "md", "csv"],
    help="Accepted: PDF, DOCX, TXT, MD and CSV. Scanned/image-only PDFs require OCR and may not contain extractable text.",
)

if uploaded_resume is not None:
    text = extract_resume_text(uploaded_resume)
    if text.strip():
        st.session_state.resume_text = text
        st.session_state.resume_skills = extract_skills_from_resume(text, jobs_df)
        st.success(f"Resume read successfully. Detected {len(st.session_state.resume_skills)} skills.")
        if st.session_state.resume_skills:
            st.write(", ".join(st.session_state.resume_skills))
    else:
        st.warning("The file was accepted, but no text could be extracted. You can enter skills manually or use an OCR-readable PDF.")

st.header("🎯 Job Role / Job Title")
job_role_query = st.text_input(
    "What job do you want?",
    value="",
    placeholder="Examples: Doctor, Nurse, Staff Nurse, Teacher, Accountant, Software Developer",
    help="Enter the job role separately from your skills. Example: Doctor + MBBS, communication.",
)

st.header(f"🧠 {T['skills']}")
candidate_skills_text = st.text_area(
    T["skills"],
    value="",
    placeholder="Example: MBBS, patient care, communication, medical terminology...",
)
manual_skills = [x.strip() for x in candidate_skills_text.split(",") if x.strip()]
all_candidate_skills = []
for skill in manual_skills + st.session_state.resume_skills:
    if normalize_text(skill) not in {normalize_text(x) for x in all_candidate_skills}:
        all_candidate_skills.append(skill)
if all_candidate_skills:
    st.info("Skills used for matching: " + ", ".join(all_candidate_skills))

# If the user changes the requested role or skills after a previous search,
# discard the old results. This prevents an old company-only list from
# remaining visible while the new role is being entered.
current_search_signature = "|".join([
    normalize_text(job_role_query),
    ",".join(sorted(normalize_text(x) for x in all_candidate_skills)),
])
if current_search_signature != st.session_state.last_search_signature:
    st.session_state.last_results = pd.DataFrame()

# ============================================================
# FIND JOBS
# ============================================================
st.divider()
find_jobs = st.button(f"🔎 {T['find']}", type="primary", use_container_width=True)

if find_jobs or not st.session_state.last_results.empty:
    if find_jobs:
        if candidate_lat is None or candidate_lon is None:
            st.error("Please set your location using GPS, Manual location, or Map location first.")
            st.stop()
        if not all_candidate_skills and not job_role_query.strip():
            st.error("Please enter a job role or provide candidate skills/resume.")
            st.stop()

        scored = []
        effective_role_query = infer_job_role(all_candidate_skills, job_role_query)
        role_requested = bool(effective_role_query)

        for _, job in jobs_df.iterrows():
            job_lat = safe_float(job.get("latitude"))
            job_lon = safe_float(job.get("longitude"))
            if job_lat is None or job_lon is None:
                continue

            job_id_for_override = clean_value(job.get("job_id"))
            override = st.session_state.company_location_overrides.get(job_id_for_override, {})
            override_lat = safe_float(override.get("latitude")) if override else None
            override_lon = safe_float(override.get("longitude")) if override else None
            active_job_lat = override_lat if override_lat is not None else job_lat
            active_job_lon = override_lon if override_lon is not None else job_lon

            distance = haversine_distance(candidate_lat, candidate_lon, active_job_lat, active_job_lon)
            if distance > 100:
                continue

            job_skills = job_skills_from_row(job)
            skill_match, skill_matches = calculate_skill_match(all_candidate_skills, job_skills)

            # Role/title matching is independent of candidate skills.
            # This is what makes searches such as "Doctor" return doctor jobs.
            role_match = role_search_score(effective_role_query, job) if role_requested else 0.0

            # When a clear profession is requested/detected, do not mix unrelated
            # jobs into the results merely because they are nearby. This is the
            # main fix for Doctor/MBBS returning Telecaller, Banking, etc.
            if role_requested and role_match <= 0:
                continue

            exact_gap_skills, transferable_gap_skills, missing_gap_skills = calculate_skill_gap(
                all_candidate_skills,
                job_skills,
            )
            loc_score = location_score(distance)

            if role_requested:
                # Role is the primary signal when the user explicitly requests
                # or the candidate skills clearly imply a profession.
                # 60% role relevance + 30% skills + 10% location.
                final_score = min(
                    role_match * 0.60 + skill_match * 0.30 + loc_score * 0.10,
                    100.0,
                )
            else:
                final_score = min(skill_match + loc_score, 100.0)

            scored.append({
                "job_id": job_id_for_override,
                "job_title": clean_value(job.get("job_title")) or "Untitled Job",
                "company": clean_value(job.get("company")) or "Company not provided",
                "location": clean_value(job.get("location")) or clean_value(job.get("location_display")),
                "address": (override.get("label") if override else "") or clean_value(job.get("address")) or clean_value(job.get("location_display")) or clean_value(job.get("location")),
                "latitude": active_job_lat,
                "longitude": active_job_lon,
                "distance_km": round(distance, 2),
                "distance_label": distance_label(distance),
                "role_match": round(role_match, 1),
                "skill_match": round(skill_match, 1),
                "location_score": round(loc_score, 1),
                "final_score": round(final_score, 1),
                "recommendation": recommendation_label(final_score),
                "skill_matches": skill_matches,
                "required_skills": job_skills,
                "covered_skills": exact_gap_skills,
                "transferable_skills": transferable_gap_skills,
                "missing_skills": missing_gap_skills,
                "salary": clean_value(job.get("salary")) or (f"₹{clean_value(job.get('salary_min'))} - ₹{clean_value(job.get('salary_max'))}" if clean_value(job.get("salary_min")) or clean_value(job.get("salary_max")) else ""),
                "employment_type": clean_value(job.get("employment_type")) or clean_value(job.get("contract_time")) or clean_value(job.get("contract_type")),
                "experience_years": clean_value(job.get("experience_years")),
                "description": clean_value(job.get("description")),
                "redirect_url": clean_value(job.get("redirect_url")),
                "location_status": clean_value(job.get("location_status")),
                "company_location_source": clean_value(override.get("source")) if override else "Source job coordinates",
            })

        if not scored:
            st.warning("No jobs with valid source coordinates were found within 100 km. Jobs without coordinates are not assigned a fake distance.")
            st.stop()

        results_df = pd.DataFrame(scored).sort_values(["final_score", "distance_km"], ascending=[False, True]).head(10).reset_index(drop=True)
        st.session_state.last_results = results_df.copy()
        st.session_state.last_search_signature = current_search_signature
    else:
        results_df = st.session_state.last_results.copy()
        for idx in results_df.index:
            jid = clean_value(results_df.at[idx, "job_id"])
            override = st.session_state.company_location_overrides.get(jid, {})
            lat = safe_float(override.get("latitude")) if override else safe_float(results_df.at[idx, "latitude"])
            lon = safe_float(override.get("longitude")) if override else safe_float(results_df.at[idx, "longitude"])
            if lat is not None and lon is not None:
                d = haversine_distance(candidate_lat, candidate_lon, lat, lon)
                results_df.at[idx, "latitude"] = lat
                results_df.at[idx, "longitude"] = lon
                results_df.at[idx, "distance_km"] = round(d, 2)
                results_df.at[idx, "distance_label"] = distance_label(d)
                results_df.at[idx, "location_score"] = round(location_score(d), 1)
                role_component = float(results_df.at[idx, "role_match"] if "role_match" in results_df.columns else 0 or 0)
                skill_component = float(results_df.at[idx, "skill_match"] if "skill_match" in results_df.columns else 0 or 0)
                if effective_role_query:
                    refreshed_score = role_component * 0.60 + skill_component * 0.30 + location_score(d) * 0.10
                else:
                    refreshed_score = skill_component + location_score(d)
                results_df.at[idx, "final_score"] = round(min(refreshed_score, 100.0), 1)
                results_df.at[idx, "recommendation"] = recommendation_label(float(results_df.at[idx, "final_score"]))
                results_df.at[idx, "company_location_source"] = clean_value(override.get("source")) if override else "Source job coordinates"
                if override and clean_value(override.get("label")):
                    results_df.at[idx, "address"] = clean_value(override.get("label"))
        results_df = results_df.sort_values(["final_score", "distance_km"], ascending=[False, True]).reset_index(drop=True)
        st.session_state.last_results = results_df.copy()
    st.divider()
    st.header(f"📍 {T['matches']}")
    st.write(f"**{T['name']}:** {candidate_name or 'Candidate'}")
    origin_name = {
        "GPS": "GPS",
        "MANUAL": "Manual",
        "MAP": "OpenStreetMap Map",
    }.get(st.session_state.location_method, "Selected")
    st.write(f"**Location origin ({origin_name}):** {candidate_location_label}")
    st.write(f"**Coordinates:** {candidate_lat:.6f}, {candidate_lon:.6f}")
    effective_role_query = infer_job_role(all_candidate_skills, job_role_query)
    if effective_role_query:
        st.write(f"**Job role used for matching:** {effective_role_query.title()}")
    st.write(f"**Skills:** {', '.join(all_candidate_skills) if all_candidate_skills else 'Not provided'}")
    st.caption(
        f"Showing {len(results_df)} best jobs. Distances are calculated from the selected "
        f"{origin_name} location to each job's active company coordinates."
    )

    # ============================================================
    # 1) DETAILED JOB LISTINGS — FIRST
    # ============================================================
    # ============================================================
    # 5) DETAILED JOB LISTS
    # ============================================================
    st.markdown("## 📋 Detailed Job Listings")
    st.caption("Full job details, company location controls, matched skills, skill gaps and application links.")

    # Company location controls are part of the Detailed Job Listings section.
    st.markdown("### 🏢 Company Location — Manual / GPS / Map")
    st.caption("Choose a job above to verify or correct its company location. Manual address, browser GPS, and OpenStreetMap are supported.")
    company_options = [f"#{i + 1} — {r['job_title']} — {r['company']}" for i, (_, r) in enumerate(results_df.iterrows())]
    selected_company_index = st.selectbox(
        "Select a company/job to view or edit its location",
        range(len(company_options)),
        format_func=lambda i: company_options[i],
        key="company_location_job_selector",
    )
    selected_company_row = results_df.iloc[selected_company_index]
    selected_job_id = clean_value(selected_company_row["job_id"])
    render_company_picker(
        selected_job_id,
        safe_float(selected_company_row["latitude"]),
        safe_float(selected_company_row["longitude"]),
        clean_value(selected_company_row["address"]) or "Address unavailable",
        candidate_lat,
        candidate_lon,
    )

    # The all-matching-jobs map is intentionally placed immediately below
    # the company-location controls, exactly as requested.
    st.markdown("## 🗺️ OpenStreetMap / Leaflet — All Matching Jobs")
    st.caption("Candidate location and all matching company/job locations. The selected company location above is used for distance when an override is active.")
    render_map(candidate_lat, candidate_lon, results_df)

    output_file = BASE_DIR / "data" / "processed" / "streamlit_real_job_recommendations.csv"
    results_df.to_csv(output_file, index=False)

    for number, (_, row) in enumerate(results_df.iterrows(), start=1):
        with st.container(border=True):
            st.markdown(f"## #{number} {row['job_title']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(T["skill_match"], f"{row['skill_match']:.1f}%")
            with c2:
                st.metric(T["distance"], f"{row['distance_km']:.2f} km")
            with c3:
                st.metric(T["location_score"], f"+{row['location_score']:.1f}")
            with c4:
                st.metric(T["final_score"], f"{row['final_score']:.1f}%")

            st.markdown(f"### 💼 Job Title")
            st.write(row["job_title"])

            if effective_role_query:
                st.metric("Job Role Match", f"{row.get('role_match', 0):.1f}%")

            st.markdown(f"### 🏢 {T['company']}")
            st.write(row["company"])

            st.markdown(f"### 📍 {T['address']}")
            st.write(row["address"])
            st.caption(f"{row['distance_km']:.2f} km away • {row['distance_label']}")

            if row["location_status"]:
                st.caption(f"Location data: {row['location_status']}")
            st.caption(f"Company location used for distance: {row['company_location_source']}")

            st.markdown(f"### ⭐ {T['recommendation']}")
            if row["recommendation"] == "Recommended":
                st.success(T["recommended"])
            elif row["recommendation"] == "Good Match":
                st.info(T["good"])
            elif row["recommendation"] == "Possible Match":
                st.warning(T["possible"])
            else:
                st.error(T["low"])

            st.markdown(f"### 🧠 {T['matched']}")
            if row["skill_matches"]:
                for match in row["skill_matches"]:
                    icon = "🟢" if match["type"] == "exact" else "🔵"
                    st.write(f"{icon} {match['candidate_skill']} → {match['job_skill']} ({match['type']})")
            else:
                st.write("No direct skill match.")

            st.markdown("### 🎯 Skill Gap for This Job")
            job_missing = row.get("missing_skills", [])
            job_transferable = row.get("transferable_skills", [])

            if isinstance(job_missing, str):
                job_missing = [x.strip() for x in job_missing.split("|") if x.strip()]
            if not isinstance(job_missing, list):
                job_missing = []

            if isinstance(job_transferable, str):
                job_transferable = []
            if not isinstance(job_transferable, list):
                job_transferable = []

            if job_missing:
                st.error("Missing skills: " + ", ".join(str(x) for x in job_missing))
                st.write(
                    "💡 Recommended to learn: "
                    + ", ".join(str(x) for x in job_missing[:8])
                )
            else:
                st.success("No major missing skills detected for this job.")

            if job_transferable:
                transferable_text = ", ".join(
                    f"{item.get('required_skill')} "
                    f"(your {item.get('candidate_skill')} is related)"
                    for item in job_transferable
                    if isinstance(item, dict)
                )
                if transferable_text:
                    st.info("🟡 Transferable skills: " + transferable_text)

            st.markdown(f"### 💡 {T['why']}")
            strength = "Very strong skill match" if row["skill_match"] >= 70 else "Strong skill match" if row["skill_match"] >= 50 else "Partial skill match"
            st.info(f"{strength}. This job is {row['distance_km']:.2f} km away. Overall recommendation score: {row['final_score']:.1f}%.")

            e1, e2, e3 = st.columns(3)
            with e1:
                if row["salary"]:
                    st.write(f"💰 {row['salary']}")
            with e2:
                if row["employment_type"]:
                    st.write(f"💼 {row['employment_type']}")
            with e3:
                if row["experience_years"]:
                    st.write(f"🎓 {row['experience_years']}")

            with st.expander("📄 Job Description / Job Details", expanded=True):
                if row["description"]:
                    st.write(row["description"])
                else:
                    st.warning(
                        "The source dataset does not contain a job description for this listing. "
                        "Use 'View Original Job' below for the complete source details."
                    )

            if row["redirect_url"]:
                st.link_button("🔗 View Original Job", row["redirect_url"])

            st.caption("Address and coordinates are displayed from the real job-source data. SkillBridge does not invent missing floor, landmark, street or building details.")


    # ============================================================
    # 2) SKILL GAP ANALYSIS — SECOND
    # ============================================================
    st.markdown("## 🎯 Skill Gap Analysis")
    st.caption("SkillBridge compares your current skills with the requirements detected from the real jobs shown above and recommends useful skills to learn next.")
    render_skill_gap_section(results_df, all_candidate_skills)

    # ============================================================
    # 3) TOP JOB LIST — THIRD
    # ============================================================
    st.markdown("## 💼 Top Job List")
    st.caption("Your best real-world job matches are summarized here after the detailed listings and skill-gap analysis.")

    quick_rows = []
    for number, (_, row) in enumerate(results_df.iterrows(), start=1):
        quick_rows.append({
            "Rank": number,
            "Job": row["job_title"],
            "Company": row["company"],
            "Location": row["location"],
            "Role Match": f"{row.get('role_match', 0):.1f}%",
            "Distance": f"{row['distance_km']:.2f} km",
            "Skill Match": f"{row['skill_match']:.1f}%",
            "Final Score": f"{row['final_score']:.1f}%",
        })
    st.dataframe(
        pd.DataFrame(quick_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("#", width="small"),
            "Job": st.column_config.TextColumn("Job", width="large"),
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Location": st.column_config.TextColumn("Location", width="medium"),
            "Role Match": st.column_config.TextColumn("Role Match", width="small"),
            "Distance": st.column_config.TextColumn("Distance", width="small"),
            "Skill Match": st.column_config.TextColumn("Skill Match", width="small"),
            "Final Score": st.column_config.TextColumn("Final Score", width="small"),
        },
    )


st.divider()
st.caption("SkillBridge AI • Real-world jobs • GPS • OpenStreetMap • Haversine distance")
