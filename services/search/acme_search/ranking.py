"""Relevance scoring for search results.

The score of a document for a query is::

    (sum of clause scores) * recency multiplier

- **Term frequency** – each matching term adds ``tf / (tf + 1.2)``, so
  repeating a word helps less and less.
- **Title boost** – a match in the title counts :data:`TITLE_BOOST` times
  as much as a match in the body.
- **Phrase boost** – an exact phrase adds :data:`PHRASE_BOOST` (times the
  title boost when it is found in the title).
- **Recency decay** – the multiplier falls from 1.0 towards
  :data:`RECENCY_FLOOR` with a half-life of :data:`RECENCY_HALF_LIFE_DAYS`.

A document that misses a required clause, or contains an excluded one,
scores ``0.0`` and is not returned. Filters other than ``in:`` are applied
by the index before ranking and are not re-checked here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence

from .query_parser import ParsedQuery
from .tokenizer import stem, tokenize

TITLE_BOOST = 3.0
PHRASE_BOOST = 2.0
TF_SATURATION = 1.2
RECENCY_HALF_LIFE_DAYS = 30.0
RECENCY_FLOOR = 0.5
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


@dataclass(frozen=True)
class Document:
    """The searchable view of a project, task or file."""

    id: str
    type: str
    title: str
    updated_at: datetime
    body: str = ""


@dataclass(frozen=True)
class ScoredDocument:
    """A document together with its relevance score."""

    document: Document
    score: float


def _saturate(tf: int) -> float:
    return tf / (tf + TF_SATURATION) if tf else 0.0


def _contains_phrase(tokens: Sequence[str], phrase: Sequence[str]) -> bool:
    size = len(phrase)
    return size > 0 and any(
        list(tokens[i:i + size]) == list(phrase) for i in range(len(tokens) - size + 1)
    )


def recency_multiplier(updated_at: datetime, now: Optional[datetime] = None) -> float:
    """Return the recency multiplier, between :data:`RECENCY_FLOOR` and 1.0.

    A document updated right now gets 1.0; one updated 30 days ago gets
    0.75; very old documents approach 0.5. Future timestamps count as now.
    """
    now = now or datetime.now(timezone.utc)
    age_days = max(0.0, (now - updated_at).total_seconds() / 86400.0)
    decay = 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)
    return RECENCY_FLOOR + (1.0 - RECENCY_FLOOR) * decay


def score_document(query: ParsedQuery, doc: Document, now: Optional[datetime] = None) -> float:
    """Score ``doc`` against ``query``; ``0.0`` means "not a match".

    A query with filters only (no text) scores every document by recency
    alone, so filter-only searches come back newest first.
    """
    fields = set(query.filter_values("in"))
    title_raw = tokenize(doc.title, False, False) if fields != {"content"} else []
    body_raw = tokenize(doc.body, False, False) if fields != {"title"} else []
    title_stems = [stem(token) for token in title_raw]
    body_stems = [stem(token) for token in body_raw]

    def term_score(term: str) -> float:
        stemmed = stem(term)
        return TITLE_BOOST * _saturate(title_stems.count(stemmed)) + _saturate(
            body_stems.count(stemmed)
        )

    all_stems = set(title_stems) | set(body_stems)
    if any(stem(term) in all_stems for term in query.excluded_terms):
        return 0.0
    for phrase in query.excluded_phrases:
        words = phrase.split()
        if _contains_phrase(title_raw, words) or _contains_phrase(body_raw, words):
            return 0.0

    total = 0.0
    for term in query.terms:
        score = term_score(term)
        if score == 0.0:
            return 0.0
        total += score
    for group in query.or_groups:
        score = max(term_score(term) for term in group)
        if score == 0.0:
            return 0.0
        total += score
    for prefix in query.prefixes:
        in_title = sum(1 for token in title_raw if token.startswith(prefix))
        in_body = sum(1 for token in body_raw if token.startswith(prefix))
        if not (in_title or in_body):
            return 0.0
        total += TITLE_BOOST * _saturate(in_title) + _saturate(in_body)
    for phrase in query.phrases:
        words = phrase.split()
        in_title = _contains_phrase(title_raw, words)
        in_body = _contains_phrase(body_raw, words)
        if not (in_title or in_body):
            return 0.0
        total += PHRASE_BOOST * (TITLE_BOOST if in_title else 0.0)
        total += PHRASE_BOOST if in_body else 0.0

    if not query.has_text:
        total = 1.0
    return total * recency_multiplier(doc.updated_at, now)


def rank(
    query: ParsedQuery,
    documents: Iterable[Document],
    now: Optional[datetime] = None,
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[ScoredDocument]:
    """Return matching documents, best first.

    Ties are broken by most recently updated, then by ID so that the
    order is stable between pages. ``limit`` is clamped to 1–200.
    """
    limit = max(1, min(int(limit), MAX_PAGE_SIZE))
    now = now or datetime.now(timezone.utc)
    scored = [ScoredDocument(doc, score_document(query, doc, now)) for doc in documents]
    matches = [item for item in scored if item.score > 0.0]
    matches.sort(key=lambda item: item.document.id)
    matches.sort(key=lambda item: item.document.updated_at, reverse=True)
    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[:limit]
