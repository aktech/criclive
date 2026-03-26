from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.events import Click, Key
from textual.reactive import var
from textual.widgets import Static
from textual.widget import Widget

from criclive.main import get_scores

DEFAULT_REFRESH_INTERVAL = 5


class MatchCard(Widget):
    DEFAULT_CSS = """
    MatchCard {
        height: auto;
        margin: 0 1;
        padding: 0 1;
        border-bottom: solid $surface-lighten-2;

        .row {
            height: 1;
        }

        .match-num {
            width: 4;
            color: $text-muted;
        }

        .team-name {
            width: 6;
            text-style: bold;
        }

        .team-score {
            color: $success;
            margin-left: 1;
        }

        .match-status {
            color: $accent;
            text-style: bold;
            margin-left: 2;
        }

        .match-title {
            color: $text-muted;
            text-style: italic;
        }

        .match-date {
            dock: right;
            width: auto;
            color: $text-muted;
            padding-right: 1;
        }

        .detail {
            display: none;
            height: auto;
            padding: 0 0 0 4;
        }

        .detail-line {
            height: 1;
            color: $text-muted;
        }

        .detail-label {
            width: 10;
            color: $text-muted;
            text-style: bold;
        }

        .detail-value {
            color: $text;
        }

        .detail-score-name {
            width: 20;
            text-style: bold;
        }

        .detail-score-value {
            color: $success;
        }
    }

    MatchCard.expanded .detail {
        display: block;
    }
    """

    expanded = var(False)

    def __init__(self, match: dict, number: int = 0) -> None:
        super().__init__()
        self.match = match
        self.number = number

    @staticmethod
    def _title_text(m: dict) -> str:
        fmt = m.get("format", "")
        title = m.get("title", "")
        if fmt:
            title = f"{title}  {fmt}"
        return title

    def compose(self) -> ComposeResult:
        m = self.match
        first = m["first_team"]
        second = m["second_team"]
        date = m.get("date", "")

        with Horizontal(classes="row"):
            yield Static(date, classes="match-date", id="date")
            yield Static(f"{self.number:>2}.", classes="match-num", id="num")
            yield Static(self._title_text(m), classes="match-title", id="title")

        with Horizontal(classes="row"):
            yield Static("", classes="match-num")
            yield Static(first["name"], classes="team-name", id="t1name")
            yield Static(first.get("score", ""), classes="team-score", id="t1score")
            yield Static(m.get("status", ""), classes="match-status", id="status")

        with Horizontal(classes="row"):
            yield Static("", classes="match-num")
            yield Static(second["name"], classes="team-name", id="t2name")
            yield Static(second.get("score", ""), classes="team-score", id="t2score")

        with Container(classes="detail"):
            yield Static("", classes="detail-line")

            with Horizontal(classes="row"):
                yield Static(first.get("full_name", first["name"]), classes="detail-score-name", id="d-t1name")
                yield Static(first.get("score", "") or "-", classes="detail-score-value", id="d-t1score")

            with Horizontal(classes="row"):
                yield Static(second.get("full_name", second["name"]), classes="detail-score-name", id="d-t2name")
                yield Static(second.get("score", "") or "-", classes="detail-score-value", id="d-t2score")

            yield Static("", classes="detail-line")
            yield Static("", classes="detail-value", id="d-status-row")
            yield Static("", classes="detail-value", id="d-venue-row")
            yield Static("", classes="detail-value", id="d-date-row")
            yield Static("", classes="detail-line")

    def on_mount(self) -> None:
        self._update_detail()

    def _update_detail(self) -> None:
        m = self.match
        status_detail = m.get("status_detail", "")
        venue = m.get("venue", "")
        date = m.get("date", "")
        self.query_one("#d-status-row", Static).update(f"Status     {status_detail}" if status_detail else "")
        self.query_one("#d-status-row", Static).display = bool(status_detail)
        self.query_one("#d-venue-row", Static).update(f"Venue      {venue}" if venue else "")
        self.query_one("#d-venue-row", Static).display = bool(venue)
        self.query_one("#d-date-row", Static).update(f"Date       {date}" if date else "")
        self.query_one("#d-date-row", Static).display = bool(date)

    def update_match(self, match: dict, number: int) -> None:
        self.match = match
        self.number = number
        first = match["first_team"]
        second = match["second_team"]

        self.query_one("#num", Static).update(f"{number:>2}.")
        self.query_one("#title", Static).update(self._title_text(match))
        self.query_one("#date", Static).update(match.get("date", ""))
        self.query_one("#t1name", Static).update(first["name"])
        self.query_one("#t1score", Static).update(first.get("score", ""))
        self.query_one("#t2name", Static).update(second["name"])
        self.query_one("#t2score", Static).update(second.get("score", ""))
        self.query_one("#status", Static).update(match.get("status", ""))

        self.query_one("#d-t1name", Static).update(first.get("full_name", first["name"]))
        self.query_one("#d-t1score", Static).update(first.get("score", "") or "-")
        self.query_one("#d-t2name", Static).update(second.get("full_name", second["name"]))
        self.query_one("#d-t2score", Static).update(second.get("score", "") or "-")
        self._update_detail()

    def on_click(self, event: Click) -> None:
        self.expanded = not self.expanded
        self.set_class(self.expanded, "expanded")
        match_id = self.match.get("match_id")
        if match_id is not None:
            app = self.app
            if self.expanded:
                app._expanded_ids.add(match_id)
            else:
                app._expanded_ids.discard(match_id)


class CricLiveApp(App):
    TITLE = "CricLive"

    refresh_interval = DEFAULT_REFRESH_INTERVAL

    CSS = """
    Screen {
        background: $background;
    }

    #banner {
        width: 100%;
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #scores {
        height: auto;
        padding: 0;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        padding: 0 2;
        background: $primary-background;
        color: $text-muted;
    }

    #no-matches {
        width: 100%;
        height: auto;
        padding: 1 4;
        text-align: center;
        color: $text-muted;
        text-style: italic;
    }

    #tip-bar {
        dock: bottom;
        height: 1;
        padding: 0 2;
        background: $surface;
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    match_count = var(0)
    filter_text = var("")
    _filtering = False
    _expanded_ids: set

    def compose(self) -> ComposeResult:
        yield Static("CricLive - Live Cricket Scores", id="banner")
        yield Container(id="scores")
        yield Static("", id="status-bar")
        yield Static(
            "Tip: Press / to search, Esc to clear, r to refresh, q to quit",
            id="tip-bar",
        )

    def on_mount(self) -> None:
        self._expanded_ids = set()
        self.action_refresh()
        self.set_interval(self.refresh_interval, self.action_refresh)

    def _update_banner(self) -> None:
        banner = self.query_one("#banner", Static)
        if self._filtering:
            banner.update(f"CricLive / {self.filter_text}\u2588")
        elif self.filter_text:
            banner.update(f"CricLive / {self.filter_text}")
        else:
            banner.update("CricLive - Live Cricket Scores")

    def on_key(self, event: Key) -> None:
        if self._filtering:
            if event.key == "escape":
                self._filtering = False
                self.filter_text = ""
                self._update_banner()
                self._apply_filter()
                event.prevent_default()
            elif event.key == "enter":
                self._filtering = False
                self._update_banner()
                event.prevent_default()
            elif event.key == "backspace":
                self.filter_text = self.filter_text[:-1]
                self._update_banner()
                self._apply_filter()
                event.prevent_default()
            elif event.is_printable and event.character:
                self.filter_text += event.character
                self._update_banner()
                self._apply_filter()
                event.prevent_default()
        elif event.key == "slash":
            self._filtering = True
            self.filter_text = ""
            self._update_banner()
            event.prevent_default()

    def action_refresh(self) -> None:
        self._update_status("Fetching scores...")
        self.run_worker(self._fetch_and_display, exclusive=True)

    def _match_matches_filter(self, match: dict) -> bool:
        if not self.filter_text:
            return True
        query = self.filter_text.lower()
        searchable = " ".join([
            match.get("title", ""),
            match["first_team"]["name"],
            match["second_team"]["name"],
            match.get("format", ""),
            match.get("status", ""),
        ]).lower()
        return query in searchable

    def _apply_filter(self) -> None:
        for card in self.query(MatchCard):
            card.display = self._match_matches_filter(card.match)
        visible = sum(1 for c in self.query(MatchCard) if c.display)
        total = self.match_count
        if self.filter_text:
            self._update_status(
                f"{visible}/{total} matches"
                f" | Auto-refresh every {self.refresh_interval}s"
                f" | / filter  Esc clear"
            )
        else:
            self._update_status(
                f"{total} match{'es' if total != 1 else ''}"
                f" | Auto-refresh every {self.refresh_interval}s"
                f" | / filter"
            )

    async def _fetch_and_display(self) -> None:
        try:
            scores = get_scores()
        except Exception as e:
            self._update_status(f"Error: {e}")
            return

        container = self.query_one("#scores", Container)
        existing = {c.match.get("match_id"): c for c in self.query(MatchCard)}
        new_ids = [m.get("match_id") for m in scores]

        # Remove cards no longer present
        for mid, card in existing.items():
            if mid not in new_ids:
                await card.remove()

        # Remove "no matches" placeholder if present
        for w in container.query("#no-matches"):
            await w.remove()

        if not scores:
            await container.mount(
                Static("No live matches at the moment.", id="no-matches")
            )
        else:
            for i, match in enumerate(scores, 1):
                mid = match.get("match_id")
                if mid in existing:
                    existing[mid].update_match(match, i)
                    existing[mid].display = self._match_matches_filter(match)
                else:
                    card = MatchCard(match, number=i)
                    await container.mount(card)
                    card.display = self._match_matches_filter(match)
                    if mid in self._expanded_ids:
                        card.expanded = True
                        card.set_class(True, "expanded")

        self.match_count = len(scores)
        self._apply_filter()

    def _update_status(self, text: str) -> None:
        self.query_one("#status-bar", Static).update(text)


def main():
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Live Cricket Scores")
    parser.add_argument("--json", action="store_true", help="Output scores as JSON")
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_REFRESH_INTERVAL,
        help=f"Auto-refresh interval in seconds (default: {DEFAULT_REFRESH_INTERVAL})",
    )
    args = parser.parse_args()

    if args.json:
        try:
            scores = get_scores()
        except Exception as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(scores, indent=2))
    else:
        app = CricLiveApp()
        app.refresh_interval = args.interval
        app.run()
