import json
import re
import sys

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

LIVE_SCORES_URL = "https://www.cricbuzz.com/cricket-match/live-scores"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_scores():
    """Fetch live cricket scores from Cricbuzz."""
    response = requests.get(LIVE_SCORES_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Cricbuzz uses Next.js with embedded JSON data in script tags
    for script in soup.find_all("script"):
        text = script.string or ""
        if "matchesList" not in text:
            continue
        return _parse_matches_from_script(text)

    return []


def _parse_matches_from_script(text):
    """Extract match data from the Next.js RSC script payload."""
    # Unescape the embedded JSON strings
    unescaped = text.replace('\\"', '"').replace("\\n", "\n")

    matches = []
    # Find all match JSON blocks: {"match":{"matchInfo":{...},"matchScore":{...}}}
    # We locate each matchInfo and extract the surrounding match object
    for m in re.finditer(r'"match":\{"matchInfo":\{', unescaped):
        start = m.start() - 1  # include the opening {
        match_data = _extract_json_object(unescaped, start)
        if match_data:
            parsed = _parse_match(match_data)
            if parsed:
                matches.append(parsed)

    # Deduplicate by matchId (data appears multiple times in RSC payload)
    seen = set()
    unique = []
    for m in matches:
        mid = m.get("match_id")
        if mid and mid not in seen:
            seen.add(mid)
            unique.append(m)

    return unique


def _extract_json_object(text, start):
    """Extract a balanced JSON object starting at position `start`."""
    if text[start] != "{":
        return None
    depth = 0
    for i in range(start, min(start + 5000, len(text))):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _parse_match(data):
    """Parse a match dict into our display format."""
    match = data.get("match", data)
    info = match.get("matchInfo", {})
    score_data = match.get("matchScore", {})

    team1_info = info.get("team1", {})
    team2_info = info.get("team2", {})

    if not team1_info or not team2_info:
        return None

    team1_score = _format_score(score_data.get("team1Score", {}))
    team2_score = _format_score(score_data.get("team2Score", {}))

    status = info.get("stateTitle", "") or info.get("state", "")

    return {
        "match_id": info.get("matchId"),
        "title": f"{info.get('seriesName', '')} - {info.get('matchDesc', '')}",
        "format": info.get("matchFormat", ""),
        "first_team": {
            "name": team1_info.get("teamSName", team1_info.get("teamName", "")),
            "score": team1_score,
        },
        "second_team": {
            "name": team2_info.get("teamSName", team2_info.get("teamName", "")),
            "score": team2_score,
        },
        "status": status,
    }


def _format_score(team_score):
    """Format innings scores into a readable string."""
    parts = []
    for key in ("inngs1", "inngs2"):
        innings = team_score.get(key)
        if innings:
            runs = innings.get("runs", "")
            wickets = innings.get("wickets", "")
            overs = innings.get("overs", "")
            score_str = f"{runs}/{wickets}"
            if overs:
                score_str += f" ({overs} ov)"
            parts.append(score_str)
    return " & ".join(parts)


def _print_scores(scores):
    """Print scores in a formatted table."""
    if not scores:
        print("No live matches at the moment.")
        return

    table = []
    for score in scores:
        first = score["first_team"]
        second = score["second_team"]
        status = score.get("status", "")
        fmt = score.get("format", "")

        first_col = first["name"]
        if first["score"]:
            first_col += f"  {first['score']}"

        second_col = second["name"]
        if second["score"]:
            second_col += f"  {second['score']}"

        table.append([first_col, "vs", second_col, fmt, status])

    print(
        tabulate(
            table,
            headers=["Team 1", "", "Team 2", "Format", "Status"],
            showindex=range(1, len(table) + 1),
            tablefmt="fancy_grid",
        )
    )


def main():
    try:
        scores = get_scores()
        _print_scores(scores)
    except requests.ConnectionError:
        print(
            "Error: Could not connect. Check your internet connection.",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print("Error: Request timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
