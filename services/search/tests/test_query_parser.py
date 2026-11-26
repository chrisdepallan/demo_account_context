"""Tests for acme_search.query_parser and acme_search.tokenizer."""

import unittest

from acme_search import Filter, QuerySyntaxError, parse_query, stem, term_frequencies, tokenize
from acme_search.query_parser import MAX_FILTERS, MAX_QUERY_LENGTH, MAX_TERMS


class TokenizerTests(unittest.TestCase):
    def test_lowercases_and_removes_stop_words(self):
        self.assertEqual(tokenize("The Budget for Q3"), ["budget", "q3"])

    def test_stemming_groups_word_forms(self):
        self.assertEqual(stem("planning"), "plan")
        self.assertEqual(stem("planned"), "plan")
        self.assertEqual(stem("files"), stem("file"))
        self.assertEqual(stem("completed"), stem("complete"))
        self.assertEqual(stem("boxes"), "box")

    def test_short_words_and_ids_are_not_stemmed(self):
        self.assertEqual(stem("bus"), "bus")
        self.assertEqual(stem("status"), "status")
        self.assertEqual(tokenize("see tsk_8G2K4M1P"), ["see", "tsk_8g2k4m1p"])

    def test_options_keep_stop_words_and_raw_forms(self):
        self.assertEqual(tokenize("The Reports", False, False), ["the", "reports"])

    def test_term_frequencies(self):
        self.assertEqual(term_frequencies(["plan", "report", "plan"]), {"plan": 2, "report": 1})


class QueryParserTests(unittest.TestCase):
    def test_full_example(self):
        parsed = parse_query(
            'type:task assignee:me "exact phrase" -excluded launch',
            current_user="Admin@Customer.example",
        )
        self.assertEqual(parsed.terms, ["launch"])
        self.assertEqual(parsed.phrases, ["exact phrase"])
        self.assertEqual(parsed.excluded_terms, ["excluded"])
        self.assertEqual(
            parsed.filters,
            [Filter("type", "task"), Filter("assignee", "admin@customer.example")],
        )

    def test_stop_words_dropped_outside_phrases_only(self):
        parsed = parse_query('the roadmap "state of the art"')
        self.assertEqual(parsed.terms, ["roadmap"])
        self.assertEqual(parsed.phrases, ["state of the art"])

    def test_or_group(self):
        parsed = parse_query("launch OR release notes")
        self.assertEqual(parsed.or_groups, [["launch", "release"]])
        self.assertEqual(parsed.terms, ["notes"])

    def test_dangling_or_is_an_error(self):
        for query in ("OR launch", "launch OR", "launch OR type:task"):
            with self.assertRaises(QuerySyntaxError):
                parse_query(query)

    def test_prefix_wildcard(self):
        self.assertEqual(parse_query("plan*").prefixes, ["plan"])
        with self.assertRaises(QuerySyntaxError):
            parse_query("pl*")

    def test_negated_filter_and_phrase(self):
        parsed = parse_query('budget -type:file -"draft copy"')
        self.assertEqual(parsed.filters, [Filter("type", "file", "=", True)])
        self.assertEqual(parsed.excluded_phrases, ["draft copy"])
        self.assertEqual(parsed.filter_values("type", negated=True), ["file"])

    def test_date_filters(self):
        parsed = parse_query("created:>=2026-01-01 updated:2026-03-01..2026-03-31 due:<2026-12-01")
        self.assertEqual(
            parsed.filters,
            [
                Filter("created", "2026-01-01", ">="),
                Filter("updated", "2026-03-01..2026-03-31", "range"),
                Filter("due", "2026-12-01", "<"),
            ],
        )

    def test_invalid_filter_values(self):
        for query in (
            "type:folder",
            "created:yesterday",
            "updated:2026-03-31..2026-03-01",
            "project:prj_123",
            "assignee:someone",
            "ext:p-d-f",
        ):
            with self.assertRaises(QuerySyntaxError, msg=query):
                parse_query(query)

    def test_unknown_key_is_plain_text(self):
        parsed = parse_query("meeting 10:30 colour:blue")
        self.assertEqual(parsed.terms, ["meeting", "10", "30", "colour", "blue"])
        self.assertEqual(parsed.filters, [])

    def test_filter_value_normalisation(self):
        parsed = parse_query('ext:.PDF project:prj_4K7M2Q9X label:"Q3 Launch" assignee:none')
        self.assertEqual(
            [(f.key, f.value) for f in parsed.filters],
            [("ext", "pdf"), ("project", "prj_4K7M2Q9X"), ("label", "q3 launch"), ("assignee", "none")],
        )

    def test_filter_only_query_is_allowed_but_empty_is_not(self):
        self.assertFalse(parse_query("type:file").has_text)
        for query in ("", "   ", "the of"):
            with self.assertRaises(QuerySyntaxError):
                parse_query(query)

    def test_limits(self):
        with self.assertRaises(QuerySyntaxError):
            parse_query("a" * (MAX_QUERY_LENGTH + 1))
        with self.assertRaises(QuerySyntaxError):
            parse_query(" ".join(f"w{i}" for i in range(MAX_TERMS + 1)))
        with self.assertRaises(QuerySyntaxError):
            parse_query(" ".join(["label:x"] * (MAX_FILTERS + 1)))
        self.assertEqual(parse_query(" ".join(f"w{i}" for i in range(MAX_TERMS))).term_count, MAX_TERMS)


if __name__ == "__main__":
    unittest.main()
