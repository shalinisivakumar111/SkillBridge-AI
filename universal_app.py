from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
import re
import html

import pandas as pd
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
APP_ROOT = Path(__file__).resolve().parent
REAL_JOBS_FILE = APP_ROOT / "data" / "processed" / "enriched_real_jobs.csv"
FALLBACK_JOBS_FILE = APP_ROOT / "data" / "processed" / "real_jobs.csv"

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


def skill_is_covered(candidate_skills, required_skill):
    """Return True when a candidate skill exactly or meaningfully covers a job skill."""
    required = normalize_text(required_skill)
    if not required:
        return False

    for candidate in candidate_skills:
        c = normalize_text(candidate)
        if not c:
            continue
        if c == required:
            return True
        if required in RELATED_SKILLS.get(c, set()):
            return True
        if c in RELATED_SKILLS.get(required, set()):
            return True
    return False


def get_skill_gaps(candidate_skills, job_skills):
    """Return required job skills not covered by the candidate."""
    gaps = []
    seen = set()
    for skill in job_skills:
        cleaned = clean_value(skill)
        normalized = normalize_text(cleaned)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        if not skill_is_covered(candidate_skills, cleaned):
            gaps.append(cleaned)
    return gaps


SKILL_LEARNING_GUIDE = {
    "python": "Build a small Python project and practice functions, files, APIs and data handling.",
    "sql": "Practice SELECT, JOIN, GROUP BY and real-world database queries.",
    "excel": "Practice formulas, lookup functions, pivot tables and basic dashboards.",
    "communication": "Practice professional communication, presentations and workplace conversations.",
    "customer service": "Practice customer handling, issue resolution and professional communication.",
    "data analysis": "Learn data cleaning, exploratory analysis and simple visualizations.",
    "machine learning": "Start with supervised learning, model evaluation and a small end-to-end project.",
    "deep learning": "Learn neural networks, training workflows and one practical computer-vision or NLP project.",
    "javascript": "Practice DOM, asynchronous JavaScript and a small interactive web application.",
    "react": "Build a small React application using components, state and API calls.",
    "html": "Practice semantic HTML and build accessible multi-section pages.",
    "css": "Practice responsive layouts, Flexbox, Grid and mobile-first design.",
    "git": "Practice branching, commits, pull requests and resolving merge conflicts.",
    "tally": "Practice ledgers, vouchers, GST workflows and basic accounting reports.",
    "accounting": "Practice journal entries, reconciliation, financial statements and bookkeeping workflows.",
    "marketing": "Learn campaign planning, audience targeting, content strategy and basic analytics.",
    "digital marketing": "Practice SEO, social campaigns, analytics and conversion tracking.",
    "sales": "Practice lead qualification, product pitching, objection handling and CRM workflows.",
    "teaching": "Practice lesson planning, assessment design and learner-centred teaching methods.",
    "patient assessment": "Strengthen structured assessment, documentation and clinical reasoning through supervised practice.",
    "diagnosis": "Strengthen differential diagnosis and evidence-based clinical reasoning through supervised practice.",
    "clinical documentation": "Practice accurate, structured clinical notes and documentation standards.",
    "emergency care": "Refresh emergency assessment, triage and protocol-based response through certified training.",
    "bls": "Refresh Basic Life Support through an appropriate certified course.",
    "acls": "Refresh Advanced Cardiovascular Life Support through an appropriate certified course.",
}


def skill_learning_tip(skill):
    key = normalize_text(skill)
    return SKILL_LEARNING_GUIDE.get(
        key,
        f"Learn {skill} through a short practical course, then build or complete one small project/task using it."
    )


def build_skill_recommendations(candidate_skills, results_df, max_items=6):
    """Aggregate missing skills across the strongest displayed jobs."""
    if results_df is None or results_df.empty:
        return []

    candidate_set = {normalize_text(x) for x in candidate_skills if clean_value(x)}
    counts = {}
    weighted = {}
    examples = {}

    for _, row in results_df.iterrows():
        gaps = row.get("skill_gaps", []) or []
        # Stronger jobs contribute more to the recommendation priority.
        weight = max(float(row.get("final_score", 0.0)) / 100.0, 0.1)
        for gap in gaps:
            skill = clean_value(gap)
            key = normalize_text(skill)
            if not key or key in candidate_set:
                continue
            counts[key] = counts.get(key, 0) + 1
            weighted[key] = weighted.get(key, 0.0) + weight
            examples.setdefault(key, row.get("job_title", "a matched job"))

    if not counts:
        return []

    total_jobs = len(results_df)
    ranked = sorted(
        counts.keys(),
        key=lambda k: (weighted.get(k, 0.0), counts.get(k, 0)),
        reverse=True,
    )

    recommendations = []
    for key in ranked[:max_items]:
        count = counts[key]
        coverage = count / max(total_jobs, 1) * 100.0
        if coverage >= 60:
            priority = "High"
        elif coverage >= 30:
            priority = "Medium"
        else:
            priority = "Useful"

        display_skill = key
        for _, row in results_df.iterrows():
            for gap in row.get("skill_gaps", []) or []:
                if normalize_text(gap) == key:
                    display_skill = clean_value(gap)
                    break
            if display_skill != key:
                break

        recommendations.append({
            "skill": display_skill,
            "priority": priority,
            "jobs": count,
            "coverage": round(coverage, 1),
            "example_job": examples.get(key, "matched jobs"),
            "tip": skill_learning_tip(display_skill),
        })

    return recommendations


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
    if not MAP_AVAILABLE:
        st.warning("Map packages are not installed. Run: pip install folium streamlit-folium")
        return

    m = folium.Map(location=[candidate_lat, candidate_lon], zoom_start=13, tiles="OpenStreetMap", control_scale=True)
    folium.Marker(
        [candidate_lat, candidate_lon],
        tooltip="Your current location",
        popup="Candidate GPS location",
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
        location = html.escape(clean_value(row.get("location")) or "")
        distance = safe_float(row.get("distance_km"))
        distance_text = f"{distance:.2f} km" if distance is not None else "Distance unavailable"
        popup = folium.Popup(f"<b>{title}</b><br>{company}<br>{location}<br>Distance: {distance_text}", max_width=350)
        folium.Marker([lat, lon], tooltip=f"{clean_value(row.get('job_title'))} • {distance_text}", popup=popup, icon=folium.Icon(color="red", icon="briefcase", prefix="fa")).add_to(m)
        bounds.append([lat, lon])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(25, 25))
    st_folium(m, width=None, height=560, returned_objects=[])


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
if "candidate_location_source" not in st.session_state:
    st.session_state.candidate_location_source = "Manual Coordinates"
if "job_location_overrides" not in st.session_state:
    st.session_state.job_location_overrides = {}

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
    candidate_name = st.text_input(T["name"], value="")
with col2:
    location_search = st.text_input("🔎 Search any location", placeholder="T Nagar, Chennai / Kakkanad, Kochi / Gandhipuram, Coimbatore...")

st.markdown(f"### 📍 {T['location']}")

location_source = st.radio(
    "Location source",
    ["Manual Coordinates", "Browser GPS"],
    horizontal=True,
    key="candidate_location_source",
    help="Choose manual coordinates or allow the browser to provide your current GPS location.",
)

candidate_lat = None
candidate_lon = None
candidate_location_label = ""
candidate_location_text = ""

if location_source == "Manual Coordinates":
    m1, m2 = st.columns(2)
    with m1:
        manual_candidate_lat = st.number_input(
            "Candidate Latitude",
            value=12.9165,
            min_value=-90.0,
            max_value=90.0,
            format="%.6f",
            key="manual_candidate_lat",
        )
    with m2:
        manual_candidate_lon = st.number_input(
            "Candidate Longitude",
            value=79.1325,
            min_value=-180.0,
            max_value=180.0,
            format="%.6f",
            key="manual_candidate_lon",
        )
    candidate_location_text = st.text_input(
        "Candidate Address / Area (optional)",
        value=st.session_state.get("manual_candidate_address", ""),
        placeholder="Example: Vellore, Tamil Nadu",
        key="manual_candidate_address",
    )
    candidate_lat = float(manual_candidate_lat)
    candidate_lon = float(manual_candidate_lon)
    candidate_location_label = candidate_location_text.strip() or "Manual coordinates"
    st.success(f"📍 Manual candidate location: {candidate_lat:.6f}, {candidate_lon:.6f}")

else:
    if not GEOLOCATION_AVAILABLE:
        st.error("streamlit-geolocation is not installed. Run: pip install streamlit-geolocation")
    else:
        st.caption("Click the location control below and allow browser location permission.")
        gps_result = streamlit_geolocation()
        if gps_result:
            lat = safe_float(gps_result.get("latitude"))
            lon = safe_float(gps_result.get("longitude"))
            if lat is not None and lon is not None:
                st.session_state.gps_location = {"latitude": lat, "longitude": lon}
                st.session_state.gps_enabled = True

        if st.session_state.gps_location:
            candidate_lat = st.session_state.gps_location["latitude"]
            candidate_lon = st.session_state.gps_location["longitude"]
            candidate_location_label = "Browser GPS"
            st.success(f"📍 Browser GPS: {candidate_lat:.6f}, {candidate_lon:.6f}")
        else:
            st.info("Allow browser location permission, or switch to Manual Coordinates.")

# Keep the location text search as a helper for filtering the real job source.
if location_search.strip():
    q = normalize_text(location_search)
    searchable = jobs_df.copy()
    searchable["_search"] = searchable.apply(
        lambda r: normalize_text(" ".join(clean_value(r.get(c, "")) for c in ["location", "location_area", "searched_location", "location_display", "company_address"])),
        axis=1,
    )
    hits = searchable[searchable["_search"].str.contains(re.escape(q), na=False)]
    if not hits.empty:
        st.info(f"Location search found {len(hits)} matching real job records.")
    else:
        st.info("No exact text match in the current job source. Distance will still use the selected candidate coordinates.")

# ============================================================
# JOB LOCATION MANAGEMENT
# ============================================================
st.markdown("### 🏢📍 Job Location")
st.caption("Real job coordinates are used by default. If a job has missing/wrong coordinates, you can manually enter an address and GPS coordinates for that specific job.")

job_options = []
for idx, row in jobs_df.iterrows():
    title = clean_value(row.get("job_title")) or "Untitled Job"
    company = clean_value(row.get("company")) or "Company not provided"
    job_options.append((idx, f"{title} — {company}"))

if job_options:
    selected_job_idx = st.selectbox(
        "Select job to add/edit manual location",
        options=[x[0] for x in job_options],
        format_func=lambda x: next(label for idx, label in job_options if idx == x),
        key="selected_job_location_index",
    )
    selected_row = jobs_df.loc[selected_job_idx]
    selected_key = str(clean_value(selected_row.get("job_id")) or selected_job_idx)
    existing_override = st.session_state.job_location_overrides.get(selected_key, {})

    j1, j2 = st.columns(2)
    with j1:
        job_manual_lat = st.number_input(
            "Job Latitude",
            value=float(existing_override.get("latitude", safe_float(selected_row.get("latitude")) or 12.9165)),
            min_value=-90.0, max_value=90.0, format="%.6f", key=f"job_lat_{selected_key}",
        )
    with j2:
        job_manual_lon = st.number_input(
            "Job Longitude",
            value=float(existing_override.get("longitude", safe_float(selected_row.get("longitude")) or 79.1325)),
            min_value=-180.0, max_value=180.0, format="%.6f", key=f"job_lon_{selected_key}",
        )
    job_manual_address = st.text_input(
        "Job Address / Area",
        value=existing_override.get("address", clean_value(selected_row.get("address")) or clean_value(selected_row.get("location"))),
        placeholder="Example: Katpadi, Vellore, Tamil Nadu",
        key=f"job_address_{selected_key}",
    )
    jb1, jb2 = st.columns(2)
    with jb1:
        if st.button("💾 Save Job Location", use_container_width=True, key=f"save_job_location_{selected_key}"):
            st.session_state.job_location_overrides[selected_key] = {
                "latitude": float(job_manual_lat),
                "longitude": float(job_manual_lon),
                "address": job_manual_address.strip(),
            }
            st.success("Job location saved for this session. Matching will use these coordinates.")
    with jb2:
        if st.button("↩️ Use Dataset Location", use_container_width=True, key=f"reset_job_location_{selected_key}"):
            st.session_state.job_location_overrides.pop(selected_key, None)
            st.success("Dataset job coordinates restored.")

if candidate_lat is not None and candidate_lon is not None:
    st.success(f"📍 Active candidate location: {candidate_location_label} — {candidate_lat:.6f}, {candidate_lon:.6f}")

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

st.header(f"🧠 {T['skills']}")
candidate_skills_text = st.text_area(T["skills"], value="", placeholder="Python, Excel, MS Office, Customer Service...")
manual_skills = [x.strip() for x in candidate_skills_text.split(",") if x.strip()]
all_candidate_skills = []
for skill in manual_skills + st.session_state.resume_skills:
    if normalize_text(skill) not in {normalize_text(x) for x in all_candidate_skills}:
        all_candidate_skills.append(skill)
if all_candidate_skills:
    st.info("Skills used for matching: " + ", ".join(all_candidate_skills))

# ============================================================
# FIND JOBS
# ============================================================
st.divider()
find_jobs = st.button(f"🔎 {T['find']}", type="primary", use_container_width=True)

if find_jobs:
    if candidate_lat is None or candidate_lon is None:
        st.error("Please enter a valid manual candidate location or enable Browser GPS.")
        st.stop()
    if not all_candidate_skills:
        st.error("Please upload a readable resume or enter candidate skills.")
        st.stop()

    scored = []
    for _, job in jobs_df.iterrows():
        job_key = str(clean_value(job.get("job_id")) or _)
        override = st.session_state.job_location_overrides.get(job_key, {})
        job_lat = safe_float(override.get("latitude")) if override else safe_float(job.get("latitude"))
        job_lon = safe_float(override.get("longitude")) if override else safe_float(job.get("longitude"))

        # CRITICAL: never copy candidate coordinates into a job.
        if job_lat is None or job_lon is None:
            continue

        distance = haversine_distance(candidate_lat, candidate_lon, job_lat, job_lon)
        if distance > 100:
            continue

        job_skills = job_skills_from_row(job)
        skill_match, skill_matches = calculate_skill_match(all_candidate_skills, job_skills)
        skill_gaps = get_skill_gaps(all_candidate_skills, job_skills)
        loc_score = location_score(distance)
        final_score = min(skill_match + loc_score, 100.0)

        scored.append({
            "job_id": clean_value(job.get("job_id")),
            "job_title": clean_value(job.get("job_title")) or "Untitled Job",
            "company": clean_value(job.get("company")) or "Company not provided",
            "location": clean_value(job.get("location")) or clean_value(job.get("location_display")),
            "address": (override.get("address") if override else "") or clean_value(job.get("address")) or clean_value(job.get("location_display")) or clean_value(job.get("location")),
            "latitude": job_lat,
            "longitude": job_lon,
            "distance_km": round(distance, 2),
            "distance_label": distance_label(distance),
            "skill_match": round(skill_match, 1),
            "location_score": round(loc_score, 1),
            "final_score": round(final_score, 1),
            "recommendation": recommendation_label(final_score),
            "skill_matches": skill_matches,
            "skill_gaps": skill_gaps,
            "salary": clean_value(job.get("salary")) or (f"₹{clean_value(job.get('salary_min'))} - ₹{clean_value(job.get('salary_max'))}" if clean_value(job.get("salary_min")) or clean_value(job.get("salary_max")) else ""),
            "employment_type": clean_value(job.get("employment_type")) or clean_value(job.get("contract_time")) or clean_value(job.get("contract_type")),
            "experience_years": clean_value(job.get("experience_years")),
            "description": clean_value(job.get("description")),
            "redirect_url": clean_value(job.get("redirect_url")),
            "location_status": clean_value(job.get("location_status")),
        })

    if not scored:
        st.warning("No jobs with valid source coordinates were found within 100 km. Jobs without coordinates are not assigned a fake distance.")
        st.stop()

    results_df = pd.DataFrame(scored).sort_values(["final_score", "distance_km"], ascending=[False, True]).head(10).reset_index(drop=True)

    st.divider()
    st.header(f"📍 {T['matches']}")
    st.write(f"**{T['name']}:** {candidate_name or 'Candidate'}")
    st.write(f"**GPS origin:** {candidate_lat:.6f}, {candidate_lon:.6f}")
    st.write(f"**Skills:** {', '.join(all_candidate_skills)}")
    st.caption(f"Showing {len(results_df)} best jobs. Distances are calculated from your browser GPS coordinates to each job's source coordinates.")

    # ------------------------------------------------------------
    # 1) MAP — SHOW THE RECOMMENDED JOBS
    # ------------------------------------------------------------
    st.divider()
    st.header("🗺️ 1. Recommended Jobs Near You")
    st.caption("The map shows the recommended jobs calculated from your candidate location. Each marker is a real job record with its calculated Haversine distance and match score.")
    render_map(candidate_lat, candidate_lon, results_df)

    # Quick recommended-job list directly below the map.
    st.markdown("### 📌 Jobs shown on the map")
    for number, (_, map_row) in enumerate(results_df.iterrows(), start=1):
        apply_text = " • Apply link available" if map_row.get("redirect_url") else ""
        st.write(
            f"**#{number} {map_row['job_title']}** — {map_row['company']} — "
            f"{map_row['distance_km']:.2f} km — Skill Match {map_row['skill_match']:.1f}% — "
            f"Final {map_row['final_score']:.1f}%{apply_text}"
        )

    # ------------------------------------------------------------
    # 2) SKILL GAP + LEARNING RECOMMENDATIONS
    # ------------------------------------------------------------
    skill_recommendations = build_skill_recommendations(all_candidate_skills, results_df)

    st.divider()
    st.header("🧩 2. Skill Gap & Improvement Recommendations")
    st.caption("These gaps come from the skills detected in the recommended jobs. A skill is recommended for improvement when it is required by one or more of the displayed jobs and is not covered by the candidate profile.")

    if skill_recommendations:
        for item in skill_recommendations:
            with st.container(border=True):
                g1, g2, g3 = st.columns([3, 1, 2])
                with g1:
                    st.markdown(f"### 🎯 {item['skill'].title()}")
                    st.write(f"Required by **{item['jobs']} of {len(results_df)}** displayed jobs ({item['coverage']:.0f}%).")
                with g2:
                    if item["priority"] == "High":
                        st.error(f"Priority: {item['priority']}")
                    elif item["priority"] == "Medium":
                        st.warning(f"Priority: {item['priority']}")
                    else:
                        st.info(f"Priority: {item['priority']}")
                with g3:
                    st.markdown("**Recommended improvement**")
                    st.write(item["tip"])
                    st.caption(f"Useful for: {item['example_job']}")
    else:
        st.success("🎉 No major skill gaps were detected across the displayed job matches. Keep strengthening your current skills.")

    output_file = APP_ROOT / "data" / "processed" / "streamlit_real_job_recommendations.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
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

            st.markdown(f"### 🏢 {T['company']}")
            st.write(row["company"])

            st.markdown(f"### 📍 {T['address']}")
            st.write(row["address"])
            st.caption(f"{row['distance_km']:.2f} km away • {row['distance_label']}")

            if row["location_status"]:
                st.caption(f"Location data: {row['location_status']}")

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

            st.markdown("### 🧩 Skill Gap for This Job")
            if row["skill_gaps"]:
                st.warning("Missing: " + ", ".join(row["skill_gaps"]))
            else:
                st.success("No skill gap detected for this job.")

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

            if row["description"]:
                with st.expander("📄 Job Description"):
                    st.write(row["description"])

            if row["redirect_url"]:
                st.link_button("🔗 View Original Job", row["redirect_url"])

            st.caption("Address and coordinates are displayed from the real job-source data. SkillBridge does not invent missing floor, landmark, street or building details.")

st.divider()
st.caption("SkillBridge AI • Real-world jobs • GPS • OpenStreetMap • Haversine distance")
