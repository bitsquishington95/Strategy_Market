import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

from app.repository.store import Repository


SITUATION_SYNONYMS: Dict[str, List[str]] = {
    "situation:missed_targets": [
        "missed target",
        "missed quota",
        "down quarter",
        "missed goals",
        "underperformed",
        "sales slump",
    ],
    "situation:product_launch_crisis": [
        "launch crisis",
        "product delay",
        "launch failure",
        "recall",
        "bug",
    ],
    "situation:key_employee_resigning": [
        "key employee left",
        "resignation",
        "lost executive",
        "cto left",
    ],
    "situation:board_meeting": ["board meeting", "board update", "board review"],
    "situation:media_interview": ["press interview", "media interview", "pr crisis"],
    "situation:competitive_attack": ["competitor attack", "market threat", "competitive pressure", "market share loss"],
    "situation:talent_management": ["hiring decision", "fire employee", "talent review", "performance review"],
    "situation:strategy_refresh": ["strategy pivot", "business model change", "strategic review", "direction change"],
    "situation:engineering_roadblock": ["technical problem", "engineering challenge", "product delay", "technical debt"],
    "situation:acquisition_opportunity": ["acquisition target", "buy company", "merger opportunity", "takeover"],
    "situation:market_downturn": ["recession", "market crash", "economic crisis", "industry downturn"],
    "situation:values_conflict": ["ethical dilemma", "values clash", "principle conflict", "moral question"],
}

PROFILE_SYNONYMS: Dict[str, Tuple[str, str]] = {
    # query token -> (pillar, field)
    "hiring": ("leadership", "hiring_philosophy"),
    "recruit": ("leadership", "hiring_philosophy"),
    "culture": ("leadership", "cultural_architecture"),
    "motivate": ("leadership", "motivation_incentives"),
    "communicat": ("leadership", "communication_style"),
    "meeting": ("operational_cadence", "meeting_culture"),
    "decision": ("operational_cadence", "decision_making_process"),
    "metric": ("operational_cadence", "key_metrics"),
    "priorit": ("operational_cadence", "focus_prioritization"),
    "accountab": ("operational_cadence", "accountability_framework"),
    "risk": ("strategic_philosophy", "risk_profile"),
    "competi": ("strategic_philosophy", "competitive_stance"),
    "innov": ("strategic_philosophy", "innovation_engine"),
    "position": ("strategic_philosophy", "market_positioning"),
    "principle": ("personal_ethos", "core_principles"),
    "work": ("personal_ethos", "work_ethic"),
    "learn": ("personal_ethos", "learning_adaptability"),
    "resilien": ("personal_ethos", "resilience_mechanism"),
    "talent": ("leadership", "talent_management"),
    "vision": ("strategic_philosophy", "core_ideology"),
    "ideology": ("strategic_philosophy", "core_ideology"),
    "focus": ("operational_cadence", "focus_prioritization"),
    "execution": ("operational_cadence", "decision_making_process"),
    "ethics": ("personal_ethos", "core_principles"),
    "mindset": ("personal_ethos", "core_principles"),
}


def _extract_candidate_tags(query: str) -> List[str]:
    q = query.lower()
    tags: List[str] = []
    for tag, syns in SITUATION_SYNONYMS.items():
        if any(s in q for s in syns):
            tags.append(tag)
    # also allow direct situation:* tokens in the query
    tags.extend([tok for tok in re.findall(r"situation:[\w_-]+", q)])
    return list(dict.fromkeys(tags))


def _profile_fields_from_query(query: str) -> List[Tuple[str, str]]:
    q = query.lower()
    fields: List[Tuple[str, str]] = []
    for hint, (pillar, field) in PROFILE_SYNONYMS.items():
        if hint in q:
            fields.append((pillar, field))
    return list(dict.fromkeys(fields))


def fuzzy_match_score(query: str, text: str) -> float:
    """Calculate a fuzzy match score between query and text."""
    if not query or not text:
        return 0.0
    
    # Convert to lowercase for case-insensitive matching
    query = query.lower()
    text = text.lower()
    
    # Check for exact matches first
    if query in text:
        return 1.0
    
    # Split query into words and check for word matches
    query_words = set(query.split())
    text_words = set(text.split())
    word_overlap = query_words.intersection(text_words)
    
    if word_overlap:
        word_score = len(word_overlap) / len(query_words)
        return min(0.8, word_score)  # Cap at 0.8 for word-level matches
    
    # Fall back to sequence matching for partial matches
    return SequenceMatcher(None, query, text).ratio() * 0.5  # Scale down sequence matches


def answer_query(
    query: str,
    repo: Repository,
    ceo_filters: Optional[List[str]] = None,
    top_k: int = 3,
) -> List[Dict]:
    tags = _extract_candidate_tags(query)
    field_hints = _profile_fields_from_query(query)

    candidates: Dict[str, Dict] = defaultdict(lambda: {"score": 0, "evidence": []})

    # Situational evidence
    if tags:
        situations = repo.query_by_situation(" ".join(tags))
        for ceo_name, items in situations.items():
            if ceo_filters and ceo_name not in ceo_filters:
                continue
            for item in items:
                # score by tag overlap size
                overlap = sum(1 for t in item.get("tags", []) if t in tags)
                candidates[ceo_name]["score"] += 3 * overlap
                candidates[ceo_name]["evidence"].append(
                    {
                        "type": "situation",
                        "title": item.get("title"),
                        "response": item.get("response"),
                        "tags": item.get("tags", []),
                    }
                )

    # Profile evidence
    for ceo_name in repo.list_ceo_names():
        if ceo_filters and ceo_name not in ceo_filters:
            continue
        prof = repo.get_ceo(ceo_name) or {}
        for pillar, field in field_hints:
            value = ((prof.get(pillar) or {}).get(field) or "").strip()
            if value:
                candidates[ceo_name]["score"] += 2
                candidates[ceo_name]["evidence"].append(
                    {"type": "profile", "pillar": pillar, "field": field, "value": value}
                )

    # Apply fuzzy matching to all CEO profiles for better recall
    if query:
        for ceo_name in repo.list_ceo_names():
            if ceo_filters and ceo_name not in ceo_filters:
                continue
            prof = repo.get_ceo(ceo_name) or {}
            
            # Check core ideology and principles with fuzzy matching
            core_ideology = ((prof.get("strategic_philosophy") or {}).get("core_ideology") or "").strip()
            if core_ideology:
                match_score = fuzzy_match_score(query, core_ideology)
                if match_score > 0.3:  # Threshold to avoid weak matches
                    candidates[ceo_name]["score"] += match_score * 3
                    candidates[ceo_name]["evidence"].append(
                        {
                            "type": "profile",
                            "pillar": "strategic_philosophy",
                            "field": "core_ideology",
                            "value": core_ideology,
                            "match_score": match_score,
                        }
                    )
            
            core_principles = ((prof.get("personal_ethos") or {}).get("core_principles") or "").strip()
            if core_principles:
                match_score = fuzzy_match_score(query, core_principles)
                if match_score > 0.3:
                    candidates[ceo_name]["score"] += match_score * 2.5
                    candidates[ceo_name]["evidence"].append(
                        {
                            "type": "profile",
                            "pillar": "personal_ethos",
                            "field": "core_principles",
                            "value": core_principles,
                            "match_score": match_score,
                        }
                    )
            
            # Check all other fields with less weight
            for pillar_name, pillar in prof.items():
                if not isinstance(pillar, dict):
                    continue
                for field_name, value in pillar.items():
                    if not value or not isinstance(value, str):
                        continue
                    if field_name in ["core_ideology", "core_principles"]:
                        continue  # Already processed above
                    
                    match_score = fuzzy_match_score(query, value)
                    if match_score > 0.4:  # Higher threshold for other fields
                        candidates[ceo_name]["score"] += match_score * 1.5
                        candidates[ceo_name]["evidence"].append(
                            {
                                "type": "profile",
                                "pillar": pillar_name,
                                "field": field_name,
                                "value": value,
                                "match_score": match_score,
                            }
                        )

    # If no explicit hints matched, fall back to general strategy and ethos
    if not tags and not field_hints and not any(c["evidence"] for c in candidates.values()):
        for ceo_name in repo.list_ceo_names():
            if ceo_filters and ceo_name not in ceo_filters:
                continue
            prof = repo.get_ceo(ceo_name) or {}
            strat = prof.get("strategic_philosophy", {})
            ethos = prof.get("personal_ethos", {})
            if strat or ethos:
                candidates[ceo_name]["score"] += 1
                if strat:
                    candidates[ceo_name]["evidence"].append(
                        {
                            "type": "profile",
                            "pillar": "strategic_philosophy",
                            "field": "core_ideology",
                            "value": strat.get("core_ideology", ""),
                        }
                    )
                if ethos:
                    candidates[ceo_name]["evidence"].append(
                        {
                            "type": "profile",
                            "pillar": "personal_ethos",
                            "field": "core_principles",
                            "value": ethos.get("core_principles", ""),
                        }
                    )

    # Rank
    ranked = sorted(
        ({"ceo": n, **v} for n, v in candidates.items()), key=lambda x: x["score"], reverse=True
    )
    return ranked[:top_k]


def format_answers(results: List[Dict]) -> str:
    if not results:
        return "No matching evidence found. Try rephrasing or add situation:* tags."
    lines: List[str] = []
    for item in results:
        ceo = item["ceo"]
        lines.append(f"{ceo} might:")
        # Prefer situational evidence first
        for ev in item["evidence"]:
            if ev["type"] == "situation":
                lines.append(f"  - {ev['title']}: {ev['response']} ({', '.join(ev.get('tags', []))})")
        # Then add profile-based guidance
        for ev in item["evidence"]:
            if ev["type"] == "profile":
                field_label = ev["field"].replace("_", " ").title()
                lines.append(f"  - {ev['pillar']}.{field_label}: {ev['value']}")
        lines.append("")
    return "\n".join(lines).rstrip()