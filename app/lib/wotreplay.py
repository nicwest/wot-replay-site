import struct
import json
import cPickle
import math
import os
import gzip
import zlib
import StringIO
from binascii import b2a_hex

from app.lib.blowfish import Blowfish


class WotReplay:
    def __init__(self, filename, static):

        self.validate = "12323411"
        self.BLOWFISH_KEY = ''.join(['\xDE', '\x72', '\xBE', '\xA0', '\xDE', '\x04', '\xBE', '\xB1',
                        '\xDE', '\xFE', '\xBE', '\xEF', '\xDE', '\xAD', '\xBE', '\xEF'])
        self.mode_list = [None, "Random", None, "Tank Company", "Special Battle", "Clan War", None, "7 Vs. 7"]
        self.finish_list = [None, "Extermination", "Base Capture", "Timeout", "Failure", "Technical"]
        self.countries = ["USSR", "Germany", "USA", "China", "France", "UK"]
        self.tanktypes = ["Unknown", "Light", "Medium", "Heavy", "Tank Destroyer", "Scumbag"]
        self.status_list = {
             1: 'Incomplete.',
             2: 'Incomplete (past 8.1), with \'Battle Result\' pickle.',
             3: 'Complete (pre 8.1).',
             4: 'Complete (past 8.1).',
             6: 'Bugged (past 8.1). Game crashed somewhere, second Json has game score',
             8: 'Bugged (past 8.1). Only first Json available, pickle from wrong replay',
             10: 'File too small to be a valid replay.',
             11: 'Invalid Magic number. This is not a valid wotreplay file.',
             12: 'Broken replay file, most likely game crashed while recording. It still has some (maybe valid) battle result data.',
             13: 'Broken replay file, cant recognize first block.',
             14: 'Broken replay file, cant recognize second block.',
             15: 'Broken replay file, cant recognize third block.',
             16: 'No compatible blocks found, can only process blocks 1-3',
             20: 'Something went wrong!',
             21: 'Could not open file',
             22: 'File Doesn\'t exist!'
        }

        th = open(os.path.join(static, 'data/tanks.json'))
        self.tankinfo = json.load(th)
        th.close()

        self.data = [None] * 3
        self.data_compressed = None


        self.status = 0
        self.mode = 0

        self.process_file(filename)

    def process_file(self, filename):

        # Check file exists
        if os.path.exists(filename):

            # Check if file is big enough to be a replay
            filesize = os.path.getsize(filename)
            if filesize > 12:
                # Open File
                if filename.endswith('gz'):
                    try:
                        fh = gzip.open(filename, 'rb')
                    except:
                        self.status = 21
                        pass
                else:
                    try:
                        fh = open(filename, 'rb')
                    except:
                        self.status = 21
                        pass
            else:
                self.status = 10
        else:
            self.status = 22

        # Check if file is valid replay
        try:
            valid = (fh.read(4)==self.validate.decode('hex'))
        except:
            self.status = 11
            valid = False
            pass


        if valid:
            while True:
                # Get replay blocks
                try:
                    blocks = struct.unpack("i",fh.read(4))[0]
                except:
                    self.status = 20
                    break

                # Check we have blocks
                if blocks == 0: self.status = 16; break

                # Assuming all games are post 8.1 set status
                if blocks == 1:
                    self.status = 1
                if blocks == 2:
                    self.status = 2
                if blocks == 3:
                    self.status = 4

                # Read first block
                first_size = struct.unpack("i",fh.read(4))[0]
                first_chunk = fh.read(first_size)

                # Check if JSON
                if first_chunk[0:1] != b'{': self.status =13; break

                # Pass it
                try:
                    self.data[0] = json.loads(first_chunk)
                except:
                    self.status = 13
                    break

                # If complete second JSON block will be here
                if self.status == 4:
                    second_size = struct.unpack("i",fh.read(4))[0]
                    second_chunk = fh.read(second_size)

                    # Check it's JSON
                    if second_chunk[0:1] != b'[': self.status =14; break

                    # Pass it
                    try:
                        self.data[1] = json.loads(second_chunk)
                    except:
                        self.status = 14
                        break

                # Complete or incomplete this should still be here
                if self.status == 4 or self.status == 2:
                    third_size = struct.unpack("i",fh.read(4))[0]
                    third_chunk = fh.read(third_size)

                    #this is a silly way of doing things but stringIO wasn't working...
                    try:
                        th = StringIO.StringIO()
                        th.write(third_chunk)
                        th.seek(0, 0)
                        third_chunk = cPickle.load(th)
                        th.close()
                        self.data[2] = third_chunk
                    except:
                        self.status = 15
                        break

                self.data_compressed = fh.read()

                break
        try:
            fh.close()
        except:
            pass

    def decrypt_file(self, data, offset=0):
        bc = 0
        pb = None
        bf = Blowfish(self.BLOWFISH_KEY)
        out = StringIO.StringIO()

        f = StringIO.StringIO(data)

        f.seek(offset)
        while True:
            b = f.read(8)
            if not b:
                break

            if len(b) < 8:
                b += '\x00' * (8 - len(b))  # pad for correct blocksize

            if bc > 0:
                db = bf.decrypt(b)
                if pb:
                    db = ''.join([chr(int(b2a_hex(a), 16) ^ int(b2a_hex(b), 16)) for a, b in zip(db, pb)])

                pb = db
                out.write(db)
            bc += 1
        out.seek(0,0)
        return out



    def decompress_file(self, data):
        out = StringIO.StringIO()
        out.write(zlib.decompress(data.read()))
        del data
        return out

    def get_replay_meta (self):
        if self.data_compressed:
            try:
                decfile = self.decrypt_file(self.data_compressed)
                outfile = self.decompress_file(decfile)
            except:
                return None, None, None

            f = outfile
            f.seek(12,0)
            version = f.read(struct.unpack("i", f.read(4))[0])
            f.seek(35,1)
            bs = struct.unpack("b", f.read(1))[0]
            player = f.read(bs)
            pos = f.tell()
            for i in range(13, 21):
                f.seek(pos + i, 0)
                try:
                    data = cPickle.load(f)
                    break
                except:
                    continue
                    # return None, None, None



            return player, version, data
        return None, None, None

    def dumpjson(self):
        print json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))

    def get_info(self):
        info = {
            'type': self.data[0]['battleType'],
            'modeReadable': self.mode_list[self.data[0]['battleType']],
            'version': self.data[0]['clientVersionFromExe'],
            'versionXML': self.data[0]['clientVersionFromXml'],
            'dateTime': self.data[0]['dateTime'],
            'gameplayID': self.data[0]['gameplayID'],
            'mapDisplayName': self.data[0]['mapDisplayName'],
            'mapName': self.data[0]['mapName'],
            'playerID': self.data[0]['playerID'],
            'playerName': self.data[0]['playerName'],
            'playerVehicle': self.data[0]['playerVehicle'],
            'status': self.status,

        }
        if self.data[2]:
            info['gameID'] = self.data[2]['arenaUniqueID']
            info['start'] = self.data[2]['common']['arenaCreateTime']
            info['end'] = self.data[2]['common']['arenaCreateTime'] + math.floor(self.data[2]['common']['duration'])
            info['duration'] = self.data[2]['common']['duration']
            info['lock'] = bool(self.data[2]['common']['vehLockMode'])
            info['bonusType'] = self.data[2]['common']['bonusType']
            info['finishReason'] = self.data[2]['common']['finishReason']
            info['finishReasonReadable'] = self.finish_list[self.data[2]['common']['finishReason']]
            info['winnerTeam'] = self.data[2]['common']['winnerTeam']
            info['victory'] = self.data[1][0]['isWinner'] > 0
        return info

    def format_vehicle(self, typeCompDescr):
        if typeCompDescr:
            countryID = typeCompDescr >> 4 & 15
            tankID = typeCompDescr >> 8 & 65535
            typeID = typeCompDescr & 15
            return countryID, tankID, typeID
        return 999, 999, 999


    def get_players(self):
        players = {}
        player_names = {}
        clans = {}

        teams = [[],[]]
        if self.data[2]:
            for playerID, player in self.data[2]['players'].items():
                players[playerID] = {
                    'name': player['name'],
                    'clan': player['clanAbbrev'],
                    'clanID': player['clanDBID'],
                    'team': player['team']
                }

                teams[player['team']-1].append(playerID)
                player_names[player['name']] = playerID

                if not player['clanDBID'] in clans.keys():
                    clans[player['clanDBID']] = {
                        'clan': player['clanAbbrev'],
                    }


            for vehicleID, vehicle in self.data[2]['vehicles'].items():
                pid = vehicle['accountDBID']
                players[pid]['vehicleID'] = vehicleID
                players[pid]['spotted'] = vehicle['spotted']
                players[pid]['dmgAT'] = vehicle['damageAssistedTrack']
                players[pid]['dmgAR'] = vehicle['damageAssistedRadio']
                players[pid]['killerID'] = vehicle['killerID']
                players[pid]['dmg'] = vehicle['damageDealt']
                players[pid]['decap'] = vehicle['droppedCapturePoints']
                players[pid]['cap'] = vehicle['capturePoints']
                players[pid]['deathReason'] = vehicle['deathReason']
                players[pid]['health'] = vehicle['health']
                players[pid]['kills'] = vehicle['kills']
                players[pid]['lifeTime'] = vehicle['lifeTime']
                players[pid]['tcd'] = vehicle['typeCompDescr']
                players[pid]['countryID'], players[pid]['tankID'], players[pid]['typeID'] = self.format_vehicle(vehicle['typeCompDescr'])

                if players[pid]['countryID'] < 999 and players[pid]['tankID'] < 999 and players[pid]['typeID'] < 999:
                    try:
                        vehicleInfo = (item for item in self.tankinfo if item["tankid"] == players[pid]['tankID'] and item["countryid"] == players[pid]['countryID']).next()
                        players[pid]['iconName'] = self.countries[vehicleInfo['countryid']].lower() + "-" + vehicleInfo['icon_orig']
                    except:
                        players[pid]['iconName'] = "noImage"
                else:
                    players[pid]['iconName'] = "noImage"


        return players, clans, teams

    def getReplayTitle(self):
        players, clans, teams = self.get_players()
        titleteams = [{}, {}]

        for team in teams:
            for playerid in team:
                player = players[playerid]

                if player['clan'] == '':
                    player['clan'] = 'No Friends'

                if player['clan'] in titleteams[player['team']-1]:
                    titleteams[player['team']-1][player['clan']] = titleteams[player['team']-1][player['clan']] + 1
                else:
                    titleteams[player['team']-1][player['clan']] = 1

        teams_sorted = [None, None]
        teams_sorted[0] = sorted(titleteams[0].items(), key=lambda x: x[1])
        teams_sorted[1] = sorted(titleteams[1].items(), key=lambda x: x[1])


        teamname_left = ' + '.join([x[0] for x in teams_sorted[0]])
        teamname_right = ' + '.join([x[0] for x in teams_sorted[1]])

        title = teamname_left + " Vs. " + teamname_right

        return title





    def debug(self):
        print self.get_info()
        for item in self.get_players():
            print item