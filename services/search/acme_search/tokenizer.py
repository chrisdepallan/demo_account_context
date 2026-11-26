"""Text analysis used at index time and at query time.

Both sides of a search must be analysed the same way, otherwise a query
term never lines up with an indexed term. The pipeline is:

1. Unicode NFKC normalisation and lowercasing.
2. Splitting into tokens on anything that is not a letter, digit or an
   underscore between two word characters (so ``tsk_8G2K4M1P`` stays whole).
3. Dropping tokens longer than :data:`MAX_TOKEN_LENGTH` characters.
4. Optionally removing stop words.
5. Optionally applying a light English stemmer.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Dict, Iterable, List

#: Tokens longer than this are not indexed (they are almost always noise).
MAX_TOKEN_LENGTH = 64

#: Common English words that carry no meaning in a search.
STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was",
        "with",
    }
)

_TOKEN_RE = re.compile(r"[^\W_]+(?:_[^\W_]+)*")

# (suffix, replacement, minimum length of what is left after stripping)
_SUFFIX_RULES = (
    ("sses", "ss", 2),
    ("ches", "ch", 2),
    ("shes", "sh", 2),
    ("xes", "x", 2),
    ("ies", "y", 2),
    ("ing", "", 4),
    ("ed", "", 3),
    ("ly", "", 4),
    ("s", "", 3),
)

# Words ending in these are left alone by the plural ``s`` rule.
_KEEP_S_ENDINGS = ("ss", "us", "is")


def stem(word: str) -> str:
    """Return a simple stem of ``word``.

    Only plain ASCII alphabetic words longer than 3 characters are stemmed,
    so IDs such as ``prj_4K7M2Q9X`` and numbers are returned unchanged.

    >>> stem("planning"), stem("files"), stem("completed"), stem("complete")
    ('plan', 'file', 'complet', 'complet')
    """
    if len(word) <= 3 or not (word.isascii() and word.isalpha()):
        return word
    result = word
    for suffix, replacement, min_rest in _SUFFIX_RULES:
        if not word.endswith(suffix):
            continue
        if suffix == "s" and word.endswith(_KEEP_S_ENDINGS):
            break
        rest = word[: -len(suffix)]
        if len(rest) < min_rest:
            break
        result = rest + replacement
        # "planning" -> "plann" -> "plan", but keep "bill", "pass", "buzz".
        if (
            suffix in ("ing", "ed")
            and len(result) >= 4
            and result[-1] == result[-2]
            and result[-1] not in "lsz"
        ):
            result = result[:-1]
        break
    if len(result) > 4 and result.endswith("e"):
        result = result[:-1]
    return result


def tokenize(text: str, remove_stop_words: bool = True, apply_stemming: bool = True) -> List[str]:
    """Split ``text`` into normalised tokens.

    :param text: raw text of a title, body or query.
    :param remove_stop_words: drop words listed in :data:`STOP_WORDS`.
    :param apply_stemming: reduce each token with :func:`stem`.
    :return: tokens in their original order; duplicates are kept.
    """
    normalised = unicodedata.normalize("NFKC", text or "").lower()
    tokens: List[str] = []
    for token in _TOKEN_RE.findall(normalised):
        if len(token) > MAX_TOKEN_LENGTH:
            continue
        if remove_stop_words and token in STOP_WORDS:
            continue
        tokens.append(stem(token) if apply_stemming else token)
    return tokens


def term_frequencies(tokens: Iterable[str]) -> Dict[str, int]:
    """Count how often each token occurs.

    >>> term_frequencies(["plan", "report", "plan"])
    {'plan': 2, 'report': 1}
    """
    return dict(Counter(tokens))
