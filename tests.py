import copy
import json
import unittest
from unittest.mock import patch, MagicMock

from criclive.main import get_scores, _format_score, _format_match_date, _parse_match


SAMPLE_MATCH = {
    "match": {
        "matchInfo": {
            "matchId": 12345,
            "seriesId": 100,
            "seriesName": "Test Series 2026",
            "matchDesc": "1st Test",
            "matchFormat": "TEST",
            "state": "Complete",
            "stateTitle": "IND won",
            "team1": {
                "teamId": 1,
                "teamName": "India",
                "teamSName": "IND",
            },
            "team2": {
                "teamId": 2,
                "teamName": "Australia",
                "teamSName": "AUS",
            },
        },
        "matchScore": {
            "team1Score": {
                "inngs1": {"inningsId": 1, "runs": 350, "wickets": 10, "overs": 98.2},
                "inngs2": {"inningsId": 3, "runs": 200, "wickets": 5, "overs": 60.0},
            },
            "team2Score": {
                "inngs1": {"inningsId": 2, "runs": 280, "wickets": 10, "overs": 85.4},
            },
        },
    }
}


class TestFormatScore(unittest.TestCase):
    def test_single_innings(self):
        score = {"inngs1": {"runs": 150, "wickets": 5, "overs": 30.2}}
        self.assertEqual(_format_score(score), "150/5 (30.2 ov)")

    def test_two_innings(self):
        score = {
            "inngs1": {"runs": 350, "wickets": 10, "overs": 98.2},
            "inngs2": {"runs": 200, "wickets": 5, "overs": 60.0},
        }
        self.assertEqual(
            _format_score(score), "350/10 (98.2 ov) & 200/5 (60.0 ov)"
        )

    def test_empty_score(self):
        self.assertEqual(_format_score({}), "")


class TestParseMatch(unittest.TestCase):
    def test_parse_valid_match(self):
        result = _parse_match(SAMPLE_MATCH)
        self.assertEqual(result["match_id"], 12345)
        self.assertEqual(result["first_team"]["name"], "IND")
        self.assertEqual(result["second_team"]["name"], "AUS")
        self.assertEqual(result["format"], "TEST")
        self.assertEqual(result["status"], "IND won")
        self.assertIn("350/10", result["first_team"]["score"])
        self.assertIn("280/10", result["second_team"]["score"])

    def test_parse_match_no_teams(self):
        data = {"match": {"matchInfo": {}, "matchScore": {}}}
        self.assertIsNone(_parse_match(data))

    def test_parse_match_ignores_malformed_start_date(self):
        data = {
            "match": {
                "matchInfo": {
                    "matchId": 12345,
                    "team1": {"teamName": "India", "teamSName": "IND"},
                    "team2": {"teamName": "Australia", "teamSName": "AUS"},
                    "startDate": "not-a-timestamp",
                },
                "matchScore": {},
            }
        }
        result = _parse_match(data)
        self.assertIsNotNone(result)
        self.assertEqual(result["date"], "")


class TestFormatMatchDate(unittest.TestCase):
    def test_formats_numeric_timestamp(self):
        self.assertEqual(_format_match_date(1700000000000), "Nov 14, 22:13 GMT")

    def test_formats_numeric_string_timestamp(self):
        self.assertEqual(_format_match_date("1700000000000"), "Nov 14, 22:13 GMT")

    def test_zero_timestamp_returns_empty(self):
        self.assertEqual(_format_match_date(0), "")
        self.assertEqual(_format_match_date("0"), "")

    def test_out_of_range_timestamp_returns_empty(self):
        self.assertEqual(_format_match_date(1e20), "")

    def test_boolean_timestamp_returns_empty(self):
        self.assertEqual(_format_match_date(True), "")

    def test_invalid_timestamp_returns_empty(self):
        self.assertEqual(_format_match_date("invalid"), "")


def _live_scores_page(*matches):
    """Build a minimal HTML page with embedded match data (compact JSON, no spaces)."""
    matches_json = ",".join(
        json.dumps(m, separators=(",", ":")).replace('"', '\\"') for m in matches
    )
    return f"""
    <html><head></head><body>
    <script>
    self.__next_f.push([1,"matchesList\\":{{\\"matches\\":[{matches_json}]}}"])
    </script>
    </body></html>
    """


class TestGetScores(unittest.TestCase):
    @patch("criclive.main.requests.get")
    def test_get_scores_parses_embedded_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = _live_scores_page(SAMPLE_MATCH)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        scores = get_scores()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["first_team"]["name"], "IND")

    @patch("criclive.main.requests.get")
    def test_get_scores_skips_malformed_match(self, mock_get):
        bad_match = copy.deepcopy(SAMPLE_MATCH)
        bad_match["match"]["matchInfo"]["matchId"] = 999
        bad_match["match"]["matchScore"]["team1Score"] = None
        mock_response = MagicMock()
        mock_response.text = _live_scores_page(bad_match, SAMPLE_MATCH)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        scores = get_scores()
        self.assertEqual([s["match_id"] for s in scores], [12345])

    @patch("criclive.main.requests.get")
    def test_get_scores_empty_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        scores = get_scores()
        self.assertEqual(scores, [])


if __name__ == "__main__":
    unittest.main()
