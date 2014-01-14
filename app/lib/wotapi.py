import urllib2
import json


class WotAPI:
    def __init__(self, server, api_keys):

        servers = {
            "ru": "http://api.worldoftanks.ru",
            "eu": "http://api.worldoftanks.eu",
            "na": "http://api.worldoftanks.com",
            "asia": "http://api.worldoftanks.asia",
            "kr": "http://api.worldoftanks.kr"
        }

        self.paths = {
            "player": "account/info", # https://eu.wargaming.net/developers/api_reference/wot/account/info/
            "player_ratings": "ratings/accounts", # https://eu.wargaming.net/developers/api_reference/wot/account/ratings/
            "player_tanks": "account/tanks",  # https://eu.wargaming.net/developers/api_reference/wot/account/tanks/
            "clan_search": "clan/list",  # https://eu.wargaming.net/developers/api_reference/wot/clan/list/
            "clan": "clan/info",  # https://eu.wargaming.net/developers/api_reference/wot/clan/info/
        }


        self.server = servers[server]
        self.key = api_keys[server]

    def get_json(self, path, vars):
        add_vars = ""
        for key, value in vars.iteritems():
            add_vars += "&"+str(key)+"="+str(value)
        url = self.server + '/wot/' + self.paths[path] + '/?application_id=' + self.key + add_vars
        # print url
        data = urllib2.urlopen(url)
        output = json.loads(data.read())
        # print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
        if output['status'] == u'ok' and 'data' in output:
            return output['data']
        return None

    def get_player_data(self, player, fields=[]):
        vars = {'account_id': player, 'fields': ','.join(fields)}
        if len(fields) < 1:
            del vars['fields']
        data = self.get_json('player', vars)
        # print data
        return data[str(player)]