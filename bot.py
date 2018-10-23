import json
import requests
import time
import datetime
import sys
import configparser
from collections import defaultdict


# credits to: https://github.com/4rqm/dhooks
class Webhook:

    def __init__(self, url, **kwargs):
        """
        Initialise a Webhook Embed Object
        """

        self.url = url
        self.username = kwargs.get('username')
        self.msg = kwargs.get('msg')
        self.color = kwargs.get('color')
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('title_url')
        self.author = kwargs.get('author')
        self.author_icon = kwargs.get('author_icon')
        self.avatar = kwargs.get('avatar')
        self.author_url = kwargs.get('author_url')
        self.desc = kwargs.get('desc')
        self.fields = kwargs.get('fields', [])
        self.image = kwargs.get('image')
        self.thumbnail = kwargs.get('thumbnail')
        self.footer = kwargs.get('footer')
        self.footer_icon = kwargs.get('footer_icon')
        self.ts = kwargs.get('ts')

    def add_field(self, **kwargs):
        '''Adds a field to `self.fields`'''
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline', True)

        field = {'name': name, 'value': value, 'inline': inline}

        self.fields.append(field)

    def set_desc(self, desc):
        self.desc = desc

    def set_author(self, **kwargs):
        self.author = kwargs.get('name')
        self.author_icon = kwargs.get('icon')
        self.author_url = kwargs.get('url')

    def set_title(self, **kwargs):
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('url')

    def set_thumbnail(self, url):
        self.thumbnail = url

    def set_image(self, url):
        self.image = url

    def set_avatar(self, avatar):
        self.avatar = avatar

    def set_color(self, color):
        self.color = color

    def set_username(self, username):
        self.username = username

    def set_footer(self, **kwargs):
        self.footer = kwargs.get('text')
        self.footer_icon = kwargs.get('icon')
        ts = kwargs.get('ts')
        if ts:
            self.ts = str(datetime.datetime.utcfromtimestamp(time.time()))
        else:
            self.ts = str(datetime.datetime.utcfromtimestamp(ts))

    def del_field(self, index):
        self.fields.pop(index)

    @property
    def json(self, *arg):
        '''
        Formats the data into a payload
        '''

        data = {}

        data["embeds"] = []
        embed = defaultdict(dict)
        if self.msg:
            data["content"] = self.msg
        if self.username:
            data["username"] = self.username
        if self.avatar:
            data["avatar_url"] = self.avatar
        if self.author:
            embed["author"]["name"] = self.author
        if self.author_icon:
            embed["author"]["icon_url"] = self.author_icon
        if self.author_url:
            embed["author"]["url"] = self.author_url
        if self.color:
            embed["color"] = self.color
        if self.desc:
            embed["description"] = self.desc
        if self.title:
            embed["title"] = self.title
        if self.title_url:
            embed["url"] = self.title_url
        if self.image:
            embed["image"]['url'] = self.image
        if self.thumbnail:
            embed["thumbnail"]['url'] = self.thumbnail
        if self.footer:
            embed["footer"]['text'] = self.footer
        if self.footer_icon:
            embed['footer']['icon_url'] = self.footer_icon
        if self.ts:
            embed["timestamp"] = self.ts

        if self.fields:
            embed["fields"] = []
        for field in self.fields:
            f = {}
            f["name"] = field['name']
            f["value"] = field['value']
            f["inline"] = field['inline']
            embed["fields"].append(f)

        data["embeds"].append(dict(embed))

        empty = all(not d for d in data["embeds"])

        if empty and 'content' not in data:
            print('You cant post an empty payload.')
        if empty:
            data['embeds'] = []

        return json.dumps(data, indent=4)

    def post(self):
        """
        Send the JSON formated object to the specified `self.url`.
        """

        headers = {'Content-Type': 'application/json'}

        result = requests.post(self.url, data=self.json, headers=headers)

        if result.status_code == 400:
            print("Post Failed, Error 400")
        else:
            print("Payload delivered successfuly. Code : " + str(result.status_code))
            time.sleep(2)


if len(sys.argv) < 2:
    print('Help: need the path to the input config file.')
    exit()

# loading configuration
config = configparser.ConfigParser()
config.read(sys.argv[1])

try:
    input_alliance = config['DEFAULT']['alliance']
    input_webhook = config['DEFAULT']['webhook']
    input_avatar = config['DEFAULT']['avatar']
    input_sleep_time = config['DEFAULT']['sleep_time']
    input_package_size = config['DEFAULT']['package_size']

except KeyError:
    print('Warning: key not valid or not found.')

# check required inputs
if not input_alliance:
    print('Error: input alliance not set.')
    exit()

if not input_webhook:
    print('Error: input webhook not set')
    exit()

# default values
if not input_sleep_time:
    input_sleep_time = 10
if not input_package_size:
    input_package_size = 50
timestamp = -1
gameinfo_url = 'https://gameinfo.albiononline.com/api/gameinfo/events?limit=' + str(input_package_size)
database_url = 'https://gameinfo.albiononline.com/api/gameinfo/items/'
killboard_url = 'https://albiononline.com/en/killboard/kill/'

# inspiration from : https://github.com/bearlikelion/ao-killbot
while True:
    result = requests.get(gameinfo_url)
    if result.status_code == 400:
        print("Post Failed, Error 400")
    else:
        print("Payload received successfuly. Code : " + str(result.status_code))

        package = result.json()

        for i in range(len(package) - 1, 0, -1):
            event_id = package[i]['EventId']
            current_ts = package[i]['TimeStamp'].split('.', 1)[0]
            current_ts = datetime.datetime.strptime(current_ts, "%Y-%m-%dT%H:%M:%S")

            if timestamp == -1 or (max((timestamp, current_ts)) == current_ts and timestamp != current_ts):
                victim_package = package[i]['Victim']
                killer_package = package[i]['Killer']

                victim_name = victim_package['Name']
                victim_alliance = victim_package['AllianceName']
                victim_guild = '[' + victim_alliance + ']' + victim_package['GuildName']
                victim_power = int(victim_package['AverageItemPower'])

                killer_name = killer_package['Name']
                killer_alliance = killer_package['AllianceName']
                killer_guild = '[' + killer_alliance + ']' + killer_package['GuildName']
                killer_power = int(killer_package['AverageItemPower'])

                if killer_package['Equipment']['MainHand']:
                    weapon_url = database_url + killer_package['Equipment']['MainHand']['Type']

                s = '[' + killer_name + ' has killed ' + victim_name + '](' + killboard_url + str(event_id) + ')'

                if victim_alliance == input_alliance or killer_alliance == input_alliance:
                    if victim_alliance == input_alliance:
                        embed_color = 0xff0000
                    else:
                        embed_color = 0x00ff00

                    embed = Webhook(input_webhook, color=embed_color)
                    embed.set_username(username='arKiller_alpha')
                    if input_avatar:
                        embed.set_avatar(avatar=input_avatar)
                    embed.set_author(name='Herald of Death')
                    embed.set_desc(s)
                    embed.add_field(name='Killer Guild', value=killer_guild)
                    embed.add_field(name='Victim Guild', value=victim_guild)
                    embed.add_field(name='Killer Power', value=killer_power)
                    embed.add_field(name='Victim Power', value=victim_power)
                    embed.add_field(name='Fame', value=victim_package['DeathFame'])
                    if weapon_url:
                        embed.set_thumbnail(weapon_url)
                    # embed.set_image(albion)
                    embed.set_footer(ts=True)
                    embed.post()

                    print(str(current_ts))

        timestamp = current_ts

    time.sleep(input_sleep_time)
