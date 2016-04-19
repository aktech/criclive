import requests
from bs4 import BeautifulSoup

url = "http://www.espncricinfo.com/ci/engine/match/index.html?view=live"

def open_url(url):
    return requests.get(url).text  # returns html

def get_bsoup_object(html):
    return BeautifulSoup(html, "lxml")  # returns soup (BeautifulSoup's object)

def get_team_divs(soup):
    teams1 = soup.find_all('div', attrs = {'class': 'innings-info-1'})
    teams2 = soup.find_all('div', attrs = {'class': 'innings-info-2'})
    return get_team_scores(teams1), get_team_scores(teams2)

def get_team_scores(team_soup):
    team = list(map(lambda x: x.contents, team_soup))
    for t in team:
        t[1] = t[1].contents
    return [[t[0].strip(), t[1]] for t in team]

def main():
    t1, t2 = get_team_divs(get_bsoup_object(open_url(url)))
    for i in range(len(t1)):
        print("%s. %s %s VS %s %s" %(i+1, t1[i][0], t1[i][1], t2[i][0], t2[i][1]))
