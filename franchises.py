import csv, requests, json

GAME_TYPES = [
    {"id": 2, "type": "Regular Season", "name": "regular_season"},
    {"id": 3, "type": "Playoffs", "name": "playoffs"}
]

def get_franchise_stats(id): 
    request = requests.get(f'https://records.nhl.com/site/api/franchise-season-results?cayenneExp=franchiseId=34 and gameTypeId={id}&include=["season.conferencesInUse", "season.divisionsInUse"]&sort=seasonId&dir=ASC')
    request = json.loads(request.text)
    return request['data']

def list_franchise_records(type):
    FRANCHISE = get_franchise_stats(type['id'])
    file_name = f"csv/franchise/winPctg-{type['name']}.csv"
    seasons = []
    for f in FRANCHISE:
        start = str(f['seasonId'])[0:4]
        end = str(f['seasonId'])[4:]
        wins = f['wins']
        ties = f['ties']
        points = int(f['points']) if f['points'] != None else 0
        games_played = int(f['gamesPlayed'])
        total_points = games_played * 2
        win_pctg = round(wins/games_played, 3)
        pts_pctg = round(points/total_points, 3)
        
        
        season = {"years": f"{start}-{end}",
                  "GP": f['gamesPlayed'],
                  "W": f['wins'],
                  "L": f['losses'],
                  "OT": f['overtimeLosses'],
                  "winPctg": win_pctg,
                  "points": f['points'] if f['points'] != None else 0,
                  "ptsPctg": pts_pctg,
                  "playoffRound": f['playoffRound'] if f['playoffRound'] else None
                }
        seasons.append(season)
    
    with open(f'{file_name}', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Season',
                             'GP',
                             'W',
                             'L',
                             'OT',
                             'Win %',
                             'Points',
                             'Point %',
                             'Playoff Round'])
            for season in seasons:
                writer.writerow([
                    season['years'],
                    season['GP'],
                    season['W'],
                    season['L'],
                    season['OT'],
                    season['winPctg'],
                    season['points'],
                    season['ptsPctg'],
                    season['playoffRound']
                    ])
            file.close()

for type in GAME_TYPES:
    list_franchise_records(type)