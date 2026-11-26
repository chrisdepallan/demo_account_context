"""Acme Cloud Search service: query parsing, tokenizing and ranking.

The rules implemented here are described in the service docs:

- ``docs/query-syntax.md`` and ``docs/filters-and-sorting.md`` – :mod:`acme_search.query_parser`
- ``docs/indexing-and-freshness.md`` – :mod:`acme_search.tokenizer` and :mod:`acme_search.ranking`
- ``docs/search-limits.md`` – the limits enforced by the parser and the ranker
"""

from .query_parser import Filter, ParsedQuery, QuerySyntaxError, parse_query
from .ranking import Document, ScoredDocument, rank, recency_multiplier, score_document
from .tokenizer import STOP_WORDS, stem, term_frequencies, tokenize

__all__ = [
    "Document",
    "Filter",
    "ParsedQuery",
    "QuerySyntaxError",
    "STOP_WORDS",
    "ScoredDocument",
    "parse_query",
    "rank",
    "recency_multiplier",
    "score_document",
    "stem",
    "term_frequencies",
    "tokenize",
]
