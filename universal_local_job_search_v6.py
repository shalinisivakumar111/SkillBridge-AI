
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
# SKILLBRIDGE AI — UNIVERSAL LOCAL JOB SEARCH
# ============================================================

APP_ROOT = Path(__file__).resolve().parent


def find_file(*relative_paths):
    candidates = []
    for base in [APP_ROOT, Path.cwd(), *APP_ROOT.parents]:
        for rel in relative_paths:
            candidates.append((base / rel).resolve())
    seen = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


REAL_JOBS_FILE = find_file(
    "data/processed/enriched_real_jobs.csv",
    "data/processed/location_enabled_jobs.csv",
    "data/processed/real_jobs.csv",
)

UNIVERSAL_JOBS_FILE = find_file(
    "data/jobs/universal_jobs.csv",
    "data/raw/jobs/universal_jobs.csv",
)


st.set_page_config(
    page_title="SkillBridge AI — Universal Local Jobs",
    page_icon="💼",
    layout="wide",
)


# ============================================================
# MULTILINGUAL UI
# ============================================================

LANGUAGES = {
    "English": {
        "title": "SKILLBRIDGE AI",
        "subtitle": "AI-Based Skill Matching for Local Employment",
        "find": "Find Local Jobs",
    },
    "తెలుగు": {
        "title": "స్కిల్‌బ్రిడ్జ్ AI",
        "subtitle": "స్థానిక ఉద్యోగాల కోసం AI ఆధారిత నైపుణ్య సరిపోలిక",
        "find": "స్థానిక ఉద్యోగాలను కనుగొనండి",
    },
    "हिन्दी": {
        "title": "स्किलब्रिज AI",
        "subtitle": "स्थानीय रोजगार के लिए AI कौशल मिलान",
        "find": "स्थानीय नौकरियां खोजें",
    },
    "தமிழ்": {
        "title": "ஸ்கில்பிரிட்ஜ் AI",
        "subtitle": "உள்ளூர் வேலைவாய்ப்புக்கான AI திறன் பொருத்தம்",
        "find": "உள்ளூர் வேலைகளை தேடுங்கள்",
    },
}


# ============================================================
# UNIVERSAL ROLE / PROFESSION TAXONOMY
# ============================================================

ROLE_ALIASES = {
    "Doctor": ["doctor", "physician", "medical officer", "mbbs", "md", "general physician", "dermatologist", "cardiologist"],
    "Nurse": ["nurse", "staff nurse", "registered nurse", "nursing"],
    "Dentist": ["dentist", "dental"],
    "Pharmacist": ["pharmacist", "pharmacy"],
    "Teacher": ["teacher", "teaching", "school teacher", "subject teacher"],
    "Professor": ["professor", "lecturer", "faculty", "college professor"],
    "Accountant": ["accountant", "accounts", "accounting", "bookkeeper", "finance"],
    "Software Developer": ["software developer", "software engineer", "developer", "programmer", "web developer", "full stack", "frontend", "backend"],
    "Data Analyst": ["data analyst", "data analysis", "business analyst", "analytics"],
    "Engineer": ["engineer", "engineering"],
    "Civil Engineer": ["civil engineer", "civil"],
    "Electrical Engineer": ["electrical engineer", "electrical"],
    "Sales": ["sales", "sales executive", "business development", "business development executive"],
    "Marketing": ["marketing", "digital marketing", "seo", "advertising"],
    "Customer Service": ["customer service", "customer support", "customer care", "support executive"],
    "Human Resources": ["human resources", "hr executive", "hrbp", "recruiter", "recruitment"],
    "Driver": ["driver", "delivery driver", "chauffeur", "delivery"],
    "Chef": ["chef", "cook", "kitchen"],
    "Security Guard": ["security guard", "security officer", "security"],
    "Lawyer": ["lawyer", "legal", "advocate", "attorney"],
    "Farmer": ["farmer", "farm worker", "agriculture", "agricultural"],
    "Electrician": ["electrician", "electrical technician"],
    "Plumber": ["plumber", "plumbing"],
    "Carpenter": ["carpenter", "carpentry"],
    "Welder": ["welder", "welding"],
    "Mechanic": ["mechanic", "automotive", "auto mechanic", "technician"],
    "Beautician": ["beautician", "beauty", "salon", "hair stylist"],
    "Social Worker": ["social worker", "social services", "community worker"],
    "Any Profession": [],
}


FAMILY_ALIASES = {
    "Healthcare": ["healthcare", "medical", "doctor", "nurse", "dentist", "pharmacist", "physician"],
    "Education": ["education", "teacher", "professor", "lecturer", "school", "college"],
    "IT": ["it", "software", "developer", "technology", "data", "computer", "programming"],
    "Finance": ["finance", "accounting", "accountant", "accounts"],
    "Engineering": ["engineering", "engineer", "civil", "electrical", "mechanical"],
    "Sales": ["sales", "business development"],
    "Marketing": ["marketing", "advertising", "seo"],
    "Services": ["service", "customer service", "support"],
    "Management": ["management", "human resources", "hr", "recruitment"],
    "Transport": ["transport", "driver", "delivery"],
    "Hospitality": ["hospitality", "chef", "cook", "hotel", "kitchen"],
    "Security": ["security", "guard"],
    "Legal": ["legal", "lawyer", "advocate"],
    "Agriculture": ["agriculture", "farmer", "farm"],
    "Skilled Trades": ["electrician", "plumber", "carpenter", "welder", "trade"],
    "Automotive": ["automotive", "mechanic", "auto"],
    "Beauty": ["beauty", "beautician", "salon"],
    "Social Services": ["social worker", "social services", "community"],
}


COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "sql",
    "mysql", "postgresql", "excel", "ms office", "microsoft office", "word",
    "powerpoint", "data entry", "office administration", "customer service",
    "customer support", "communication", "sales", "marketing", "digital marketing",
    "accounting", "tally", "power bi", "tableau", "data analysis", "data analyst",
    "pandas", "numpy", "machine learning", "deep learning", "html", "css",
    "react", "node.js", "django", "flask", "php", "laravel", "wordpress",
    "graphic design", "photoshop", "figma", "teaching", "patient assessment",
    "diagnosis", "emergency care", "bls", "acls", "clinical documentation",
    "mbbs", "md", "general medicine", "nursing", "pharmacy", "dentistry",
    "civil engineering", "electrical engineering", "plumbing", "welding",
    "carpentry", "automotive repair", "driving", "tamil", "telugu", "hindi",
    "english", "linux", "git", "aws", "azure",
}


RELATED_SKILLS = {
    "customer service": {"customer service", "customer support", "communication", "sales", "problem solving"},
    "communication": {"communication", "english", "customer service", "customer support", "sales"},
    "excel": {"excel", "ms excel", "ms office", "data entry", "accounting", "statistics"},
    "python": {"python", "pandas", "numpy", "django", "flask"},
    "javascript": {"javascript", "typescript", "react", "node.js", "node"},
    "web development": {"web development", "html", "css", "javascript", "react"},
    "teaching": {"teaching", "lesson planning", "classroom management", "assessment"},
    "nursing": {"nursing", "patient care", "patient assessment", "clinical documentation"},
    "doctor": {"doctor", "physician", "patient assessment", "diagnosis", "general medicine"},
    "mbbs": {"mbbs", "doctor", "general medicine", "patient assessment"},
}


SKILL_LEARNING_GUIDE = {
    "python": "Practice Python functions, data structures, files/APIs and build one small project.",
    "sql": "Practice SELECT, JOIN, GROUP BY and real-world database queries.",
    "excel": "Practice formulas, lookup functions, pivot tables and a small dashboard.",
    "communication": "Practice professional communication, presentations and workplace conversations.",
    "customer service": "Practice customer handling, issue resolution and professional communication.",
    "data analysis": "Learn data cleaning, exploratory analysis and practical data visualization.",
    "machine learning": "Learn supervised learning, evaluation and build one end-to-end project.",
    "deep learning": "Learn neural networks and complete one practical computer-vision or NLP project.",
    "javascript": "Practice DOM, asynchronous JavaScript and a small interactive web application.",
    "teaching": "Practice lesson planning, assessment design and learner-centred teaching.",
    "patient assessment": "Strengthen structured assessment, documentation and clinical reasoning under appropriate supervision.",
    "diagnosis": "Strengthen differential diagnosis and evidence-based clinical reasoning under appropriate supervision.",
    "clinical documentation": "Practice accurate, structured clinical notes and documentation standards.",
    "bls": "Refresh Basic Life Support through an appropriate certified course.",
    "acls": "Refresh Advanced Cardiovascular Life Support through an appropriate certified course.",
    "tally": "Practice ledgers, vouchers, GST workflows and basic accounting reports.",
    "sales": "Practice lead qualification, pitching, objection handling and CRM workflows.",
    "marketing": "Practice campaign planning, audience targeting, content strategy and analytics.",
}


# ============================================================
# HELPERS
# ============================================================

def norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower().replace("_", " ").replace("-", " "))


def clean(value):
    if value is None or pd.isna(value):
        return ""
    s = str(value).strip()
    return "" if s.lower() in {"nan", "none", "null"} else s


def num(value):
    try:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = radians(float(lat1)), radians(float(lat2))
    dp = radians(float(lat2) - float(lat1))
    dl = radians(float(lon2) - float(lon1))
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def job_family(row):
    text = norm(" ".join(
        clean(row.get(c, ""))
        for c in ["job_family", "family", "category", "category_tag", "job_title", "description"]
    ))
    for family, aliases in FAMILY_ALIASES.items():
        if any(alias in text for alias in aliases):
            return family
    return "Other"


def detect_role(row):
    text = norm(" ".join(
        clean(row.get(c, ""))
        for c in ["role_id", "role_name", "job_title", "job_family", "category", "description"]
    ))
    best = "Other"
    best_len = 0
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            if alias and alias in text and len(alias) > best_len:
                best = role
                best_len = len(alias)
    return best


def extract_job_skills(row):
    text = norm(" ".join(
        clean(row.get(c, ""))
        for c in [
            "skills", "required_skills", "job_skills", "category",
            "category_tag", "job_title", "description", "job_family", "role_name"
        ]
    ))

    found = []
    for skill in sorted(COMMON_SKILLS, key=len, reverse=True):
        if skill in text and skill not in found:
            found.append(skill)

    for field in ["skills", "required_skills", "job_skills"]:
        for item in clean(row.get(field, "")).split(","):
            item = norm(item)
            if item and item not in found:
                found.append(item)

    return found


def skill_match(candidate_skills, required_skills):
    cands = [norm(x) for x in candidate_skills if clean(x)]
    reqs = [norm(x) for x in required_skills if clean(x)]
    if not reqs:
        # Do not award a fake 100% when a job has no structured skill data.
        return 0.0, [], reqs

    matches = []
    used = set()

    for req in reqs:
        best = None
        for cand in cands:
            if cand == req:
                score, typ = 1.0, "exact"
            elif req in RELATED_SKILLS.get(cand, set()) or cand in RELATED_SKILLS.get(req, set()):
                score, typ = 0.65, "related"
            else:
                score, typ = 0.0, ""
            if score and (best is None or score > best[0]):
                best = (score, cand, typ)

        if best:
            matches.append({
                "candidate_skill": best[1],
                "job_skill": req,
                "type": best[2],
                "score": best[0],
            })
            used.add(req)

    score = (sum(m["score"] for m in matches) / len(reqs)) * 100
    gaps = [req for req in reqs if req not in used]
    return min(score, 100.0), matches, gaps


def role_match(candidate_role, row):
    if candidate_role == "Any Profession":
        return 50.0

    target = norm(candidate_role)
    text = norm(" ".join(
        clean(row.get(c, ""))
        for c in ["role_id", "role_name", "job_title", "job_family", "category", "category_tag"]
    ))

    aliases = ROLE_ALIASES.get(candidate_role, [])
    if any(alias in text for alias in aliases):
        return 100.0

    # Family-level fallback for universal jobs.
    family = job_family(row)
    if target in norm(family):
        return 70.0

    return 0.0


def location_score(distance, radius):
    if radius <= 0:
        return 0.0
    # Smooth score: nearby jobs get more weight, but never creates a 100% match.
    return max(0.0, 25.0 * (1.0 - min(distance / radius, 1.0)))


def learning_tip(skill):
    key = norm(skill)
    return SKILL_LEARNING_GUIDE.get(
        key,
        f"Learn {skill} with a short practical course and complete one small real-world task using it."
    )


def recommendation_label(score):
    if score >= 85:
        return "Excellent Match"
    if score >= 70:
        return "Strong Match"
    if score >= 55:
        return "Good Potential"
    if score >= 40:
        return "Possible Match"
    return "Low Match"


def recommendation_explanation(row):
    matched_count = len(row.get("skill_matches", []) or [])
    gap_count = len(row.get("skill_gaps", []) or [])
    role = float(row.get("role_match", 0) or 0)
    skill = float(row.get("skill_match", 0) or 0)
    distance = float(row.get("distance_km", 0) or 0)
    score = float(row.get("final_score", 0) or 0)

    return {
        "label": recommendation_label(score),
        "role": role,
        "skill": skill,
        "distance": distance,
        "matched_count": matched_count,
        "gap_count": gap_count,
    }


def aggregate_skill_gaps(results, candidate_skills, limit=8):
    if results.empty:
        return []

    candidate_set = {norm(x) for x in candidate_skills}
    stats = {}

    for _, row in results.iterrows():
        for gap in row["skill_gaps"]:
            key = norm(gap)
            if not key or key in candidate_set:
                continue
            if key not in stats:
                stats[key] = {"skill": gap, "jobs": 0, "weight": 0.0, "example": row["job_title"]}
            stats[key]["jobs"] += 1
            stats[key]["weight"] += max(row["final_score"], 1.0) / 100.0

    total = len(results)
    ranked = sorted(stats.values(), key=lambda x: (x["weight"], x["jobs"]), reverse=True)

    output = []
    for item in ranked[:limit]:
        coverage = item["jobs"] / total * 100
        priority = "High" if coverage >= 60 else "Medium" if coverage >= 30 else "Useful"
        output.append({
            **item,
            "coverage": coverage,
            "priority": priority,
            "tip": learning_tip(item["skill"]),
        })
    return output


def load_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except Exception:
        return pd.read_csv(path, encoding="latin1", low_memory=False)


@st.cache_data
def load_jobs():
    frames = []

    # Real local jobs: primary source.
    if REAL_JOBS_FILE:
        try:
            real = load_csv(REAL_JOBS_FILE)
            real["source_type"] = "Real local job source"
            frames.append(real)
        except Exception:
            pass

    # Universal role dataset: adds explicit profession/job-family information.
    if UNIVERSAL_JOBS_FILE:
        try:
            universal = load_csv(UNIVERSAL_JOBS_FILE)
            universal["source_type"] = "Universal role dataset"
            frames.append(universal)
        except Exception:
            pass

    if not frames:
        return pd.DataFrame()

    all_frames = []

    for df in frames:
        df = df.copy()

        aliases = {
            "job_id": ["job_id", "source_job_id", "id", "role_id"],
            "job_title": ["job_title", "title", "role_name"],
            "company": ["company", "company_name", "employer"],
            "location": ["location", "location_display", "searched_location", "city"],
            "address": ["company_address", "address", "location_area", "location_display", "location"],
            "latitude": ["latitude", "lat"],
            "longitude": ["longitude", "lon", "lng"],
            "redirect_url": ["redirect_url", "url", "apply_url", "application_url"],
            "description": ["description", "job_description"],
            "skills": ["skills", "required_skills", "job_skills"],
            "job_family": ["job_family", "family"],
            "role_id": ["role_id"],
            "role_name": ["role_name"],
            "salary": ["salary"],
        }

        for target, choices in aliases.items():
            if target not in df.columns:
                for choice in choices:
                    if choice in df.columns:
                        df[target] = df[choice]
                        break
                else:
                    df[target] = ""

        df["job_title"] = df["job_title"].map(clean)
        df["company"] = df["company"].map(clean)
        df["location"] = df["location"].map(clean)
        df["address"] = df["address"].map(clean)
        df["role"] = df.apply(detect_role, axis=1)
        df["family"] = df.apply(job_family, axis=1)

        # Remove unusable rows.
        df = df[df["job_title"].str.len() > 0].copy()
        all_frames.append(df)

    jobs = pd.concat(all_frames, ignore_index=True, sort=False)

    # Prefer real job records when duplicate title/company/location exists.
    jobs["_dedupe"] = (
        jobs["job_title"].map(norm) + "|" +
        jobs["company"].map(norm) + "|" +
        jobs["location"].map(norm)
    )
    jobs = jobs.drop_duplicates("_dedupe", keep="first").drop(columns=["_dedupe"], errors="ignore")
    return jobs.reset_index(drop=True)


def render_map(candidate_lat, candidate_lon, results):
    if not MAP_AVAILABLE:
        st.error("Map support is missing. Install: pip install folium streamlit-folium")
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
        popup="📍 Candidate",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    bounds = [[candidate_lat, candidate_lon]]

    for _, row in results.iterrows():
        lat, lon = num(row["latitude"]), num(row["longitude"])
        if lat is None or lon is None:
            continue

        title = html.escape(row["job_title"])
        company = html.escape(row["company"] or "Company not provided")
        dist = row["distance_km"]
        score = row["final_score"]
        popup = folium.Popup(
            f"<b>{title}</b><br>{company}<br>"
            f"📍 {dist:.2f} km<br>🎯 Match {score:.1f}%",
            max_width=320,
        )

        folium.Marker(
            [lat, lon],
            tooltip=f"{row['job_title']} • {dist:.2f} km",
            popup=popup,
            icon=folium.Icon(color="red", icon="briefcase", prefix="fa"),
        ).add_to(m)

        bounds.append([lat, lon])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(30, 30))

    st_folium(m, width=None, height=560, returned_objects=[])


# ============================================================
# APP
# ============================================================

language = st.sidebar.selectbox(
    "Language / భాష / भाषा / மொழி",
    list(LANGUAGES.keys()),
)
T = LANGUAGES[language]

st.sidebar.markdown(
    """
### SkillBridge AI
**Universal • Local • Multilingual**

Doctor • Teacher • Nurse • Engineer • Developer • Driver • Farmer • Trades • and more
"""
)

st.title(f"💼 {T['title']}")
st.subheader(T["subtitle"])
st.caption("Universal profession search • GPS • Manual location • OpenStreetMap • Skill gap recommendations")

jobs = load_jobs()

if jobs.empty:
    st.error("No job data could be loaded.")
    st.code(
        "Expected one of:\n"
        "data/processed/enriched_real_jobs.csv\n"
        "data/jobs/universal_jobs.csv\n\n"
        f"App folder: {APP_ROOT}"
    )
    st.stop()

st.success(
    f"Loaded {len(jobs):,} universal/local job records "
    f"from {jobs['source_type'].nunique()} job sources."
)

# ============================================================
# SEARCH CONTROLS
# ============================================================

st.header("🔎 Universal Local Job Search")

c1, c2 = st.columns(2)

with c1:
    profession = st.selectbox(
        "Job / Profession",
        list(ROLE_ALIASES.keys()),
        help="Choose Doctor, Teacher, Engineer, Developer, Driver, Farmer, trades, services, or any profession.",
    )

with c2:
    keyword = st.text_input(
        "Optional job search",
        placeholder="e.g. dermatologist, mathematics teacher, Python developer, electrician",
    )

f1, f2, f3 = st.columns(3)

with f1:
    candidate_name = st.text_input("Candidate Name", value="Candidate")

with f2:
    radius = st.slider(
        "Local search radius (km)",
        min_value=1,
        max_value=100,
        value=25,
    )

with f3:
    max_jobs = st.slider(
        "Jobs to recommend",
        min_value=5,
        max_value=30,
        value=10,
    )

# ============================================================
# CANDIDATE LOCATION
# ============================================================

st.header("📍 Candidate Location")

location_mode = st.radio(
    "Location method",
    ["Manual Location", "Browser GPS"],
    horizontal=True,
)

candidate_lat = None
candidate_lon = None
candidate_location_name = ""

if location_mode == "Manual Location":
    # Manual coordinates are deliberate and transparent.
    a1, a2 = st.columns(2)

    with a1:
        candidate_lat = st.number_input(
            "Latitude",
            value=12.9165,
            min_value=-90.0,
            max_value=90.0,
            format="%.6f",
        )

    with a2:
        candidate_lon = st.number_input(
            "Longitude",
            value=79.1325,
            min_value=-180.0,
            max_value=180.0,
            format="%.6f",
        )

    candidate_location_name = st.text_input(
        "Area / City",
        value="Vellore",
        placeholder="Vellore / Chennai / Madurai / Kochi / your locality",
    )

    st.success(
        f"📍 Candidate location: {candidate_location_name or 'Manual'} "
        f"({candidate_lat:.6f}, {candidate_lon:.6f})"
    )

else:
    if not GEOLOCATION_AVAILABLE:
        st.error("GPS package is not installed. Run: pip install streamlit-geolocation")
    else:
        gps = streamlit_geolocation()
        if gps:
            candidate_lat = num(gps.get("latitude"))
            candidate_lon = num(gps.get("longitude"))

        if candidate_lat is not None and candidate_lon is not None:
            candidate_location_name = "Browser GPS"
            st.success(
                f"📍 GPS detected: {candidate_lat:.6f}, {candidate_lon:.6f}"
            )
        else:
            st.info("Allow browser location permission to use GPS.")

# ============================================================
# CANDIDATE SKILLS
# ============================================================

st.header("🧠 Candidate Skills")

skills_text = st.text_area(
    "Enter skills separated by commas",
    placeholder="MBBS, diagnosis, patient assessment, BLS, ACLS",
    help="Skills drive the recommendation score and skill-gap analysis.",
)

candidate_skills = [x.strip() for x in skills_text.split(",") if x.strip()]

uploaded = st.file_uploader(
    "Optional Resume",
    type=["pdf", "txt", "md", "docx"],
)

if uploaded is not None:
    try:
        if uploaded.name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            text = "\n".join((p.extract_text() or "") for p in PdfReader(uploaded).pages)
        elif uploaded.name.lower().endswith(".docx"):
            from docx import Document
            text = "\n".join(p.text for p in Document(uploaded).paragraphs)
        else:
            text = uploaded.getvalue().decode("utf-8", errors="ignore")

        resume_found = []
        normalized = norm(text)
        for skill in sorted(COMMON_SKILLS, key=len, reverse=True):
            if skill in normalized and skill not in resume_found:
                resume_found.append(skill)

        for skill in resume_found:
            if norm(skill) not in {norm(x) for x in candidate_skills}:
                candidate_skills.append(skill)

        if resume_found:
            st.success("Resume skills detected: " + ", ".join(resume_found))
    except Exception as exc:
        st.warning(f"Resume could not be read: {exc}")

if candidate_skills:
    st.info("Matching skills: " + ", ".join(candidate_skills))


# ============================================================
# SEARCH
# ============================================================

if st.button(f"🔎 {T['find']}", type="primary", width="stretch"):

    if candidate_lat is None or candidate_lon is None:
        st.error("Please enter a candidate location or enable Browser GPS.")
        st.stop()

    if not candidate_skills:
        st.warning(
            "No skills entered. The system can still show local jobs, "
            "but skill matching and skill-gap recommendations will be limited."
        )

    working = jobs.copy()

    # Profession filtering.
    if profession != "Any Profession":
        role_scores = working.apply(
            lambda row: role_match(profession, row),
            axis=1,
        )
        working["_role_match"] = role_scores
        working = working[working["_role_match"] > 0].copy()
    else:
        working["_role_match"] = 50.0

    # Free-text profession/job search.
    if keyword.strip():
        q = norm(keyword)
        working = working[
            working.apply(
                lambda row: q in norm(" ".join(
                    clean(row.get(c, ""))
                    for c in [
                        "job_title", "company", "location",
                        "address", "role", "family", "description",
                        "category", "category_tag",
                    ]
                )),
                axis=1,
            )
        ].copy()

    if working.empty:
        st.warning(
            f"No jobs found for **{profession}**"
            + (f" matching **{keyword}**" if keyword.strip() else "")
            + ". Try Any Profession, a larger radius, or another search term."
        )
        st.stop()

    results = []

    for _, row in working.iterrows():
        lat = num(row.get("latitude"))
        lon = num(row.get("longitude"))

        # Never invent a job location.
        if lat is None or lon is None:
            continue

        distance = haversine(candidate_lat, candidate_lon, lat, lon)

        if distance > radius:
            continue

        required = extract_job_skills(row)
        skill_score, matches, gaps = skill_match(candidate_skills, required)

        role_score = float(row["_role_match"])

        # Transparent weighted score.
        # Role 40%, skills 40%, local distance 20%.
        # With Any Profession role_score=50, so it cannot create a fake 100%.
        loc = location_score(distance, radius)
        final = min(
            0.40 * role_score
            + 0.40 * skill_score
            + 0.80 * loc,
            100.0,
        )

        # If structured skills are absent, explicitly reduce confidence.
        if not required:
            final *= 0.75

        results.append({
            "job_id": clean(row.get("job_id")),
            "job_title": clean(row.get("job_title")) or "Untitled Job",
            "company": clean(row.get("company")) or "Company not provided",
            "location": clean(row.get("location")),
            "address": clean(row.get("address")) or clean(row.get("location")),
            "latitude": lat,
            "longitude": lon,
            "role": row.get("role", "Other"),
            "family": row.get("family", "Other"),
            "distance_km": distance,
            "role_match": role_score,
            "skill_match": skill_score,
            "final_score": final,
            "skill_matches": matches,
            "skill_gaps": gaps,
            "redirect_url": clean(row.get("redirect_url")),
            "description": clean(row.get("description")),
            "salary": clean(row.get("salary")),
            "source_type": clean(row.get("source_type")),
        })

    if not results:
        st.warning(
            "No jobs with valid coordinates were found inside the selected local radius. "
            "Jobs without coordinates are not assigned a fake distance."
        )
        st.stop()

    results_df = (
        pd.DataFrame(results)
        .sort_values(["final_score", "distance_km"], ascending=[False, True])
        .head(max_jobs)
        .reset_index(drop=True)
    )

    # ========================================================
    # LOCAL EMPLOYMENT INTELLIGENCE
    # ========================================================

    st.divider()
    st.header("📊 Local Employment Intelligence")

    total_local = len(results_df)
    avg_distance = results_df["distance_km"].mean()
    avg_match = results_df["final_score"].mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Jobs Recommended", total_local)
    with k2:
        st.metric("Avg. Distance", f"{avg_distance:.1f} km")
    with k3:
        st.metric("Avg. Recommendation", f"{avg_match:.1f}%")
    with k4:
        st.metric("Job Families", int(results_df["family"].nunique()))

    family_counts = (
        results_df["family"]
        .value_counts()
        .rename("Jobs")
        .rename_axis("Job Family")
        .reset_index()
    )
    skill_demand = {}

    for _, r in results_df.iterrows():
        # Count the skills actually present in the job's structured/derived skill list.
        for skill in extract_job_skills(r):
            key = norm(skill)
            if key:
                skill_demand[key] = skill_demand.get(key, 0) + 1

    if skill_demand:
        demand_df = (
            pd.DataFrame(
                [{"Skill": skill.title(), "Jobs Requiring It": count}
                 for skill, count in skill_demand.items()]
            )
            .sort_values("Jobs Requiring It", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
    else:
        demand_df = pd.DataFrame(columns=["Skill", "Jobs Requiring It"])

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 🏘️ Local Job Families")
        if not family_counts.empty:
            st.dataframe(
                family_counts,
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No job-family demand data is available.")

    with d2:
        st.markdown("#### 🔥 Most Requested Skills")
        if not demand_df.empty:
            st.dataframe(demand_df, width="stretch", hide_index=True)
        else:
            st.info("The current job records do not contain enough structured skill data.")

    # ========================================================
    # COMMUNITY NEEDS
    # ========================================================

    st.divider()
    st.header("🏘️ Local Community Job Demand")

    family_counts = results_df["family"].value_counts()

    if not family_counts.empty:
        demand_text = " • ".join(
            f"{family}: {count}"
            for family, count in family_counts.head(6).items()
        )
        st.info(
            f"Within {radius} km, the current recommendation pool shows: {demand_text}"
        )

    # ========================================================
    # MAP
    # ========================================================

    st.divider()
    st.header("🗺️ Recommended Local Jobs")

    st.caption(
        "Blue = candidate. Red = recommended jobs. "
        "Distances are calculated using Haversine distance from the candidate coordinates "
        "to the job's source coordinates."
    )

    render_map(candidate_lat, candidate_lon, results_df)

    # ========================================================
    # JOB SEARCH RESULTS
    # ========================================================

    st.header("💼 Jobs for Every Profession")
    st.caption(
        "Recommendation score is a ranking signal, not a hiring guarantee. "
        "It combines profession relevance, available skill evidence, and local distance. "
        "A job cannot receive a perfect score merely because the profession matches."
    )

    for i, row in results_df.iterrows():
        with st.container(border=True):
            st.markdown(f"## {i + 1}. {row['job_title']}")

            explanation = recommendation_explanation(row)

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Profession", row["role"])

            with c2:
                st.metric("Skill Match", f"{row['skill_match']:.1f}%")

            with c3:
                st.metric("Distance", f"{row['distance_km']:.2f} km")

            with c4:
                st.metric(
                    "Recommendation",
                    f"{row['final_score']:.1f}%",
                    delta=explanation["label"],
                )

            st.markdown("### 🤖 Why this job is recommended")
            e1, e2, e3 = st.columns(3)
            with e1:
                st.write(f"**Role relevance:** {explanation['role']:.1f}%")
            with e2:
                st.write(f"**Skill evidence:** {explanation['skill']:.1f}%")
            with e3:
                st.write(f"**Local distance:** {explanation['distance']:.2f} km")

            st.caption(
                f"{explanation['matched_count']} matched skill(s) • "
                f"{explanation['gap_count']} skill gap(s) • "
                f"Ranking: {explanation['label']}"
            )

            st.write(f"🏢 **Company:** {row['company']}")
            st.write(f"📍 **Job Location:** {row['address']}")
            st.write(f"🧭 **Coordinates:** {row['latitude']:.6f}, {row['longitude']:.6f}")

            if row["skill_matches"]:
                st.markdown("### 🟢 Matched Skills")
                st.write(", ".join(
                    f"{m['candidate_skill']} → {m['job_skill']}"
                    for m in row["skill_matches"]
                ))

            st.markdown("### 🧩 Skill Gap")

            if row["skill_gaps"]:
                st.warning(
                    "Missing skills: " + ", ".join(row["skill_gaps"])
                )
            else:
                if row["skill_match"] > 0:
                    st.success("No detected skill gap for the structured skills in this job.")
                else:
                    st.info("This job does not contain enough structured skill data for a reliable gap analysis.")

            if row["description"]:
                with st.expander("📄 Job Description"):
                    st.write(row["description"])

            if row["redirect_url"]:
                st.link_button(
                    "🔗 Apply / View Original Job",
                    row["redirect_url"],
                )
            else:
                st.caption("No application URL is available in the source record.")

    # ========================================================
    # SKILL GAP RECOMMENDATIONS
    # ========================================================

    st.divider()
    st.header("🧩 Skill Gap & Skills to Improve")

    if candidate_skills:
        st.markdown("#### Your Current Skills")
        st.write(" • ".join(f"✓ {s}" for s in candidate_skills))

    recommendations = aggregate_skill_gaps(
        results_df,
        candidate_skills,
        limit=8,
    )

    if not recommendations:
        st.success(
            "No high-frequency skill gaps were detected in the recommended jobs."
        )
    else:
        for item in recommendations:
            with st.container(border=True):
                a, b = st.columns([3, 1])

                with a:
                    st.markdown(f"### 🎯 {item['skill'].title()}")
                    st.write(
                        f"Required by **{item['jobs']} of {len(results_df)}** "
                        f"recommended jobs ({item['coverage']:.0f}%)."
                    )
                    st.write(f"**How to improve:** {item['tip']}")
                    st.caption(f"Example job: {item['example']}")

                with b:
                    if item["priority"] == "High":
                        st.error("HIGH PRIORITY")
                    elif item["priority"] == "Medium":
                        st.warning("MEDIUM PRIORITY")
                    else:
                        st.info("USEFUL")

    if recommendations:
        high_priority = sum(1 for item in recommendations if item["priority"] == "High")
        medium_priority = sum(1 for item in recommendations if item["priority"] == "Medium")
        st.info(
            f"🚀 Improvement roadmap: {high_priority} high-priority and "
            f"{medium_priority} medium-priority skill gap(s) were found from the "
            f"recommended local jobs. Improving these skills can strengthen eligibility "
            f"for more of the jobs shown above."
        )

    st.success(
        "Universal search complete: profession + skills + local distance + community demand + skill gaps."
    )
    st.caption(
        "Community-demand metrics are calculated from the jobs returned by this local search. "
        "They describe the current dataset/search pool and are not a forecast of the whole labor market."
    )
    if not family_counts.empty:
        # family_counts is a Series here (it was intentionally reduced for the
        # community-demand summary above), so use its index/value directly.
        top_family = str(family_counts.index[0])
        top_count = int(family_counts.iloc[0])
        st.info(
            f"🏘️ Local need signal: **{top_family}** is the largest job-family group "
            f"in the current {radius} km recommendation pool ({top_count} job(s))."
        )


st.divider()
st.caption(
    "SkillBridge AI • Universal Local Employment • GPS • OpenStreetMap • "
    "Haversine Distance • Skill Gap Recommendations • Multilingual"
)
