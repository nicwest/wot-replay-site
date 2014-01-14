from app.lib import wotapi
from config import WOT_API_KEY

api = wotapi.WotAPI('eu', WOT_API_KEY)
# api.get_json('player', {'account_id': 507235309, 'fields': 'nickname'})
print api.get_player_data(500915395, ['nickname', 'clan.clan_id'])
