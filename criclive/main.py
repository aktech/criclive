import requests
from bs4 import BeautifulSoup

from tabulate import tabulate

SOURCE_URL = "https://www.espncricinfo.com/scores/"


def print_scores(scores):
    table = [
        [
            f"{score['first_team']['name']} {score['first_team']['score']}",
            f"{score['second_team']['name']} {score['second_team']['score']}"
        ]
        for score in scores
    ]
    table_len = len(table)
    print(tabulate(
        table,
        showindex=range(1, table_len + 1),
        tablefmt='fancy_grid')
    )


def get_scores():
    html = requests.get(SOURCE_URL).text
    soup = BeautifulSoup(html, "lxml")
    competitors = soup.find_all('ul', attrs={'class': 'cscore_competitors'})

    scores = []

    for each_competitor in competitors:
        team_scores = list(map(_extract_score, each_competitor.find_all('div', {'class': 'cscore_score'})))
        team_names = list(map(lambda x: x.contents[0], each_competitor.find_all('span', {'class': 'cscore_name--long'})))

        scores.append(
            {
                'first_team': {
                    'name': team_names[0],
                    'score': team_scores[0]
                },
                'second_team': {
                    'name': team_names[1],
                    'score': team_scores[1]
                },
            }
        )
    return scores


def _extract_score(score_soup):
    score_string = score_soup.contents
    if len(score_string) == 2:
        score, overs = score_string
        overs_content = overs.contents
        score_string = [f'{score} {overs_content[0]}']
    return score_string


def main():
    scores = get_scores()
    print_scores(scores)

