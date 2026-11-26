"""Parse a search query string into a structured :class:`ParsedQuery`.

Supported syntax (see ``docs/query-syntax.md``)::

    type:task assignee:me "exact phrase" -excluded launch OR release plan*

- plain words are required (AND), stop words are ignored
- ``"quoted text"`` is an exact phrase
- a leading ``-`` excludes a word, a phrase or a filter
- ``OR`` (upper case) between two plain words matches either
- ``word*`` is a prefix match (at least 3 characters before the ``*``)
- ``key:value`` is a filter when ``key`` is one of :data:`FILTER_KEYS`
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Tuple

from .tokenizer import tokenize

MAX_QUERY_LENGTH = 512
MAX_TERMS = 32
MAX_FILTERS = 10
MIN_PREFIX_LENGTH = 3

_ENUM_FILTERS = {
    "type": ("project", "task", "file"),
    "status": ("open", "completed", "archived"),
    "in": ("title", "content"),
    "has": ("attachment", "comment", "due"),
}
_DATE_FILTERS = ("created", "updated", "due")
_PERSON_FILTERS = ("assignee", "owner")
FILTER_KEYS = frozenset(_ENUM_FILTERS) | frozenset(_DATE_FILTERS) | frozenset(_PERSON_FILTERS) | {
    "project",
    "label",
    "ext",
}

_LEXEME_RE = re.compile(
    r'(?P<neg>-)?(?:(?P<key>[A-Za-z_]+):)?(?:"(?P<quoted>[^"]*)"|(?P<bare>\S+))'
)
_PROJECT_ID_RE = re.compile(r"^prj_[A-Z0-9]{8}$")
_EXT_RE = re.compile(r"^[a-z0-9]{1,10}$")
_DATE_OP_RE = re.compile(r"^(>=|<=|>|<)?(.+)$")


class QuerySyntaxError(ValueError):
    """Raised when a query breaks a syntax rule or a limit (HTTP 400)."""


@dataclass(frozen=True)
class Filter:
    """One ``key:value`` filter.

    ``operator`` is ``=`` for most filters; date filters may also use
    ``>``, ``>=``, ``<``, ``<=`` or ``range`` (value ``start..end``).
    """

    key: str
    value: str
    operator: str = "="
    negated: bool = False


@dataclass
class ParsedQuery:
    """Structured form of a query string."""

    terms: List[str] = field(default_factory=list)
    phrases: List[str] = field(default_factory=list)
    prefixes: List[str] = field(default_factory=list)
    or_groups: List[List[str]] = field(default_factory=list)
    excluded_terms: List[str] = field(default_factory=list)
    excluded_phrases: List[str] = field(default_factory=list)
    filters: List[Filter] = field(default_factory=list)

    @property
    def has_text(self) -> bool:
        """True when the query has at least one positive text clause."""
        return bool(self.terms or self.phrases or self.prefixes or self.or_groups)

    @property
    def term_count(self) -> int:
        """Number of text clauses counted against :data:`MAX_TERMS`."""
        return (
            len(self.terms) + len(self.phrases) + len(self.prefixes)
            + sum(len(group) for group in self.or_groups)
            + len(self.excluded_terms) + len(self.excluded_phrases)
        )

    def filter_values(self, key: str, negated: bool = False) -> List[str]:
        """Return the values of every filter with ``key``."""
        return [f.value for f in self.filters if f.key == key and f.negated == negated]


def _parse_date(text: str) -> str:
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise QuerySyntaxError(f"invalid date {text!r}: use YYYY-MM-DD") from None


def _date_filter(key: str, raw: str, negated: bool) -> Filter:
    if ".." in raw:
        start, _, end = raw.partition("..")
        start, end = _parse_date(start), _parse_date(end)
        if start > end:
            raise QuerySyntaxError(f"{key}: range start is after its end")
        return Filter(key, f"{start}..{end}", "range", negated)
    match = _DATE_OP_RE.match(raw)
    operator, value = match.group(1) or "=", match.group(2)
    return Filter(key, _parse_date(value), operator, negated)


def _build_filter(key: str, raw: str, negated: bool, current_user: Optional[str]) -> Filter:
    """Validate one filter value and return the normalised :class:`Filter`."""
    if not raw:
        raise QuerySyntaxError(f"filter {key!r} has no value")
    if key in _DATE_FILTERS:
        return _date_filter(key, raw, negated)
    if key == "project":
        if not _PROJECT_ID_RE.match(raw):
            raise QuerySyntaxError("project: expected an ID like prj_4K7M2Q9X")
        return Filter(key, raw, "=", negated)
    value = raw.lower()
    if key in _ENUM_FILTERS and value not in _ENUM_FILTERS[key]:
        allowed = ", ".join(_ENUM_FILTERS[key])
        raise QuerySyntaxError(f"{key}: {raw!r} is not one of {allowed}")
    if key == "ext":
        value = value.lstrip(".")
        if not _EXT_RE.match(value):
            raise QuerySyntaxError(f"ext: {raw!r} is not a file extension")
    if key in _PERSON_FILTERS:
        if value == "me":
            value = (current_user or "me").lower()
        elif not (value == "none" and key == "assignee") and "@" not in value:
            raise QuerySyntaxError(f"{key}: use me, an email address or assignee:none")
    return Filter(key, value, "=", negated)


def parse_query(query: str, current_user: Optional[str] = None) -> ParsedQuery:
    """Parse ``query`` and enforce the documented limits.

    :param query: the raw query string typed by the user.
    :param current_user: email that ``assignee:me`` / ``owner:me`` resolve to.
    :raises QuerySyntaxError: on an empty query, a bad filter value, a
        dangling ``OR``, a short wildcard or a limit being exceeded.
    """
    if len(query) > MAX_QUERY_LENGTH:
        raise QuerySyntaxError(f"query is longer than {MAX_QUERY_LENGTH} characters")
    parsed = ParsedQuery()
    groups: List[List[str]] = []  # positive plain terms; len > 1 means OR
    pending_or = False
    last_was_plain = False

    for match in _LEXEME_RE.finditer(query):
        negated = bool(match.group("neg"))
        key, quoted, bare = match.group("key"), match.group("quoted"), match.group("bare")
        is_or = bare == "OR" and not negated and not key
        if is_or:
            if not last_was_plain or pending_or:
                raise QuerySyntaxError("OR must sit between two plain words")
            pending_or, last_was_plain = True, False
            continue
        plain_tokens: Tuple[str, ...] = ()
        if key and key.lower() in FILTER_KEYS:
            raw = quoted if quoted is not None else bare
            parsed.filters.append(_build_filter(key.lower(), raw, negated, current_user))
        elif quoted is not None:
            phrase = " ".join(tokenize(f"{key or ''} {quoted}", False, False))
            if phrase:
                (parsed.excluded_phrases if negated else parsed.phrases).append(phrase)
        elif bare.endswith("*") and not key:
            prefix = bare[:-1].lower()
            if negated or len(prefix) < MIN_PREFIX_LENGTH or not prefix.isalnum():
                raise QuerySyntaxError(
                    f"wildcard needs at least {MIN_PREFIX_LENGTH} letters or digits "
                    "before * and cannot be excluded"
                )
            parsed.prefixes.append(prefix)
        else:
            tokens = tokenize(f"{key or ''} {bare}", True, False)
            if negated:
                parsed.excluded_terms.extend(tokens)
            else:
                plain_tokens = tuple(tokens)
        last_was_plain = bool(plain_tokens)
        if pending_or:
            if not plain_tokens:
                raise QuerySyntaxError("OR must sit between two plain words")
            groups[-1].append(plain_tokens[0])
            plain_tokens = plain_tokens[1:]
            pending_or = False
        groups.extend([token] for token in plain_tokens)

    if pending_or:
        raise QuerySyntaxError("OR must sit between two plain words")
    for group in groups:
        if len(group) == 1:
            parsed.terms.append(group[0])
        else:
            parsed.or_groups.append(group)
    if not parsed.has_text and not parsed.filters:
        raise QuerySyntaxError("query has nothing to search for")
    if parsed.term_count > MAX_TERMS:
        raise QuerySyntaxError(f"query has more than {MAX_TERMS} terms")
    if len(parsed.filters) > MAX_FILTERS:
        raise QuerySyntaxError(f"query has more than {MAX_FILTERS} filters")
    return parsed
