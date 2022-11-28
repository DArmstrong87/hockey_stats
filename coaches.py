import csv, requests, json


GAME_TYPES = [
    {"id": 2, "type": "Regular Season", "name": "regular_season"},
    {"id": 3, "type": "Playoffs", "name": "playoffs"}
]
SORT_BY = 'winPctg'

def get_coaches(id):
    request = requests.get(f"https://records.nhl.com/site/api/coach-franchise-records?cayenneExp=gameTypeId={id}&include=coach.id")
    request = json.loads(request.text)
    return request['data']


def rank_coaches(type):
    COACHES = get_coaches(type['id'])
    coaches_active = {"file_name": f"csv/coach/coaches_active_{type['name']}.csv",
                    "list": [c for c in COACHES if c['activeCoach']]}
    coaches_all_time = {"file_name": f"csv/coach/coaches_all_time_{type['name']}.csv",
                        "list": [c for c in COACHES]}
    percentages_with_cup = []

    for coach_list in [coaches_active, coaches_all_time]:
        file_name = coach_list['file_name']
        coach_list = coach_list['list']
        unique_coaches = []

        for coach in coach_list:
            name = coach['coachName']
            coach_stats = [c for c in coach_list if name == c['coachName']]
            num = len(coach_stats)
            seasons = sum([c['seasons'] for c in coach_list if name == c['coachName']])
            wins = sum([c['wins'] for c in coach_list if name == c['coachName']])

            # Win percentages
            winPctg = sum([c['winPctg'] for c in coach_stats]) / num
            homeWinPctg = sum([c['homeWinPctg'] for c in coach_stats if c['homeWinPctg']]) / num
            roadWinPctg = sum([c['roadWinPctg'] for c in coach_stats if c['roadWinPctg']]) / num
            pointPctg = sum([c['pointPctg'] for c in coach_stats if c['pointPctg']]) / num

            teams = [c['teamName'] for c in coach_list if name == c['coachName']]
            cups = sum([c['stanleyCups'] for c in coach_list if name == c['coachName']])

            unique_coach = {
                'coachName': name,
                'stanleyCups': cups,
                'teams': teams,
                'winPctg': round(winPctg, 3),
                'homeWinPctg': round(homeWinPctg, 3),
                'roadWinPctg': round(roadWinPctg, 3),
                'pointPctg': round(pointPctg, 3),
                'seasons': seasons,
                'wins': wins
            }

            if name not in [c['coachName'] for c in unique_coaches]:
                unique_coaches.append(unique_coach)

        sorted_win_pctg = sorted(unique_coaches, key=lambda c: c[SORT_BY], reverse=True)
        num_coaches = len(sorted_win_pctg)
        coaches_with_cup = len([c for c in unique_coaches if c['stanleyCups'] > 0])
        percentages_with_cup.append(round(coaches_with_cup / num_coaches * 100, 2))

        with open(f'{file_name}', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Coach', 'Win %', 'Home Win %',
                            'Road Win %', 'Points %', 'Wins', 'Seasons', 'Stanley Cups', 'Teams'])
            for c in sorted_win_pctg:
                writer.writerow([c['coachName'],
                                c['winPctg'],
                                c['homeWinPctg'],
                                c['roadWinPctg'],
                                c['pointPctg'],
                                c['wins'],
                                c['seasons'],
                                c['stanleyCups'],
                                f"{c['teams']}"])
        file.close()

    if type['id'] == 2:
        with open(f'csv/coach/coaches_cup_winners.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['% Active with Cup', '% All-Time with Cup'])
            writer.writerow(percentages_with_cup)
        file.close()


def rank_coaches_team(type):
    COACHES = get_coaches(type['id'])
    coaches_active_team = {"file_name": f"csv/coach/coaches_active_team_{type['name']}.csv",
                        "list": [c for c in COACHES if c['activeCoach']]}
    coaches_all_time_team = {"file_name": f"csv/coach/coaches_all_time_team_{type['name']}.csv","list": [c for c in COACHES]}

    for coach_list in [coaches_active_team, coaches_all_time_team]:
        file_name = coach_list['file_name']
        coach_list = coach_list['list']
        formatted_coach_list = []

        for coach in coach_list:
            name = coach['coachName']

            coach = {
                'coachName': name,
                'stanleyCups': coach['stanleyCups'],
                'team': coach['teamName'],
                'winPctg': round(coach['winPctg'], 3),
                'homeWinPctg': round(coach['homeWinPctg'], 3) if coach['homeWinPctg'] else None,
                'roadWinPctg': round(coach['roadWinPctg'], 3) if coach['roadWinPctg'] else None,
                'pointPctg': round(coach['pointPctg'], 3) if coach['pointPctg'] else None,
                'wins': coach['wins'],
                'seasons': coach['seasons']
            }

            formatted_coach_list.append(coach)

        sorted_win_pctg = sorted(formatted_coach_list, key=lambda c: c[SORT_BY], reverse=True)

        with open(f'{file_name}', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Coach', 'Team', 'Win %', 'Home Win %',
                            'Road Win %', 'Points %', 'Wins', 'Seasons', 'Stanley Cups'])
            for c in sorted_win_pctg:
                writer.writerow([c['coachName'],
                                c['team'],
                                c['winPctg'],
                                c['homeWinPctg'],
                                c['roadWinPctg'],
                                c['pointPctg'],
                                c['wins'],
                                c['seasons'],
                                c['stanleyCups']
                                ])
        file.close()

for type in GAME_TYPES:
    rank_coaches(type)
    rank_coaches_team(type)
