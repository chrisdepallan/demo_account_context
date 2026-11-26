"""Tests for acme_search.ranking."""

import unittest
from datetime import datetime, timedelta, timezone

from acme_search import Document, parse_query, rank, recency_multiplier, score_document
from acme_search.ranking import MAX_PAGE_SIZE, RECENCY_FLOOR

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def make_doc(doc_id, title, body="", age_days=0.0, doc_type="task"):
    return Document(doc_id, doc_type, title, NOW - timedelta(days=age_days), body)


class RecencyTests(unittest.TestCase):
    def test_new_document_has_full_weight(self):
        self.assertAlmostEqual(recency_multiplier(NOW, NOW), 1.0)

    def test_half_life_is_30_days(self):
        self.assertAlmostEqual(recency_multiplier(NOW - timedelta(days=30), NOW), 0.75)

    def test_never_drops_below_floor(self):
        value = recency_multiplier(NOW - timedelta(days=3650), NOW)
        self.assertGreaterEqual(value, RECENCY_FLOOR)
        self.assertAlmostEqual(value, RECENCY_FLOOR, places=6)

    def test_future_timestamp_counts_as_now(self):
        self.assertAlmostEqual(recency_multiplier(NOW + timedelta(days=2), NOW), 1.0)


class ScoringTests(unittest.TestCase):
    def test_title_match_beats_body_match(self):
        query = parse_query("budget")
        in_title = make_doc("tsk_AAAAAAA1", "Budget review", "numbers")
        in_body = make_doc("tsk_AAAAAAA2", "Review", "the budget numbers")
        self.assertGreater(score_document(query, in_title, NOW), score_document(query, in_body, NOW))

    def test_term_frequency_saturates(self):
        query = parse_query("budget")
        once = score_document(query, make_doc("tsk_AAAAAAA1", "x", "budget"), NOW)
        twice = score_document(query, make_doc("tsk_AAAAAAA2", "x", "budget budget"), NOW)
        many = score_document(query, make_doc("tsk_AAAAAAA3", "x", "budget " * 50), NOW)
        self.assertLess(once, twice)
        self.assertLess(twice - once, once)
        self.assertLess(many, 1.0)

    def test_all_terms_are_required(self):
        query = parse_query("budget review")
        self.assertEqual(score_document(query, make_doc("tsk_AAAAAAA1", "Budget"), NOW), 0.0)
        self.assertGreater(score_document(query, make_doc("tsk_AAAAAAA2", "Budget reviews"), NOW), 0.0)

    def test_excluded_term_and_phrase_remove_document(self):
        doc = make_doc("tsk_AAAAAAA1", "Budget draft copy")
        self.assertEqual(score_document(parse_query("budget -drafts"), doc, NOW), 0.0)
        self.assertEqual(score_document(parse_query('budget -"draft copy"'), doc, NOW), 0.0)
        self.assertGreater(score_document(parse_query('budget -"copy draft"'), doc, NOW), 0.0)

    def test_phrase_needs_exact_order(self):
        query = parse_query('"launch plan"')
        self.assertGreater(score_document(query, make_doc("tsk_AAAAAAA1", "Q3 launch plan"), NOW), 0.0)
        self.assertEqual(score_document(query, make_doc("tsk_AAAAAAA2", "Plan the launch"), NOW), 0.0)

    def test_or_group_and_prefix(self):
        query = parse_query("launch OR release")
        self.assertGreater(score_document(query, make_doc("tsk_AAAAAAA1", "Release notes"), NOW), 0.0)
        self.assertEqual(score_document(query, make_doc("tsk_AAAAAAA2", "Budget"), NOW), 0.0)
        prefix = parse_query("road*")
        self.assertGreater(score_document(prefix, make_doc("tsk_AAAAAAA3", "Roadmap"), NOW), 0.0)
        self.assertEqual(score_document(prefix, make_doc("tsk_AAAAAAA4", "Broad"), NOW), 0.0)

    def test_in_title_filter_ignores_body(self):
        doc = make_doc("tsk_AAAAAAA1", "Notes", "budget")
        self.assertEqual(score_document(parse_query("budget in:title"), doc, NOW), 0.0)
        self.assertGreater(score_document(parse_query("budget in:content"), doc, NOW), 0.0)


class RankTests(unittest.TestCase):
    def test_newer_document_ranks_first_when_text_is_equal(self):
        docs = [
            make_doc("tsk_AAAAAAA1", "Budget", age_days=90),
            make_doc("tsk_AAAAAAA2", "Budget", age_days=1),
        ]
        ranked = rank(parse_query("budget"), docs, NOW)
        self.assertEqual([item.document.id for item in ranked], ["tsk_AAAAAAA2", "tsk_AAAAAAA1"])

    def test_non_matches_are_dropped(self):
        docs = [make_doc("tsk_AAAAAAA1", "Budget"), make_doc("fil_AAAAAAA2", "Holiday rota")]
        self.assertEqual(len(rank(parse_query("budget"), docs, NOW)), 1)

    def test_filter_only_query_orders_by_recency(self):
        docs = [make_doc(f"tsk_AAAAAAA{i}", "Anything", age_days=i * 10) for i in (3, 1, 2)]
        ranked = rank(parse_query("type:task"), docs, NOW)
        self.assertEqual([item.document.id[-1] for item in ranked], ["1", "2", "3"])

    def test_ties_break_on_id(self):
        docs = [make_doc("tsk_AAAAAAA2", "Budget"), make_doc("tsk_AAAAAAA1", "Budget")]
        ranked = rank(parse_query("budget"), docs, NOW)
        self.assertEqual([item.document.id for item in ranked], ["tsk_AAAAAAA1", "tsk_AAAAAAA2"])

    def test_limit_is_clamped(self):
        docs = [make_doc(f"tsk_{i:08d}", "Budget") for i in range(MAX_PAGE_SIZE + 20)]
        self.assertEqual(len(rank(parse_query("budget"), docs, NOW, limit=500)), MAX_PAGE_SIZE)
        self.assertEqual(len(rank(parse_query("budget"), docs, NOW, limit=0)), 1)
        self.assertEqual(len(rank(parse_query("budget"), docs, NOW)), 50)


if __name__ == "__main__":
    unittest.main()
