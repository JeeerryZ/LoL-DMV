import collections
from bs4 import BeautifulSoup
from riotwatcher import LolWatcher, ApiError
import pandas as pd
import csv
import os.path
import requests
import yaml


api_key = ''
region = ''
user_name = ''
championsDict = {}


def downloadChampions():
    latest = watcher.data_dragon.versions_for_region(region)['n']['champion']
    champions = watcher.data_dragon.champions(
        latest, False, 'pt_BR')['data']

    for key in champions:
        id = champions[key]['key']
        name = champions[key]['name']
        championsDict[int(id)] = name

    w = csv.writer(open("champions.csv", "w", newline=''))

    for key, value in championsDict.items():
        w.writerow([key, value])


#----------------------LOADING------------------------#

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    api_key = config['api_key']
    region = config['region']
    user_name = config['summoner_name']

if os.path.exists('champions.csv'):
    r = csv.reader(open('champions.csv', 'r'))
    for row in r:
        championsDict[int(row[0])] = row[1]
else:
    print("Downloading champions...")
    downloadChampions()

#-----------------------------------------------------#

#-----------------------SETUP-------------------------#

watcher = LolWatcher(api_key)
user = watcher.summoner.by_name(region, user_name)
user_id = user['id']
user_puuid = user['puuid']

#-----------------------------------------------------#


def getUsername():
    return user_name


def getInfo(name):
    url = f'https://br.op.gg/summoner?userName={name}'
    _request = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    bsoup = BeautifulSoup(_request, 'html.parser')
    info = {}
    wr = ''
    try:
        wr = bsoup.find('div', {'class': 'ratio'}).getText().split(' ')[2]
    except:
        wr = '0%'
    info['WR'] = wr
    return info


def getChampion(id):
    return championsDict.get(id)


def isPlaying():
    try:
        watcher.spectator.by_summoner(region, user_id)
    except:
        return False
    return True


def getMatch():
    return watcher.spectator.by_summoner(region, user_id)


def getMatchDetails(_match, with_pd=False):

    participants = _match['participants']

    match = {}
    # Match id
    match['Gameid'] = _match['gameId']
    # Gamemode
    match['Gamemode'] = _match['gameMode']
    # Gametype
    match['Gametype'] = _match['gameType']
    # Time elapsed
    match['Time'] = int(_match['gameLength']) + \
        180 if int(_match['gameLength']) != 0 else 0
    # Players
    match['Players'] = []

    dataframe = []
    for participant in participants:
        summoner_id = participant['summonerId']
        summoner_name = participant['summonerName']
        champion_id = participant['championId']
        summoner_data = watcher.league.by_summoner(region, summoner_id)
        summoner_wr = getInfo(summoner_name)['WR']
        user_data = watcher.summoner.by_id(region, summoner_id)
        team = 'Blue' if participant['teamId'] == 100 else 'Red'
        rank = "UNRANKED" if summoner_data == [
        ] else f"{summoner_data[0]['tier']}"

        if with_pd:
            dataframe_row = {}
            dataframe_row['Champion'] = getChampion(champion_id)
            dataframe_row['Name'] = summoner_name
            dataframe_row['Elo'] = rank
            dataframe_row['Level'] = user_data['summonerLevel']
            dataframe.append(dataframe_row)
        else:
            match['Players'].append({
                'Name': summoner_name,
                'Champion': getChampion(champion_id),
                'Elo': rank,
                'Level': user_data['summonerLevel'],
                'Team': team,
                'WR': summoner_wr
            })
    if with_pd:
        writeToCache(match)
        return pd.DataFrame(dataframe)
    else:
        global roles
        writeToCache(match)
        return match


def writeToCache(match):
    with open('cache.yml', 'w') as f:
        yaml.dump(match, f)


def getRemainingTime(matchTime):
    return (60*25)-matchTime if matchTime <= (60*25) else 0


MatchData = collections.namedtuple(
    'MatchData', 'gameId, gameType, matchTime, gameMinutes, gameSeconds, names, champions, elos')


def filterData(match, client, emojis):
    """Returns match data ready to be sent to the discord client via embed with support for emojis.

    Args:
        match (match): Match to extract data from.
        client (Bot): Current discord client instance for creating emojis and sendind messages
        emojis (str): List of emojis to use for the embed fields.
    Returns:
        A tuple with 8 arguments with each detail from given match.

    """

    gameId = match['Gameid']
    matchTime = match['Time']
    gameType = 'Ranked 5v5' if match['Gametype'] == 'MATCHED_GAME' else 'Normal 5v5'
    gameMinutes, gameSeconds = divmod(matchTime, 60)
    names = []
    champions = []
    elos = []
    for players in match['Players']:
        wr_no_percent = int(players['WR'].replace('%', ''))
        names.append(
            f"{str(client.get_emoji(emojis.PASSED)) if wr_no_percent >= 50 else client.get_emoji(emojis.FAILED)} {players['Name']} - {players['WR']}")
        champions.append(
            f"{players['Champion']}{str(client.get_emoji(emojis.NO_BACKGROUND))}")
        elos.append(str(client.get_emoji(emojis.getEmoji(
            players['Elo']))) if players['Elo'] != 'UNRANKED' else str(client.get_emoji(emojis.NO_BACKGROUND)))

    names.insert(int(len(names)/2), ' ')
    champions.insert(int(len(champions)/2), ' ')
    elos.insert(int(len(elos)/2), ' ')

    names = '\n'.join(names)
    champions = '\n'.join(champions)
    elos = '\n'.join(elos)

    return MatchData(gameId, gameType, matchTime, gameMinutes, gameSeconds, names, champions, elos)


async def searchMatch():
    if isPlaying():
        m = getMatchDetails(getMatch())
        return m
