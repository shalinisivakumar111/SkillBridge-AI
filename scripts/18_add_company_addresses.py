import pandas as pd
from pathlib import Path

print("=" * 70)
print("              SKILLBRIDGE AI")
print("        ADD COMPANY ADDRESS DATA")
print("=" * 70)

INPUT_FILE = Path("data/processed/final_local_jobs.csv")
OUTPUT_FILE = Path("data/processed/final_local_jobs.csv")

df = pd.read_csv(INPUT_FILE)

# Demo/hackathon addresses.
# These describe the dataset location only and are NOT claimed
# to be real street addresses.
addresses = {
    "L001": "Secunderabad, Telangana",
    "L002": "Hyderabad, Telangana",
    "L003": "Hyderabad, Telangana",
    "L004": "Secunderabad, Telangana",
    "L005": "Hyderabad, Telangana",
    "L006": "Hyderabad, Telangana",
    "L007": "Secunderabad, Telangana",
    "L008": "Hyderabad, Telangana",
    "L009": "Secunderabad, Telangana",
    "L010": "Hyderabad, Telangana",
    "L011": "Secunderabad, Telangana",
    "L012": "Hyderabad, Telangana",
    "L013": "Secunderabad, Telangana",
    "L014": "Hyderabad, Telangana",
    "L015": "Secunderabad, Telangana",
}

df["address"] = df["job_id"].map(addresses)

# Fallback if a new job is added later.
df["address"] = df["address"].fillna(
    df["location"].astype(str) + ", Telangana"
)

df.to_csv(OUTPUT_FILE, index=False)

print()
print("Address column added successfully.")
print()
print(df[[
    "job_id",
    "job_title",
    "company",
    "location",
    "address"
]].to_string(index=False))

print()
print("=" * 70)
print("ADDRESS DATA READY")
print("=" * 70)
