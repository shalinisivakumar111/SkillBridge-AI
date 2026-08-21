import sys
from pathlib import Path
import math
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.universal_engine import recommend_jobs

JOBS_FILE = ROOT / "data" / "jobs" / "universal_jobs.csv"
ROLES_FILE = ROOT / "data" / "jobs" / "roles.csv"

try:
    import folium
    from streamlit_folium import st_folium
    MAP_OK = True
except ImportError:
    MAP_OK = False

st.set_page_config(
    page_title="SkillBridge AI",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 SkillBridge AI")
st.subheader("Universal Local Job & Skill Recommendation System")
st.write(
    "Match Doctors, Teachers, Engineers, Developers, Accountants, "
    "Electricians and other job seekers with relevant local jobs."
)

@st.cache_data
def load_data():
    jobs = pd.read_csv(JOBS_FILE)
    roles = pd.read_csv(ROLES_FILE)
    return jobs, roles

if not JOBS_FILE.exists():
    st.error(f"Missing universal jobs dataset: {JOBS_FILE}")
    st.stop()

if not ROLES_FILE.exists():
    st.error(f"Missing roles dataset: {ROLES_FILE}")
    st.stop()

jobs_df, roles_df = load_data()

def num(v, default=0.0):
    try:
        if pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default

def text(row, *cols, default="Not provided"):
    for col in cols:
        if col in row:
            value = row[col]
            if not pd.isna(value):
                value = str(value).strip()
                if value and value.lower() not in ["nan", "none", "null"]:
                    return value
    return default

def lat_of(row):
    for c in ["latitude", "lat", "job_latitude", "company_latitude"]:
        if c in row:
            try:
                if not pd.isna(row[c]):
                    return float(row[c])
            except Exception:
                pass
    return None

def lon_of(row):
    for c in ["longitude", "lon", "lng", "job_longitude", "company_longitude"]:
        if c in row:
            try:
                if not pd.isna(row[c]):
                    return float(row[c])
            except Exception:
                pass
    return None

def distance_km(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return None

    R = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return R * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("👤 Candidate Profile")

candidate_name = st.sidebar.text_input(
    "Candidate Name",
    "Candidate"
)

role_list = sorted(
    roles_df["role_name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_role = st.sidebar.selectbox(
    "Job Role / Profession",
    role_list
)

skills_text = st.sidebar.text_area(
    "Candidate Skills",
    placeholder="MBBS, diagnosis, patient care, BLS",
    height=150
)

st.sidebar.markdown("---")

st.sidebar.header("📍 Candidate Location")

location_source = st.sidebar.radio(
    "Location source",
    ["Manual", "Browser GPS", "OpenStreetMap"]
)

if "candidate_lat" not in st.session_state:
    st.session_state.candidate_lat = 12.9165

if "candidate_lon" not in st.session_state:
    st.session_state.candidate_lon = 79.1325

# ============================================================
# MANUAL
# ============================================================

if location_source == "Manual":

    st.session_state.candidate_lat = st.sidebar.number_input(
        "Latitude",
        value=float(st.session_state.candidate_lat),
        format="%.6f"
    )

    st.session_state.candidate_lon = st.sidebar.number_input(
        "Longitude",
        value=float(st.session_state.candidate_lon),
        format="%.6f"
    )

# ============================================================
# BROWSER GPS
# ============================================================

elif location_source == "Browser GPS":

    st.sidebar.info(
        "Click below to request your browser's current location."
    )

    st.sidebar.markdown(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                window.parent.postMessage({
                    type: "SKILLBRIDGE_GPS",
                    lat: lat,
                    lon: lon
                }, "*");
            }
        );
        </script>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.caption(
        "If the browser asks for location permission, choose Allow."
    )

    st.sidebar.write(
        f"Current latitude: {st.session_state.candidate_lat:.6f}"
    )

    st.sidebar.write(
        f"Current longitude: {st.session_state.candidate_lon:.6f}"
    )

# ============================================================
# OPENSTREETMAP
# ============================================================

elif location_source == "OpenStreetMap":

    if not MAP_OK:
        st.sidebar.error(
            "Install map support with:"
        )
        st.sidebar.code(
            "pip install folium streamlit-folium"
        )
    else:

        osm = folium.Map(
            location=[
                st.session_state.candidate_lat,
                st.session_state.candidate_lon
            ],
            zoom_start=12,
            tiles="OpenStreetMap"
        )

        folium.Marker(
            [
                st.session_state.candidate_lat,
                st.session_state.candidate_lon
            ],
            tooltip="Candidate location",
            popup="Candidate",
            icon=folium.Icon(
                color="blue",
                icon="user",
                prefix="fa"
            )
        ).add_to(osm)

        st.sidebar.caption(
            "Click the map to select candidate location."
        )

        clicked = st_folium(
            osm,
            width=300,
            height=300,
            returned_objects=["last_clicked"],
            key="candidate_location_map"
        )

        if clicked and clicked.get("last_clicked"):

            point = clicked["last_clicked"]

            st.session_state.candidate_lat = float(
                point["lat"]
            )

            st.session_state.candidate_lon = float(
                point["lng"]
            )

# ============================================================
# PROFILE
# ============================================================

st.header("👤 Candidate Profile")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Profession", selected_role)

with c2:
    skills = [
        x.strip()
        for x in skills_text.split(",")
        if x.strip()
    ]
    st.metric("Skills", len(skills))

with c3:
    st.metric("Universal Jobs", len(jobs_df))

st.write(
    "**Skills:** "
    + (", ".join(skills) if skills else "None entered")
)

st.write(
    f"**Candidate Location:** "
    f"{st.session_state.candidate_lat:.6f}, "
    f"{st.session_state.candidate_lon:.6f}"
)

# ============================================================
# FIND JOBS
# ============================================================

if st.button(
    "🔎 FIND MATCHING LOCAL JOBS",
    type="primary",
    use_container_width=True
):

    if not skills:
        st.error("Please enter at least one skill.")
        st.stop()

    with st.spinner(
        f"Finding relevant {selected_role} jobs..."
    ):

        matches = recommend_jobs(
            jobs_df,
            skills,
            st.session_state.candidate_lat,
            st.session_state.candidate_lon,
            requested_role=selected_role,
            limit=15
        )

    if matches is None:
        matches = []

    result_rows = []

    for item in matches:

        if isinstance(item, dict):
            row = dict(item)
        elif hasattr(item, "to_dict"):
            row = item.to_dict()
        else:
            row = dict(item)

        jlat = lat_of(row)
        jlon = lon_of(row)

        dist = distance_km(
            st.session_state.candidate_lat,
            st.session_state.candidate_lon,
            jlat,
            jlon
        )

        row["_distance"] = dist

        result_rows.append(row)

    st.session_state.matches = result_rows

# ============================================================
# DISPLAY
# ============================================================

if "matches" in st.session_state:

    results = st.session_state.matches

    st.divider()

    st.header("📋 Detailed Job Listings")

    if not results:

        st.warning(
            f"No relevant {selected_role} jobs were found."
        )

        st.info(
            "Unrelated jobs are intentionally excluded."
        )

        st.stop()

    st.success(
        f"{len(results)} relevant {selected_role} job(s) found."
    )

    # ========================================================
    # MAP
    # ========================================================

    st.header("🗺️ Candidate + Job Locations")

    if not MAP_OK:

        st.error(
            "Map packages are missing. Run:"
        )

        st.code(
            "pip install folium streamlit-folium"
        )

    else:

        main_map = folium.Map(
            location=[
                st.session_state.candidate_lat,
                st.session_state.candidate_lon
            ],
            zoom_start=11,
            tiles="OpenStreetMap"
        )

        folium.Marker(
            [
                st.session_state.candidate_lat,
                st.session_state.candidate_lon
            ],
            tooltip="👤 Candidate",
            popup=(
                f"Candidate<br>"
                f"Profession: {selected_role}"
            ),
            icon=folium.Icon(
                color="blue",
                icon="user",
                prefix="fa"
            )
        ).add_to(main_map)

        bounds = [[
            st.session_state.candidate_lat,
            st.session_state.candidate_lon
        ]]

        mapped = 0

        for i, row in enumerate(results, 1):

            jlat = lat_of(row)
            jlon = lon_of(row)

            if jlat is None or jlon is None:
                continue

            mapped += 1

            title = text(
                row,
                "job_title",
                "title",
                default="Job"
            )

            company = text(
                row,
                "company",
                "company_name",
                default="Company not provided"
            )

            location = text(
                row,
                "location",
                "address",
                default="Location not provided"
            )

            dist = distance_km(
                st.session_state.candidate_lat,
                st.session_state.candidate_lon,
                jlat,
                jlon
            )

            popup = (
                f"<b>#{i} {title}</b><br>"
                f"Company: {company}<br>"
                f"Location: {location}<br>"
                f"Distance: "
                f"{dist:.2f} km"
                if dist is not None
                else
                f"<b>#{i} {title}</b><br>"
                f"Company: {company}<br>"
                f"Location: {location}"
            )

            folium.Marker(
                [jlat, jlon],
                tooltip=f"#{i} {title}",
                popup=folium.Popup(
                    popup,
                    max_width=350
                ),
                icon=folium.Icon(
                    color="red",
                    icon="briefcase",
                    prefix="fa"
                )
            ).add_to(main_map)

            bounds.append([jlat, jlon])

        if len(bounds) > 1:
            main_map.fit_bounds(
                bounds,
                padding=(30, 30)
            )

        st_folium(
            main_map,
            width=None,
            height=600,
            key="matching_jobs_map"
        )

        st.caption(
            f"🔵 Candidate location | "
            f"🔴 Job locations | "
            f"{mapped} job location(s) mapped"
        )

    # ========================================================
    # JOB CARDS
    # ========================================================

    for i, row in enumerate(results, 1):

        title = text(
            row,
            "job_title",
            "title",
            default="Job"
        )

        company = text(
            row,
            "company",
            "company_name",
            default="Company not provided"
        )

        location = text(
            row,
            "location",
            "address",
            default="Location not provided"
        )

        role_match = num(
            row.get("role_match", 0)
        )

        skill_match = num(
            row.get("skill_match", 0)
        )

        final_score = num(
            row.get("final_score", 0)
        )

        # Prevent misleading 100% display.
        final_score = min(
            final_score,
            95.0
        )

        dist = row.get("_distance")

        with st.container(border=True):

            st.markdown(
                f"## #{i} — {title}"
            )

            a, b, c, d = st.columns(4)

            with a:
                st.metric(
                    "Role Match",
                    f"{role_match:.1f}%"
                )

            with b:
                st.metric(
                    "Skill Match",
                    f"{skill_match:.1f}%"
                )

            with c:
                st.metric(
                    "Distance",
                    (
                        f"{dist:.2f} km"
                        if dist is not None
                        else "Unavailable"
                    )
                )

            with d:
                st.metric(
                    "Overall Match",
                    f"{final_score:.1f}%"
                )

            st.markdown("### 👔 Job")

            st.write(title)

            st.markdown("### 🏢 Company")

            st.write(company)

            st.markdown("### 📍 Job Location")

            st.write(location)

            jlat = lat_of(row)
            jlon = lon_of(row)

            if jlat is not None and jlon is not None:

                st.caption(
                    f"Job coordinates: "
                    f"{jlat:.6f}, {jlon:.6f}"
                )

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            description = text(
                row,
                "description",
                "job_description",
                default=""
            )

            if description:
                st.markdown(
                    "### 📄 Job Description"
                )
                st.write(description)

            # ------------------------------------------------
            # SKILLS
            # ------------------------------------------------

            matched = row.get(
                "matched_skills",
                []
            )

            if isinstance(matched, str):

                matched = [
                    x.strip()
                    for x in matched.replace(
                        "|", ","
                    ).split(",")
                    if x.strip()
                ]

            st.markdown(
                "### 🟢 Matching Skills"
            )

            if matched:
                st.write(
                    ", ".join(
                        str(x)
                        for x in matched
                    )
                )
            else:
                st.write(
                    "No direct skill match."
                )

            # ------------------------------------------------
            # GAP
            # ------------------------------------------------

            gaps = row.get(
                "skill_gaps",
                []
            )

            if isinstance(gaps, str):

                gaps = [
                    x.strip()
                    for x in gaps.replace(
                        "|", ","
                    ).split(",")
                    if x.strip()
                ]

            st.markdown(
                "### 🎯 Skill Gap"
            )

            if gaps:
                st.warning(
                    "Recommended to learn: "
                    + ", ".join(
                        str(x)
                        for x in gaps
                    )
                )
            else:
                st.success(
                    "No major skill gaps."
                )

            # ------------------------------------------------
            # APPLY
            # ------------------------------------------------

            apply_url = text(
                row,
                "redirect_url",
                "apply_url",
                "job_url",
                "url",
                default=""
            )

            if apply_url:

                st.link_button(
                    "🔗 APPLY FOR THIS JOB",
                    apply_url,
                    use_container_width=True
                )

            else:

                st.info(
                    "Application link unavailable "
                    "in this job record."
                )

    # ========================================================
    # SUMMARY
    # ========================================================

    st.divider()

    st.header("💼 Top Job List")

    summary = []

    for i, row in enumerate(results, 1):

        dist = row.get("_distance")

        score = min(
            num(row.get("final_score", 0)),
            95.0
        )

        summary.append({
            "#": i,
            "Job": text(
                row,
                "job_title",
                "title",
                default="Job"
            ),
            "Company": text(
                row,
                "company",
                "company_name",
                default="Company not provided"
            ),
            "Location": text(
                row,
                "location",
                "address",
                default="Location not provided"
            ),
            "Distance": (
                f"{dist:.2f} km"
                if dist is not None
                else "N/A"
            ),
            "Role Match": (
                f"{num(row.get('role_match', 0)):.1f}%"
            ),
            "Skill Match": (
                f"{num(row.get('skill_match', 0)):.1f}%"
            ),
            "Overall": f"{score:.1f}%"
        })

    st.dataframe(
        pd.DataFrame(summary),
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.caption(
    "SkillBridge AI • Universal Jobs • "
    "Local Matching • GPS • OpenStreetMap • "
    "Leaflet • Skill Recommendations"
)
