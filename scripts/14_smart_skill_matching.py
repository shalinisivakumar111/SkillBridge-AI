import os
import re
import pandas as pd


# ============================================================
# SKILLBRIDGE AI
# INTELLIGENT LOCAL EMPLOYMENT MATCHING
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CANDIDATE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "candidate_skills.csv"
)

JOBS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_local_jobs.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "smart_job_recommendations.csv"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text):

    if pd.isna(text):
        return ""

    text = str(text).lower().strip()

    text = text.replace("&", " and ")

    text = re.sub(
        r"[^a-z0-9+#.\- ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SKILL ALIASES
#
# These represent essentially equivalent skills.
# ============================================================

ALIASES = {

    "ms office": {
        "ms office",
        "microsoft office",
        "office"
    },

    "excel": {
        "excel",
        "ms excel",
        "microsoft excel"
    },

    "data entry": {
        "data entry",
        "data input"
    },

    "customer service": {
        "customer service",
        "customer support",
        "client service"
    },

    "communication": {
        "communication",
        "english communication",
        "communication skills",
        "effective communication"
    },

    "problem solving": {
        "problem solving",
        "problem-solving"
    },

    "python": {
        "python",
        "python programming"
    },

    "sql": {
        "sql",
        "sql programming"
    },

    "git": {
        "git",
        "git version control"
    },

    "graphic design": {
        "graphic design",
        "graphics design"
    },

    "photoshop": {
        "photoshop",
        "adobe photoshop"
    },

    "illustrator": {
        "illustrator",
        "adobe illustrator"
    },

    "accounting": {
        "accounting",
        "accountancy"
    },

    "bookkeeping": {
        "bookkeeping",
        "book keeping"
    },

    "tally": {
        "tally",
        "tally erp",
        "tally prime"
    },

    "digital marketing": {
        "digital marketing",
        "online marketing"
    },

    "social media": {
        "social media",
        "social media management"
    },

    "networking": {
        "networking",
        "computer networking"
    },

    "computer hardware": {
        "computer hardware",
        "hardware"
    },

    "troubleshooting": {
        "troubleshooting",
        "technical troubleshooting"
    },

    "mobile repair": {
        "mobile repair",
        "mobile phone repair",
        "smartphone repair"
    }
}


# ============================================================
# STRONG RELATED SKILLS
# ============================================================

RELATED_SKILLS = {

    # Office jobs
    "office administration": {
        "ms office",
        "excel",
        "data entry"
    },

    "ms office": {
        "office administration",
        "excel",
        "data entry"
    },

    "excel": {
        "office administration",
        "ms office",
        "data entry"
    },

    "data entry": {
        "office administration",
        "ms office",
        "excel"
    },

    # Customer-facing jobs
    "customer service": {
        "communication",
        "sales"
    },

    "sales": {
        "customer service",
        "communication",
        "negotiation"
    },

    "communication": {
        "customer service",
        "sales"
    },

    # Accounting
    "accounting": {
        "bookkeeping",
        "tally",
        "excel"
    },

    "bookkeeping": {
        "accounting",
        "tally",
        "excel"
    },

    "tally": {
        "accounting",
        "bookkeeping",
        "excel"
    },

    # Technical support
    "networking": {
        "computer hardware",
        "troubleshooting"
    },

    "computer hardware": {
        "networking",
        "troubleshooting"
    },

    "troubleshooting": {
        "computer hardware",
        "networking"
    },

    # Design
    "graphic design": {
        "photoshop",
        "illustrator"
    },

    "photoshop": {
        "graphic design",
        "illustrator"
    },

    "illustrator": {
        "graphic design",
        "photoshop"
    }
}


# ============================================================
# GENERIC SKILLS
#
# These are useful but should never dominate the ranking.
# ============================================================

GENERIC_SKILLS = {

    "communication",
    "problem solving",
    "creativity",
    "teamwork",
    "english"
}


# ============================================================
# LANGUAGE SKILLS
#
# Languages only match themselves.
# ============================================================

LANGUAGE_SKILLS = {

    "telugu",
    "hindi",
    "english",
    "tamil",
    "kannada",
    "malayalam",
    "marathi",
    "bengali",
    "urdu"
}


# ============================================================
# ALIAS LOOKUP
# ============================================================

def build_alias_lookup():

    lookup = {}

    for canonical, aliases in ALIASES.items():

        canonical = normalize(canonical)

        lookup[canonical] = canonical

        for alias in aliases:

            lookup[
                normalize(alias)
            ] = canonical

    return lookup


ALIAS_LOOKUP = build_alias_lookup()


# ============================================================
# CANONICAL SKILL
# ============================================================

def canonical_skill(skill):

    skill = normalize(skill)

    if not skill:
        return ""

    return ALIAS_LOOKUP.get(
        skill,
        skill
    )


# ============================================================
# PARSE SKILL LIST
# ============================================================

def parse_skills(value):

    if pd.isna(value):
        return []

    text = str(value)

    text = text.replace(
        "|",
        ","
    )

    text = text.replace(
        ";",
        ","
    )

    text = text.replace(
        "\n",
        ","
    )

    parts = text.split(",")

    skills = []

    for part in parts:

        skill = canonical_skill(part)

        if skill:
            skills.append(skill)

    return list(
        dict.fromkeys(skills)
    )


# ============================================================
# LANGUAGE CHECK
# ============================================================

def is_language(skill):

    skill = canonical_skill(skill)

    return skill in LANGUAGE_SKILLS


# ============================================================
# FIND MATCH
#
# Returns:
#
# 1.00 = exact
# 0.90 = equivalent
# 0.60 = strong related
# 0.15 = generic supporting skill
# 0.00 = no match
# ============================================================

def find_match(
    candidate_skill,
    job_skill
):

    candidate = canonical_skill(
        candidate_skill
    )

    job = canonical_skill(
        job_skill
    )

    if not candidate or not job:

        return 0.0, "none"


    # --------------------------------------------------------
    # EXACT
    # --------------------------------------------------------

    if candidate == job:

        return 1.00, "exact"


    # --------------------------------------------------------
    # LANGUAGE SAFETY
    #
    # Telugu should not match customer service.
    # Hindi should not match communication.
    # --------------------------------------------------------

    if (
        is_language(candidate)
        or is_language(job)
    ):

        return 0.0, "none"


    # --------------------------------------------------------
    # ALIAS / EQUIVALENT
    #
    # Same canonical concept.
    # --------------------------------------------------------

    candidate_aliases = ALIASES.get(
        candidate,
        set()
    )

    job_aliases = ALIASES.get(
        job,
        set()
    )

    if (
        candidate in job_aliases
        or job in candidate_aliases
    ):

        return 0.90, "equivalent"


    # --------------------------------------------------------
    # STRONG RELATED
    # --------------------------------------------------------

    candidate_related = {
        canonical_skill(x)
        for x in RELATED_SKILLS.get(
            candidate,
            set()
        )
    }

    if job in candidate_related:

        return 0.60, "related"


    job_related = {
        canonical_skill(x)
        for x in RELATED_SKILLS.get(
            job,
            set()
        )
    }

    if candidate in job_related:

        return 0.60, "related"


    # --------------------------------------------------------
    # GENERIC SUPPORT
    #
    # Generic skills receive only a small contribution.
    # --------------------------------------------------------

    if candidate in GENERIC_SKILLS:

        if job in GENERIC_SKILLS:

            return 0.15, "supporting"


    if job in GENERIC_SKILLS:

        if candidate in RELATED_SKILLS:

            return 0.15, "supporting"


    return 0.0, "none"


# ============================================================
# MATCH JOB
# ============================================================

def match_job(
    candidate_skills,
    job_skills
):

    if not job_skills:

        return {
            "score": 0.0,
            "matched": [],
            "types": []
        }


    total = 0.0

    matched = []

    types = []


    # --------------------------------------------------------
    # Every job requirement is evaluated.
    # --------------------------------------------------------

    for job_skill in job_skills:

        best_score = 0.0

        best_candidate = None

        best_type = "none"


        for candidate_skill in candidate_skills:

            score, match_type = find_match(
                candidate_skill,
                job_skill
            )

            if score > best_score:

                best_score = score

                best_candidate = candidate_skill

                best_type = match_type


        if best_score > 0:

            total += best_score

            matched.append(
                f"{best_candidate} → {job_skill}"
            )

            types.append(
                best_type
            )


    # --------------------------------------------------------
    # JOB REQUIREMENT COVERAGE
    # --------------------------------------------------------

    job_coverage = (
        total / len(job_skills)
    )


    # --------------------------------------------------------
    # CANDIDATE COVERAGE
    # --------------------------------------------------------

    candidate_matched = 0


    for candidate_skill in candidate_skills:

        found = False

        for job_skill in job_skills:

            score, _ = find_match(
                candidate_skill,
                job_skill
            )

            if score > 0:

                found = True

                break


        if found:

            candidate_matched += 1


    candidate_coverage = (

        candidate_matched /
        len(candidate_skills)

        if candidate_skills

        else 0
    )


    # --------------------------------------------------------
    # FINAL SKILL SCORE
    #
    # Job coverage is more important.
    # --------------------------------------------------------

    skill_score = (

        job_coverage * 0.80

        +

        candidate_coverage * 0.20
    )


    return {

        "score":
            skill_score * 100,

        "matched":
            matched,

        "types":
            types
    }


# ============================================================
# LOCATION BONUS
# ============================================================

def calculate_local_bonus(
    candidate_location,
    job_location
):

    candidate_location = normalize(
        candidate_location
    )

    job_location = normalize(
        job_location
    )


    # Hyderabad / Secunderabad
    if (
        "hyderabad" in job_location
        or "secunderabad" in job_location
    ):

        return 5.0


    # Remote jobs
    if (
        "work from home" in job_location
        or "remote" in job_location
    ):

        return 3.0


    return 0.0


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "              SKILLBRIDGE AI"
    )

    print(
        "      INTELLIGENT LOCAL EMPLOYMENT"
    )

    print(
        "             MATCHING ENGINE"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # Candidate
    # --------------------------------------------------------

    print(
        "\nLoading candidate skills..."
    )


    if not os.path.exists(
        CANDIDATE_FILE
    ):

        print(
            "❌ candidate_skills.csv not found"
        )

        return


    candidate_df = pd.read_csv(
        CANDIDATE_FILE
    )


    if "skill" not in candidate_df.columns:

        print(
            "❌ skill column missing"
        )

        print(
            candidate_df.columns.tolist()
        )

        return


    candidate_skills = [

        canonical_skill(skill)

        for skill
        in candidate_df["skill"].dropna()

    ]


    candidate_skills = list(
        dict.fromkeys(
            x
            for x in candidate_skills
            if x
        )
    )


    print(
        f"Candidate skills: "
        f"{len(candidate_skills)}"
    )


    for skill in candidate_skills:

        print(
            f"  ✓ {skill}"
        )


    # --------------------------------------------------------
    # Jobs
    # --------------------------------------------------------

    print(
        "\nLoading local jobs..."
    )


    if not os.path.exists(
        JOBS_FILE
    ):

        print(
            "❌ final_local_jobs.csv not found"
        )

        return


    jobs = pd.read_csv(
        JOBS_FILE
    )


    print(
        f"Local jobs: {len(jobs)}"
    )


    required_columns = [

        "job_id",
        "job_title",
        "company",
        "location",
        "skills"

    ]


    missing = [

        column

        for column
        in required_columns

        if column not in jobs.columns

    ]


    if missing:

        print(
            f"❌ Missing columns: "
            f"{missing}"
        )

        return


    # --------------------------------------------------------
    # Candidate location
    # --------------------------------------------------------

    candidate_location = "Hyderabad"


    print(
        "\nCandidate location: "
        f"{candidate_location}"
    )


    print(
        "\nFinding intelligent local matches..."
    )


    results = []


    # --------------------------------------------------------
    # Match every job
    # --------------------------------------------------------

    for _, job in jobs.iterrows():


        job_skills = parse_skills(
            job["skills"]
        )


        match = match_job(

            candidate_skills,

            job_skills

        )


        skill_score = match[
            "score"
        ]


        local_bonus = calculate_local_bonus(

            candidate_location,

            job["location"]

        )


        final_score = min(

            skill_score
            +
            local_bonus,

            100.0

        )


        results.append({

            "job_id":
                job["job_id"],

            "job_title":
                job["job_title"],

            "company":
                job["company"],

            "location":
                job["location"],

            "skill_match":
                round(
                    skill_score,
                    2
                ),

            "local_bonus":
                local_bonus,

            "final_score":
                round(
                    final_score,
                    2
                ),

            "matched_skills":
                "; ".join(
                    match["matched"]
                ),

            "match_types":
                "; ".join(
                    match["types"]
                )

        })


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )


    results_df.sort_values(

        by=[
            "final_score",
            "skill_match"
        ],

        ascending=False,

        inplace=True

    )


    results_df.reset_index(
        drop=True,
        inplace=True
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    os.makedirs(

        os.path.dirname(
            OUTPUT_FILE
        ),

        exist_ok=True

    )


    results_df.to_csv(

        OUTPUT_FILE,

        index=False

    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\n")

    print("=" * 70)

    print(
        "           TOP SMART LOCAL JOBS"
    )

    print("=" * 70)


    for index, row in results_df.head(10).iterrows():


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
            f"{row['skill_match']:.1f}%"
        )


        print(
            f"   Local Bonus: "
            f"+{row['local_bonus']:.1f}%"
        )


        print(
            f"   Final Score: "
            f"{row['final_score']:.1f}%"
        )


        print(
            f"   Matched Skills: "
            f"{row['matched_skills']}"
        )


        print(
            f"   Match Type: "
            f"{row['match_types']}"
        )


    print("\n")

    print("=" * 70)

    print(
        "✅ INTELLIGENT LOCAL MATCHING COMPLETE"
    )

    print("=" * 70)


    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":

    main()