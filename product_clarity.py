"""Deterministic reference architecture for an adaptive Product Clarity coach.

This is intentionally model-agnostic. A Custom GPT can use the same state,
diagnostic, completion, and output rules while the language model handles the
natural-language conversation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


STAGES = (
    "product_idea",
    "primary_customer",
    "problem",
    "solution",
    "value_proposition",
    "potential_advantage",
    "must_have",
    "nice_to_have",
    "later",
)


QUESTIONS = {
    "product_idea": "In one sentence, what are you trying to create?",
    "primary_customer": "Who is the single primary customer for version 1?",
    "problem": "What specific recurring problem does that customer face today?",
    "solution": "What is the smallest solution that would solve that problem?",
    "value_proposition": "Why would that customer choose or pay for this solution?",
    "potential_advantage": "What credible advantage could make this hard to replace?",
    "must_have": "Which features are essential for version 1 to deliver the core outcome?",
    "nice_to_have": "Which useful features can wait until after version 1?",
    "later": "Which ideas are explicitly out of scope until a later stage?",
}


OUT_OF_SCOPE_TERMS = {
    "patent": "intellectual-property strategy",
    "manufacturer": "manufacturer sourcing",
    "manufacturing": "manufacturing planning",
    "brand name": "branding",
    "logo": "branding",
    "marketing campaign": "marketing execution",
    "facebook ads": "marketing execution",
}


@dataclass
class CoachState:
    answers: Dict[str, str] = field(default_factory=dict)
    challenges: List[str] = field(default_factory=list)


def normalize(value: str) -> str:
    return " ".join(value.strip().split())


def list_items(value: str) -> List[str]:
    if not value:
        return []
    separators = ["\n", ";", ","]
    items = [value]
    for separator in separators:
        expanded: List[str] = []
        for item in items:
            expanded.extend(item.split(separator))
        items = expanded
    return [normalize(item).lstrip("-• ") for item in items if normalize(item)]


def scope_redirect(message: str) -> Optional[str]:
    lowered = message.lower()
    for term, category in OUT_OF_SCOPE_TERMS.items():
        if term in lowered:
            return (
                f"{category.capitalize()} belongs to a later Mind to Market stage. "
                "For Product Clarity, let us first define the customer, problem, "
                "solution, value, advantage, and version-1 scope."
            )
    return None


def diagnose(state: CoachState) -> List[str]:
    challenges: List[str] = []
    customer = state.answers.get("primary_customer", "").lower()
    problem = state.answers.get("problem", "")
    solution = state.answers.get("solution", "")
    must_have = list_items(state.answers.get("must_have", ""))

    if any(term in customer for term in ("everyone", "anyone", "all people", "all businesses")):
        challenges.append(
            "The primary customer is too broad. Choose one specific early-adopter segment for version 1."
        )
    if problem and len(problem.split()) < 6:
        challenges.append(
            "The problem statement needs a concrete situation, consequence, and current workaround."
        )
    if solution and not problem:
        challenges.append(
            "A solution is defined before the customer problem. Validate the problem before refining features."
        )
    if len(must_have) > 5:
        challenges.append(
            "Version 1 has more than five must-have features. Reclassify anything not required for the core outcome."
        )
    return challenges


def missing_fields(state: CoachState) -> List[str]:
    return [field for field in STAGES if not normalize(state.answers.get(field, ""))]


def next_step(state: CoachState) -> Optional[tuple[str, str]]:
    state.challenges = diagnose(state)
    customer = state.answers.get("primary_customer", "").lower()
    problem = state.answers.get("problem", "")
    solution = state.answers.get("solution", "")
    must_have = list_items(state.answers.get("must_have", ""))
    if any(term in customer for term in ("everyone", "anyone", "all people", "all businesses")):
        return "primary_customer", state.challenges[0]
    if problem and len(problem.split()) < 6:
        return "problem", next(item for item in state.challenges if "problem statement" in item)
    if solution and not problem:
        return "problem", next(item for item in state.challenges if "solution is defined" in item.lower())
    if len(must_have) > 5:
        return "must_have", next(item for item in state.challenges if "more than five" in item)
    missing = missing_fields(state)
    return (missing[0], QUESTIONS[missing[0]]) if missing else None


def next_question(state: CoachState) -> Optional[str]:
    step = next_step(state)
    return step[1] if step else None


def record_answer(state: CoachState, field_name: str, value: str) -> None:
    if field_name not in STAGES:
        raise ValueError(f"Unknown Product Clarity field: {field_name}")
    cleaned = normalize(value)
    if not cleaned:
        raise ValueError("Answers cannot be empty")
    state.answers[field_name] = cleaned
    state.challenges = diagnose(state)


def readiness(state: CoachState) -> Dict[str, object]:
    answered = len(STAGES) - len(missing_fields(state))
    challenges = diagnose(state)
    score = round(100 * answered / len(STAGES))
    if challenges:
        score = max(0, score - min(30, 10 * len(challenges)))
    if score >= 90 and not challenges:
        status = "Ready for the next Mind to Market stage"
    elif score >= 60:
        status = "Promising, but needs focused refinement"
    else:
        status = "Not yet clear enough to advance"
    return {"score": score, "status": status, "open_issues": challenges + missing_fields(state)}


def snapshot(state: CoachState) -> Dict[str, object]:
    result: Dict[str, object] = {
        "product_statement": state.answers.get("product_idea", ""),
        "primary_customer": state.answers.get("primary_customer", ""),
        "problem": state.answers.get("problem", ""),
        "solution": state.answers.get("solution", ""),
        "value_proposition": state.answers.get("value_proposition", ""),
        "potential_advantage": state.answers.get("potential_advantage", ""),
        "version_1": {
            "must_have": list_items(state.answers.get("must_have", "")),
            "nice_to_have": list_items(state.answers.get("nice_to_have", "")),
            "later": list_items(state.answers.get("later", "")),
        },
    }
    result["readiness"] = readiness(state)
    return result


def build_state(pairs: Iterable[tuple[str, str]]) -> CoachState:
    state = CoachState()
    for field_name, value in pairs:
        record_answer(state, field_name, value)
    return state
