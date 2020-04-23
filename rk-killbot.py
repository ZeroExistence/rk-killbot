import discord
import asyncio
import requests
import random
import traceback
import dateutil.parser as dtp
from dotenv import load_dotenv
import datetime as dt
import os

# Initial Loading
load_dotenv()
DIS_TOKEN = os.getenv("DIS_TOKEN")
DIS_CHANNEL = int(os.getenv("DIS_CHANNEL"))
GUILD = os.getenv("GUILD")

# Main
class RKKillBot(discord.Client):
    last_event_id = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def fetch_kills(self):
        response = requests.get(
            "https://gameinfo.albiononline.com/api/gameinfo/events?limit=51&offset=0",
        )
        if response:
            try:
                return response.json()
            except Exception:
                traceback.print_exc()
                print(response)
                pass
        else:
            print("Error:")
            print(response)
            return False

    def parse_kill(self, kill):
        if kill['EventId'] > self.last_event_id:
            #if kill['Killer']['GuildName']:
            if kill['Killer']['GuildName'] == GUILD or kill['Victim']['GuildName'] == GUILD:
                if kill['Victim']['DeathFame'] == 0:
                    pass

                victory = False
                if kill['Killer']['GuildName'] == GUILD:
                    victory = True
                    icon_url = 'https://i.imgur.com/CeqX0CY.png'
                    color = 0x008000
                else:
                    icon_url = 'https://albiononline.com/assets/images/killboard/kill__date.png'
                    color = 0x800000

                assisted_by = 0
                if kill['numberOfParticipants'] == 1:
                    solo_kill = [
                        'All on their own',
                        'Without assitance from anyone',
                        'All by himself',
                        'SOLO KILL'
                    ]
                    assisted_by = random.choice(solo_kill)
                else:
                    assists = []
                    for participant in kill['Participants']:
                        if participant['Name'] != kill['Killer']['Name']:
                            assists.append(participant['Name'])
                    assisted_by = "Assisted By: {0}".format(', '.join(assists))

                item_count = 0
                for item in kill['Victim']['Inventory']:
                    if item != None:
                        item_count += 1

                item_destroyed_text = ""
                if item_count > 0:
                    item_destroyed_text = "Dropped {0} items".format(item_count)

                data_embed = discord.Embed(
                    title="{0} | {1}".format(assisted_by, item_destroyed_text),
                    description = 'Gaining {0} fame'.format(kill['TotalVictimKillFame']),
                    timestamp = dtp.parse(kill['TimeStamp']),
                    color = color,
                )
                data_embed.set_author(
                    name = '{0} killed {1}'.format(kill['Killer']['Name'],kill['Victim']['Name']),
                    icon_url = icon_url,
                    url = 'https://albiononline.com/en/killboard/kill/{0}'.format(kill['EventId'])
                )
                data_embed.add_field(
                    name = "Killer Guild",
                    value = "[{0} - {1}]".format(kill['Killer']['AllianceName'],kill['Killer']['GuildName']),
                    inline = True
                )
                data_embed.add_field(
                    name = "Victim Guild",
                    value = "[{0} - {1}]".format(kill['Victim']['AllianceName'],kill['Victim']['GuildName']),
                    inline = True
                )
                # data_embed.add_field(
                #     name = "Killer IP",
                #     value = round(kill['Killer']['AverageItemPower']),
                #     inline = True
                # )
                # data_embed.add_field(
                #     name = "Victim IP",
                #     value = round(kill['Victim']['AverageItemPower']),
                #     inline = True
                # )
                data_embed.set_footer(
                    text = "Kill #{0}".format(kill['EventId'])
                )
                return data_embed
        else:
            return False

    async def my_background_task(self):
        await self.wait_until_ready()
        last_event_id = 0
        channel = self.get_channel(DIS_CHANNEL)
        while not self.is_closed():

            try:
                #Fetch\
                kills = self.fetch_kills()
                if kills:
                    #Parse
                    for kill in kills:
                        #Post_kill
                        data_embed = self.parse_kill(kill)
                        if data_embed:
                            await channel.send(embed=data_embed)
                            await asyncio.sleep(1)

                    self.last_event_id = kills[0]['EventId']
                    print("{0} : {1}".format(dt.datetime.now(), self.last_event_id))
                    await asyncio.sleep(60)

            except Exception:
                traceback.print_exc()
                pass


client = RKKillBot()
client.run(DIS_TOKEN)
