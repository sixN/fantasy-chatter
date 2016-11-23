import mechanicalsoup
import argparse
import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
# available since 2.4.0
from selenium.webdriver.support.ui import WebDriverWait
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
from pprint import pprint
import plugins


def _initialise(bot):
    # plugins.register_handler(_handle_me_action)
    plugins.register_user_command(["ff"])


def ff(bot, event, *args):

    re_firstname = re.compile('^[\S]+')

    # May want to switch to https
    url_scoreboard = 'http://games.espn.com/ffl/scoreboard?leagueId=591765&seasonId=2016'
    url_team = 'http://games.espn.com/ffl/clubhouse?leagueId=591765&teamId=6&seasonId=2016'

    #login xpaths
    xp_login = '//*[@id="disneyid-iframe"]'
    xp_username = "//*[@id='did-ui']/div/div/section/section/form/section/div[1]/div/label/span[2]/input"
    xp_password = "//*[@id='did-ui']/div/div/section/section/form/section/div[2]/div/label/span[2]/input"
    xp_submit = "//*[@id='did-ui']/div/div/section/section/form/section/div[3]/button"

    #replace with get password from json
    un = 'usernamehere'
    pw = 'passwordhere'

    driver = webdriver.PhantomJS()
    driver.get(url_scoreboard)

    WebDriverWait(driver, 9000).until(
        EC.presence_of_all_elements_located((By.XPATH, xp_login)))
    frms = driver.find_elements_by_xpath("(//iframe)")

    driver.switch_to_frame(frms[2])

    password = (driver.find_elements_by_xpath(xp_password))[0]
    #password = password[0]
    password.send_keys(pw)

    username = (driver.find_elements_by_xpath(xp_username))[0]
    #username = username[0]
    username.send_keys(un)

    submit_btn = (driver.find_elements_by_xpath(xp_submit))[0]
    submit_btn.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "scoreboardMatchups")))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Get cats of matchups, all cats are same

    tableSubHead = soup.find_all('table', class_='ptsBased matchup')

    message = ""
    for table in tableSubHead:
        verb = ""

        # there are three <tr> sections, the first two are teams, the third is
        # matchup details
        teams = table.find_all('tr')

        team1 = teams[0].find('a')['title']
        team2 = teams[1].find('a')['title']

        team1_score = float(teams[0].find('td', class_='score')['title'])
        team2_score = float(teams[1].find('td', class_='score')['title'])

        team1_owner = teams[0].find('span', class_='owners').string
        team2_owner = teams[1].find('span', class_='owners').string

        team1_owner_firstname = re_firstname.match(team1_owner).group()
        team2_owner_firstname = re_firstname.match(team2_owner).group()

        team1_nick = teams[0].find('span', class_='abbrev').string
        team2_nick = teams[1].find('span', class_='abbrev').string

        if (team1_score > team2_score):
            message += "<i><b>{}</b> leads {} <b>{:.1f}</b> to <b>{:.1f}</b></i>\n".format(
                team1_owner_firstname, team2_owner_firstname, team1_score, team2_score)
        elif (team1_score < team2_score):
            message += "<i>{} trails <b>{}</b> <b>{:.1f}</b> to <b>{:.1f}</b></i>\n".format(
                team1_owner_firstname, team2_owner_firstname, team1_score, team2_score)
        else:
            message += "<i>{} and {} are <b>tied</b> at <b>{:.1f}</b></i>\n".format(
                team1_owner_firstname, team2_owner_firstname, team1_score)

    driver.close()
    yield from bot.coro_send_message(event.conv, message)
