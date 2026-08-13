import difflib
from dataclasses import dataclass, field


@dataclass
class MatchResult:
    value: str | None
    matched_key: str | None
    needs_confirmation: bool


@dataclass
class NeedsConfirmation:
    question: str
    skill_id: str
    arguments: dict
    guessed_key: str


@dataclass
class NeedsSelection:
    question: str
    options: list
    skill_id: str
    arguments: dict
    video_map: dict = field(default_factory=dict)


def find_match(
    query: str,
    candidates: dict,
    auto_threshold: float = 0.7,
    confirm_threshold: float = 0.5,
    exclude: set | None = None,
) -> MatchResult:
    exclude = exclude or set()
    available = {
        key: val
        for key, val in candidates.items()
        if key not in exclude
    }

    if query in available:
        return MatchResult(
            value=available[query],
            matched_key=query,
            needs_confirmation=False,
        )

    close = difflib.get_close_matches(
        query,
        available.keys(),
        n=1,
        cutoff=confirm_threshold,
    )

    if not close:
        return MatchResult(
            value=None,
            matched_key=None,
            needs_confirmation=False,
        )

    matched_key = close[0]

    ratio = difflib.SequenceMatcher(
        None,
        query,
        matched_key,
    ).ratio()

    return MatchResult(
        value=available[matched_key],
        matched_key=matched_key,
        needs_confirmation=ratio < auto_threshold,
    )