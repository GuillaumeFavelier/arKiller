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
            print("requests.post() return code : " + str(result.status_code))
            time.sleep(2)


def send_embed(package, victory_event, params):
    event_id = package['EventId']
    victim_package = package['Victim']
    victim_alliance = victim_package['AllianceName']
    victim_guild = victim_package['GuildName']
    victim_name = victim_package['Name']

    killer_package = package['Killer']
    killer_alliance = killer_package['AllianceName']
    killer_guild = killer_package['GuildName']
    killer_name = killer_package['Name']

    description = '[' + killer_name + ' has killed ' + victim_name + '](' + params['killboard_url'] + str(event_id) + ')'
    victim_power = int(victim_package['AverageItemPower'])
    killer_power = int(killer_package['AverageItemPower'])

    weapon_url = ''
    if killer_package['Equipment']['MainHand']:
        weapon_url = params['database_url'] + killer_package['Equipment']['MainHand']['Type']

    if victory_event:
        embed_color = 0x00ff00
    else:
        embed_color = 0xff0000

    embed = Webhook(params['webhook'], color=embed_color)
    embed.set_username(username='arKiller_alpha')
    if params['avatar']:
        embed.set_avatar(avatar=params['avatar'])
    embed.set_author(name='Herald of Death')
    embed.set_desc(description)
    if killer_alliance:
        embed.add_field(name='Killer Alliance', value=killer_alliance)
    else:
        embed.add_field(name='Killer Alliance', value='*-None-*')
    if victim_alliance:
        embed.add_field(name='Victim Alliance', value=victim_alliance)
    else:
        embed.add_field(name='Victim Alliance', value='*-None-*')
    if killer_guild:
        embed.add_field(name='Killer Guild', value=killer_guild)
    else:
        embed.add_field(name='Killer Guild', value='*-None-*')
    if victim_guild:
        embed.add_field(name='Victim Guild', value=victim_guild)
    else:
        embed.add_field(name='Victim Guild', value='*-None-*')
    embed.add_field(name='Killer Power', value=killer_power)
    embed.add_field(name='Victim Power', value=victim_power)
    embed.add_field(name='Fame', value=victim_package['DeathFame'])
    if weapon_url:
        embed.set_thumbnail(weapon_url)
    embed.set_footer(ts=True)
    embed.post()


def init_params():
    # define default variables
    params = {
        'filter': '',
        'alliance': '',
        'guild': '',
        'webhook': '',
        'avatar': '',
        'sleep_time': '',
        'package_size': '',
        'gameinfo_url': 'https://gameinfo.albiononline.com/api/gameinfo/events?limit=',
        'database_url': 'https://gameinfo.albiononline.com/api/gameinfo/items/',
        'killboard_url': 'https://albiononline.com/en/killboard/kill/'}
    return params


def get_params():
    # loading configuration
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # define default variables
    params = init_params()
    try:
        params['filter'] = config['DEFAULT']['filter']
        params['alliance'] = config['DEFAULT']['alliance']
        params['guild'] = config['DEFAULT']['guild']
        params['webhook'] = config['DEFAULT']['webhook']
        params['avatar'] = config['DEFAULT']['avatar']
        params['sleep_time'] = config['DEFAULT']['sleep_time']
        params['package_size'] = config['DEFAULT']['package_size']
    except KeyError:
        print('Warning: default key not valid or not found.')

    return params


def check_params(params):
    # check required inputs
    if not params['filter']:
        print('Error: input filter not set.')
        exit()

    if params['filter'] == 'alliance' and not params['alliance']:
        print('Error: input alliance not set.')
        exit()

    if params['filter'] == 'guild' and not params['guild']:
        print('Error: input guild not set.')
        exit()

    if not params['webhook']:
        print('Error: input webhook not set')
        exit()

    # default values
    if not params['sleep_time']:
        params['sleep_time'] = 1
    if not params['package_size']:
        params['package_size'] = 50


def main():
    if len(sys.argv) < 2:
        print('Help: need the path to the input config file.')
        exit()

    params = get_params()
    check_params(params)

    timestamp = -1

    # inspiration from : https://github.com/bearlikelion/ao-killbot
    while True:
        try:
            result = requests.get(params['gameinfo_url'] + str(params['package_size']))
        except requests.exceptions.RequestException as e:
            print(e)

        print("requests.get() return code : " + str(result.status_code))

        package = result.json()

        current_ts = -1

        for i in range(len(package) - 1, 0, -1):
            current_package = package[i]
            current_ts = current_package['TimeStamp'].split('.', 1)[0]
            current_ts = datetime.datetime.strptime(current_ts, "%Y-%m-%dT%H:%M:%S")

            if timestamp == -1 or (max((timestamp, current_ts)) == current_ts and timestamp != current_ts):
                victim_package = current_package['Victim']
                victim_alliance = victim_package['AllianceName']
                victim_guild = victim_package['GuildName']

                killer_package = current_package['Killer']
                killer_alliance = killer_package['AllianceName']
                killer_guild = killer_package['GuildName']

                alliance_event = (params['filter'] == 'alliance' and (victim_alliance == params['alliance'] or killer_alliance == params['alliance']))
                guild_event = (params['filter'] == 'guild' and (victim_guild == params['guild'] or killer_guild == params['guild']))
                victory_event = (guild_event and (killer_guild == params['guild'])) or (alliance_event and (killer_alliance == params['alliance']))

                if alliance_event or guild_event:
                    send_embed(current_package, victory_event, params)
                    print(str(current_ts))

        timestamp = current_ts

        time.sleep(params['sleep_time'])


if __name__ == '__main__':
    main()
