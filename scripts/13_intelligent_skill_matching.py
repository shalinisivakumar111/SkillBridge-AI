import pandas as pd
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher


# ============================================================
# SKILLBRIDGE AI
# INTELLIGENT OFFLINE SKILL MATCHING
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CANDIDATE_SKILLS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "candidate_skills.csv"
)

LOCAL_JOBS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_local_jobs.csv"
)

ESCO_SKILLS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "skill_dictionary.csv"
)

ESCO_RELATIONS = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "esco",
    "skillSkillRelations_en.csv"
)

OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "intelligent_job_recommendations.csv"
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

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
# LOAD DATA
# ============================================================

def load_data():

    print("\nLoading candidate skills...")

    candidate_df = pd.read_csv(
        CANDIDATE_SKILLS
    )

    candidate_skills = []

    for skill in candidate_df["skill"].dropna():

        skill = clean_text(skill)

        if skill:
            candidate_skills.append(skill)

    candidate_skills = list(
        dict.fromkeys(candidate_skills)
    )

    print(
        f"Candidate skills: {len(candidate_skills)}"
    )

    print("\nLoading local jobs...")

    jobs = pd.read_csv(
        LOCAL_JOBS
    )

    print(
        f"Local jobs loaded: {len(jobs)}"
    )

    print("\nLoading ESCO skill dictionary...")

    esco_skills = pd.read_csv(
        ESCO_SKILLS
    )

    print(
        f"ESCO skills loaded: {len(esco_skills):,}"
    )

    print("\nLoading ESCO skill relationships...")

    relations = pd.read_csv(
        ESCO_RELATIONS
    )

    print(
        f"ESCO relationships loaded: {len(relations):,}"
    )

    return (
        candidate_skills,
        jobs,
        esco_skills,
        relations
    )


# ============================================================
# BUILD ESCO INDEX
# ============================================================

def build_skill_index(esco_skills):

    print("\nBuilding ESCO skill index...")

    skill_to_uri = {}

    uri_to_skill = {}

    alias_to_uri = {}

    for _, row in esco_skills.iterrows():

        uri = str(
            row.get("skill_id", "")
        ).strip()

        skill = clean_text(
            row.get("skill", "")
        )

        aliases = clean_text(
            row.get("aliases", "")
        )

        if not uri or not skill:
            continue

        skill_to_uri[skill] = uri

        uri_to_skill[uri] = skill

        if aliases:

            for alias in aliases.split():

                alias = clean_text(alias)

                if alias:
                    alias_to_uri[alias] = uri

    print(
        f"Indexed ESCO skills: {len(uri_to_skill):,}"
    )

    return (
        skill_to_uri,
        uri_to_skill,
        alias_to_uri
    )


# ============================================================
# FIND BEST ESCO SKILL
# ============================================================

def find_skill_uri(
    skill,
    skill_to_uri,
    uri_to_skill
):

    skill = clean_text(skill)

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if skill in skill_to_uri:

        return skill_to_uri[skill]

    # --------------------------------------------------------
    # Word-based matching
    # --------------------------------------------------------

    best_uri = None
    best_score = 0

    for uri, esco_skill in uri_to_skill.items():

        if not esco_skill:
            continue

        score = SequenceMatcher(
            None,
            skill,
            esco_skill
        ).ratio()

        if score > best_score:

            best_score = score
            best_uri = uri

    # Only accept reasonably similar skills
    if best_score >= 0.75:

        return best_uri

    return None


# ============================================================
# BUILD RELATED SKILL GRAPH
# ============================================================

def build_relation_graph(relations):

    print("\nBuilding ESCO skill relationship graph...")

    graph = defaultdict(set)

    for _, row in relations.iterrows():

        original = str(
            row["originalSkillUri"]
        ).strip()

        related = str(
            row["relatedSkillUri"]
        ).strip()

        if not original or not related:
            continue

        graph[original].add(
            related
        )

        # Make relationship bidirectional
        graph[related].add(
            original
        )

    print(
        f"Skills with relationships: {len(graph):,}"
    )

    return graph


# ============================================================
# TOKENIZE JOB SKILLS
# ============================================================

def extract_job_skills(job_skill_text):

    if pd.isna(job_skill_text):

        return []

    text = str(
        job_skill_text
    )

    # Common separators
    text = text.replace(
        ";",
        ","
    )

    text = text.replace(
        "|",
        ","
    )

    # --------------------------------------------------------
    # Try comma-separated skills
    # --------------------------------------------------------

    parts = text.split(",")

    skills = []

    for part in parts:

        part = clean_text(part)

        if part:

            skills.append(part)

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    skills = list(
        dict.fromkeys(skills)
    )

    return skills


# ============================================================
# SKILL MATCH
# ============================================================

def compare_skill(
    candidate_skill,
    job_skill,
    candidate_uri,
    job_uri,
    relation_graph
):

    candidate_skill = clean_text(
        candidate_skill
    )

    job_skill = clean_text(
        job_skill
    )

    # ========================================================
    # LEVEL 1 — EXACT MATCH
    # ========================================================

    if candidate_skill == job_skill:

        return 1.0, "exact"

    # ========================================================
    # LEVEL 2 — ESCO RELATED SKILL
    # ========================================================

    if candidate_uri and job_uri:

        related = relation_graph.get(
            candidate_uri,
            set()
        )

        if job_uri in related:

            return 0.6, "esco_related"

    # ========================================================
    # LEVEL 3 — TEXT SIMILARITY
    # ========================================================

    similarity = SequenceMatcher(
        None,
        candidate_skill,
        job_skill
    ).ratio()

    if similarity >= 0.80:

        return 0.5, "text_similar"

    if similarity >= 0.65:

        return 0.3, "partial"

    # ========================================================
    # LEVEL 4 — WORD OVERLAP
    # ========================================================

    candidate_words = set(
        candidate_skill.split()
    )

    job_words = set(
        job_skill.split()
    )

    if candidate_words and job_words:

        overlap = (
            len(
                candidate_words
                & job_words
            )
            /
            len(
                candidate_words
                | job_words
            )
        )

        if overlap >= 0.5:

            return 0.3, "word_overlap"

    return 0.0, ""


# ============================================================
# MATCH JOB
# ============================================================

def match_job(
    candidate_skills,
    job_skills,
    candidate_uri_map,
    job_uri_map,
    relation_graph
):

    if not job_skills:

        return (
            0,
            [],
            []
        )

    total_score = 0

    matched_skills = []

    match_types = []

    for candidate_skill in candidate_skills:

        best_score = 0
        best_job_skill = None
        best_type = ""

        candidate_uri = (
            candidate_uri_map.get(
                candidate_skill
            )
        )

        for job_skill in job_skills:

            job_uri = (
                job_uri_map.get(
                    job_skill
                )
            )

            score, match_type = compare_skill(
                candidate_skill,
                job_skill,
                candidate_uri,
                job_uri,
                relation_graph
            )

            if score > best_score:

                best_score = score
                best_job_skill = job_skill
                best_type = match_type

        if best_score > 0:

            total_score += best_score

            matched_skills.append(
                f"{candidate_skill} → {best_job_skill}"
            )

            match_types.append(
                best_type
            )

    # --------------------------------------------------------
    # Normalize score
    # --------------------------------------------------------

    score = (
        total_score
        /
        len(candidate_skills)
    )

    return (
        score,
        matched_skills,
        match_types
    )


# ============================================================
# LOCAL BONUS
# ============================================================

def calculate_local_bonus(
    candidate_location,
    job_location
):

    candidate_location = clean_text(
        candidate_location
    )

    job_location = clean_text(
        job_location
    )

    if not candidate_location:
        return 0

    if not job_location:
        return 0

    # --------------------------------------------------------
    # Location keyword matching
    # --------------------------------------------------------

    candidate_words = set(
        candidate_location.split()
    )

    job_words = set(
        job_location.split()
    )

    if candidate_words & job_words:

        return 0.10

    return 0


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "              SKILLBRIDGE AI"
    )

    print(
        "       INTELLIGENT OFFLINE MATCHING"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    (
        candidate_skills,
        jobs,
        esco_skills,
        relations
    ) = load_data()

    # --------------------------------------------------------
    # Build ESCO indexes
    # --------------------------------------------------------

    (
        skill_to_uri,
        uri_to_skill,
        alias_to_uri
    ) = build_skill_index(
        esco_skills
    )

    relation_graph = build_relation_graph(
        relations
    )

    # --------------------------------------------------------
    # Map candidate skills to ESCO
    # --------------------------------------------------------

    candidate_uri_map = {}

    print(
        "\nMapping candidate skills to ESCO..."
    )

    for skill in candidate_skills:

        uri = find_skill_uri(
            skill,
            skill_to_uri,
            uri_to_skill
        )

        candidate_uri_map[
            skill
        ] = uri

        if uri:

            print(
                f"  ✓ {skill}"
            )

        else:

            print(
                f"  ⚠ {skill} → no ESCO match"
            )

    # --------------------------------------------------------
    # Prepare results
    # --------------------------------------------------------

    results = []

    print(
        "\nMatching candidate against local jobs..."
    )

    # --------------------------------------------------------
    # Process each job
    # --------------------------------------------------------

    for _, job in jobs.iterrows():

        job_skills = extract_job_skills(
            job.get(
                "skills",
                ""
            )
        )

        # Map job skills to ESCO
        job_uri_map = {}

        for job_skill in job_skills:

            uri = find_skill_uri(
                job_skill,
                skill_to_uri,
                uri_to_skill
            )

            job_uri_map[
                job_skill
            ] = uri

        # ----------------------------------------------------
        # Skill matching
        # ----------------------------------------------------

        (
            skill_score,
            matched_skills,
            match_types
        ) = match_job(
            candidate_skills,
            job_skills,
            candidate_uri_map,
            job_uri_map,
            relation_graph
        )

        # ----------------------------------------------------
        # Local bonus
        # ----------------------------------------------------

        local_bonus = calculate_local_bonus(
            "Hyderabad",
            job.get(
                "location",
                ""
            )
        )

        # ----------------------------------------------------
        # Final score
        # ----------------------------------------------------

        final_score = (
            skill_score
            +
            local_bonus
        )

        # Don't exceed 100%
        final_score = min(
            final_score,
            1.0
        )

        results.append({

            "job_id":
                job.get(
                    "job_id",
                    ""
                ),

            "job_title":
                job.get(
                    "job_title",
                    ""
                ),

            "company":
                job.get(
                    "company",
                    ""
                ),

            "location":
                job.get(
                    "location",
                    ""
                ),

            "skill_match":
                round(
                    skill_score * 100,
                    2
                ),

            "local_bonus":
                round(
                    local_bonus * 100,
                    2
                ),

            "final_score":
                round(
                    final_score * 100,
                    2
                ),

            "matched_skills":
                "; ".join(
                    matched_skills
                ),

            "match_types":
                "; ".join(
                    match_types
                ),

            "job_skills":
                "; ".join(
                    job_skills
                )
        })

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort by final score
    # --------------------------------------------------------

    results_df.sort_values(
        by="final_score",
        ascending=False,
        inplace=True
    )

    results_df.reset_index(
        drop=True,
        inplace=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(
            OUTPUT
        ),
        exist_ok=True
    )

    results_df.to_csv(
        OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)

    print(
        "          INTELLIGENT MATCH RESULTS"
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
            f"{row['skill_match']}%"
        )

        print(
            f"   Local Bonus: "
            f"+{row['local_bonus']}%"
        )

        print(
            f"   Final Score: "
            f"{row['final_score']}%"
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
        "✅ INTELLIGENT SKILL MATCHING COMPLETE"
    )

    print("=" * 70)

    print(
        f"\nSaved to:"
    )

    print(
        OUTPUT
    )


if __name__ == "__main__":

    main()