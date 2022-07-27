from time import sleep
from discord.ext import commands, tasks
from datetime import datetime
import discord
import yaml
from lol_manager import getMatch, searchMatch, getUsername, isPlaying, getRemainingTime, filterData

client = commands.Bot(command_prefix='!')

channel = None
discord_key = ''
curMatchId = ''


class emojis():
    IRON = 999136386856800307
    BRONZE = 999136386856800307
    SILVER = 999136388328992808
    GOLD = 999136393504772217
    PLATINUM = 999136397371912202
    DIAMOND = 999136392296812604
    MASTER = 999136390916882572
    GRANDMASTER = 999136398743449781
    CHALLENGER = 999136400425365634
    BLUE = ':blue_circle:'
    RED = ':red_circle:'
    FAILED = 999405999091880077
    PASSED = 999406000736043008
    NO_BACKGROUND = 999802179005194300

    def getEmoji(elo):
        if elo == 'IRON':
            return emojis.IRON
        elif elo == 'BRONZE':
            return emojis.BRONZE
        elif elo == 'SILVER':
            return emojis.SILVER
        elif elo == 'GOLD':
            return emojis.GOLD
        elif elo == 'PLATINUM':
            return emojis.PLATINUM
        elif elo == 'DIAMOND':
            return emojis.DIAMOND
        elif elo == 'MASTER':
            return emojis.MASTER
        elif elo == 'GRANDMASTER':
            return emojis.GRANDMASTER
        elif elo == 'CHALLENGER':
            return emojis.CHALLENGER


with open('config.yml', 'r') as f:
    discord_key = yaml.safe_load(f)['discord_key']

with open('cache.yml', 'r') as f:
    cache = yaml.safe_load(f)
    if cache != None and cache.get('Gameid') != None:
        curMatchId = cache.get('Gameid')


def getChannelId():
    with open('config.yml') as f:
        config = yaml.safe_load(f)
        if config != None:
            if config.get('channel_id') != None:
                return config.get('channel_id')


@client.event
async def on_ready():
    print(f'Logged in as:  {client.user.name} - {client.user.id}')
    global channel
    channel = client.get_channel(getChannelId())
    print(f"Channel id found in config ({channel.id})")
    matchFindLoop.start()
    await client.change_presence(activity=discord.Game(f"partida de {getUsername()}"))


@client.command(aliases=['set_channel'])
async def setChannel(ctx):
    channel = ctx.channel.id
    with open('config.yml', 'w') as f:
        config = {'channel_id': channel}
        yaml.dump(config, f)


@tasks.loop(seconds=60)
async def matchFindLoop():
    global channel
    global curMatchId
    if(isPlaying()):
        match = await searchMatch()

        gameId = match['Gameid']
        matchTime = match['Time']
        remainingTime = getRemainingTime(matchTime)

        if(gameId == curMatchId):
            sleep(remainingTime)
            return

        date = datetime.now()
        print(f"Match found at: {datetime.strftime(date, '%H:%M:%S')}")

        gameId, gameType, matchTime, gameMinutes, gameSeconds, names, champions, elos = filterData(
            match, client, emojis)

        curMatchId = gameId

        embed = discord.Embed(title='Partida encontrada',
                              description=f"{gameType} {gameMinutes:02d}:{gameSeconds:02d}", color=0xf50000)
        embed.add_field(name='Nome', value=names, inline=True)
        embed.add_field(name='Champion', value=champions, inline=True)
        embed.add_field(name='Elo', value=elos, inline=True)
        embed.set_footer(text=f"ID: {gameId}")

        await channel.send(embed=embed)

        sleep(remainingTime)
    else:
        print('No match found... Waiting 60 seconds for searching again')


client.run(discord_key)
