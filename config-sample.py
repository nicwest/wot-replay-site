import os

#rename this file to 'config.py' and fill in the required info.

basedir = os.path.abspath(os.path.dirname(__file__))


#database stuff
_dbname = ""
_dbusername = ""
_dbpassword = ""
_dbhost = ""

SQLALCHEMY_DATABASE_URI = 'mysql://'+_dbusername+':'+_dbpassword+'@'+_dbhost+'/'+_dbname
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'WHYSHOULDITELLYOU?'

#each server I think needs it's own application
WOT_API_KEYS = {'eu': '',
                'na': '',
                'ru': '',
                'kr': '',
                'asia': ''}


MEDIA_FOLDER = 'media'
REPLAY_FOLDER = os.path.join(MEDIA_FOLDER, 'replays')
CLAN_ICONS_FOLDER = os.path.join(MEDIA_FOLDER, 'clan-icons')