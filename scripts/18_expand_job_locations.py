from pathlib import Path
import pandas as pd

# ============================================================
# SKILLBRIDGE AI
# EXPAND LOCAL JOB LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "final_local_jobs.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "location_enabled_jobs.csv"

print("=" * 70)
print("              SKILLBRIDGE AI")
print("          LOCATION ENABLED JOB DATA")
print("=" * 70)

# ------------------------------------------------------------
# Load existing jobs
# ------------------------------------------------------------

print("\nLoading existing jobs...")

df = pd.read_csv(INPUT_FILE)

print(f"Existing jobs: {len(df)}")

# ------------------------------------------------------------
# City information
#
# These are city-center coordinates for the demo/hackathon
# dataset. They are NOT exact employer addresses.
# ------------------------------------------------------------

CITY_DATA = {
    "Chennai": {
        "state": "Tamil Nadu",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "areas": [
            "Anna Nagar",
            "T Nagar",
            "Adyar",
            "Velachery",
            "Guindy"
        ]
    },

    "Madurai": {
        "state": "Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198,
        "areas": [
            "Anna Nagar",
            "KK Nagar",
            "Mattuthavani",
            "Tallakulam",
            "Simmakkal"
        ]
    },

    "Coimbatore": {
        "state": "Tamil Nadu",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "areas": [
            "RS Puram",
            "Gandhipuram",
            "Peelamedu",
            "Saibaba Colony",
            "Singanallur"
        ]
    },

    "Salem": {
        "state": "Tamil Nadu",
        "latitude": 11.6643,
        "longitude": 78.1460,
        "areas": [
            "Fairlands",
            "Hasthampatti",
            "Suramangalam",
            "Ammapet",
            "Swarnapuri"
        ]
    },

    "Tiruchirappalli": {
        "state": "Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047,
        "areas": [
            "Srirangam",
            "Thillai Nagar",
            "Cantonment",
            "Woraiyur",
            "KK Nagar"
        ]
    },

    "Tirunelveli": {
        "state": "Tamil Nadu",
        "latitude": 8.7139,
        "longitude": 77.7567,
        "areas": [
            "Palayamkottai",
            "Vannarpettai",
            "Perumalpuram",
            "Maharaja Nagar",
            "Tirunelveli Junction"
        ]
    },

    "Vellore": {
        "state": "Tamil Nadu",
        "latitude": 12.9165,
        "longitude": 79.1325,
        "areas": [
            "Katpadi",
            "Sathuvachari",
            "Gandhi Nagar",
            "Thorapadi",
            "Bagayam"
        ]
    },

    "Bengaluru": {
        "state": "Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "areas": [
            "Whitefield",
            "Electronic City",
            "Koramangala",
            "Indiranagar",
            "Yelahanka"
        ]
    },

    "Hyderabad": {
        "state": "Telangana",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "areas": [
            "Ameerpet",
            "Madhapur",
            "Kukatpally",
            "Gachibowli",
            "Secunderabad"
        ]
    },

    "Kochi": {
        "state": "Kerala",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "areas": [
            "Edappally",
            "Kakkanad",
            "Vyttila",
            "Kaloor",
            "Fort Kochi"
        ]
    },

    "Thiruvananthapuram": {
        "state": "Kerala",
        "latitude": 8.5241,
        "longitude": 76.9366,
        "areas": [
            "Technopark",
            "Kazhakkoottam",
            "Pattom",
            "Kesavadasapuram",
            "Kowdiar"
        ]
    },

    "Kozhikode": {
        "state": "Kerala",
        "latitude": 11.2588,
        "longitude": 75.7804,
        "areas": [
            "Nadakkavu",
            "Mavoor Road",
            "Kallai",
            "West Hill",
            "Palayam"
        ]
    },

    "Kollam": {
        "state": "Kerala",
        "latitude": 8.8932,
        "longitude": 76.6141,
        "areas": [
            "Chinnakada",
            "Kadappakada",
            "Kottarakkara",
            "Karunagappally",
            "Asramam"
        ]
    }
}

# ------------------------------------------------------------
# Existing job templates
# ------------------------------------------------------------

JOB_TEMPLATES = [
    {
        "job_title": "Data Entry Operator",
        "skills": "MS Excel, MS Office, Data Entry, English Communication",
        "salary": "₹15,000 - ₹22,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "Computer Operator",
        "skills": "MS Office, Excel, Computer Operations, Communication",
        "salary": "₹16,000 - ₹24,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "Customer Support Executive",
        "skills": "Communication, Customer Service, English, Problem Solving",
        "salary": "₹18,000 - ₹28,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "Sales Executive",
        "skills": "Sales, Communication, Customer Service, Negotiation",
        "salary": "₹18,000 - ₹30,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "Office Assistant",
        "skills": "MS Office, Excel, Data Entry, Communication",
        "salary": "₹15,000 - ₹23,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "Account Assistant",
        "skills": "Accounting, Tally, Excel, MS Office",
        "salary": "₹20,000 - ₹32,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Junior Accountant",
        "skills": "Accounting, Tally, GST, Excel, Bookkeeping",
        "salary": "₹22,000 - ₹35,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Digital Marketing Executive",
        "skills": "Digital Marketing, SEO, Social Media, Communication, Content Writing",
        "salary": "₹20,000 - ₹35,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Teacher",
        "skills": "Teaching, Communication, Mathematics, Classroom Management",
        "salary": "₹18,000 - ₹30,000",
        "employment_type": "Full-time",
        "experience_years": 0
    },

    {
        "job_title": "IT Support Technician",
        "skills": "Computer Hardware, Networking, Troubleshooting, Windows",
        "salary": "₹22,000 - ₹38,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Python Developer",
        "skills": "Python, SQL, Flask, Git, Communication",
        "salary": "₹30,000 - ₹60,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Web Developer",
        "skills": "HTML, CSS, JavaScript, React, Git",
        "salary": "₹25,000 - ₹50,000",
        "employment_type": "Full-time",
        "experience_years": 1
    },

    {
        "job_title": "Graphic Designer",
        "skills": "Graphic Design, Photoshop, Illustrator, Creativity",
        "salary": "₹20,000 - ₹40,000",
        "employment_type": "Full-time",
        "experience_years": 1
    }
]

# ------------------------------------------------------------
# Company names
# ------------------------------------------------------------

COMPANY_PREFIXES = [
    "Community",
    "Local",
    "City",
    "Regional",
    "SkillBridge"
]

COMPANY_SUFFIXES = [
    "Services",
    "Solutions",
    "Center",
    "Technologies",
    "Business Hub",
    "Employment Services"
]

# ------------------------------------------------------------
# Build expanded dataset
# ------------------------------------------------------------

rows = []

job_counter = 1

for city, city_info in CITY_DATA.items():

    for job_index, template in enumerate(JOB_TEMPLATES):

        area = city_info["areas"][job_index % len(city_info["areas"])]

        prefix = COMPANY_PREFIXES[job_index % len(COMPANY_PREFIXES)]
        suffix = COMPANY_SUFFIXES[job_index % len(COMPANY_SUFFIXES)]

        company = f"{prefix} {template['job_title'].replace(' ', '')} {suffix}"

        # Demo address.
        # Clearly label this as a dataset/demo location rather
        # than claiming it is a verified employer address.
        address = (
            f"{area}, {city}, "
            f"{city_info['state']}, India"
        )

        rows.append({
            "job_id": f"LOC{job_counter:04d}",
            "job_title": template["job_title"],
            "company": company,
            "location": city,
            "address": address,
            "latitude": city_info["latitude"],
            "longitude": city_info["longitude"],
            "skills": template["skills"],
            "salary": template["salary"],
            "employment_type": template["employment_type"],
            "experience_years": template["experience_years"],
            "community_need": "Local employment opportunity",
            "local_job": True
        })

        job_counter += 1

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

expanded_df = pd.DataFrame(rows)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

expanded_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 70)
print("LOCATION DATASET CREATED")
print("=" * 70)

print(f"\nTotal jobs: {len(expanded_df)}")
print(f"Total cities: {expanded_df['location'].nunique()}")

print("\nLocations available:")

for city in sorted(expanded_df["location"].unique()):
    count = (
        expanded_df["location"] == city
    ).sum()

    print(f"  ✓ {city}: {count} jobs")

print("\nColumns:")
for column in expanded_df.columns:
    print(f"  ✓ {column}")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nIMPORTANT:")
print("These are demo/hackathon job records.")
print("The addresses are location examples, not verified employer addresses.")

print("\nNext stage:")
print("GPS + distance-based local job matching")
