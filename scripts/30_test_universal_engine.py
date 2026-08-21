import sys
from pathlib import Path

# Add project root so Python can find src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.universal_engine import recommend_jobs


JOBS_FILE = PROJECT_ROOT / "data" / "jobs" / "universal_jobs.csv"


def print_results(title, results):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    if not results:
        print("NO MATCHING JOBS FOUND")
        return

    for i, job in enumerate(results, 1):
        print(
            f"{i}. {job.get('job_title', 'Unknown Job')} | "
            f"{job.get('company', 'Company not provided')} | "
            f"Role={job.get('role_match', 0)}% | "
            f"Skills={job.get('skill_match', 0)}% | "
            f"Distance={job.get('distance_km', 0)} km | "
            f"Final={job.get('final_score', 0)}%"
        )


def main():

    print("=" * 70)
    print("              SKILLBRIDGE AI")
    print("       UNIVERSAL JOB MATCHING TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # LOAD JOBS
    # ------------------------------------------------------------

    jobs = pd.read_csv(JOBS_FILE)

    print(f"\nJobs loaded: {len(jobs)}")

    print("\nAvailable job families:")
    print(jobs["job_family"].value_counts().to_string())

    # ------------------------------------------------------------
    # DOCTOR
    # ------------------------------------------------------------

    doctor_skills = [
        "MBBS",
        "MD",
        "Diagnosis",
        "Patient Care",
        "BLS",
        "Communication",
    ]

    doctor_results = recommend_jobs(
        jobs,
        doctor_skills,
        12.9165,
        79.1325,
        requested_role="Doctor",
        limit=10,
    )

    print_results("DOCTOR TEST", doctor_results)

    # ------------------------------------------------------------
    # TEACHER
    # ------------------------------------------------------------

    teacher_skills = [
        "Teaching",
        "Communication",
        "Lesson Planning",
        "Classroom Management",
    ]

    teacher_results = recommend_jobs(
        jobs,
        teacher_skills,
        12.9165,
        79.1325,
        requested_role="Teacher",
        limit=10,
    )

    print_results("TEACHER TEST", teacher_results)

    # ------------------------------------------------------------
    # ELECTRICIAN
    # ------------------------------------------------------------

    electrician_skills = [
        "Electrical Wiring",
        "Maintenance",
        "Repair",
        "Electrical Safety",
    ]

    electrician_results = recommend_jobs(
        jobs,
        electrician_skills,
        12.9165,
        79.1325,
        requested_role="Electrician",
        limit=10,
    )

    print_results("ELECTRICIAN TEST", electrician_results)

    # ------------------------------------------------------------
    # ACCOUNTANT
    # ------------------------------------------------------------

    accountant_skills = [
        "Accounting",
        "Excel",
        "Bookkeeping",
        "Financial Reporting",
    ]

    accountant_results = recommend_jobs(
        jobs,
        accountant_skills,
        12.9165,
        79.1325,
        requested_role="Accountant",
        limit=10,
    )

    print_results("ACCOUNTANT TEST", accountant_results)

    # ------------------------------------------------------------
    # SOFTWARE DEVELOPER
    # ------------------------------------------------------------

    developer_skills = [
        "Python",
        "JavaScript",
        "Programming",
        "Software Development",
    ]

    developer_results = recommend_jobs(
        jobs,
        developer_skills,
        12.9165,
        79.1325,
        requested_role="Software Developer",
        limit=10,
    )

    print_results("SOFTWARE DEVELOPER TEST", developer_results)

    # ------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("UNIVERSAL ENGINE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
