import datetime
import unittest

from Backend.RealtimeSearchEngine import GoogleSearch, build_search_query


class GoogleSearchTests(unittest.TestCase):
    def test_build_search_query_includes_current_year(self):
        current_year = datetime.datetime.now().strftime("%Y")
        query = build_search_query("latest AI breakthrough")
        self.assertIn(current_year, query)
        self.assertTrue(query.lower().startswith("latest ai breakthrough"))

    def test_google_search_returns_live_results(self):
        output = GoogleSearch("latest AI breakthrough 2026")
        self.assertIsInstance(output, str)
        self.assertNotIn("could not be completed", output)
        self.assertNotIn("No Google search results were found", output)
        self.assertTrue(len(output.strip()) > 100)


if __name__ == "__main__":
    unittest.main()
