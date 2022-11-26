import csv, requests, json

GAME_TYPES = [
    {"id": 2, "type": "Regular Season", "name": "regular_season"},
    {"id": 3, "type": "Playoffs", "name": "playoffs"}
]

def get_gms(id): 
    request = requests.get(f'https://records.nhl.com/site/api/general-manager-franchise-records?cayenneExp=gameTypeId={id}&include=generalManager.id')
    request = json.loads(request.text)
    return request['data']

SORT_BY = 'winPctg'

def rank_gms(type):
    GMS = get_gms(type['id'])
    gms_active = {"file_name": f"csv/gm/gms_active_{type['name']}.csv",
                    "list": [gm for gm in GMS if gm['activeGm']]}
    gms_all_time = {"file_name": f"csv/gm/gms_all_time_{type['name']}.csv",
                        "list": [gm for gm in GMS if gm['seasons'] > 1]}
    percentages_with_cup = []

    for gm_list in [gms_active, gms_all_time]:
        file_name = gm_list['file_name']
        gm_list = gm_list['list']
        unique_gms = []

        for gm in gm_list:
            name = gm['fullName']
            gm_stats = [gm for gm in gm_list if name == gm['fullName']]
            num = len(gm_stats)
            seasons = sum([gm['seasons'] for gm in gm_list if name == gm['fullName']])
            wins = sum([gm['wins'] for gm in gm_list if name == gm['fullName']])
            

            # Win percentages
            winPctg = sum([gm['winPctg'] for gm in gm_stats]) / num
            home_games = sum([gm['homeGames'] for gm in gm_stats])
            home_wins = sum([gm['homeWins'] for gm in gm_stats])
            homeWinPctg = home_wins / home_games
            road_games = sum([gm['roadGames'] for gm in gm_stats])
            road_wins = sum([gm['roadWins'] for gm in gm_stats])
            roadWinPctg = road_wins / road_games

            pointPctg = sum([gm['pointPctg'] for gm in gm_stats if gm['pointPctg']]) / num

            teams = [gm['teamName'] for gm in gm_list if name == gm['fullName']]
            cups = sum([gm['stanleyCups'] for gm in gm_list if name == gm['fullName']])

            unique_gm = {
                'fullName': name,
                'stanleyCups': cups,
                'teams': teams,
                'winPctg': round(winPctg, 3),
                'homeWinPctg': round(homeWinPctg, 3),
                'roadWinPctg': round(roadWinPctg, 3),
                'pointPctg': round(pointPctg, 3),
                'seasons': seasons,
                'wins': wins
            }

            if name not in [gm['fullName'] for gm in unique_gms]:
                unique_gms.append(unique_gm)

        sorted_win_pctg = sorted(unique_gms, key=lambda c: c[SORT_BY], reverse=True)
        num_gms = len(sorted_win_pctg)
        gms_with_cup = len([gm for gm in unique_gms if gm['stanleyCups'] > 0])
        percentages_with_cup.append(round(gms_with_cup / num_gms * 100, 2))

        with open(f'{file_name}', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['GM', 'Win %', 'Home Win %',
                            'Road Win %', 'Points %', 'Wins', 'Stanley Cups', 'Seasons', 'Teams'])
            for gm in sorted_win_pctg:
                writer.writerow([gm['fullName'],
                                gm['winPctg'],
                                gm['homeWinPctg'],
                                gm['roadWinPctg'],
                                gm['pointPctg'],
                                gm['wins'],
                                gm['stanleyCups'],
                                gm['seasons'],
                                gm['teams']])
        file.close()

    if type['id'] == 2:
        with open(f'csv/gm/gms_cup_winners.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['% Active with Cup', '% All-Time with Cup'])
            writer.writerow(percentages_with_cup)
        file.close()


def rank_gms_team(type):
    GMS = get_gms(type['id'])
    gms_active_team = {"file_name": f"csv/gm/gms_active_team_{type['name']}.csv",
                    "list": [gm for gm in GMS if gm['activeGm']]}
    gms_all_time_team = {"file_name": f"csv/gm/gms_all_time_team_{type['name']}.csv",
                        "list": [gm for gm in GMS if gm['seasons'] > 1]}

    for gm_list in [gms_active_team, gms_all_time_team]:
        file_name = gm_list['file_name']
        gm_list = gm_list['list']
        formatted_gm_list = []

        for gm in gm_list:
            name = gm['fullName']

            # Win percentages
            home_games = gm['homeGames']
            home_wins = gm['homeWins']
            homeWinPctg = home_wins / home_games if home_games > 0 else 0
            road_games = gm['roadGames']
            road_wins = gm['roadWins']
            roadWinPctg = road_wins / road_games if road_games > 0 else 0

            unique_gm = {
                'fullName': name,
                'stanleyCups': gm['stanleyCups'],
                'team': gm['teamName'],
                'winPctg': round(gm['winPctg'], 3),
                'homeWinPctg': round(homeWinPctg, 3),
                'roadWinPctg': round(roadWinPctg, 3),
                'pointPctg': round(gm['pointPctg'], 3),
                'wins': gm['wins'],
                'seasons': gm['seasons']
            }

            formatted_gm_list.append(unique_gm)

        sorted_win_pctg = sorted(formatted_gm_list, key=lambda gm: gm[SORT_BY], reverse=True)

        with open(f'{file_name}', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['GM', 'Win %', 'Home Win %',
                            'Road Win %', 'Points %', 'Wins', 'Seasons', 'Stanley Cups', 'Team'])
            for gm in sorted_win_pctg:
                writer.writerow([gm['fullName'],
                                gm['winPctg'],
                                gm['homeWinPctg'],
                                gm['roadWinPctg'],
                                gm['pointPctg'],
                                gm['wins'],
                                gm['seasons'],
                                gm['stanleyCups'],
                                gm['team']])
        file.close()

for type in GAME_TYPES:
    rank_gms(type)
    rank_gms_team(type)