from datetime import datetime, timedelta
import decimal
import pytz
import xmltodict
import csv


from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from django.db.models import Q
from django.utils import timezone

from config import celery_app

from apps.fantasy import requests
from apps.fantasy.models import Athlete, Game, GameAthleteStat, GameTeam, Team
from apps.core import utils

User = get_user_model()

athlete_ids = [10009104, 10001087, 10008455, 10003268, 10000040, 10001958, 10009269, 10008438, 10000029, 10007421, 10006276, 10006099, 10009865, 10001105, 10007068, 10009589, 10005913, 10005250, 10006790, 10000780, 10005445, 10001961, 10000689, 10006622, 10001133, 10006826, 10003340, 10000809, 10001862, 10005377, 10005480, 10005839, 10000981, 10007010, 10006953, 10008662, 10006969, 10007647, 10006492, 10006717, 10006354, 10007075, 10009032, 10001270, 10001261, 10007419, 10006518, 10006394, 10006417, 10006807, 10008608, 10000381, 10009500, 10008369, 10007008, 10001072, 10000249, 10000637, 10005751, 10005910, 10000164, 10000165, 10000177, 10000453, 10001896, 10007062, 10001940, 10003163, 10003298, 10001827, 10000839, 10001161, 10000837, 10008360, 10006571, 10007641, 10008525, 10002001, 10008694, 10005307, 10006046, 10007727, 10006940, 10000492, 10009344, 10000084, 10000343, 10009296, 10002113, 10001182, 10001305, 10003212, 10000151, 10005302, 10001207, 10002054, 10008206, 10000258, 10006462, 10006154, 10000633, 10008437, 10000261, 10000998, 10008721, 10010464, 10006960, 10003133, 10001154, 10005879, 10005654, 10005575, 10000469, 10007024, 10008325, 10009298, 10001945, 10000312, 10000534, 10006804, 10002075, 10007359, 10007121, 10006212, 10000686, 10007781, 10002115, 10007028, 10006353, 10007245, 10000060, 10007294, 10006718, 10006506, 10008190, 10006695, 10006611, 10006439, 10005586, 10001910, 10010180, 10000352, 10005878, 10006088, 10001926, 10005660, 10009350, 10007055, 10007106, 10009253, 10007061, 10006418, 10000405, 10000601, 10002076, 10003204, 10005353, 10006345, 10006371, 10006344, 10006157, 10006637, 10007070, 10007277, 10000440, 10005351, 10005352, 10005835, 10005998, 10006172, 10007115, 10006871, 10007011, 10000494, 10000213, 10005308, 10000133, 10000438, 10011494, 10000301, 10006614, 10001871, 10007675, 10005650, 10006112, 10000155, 10009262, 10010729, 10007048, 10000845, 10000485, 10000719, 10003328, 10005405, 10000357, 10005589, 10006007, 10000481, 10006868, 10007148, 10007152, 10009010, 10009354, 10009116, 10003360, 10000432, 10007637, 10008767, 10007231, 10010605, 10002013, 10007427, 10000525, 10000353, 10005530, 10002059, 10001369, 10009140, 10010332, 10001901, 10008618, 10009338, 10007589, 10000613, 10005970, 10006760, 10009274, 10005210, 10008667, 10000600, 10008984, 10001361, 10000484, 10007049, 10008331, 10001132, 10005922, 10000768, 10007604, 10006662, 10006893, 10006902, 10000805, 10008769, 10002061, 10007341, 10007263, 10008338, 10007085, 10000176, 10000041, 10000077, 10000640, 10001091, 10001955, 10002094, 10003122, 10003192, 10007125, 10007046, 10003314, 10001325, 10005607, 10000618, 10000555, 10002049, 10000364, 10007299, 10000225, 10006085, 10000270, 10005191, 10000346, 10005472, 10007153, 10000685, 10009327, 10001946, 10005534, 10009155, 10007256, 10005448, 10008537, 10008429, 10008679,
               10007082, 10007151, 10001179, 10005433, 10000691, 10001010, 10006841, 10002074, 10007200, 10000539, 10000082, 10001889, 10008980, 10008358, 10006837, 10007058, 10007041, 10006935, 10007274, 10005264, 10010721, 10005288, 10001934, 10001918, 10005493, 10000775, 10000779, 10000857, 10007040, 10003219, 10009300, 10006008, 10007050, 10008431, 10000886, 10000095, 10010317, 10010327, 10006850, 10001077, 10001907, 10001911, 10005542, 10005722, 10006033, 10000900, 10001009, 10001085, 10000437, 10000770, 10006775, 10007009, 10007367, 10000787, 10000330, 10000426, 10000880, 10012307, 10005249, 10000217, 10002087, 10001966, 10000690, 10001313, 10005406, 10000777, 10007554, 10007117, 10001865, 10000397, 10005476, 10007655, 10000970, 10000986, 10008677, 10006466, 10002077, 10007398, 10006195, 10006200, 10001264, 10007090, 10006682, 10001971, 10003376, 10008439, 10006535, 10007096, 10006568, 10005569, 10002091, 10000242, 10008483, 10007035, 10006118, 10002005, 10005787, 10002093, 10000675, 10000731, 10001365, 10000439, 10006124, 10000859, 10009271, 10009878, 10007287, 10002082, 10008357, 10007006, 10000807, 10005232, 10008281, 10000746, 10007228, 10006053, 10007765, 10007111, 10005309, 10002045, 10005366, 10000344, 10006867, 10006512, 10005919, 10005664, 10006540, 10006299, 10000247, 10009582, 10009636, 10007144, 10006198, 10007217, 10007203, 10005672, 10000129, 10007416, 10007562, 10000530, 10001053, 10001943, 10001271, 10007812, 10005633, 10003312, 10006242, 10000273, 10005368, 10001234, 10005311, 10005315, 10001248, 10004421, 10000215, 10001129, 10001130, 10001222, 10003177, 10000646, 10006977, 10009268, 10005773, 10001209, 10000813, 10000958, 10005772, 10006767, 10006907, 10001191, 10000284, 10000071, 10002099, 10007043, 10005680, 10006044, 10001947, 10006284, 10009303, 10000311, 10008490, 10005834, 10001939, 10009359, 10006863, 10007284, 10007135, 10000020, 10003325, 10007369, 10010374, 10009285, 10005822, 10008749, 10000031, 10003149, 10001166, 10000393, 10000406, 10005741, 10007017, 10005503, 10008529, 10006792, 10008292, 10012277, 10001162, 10001250, 10003259, 10007033, 10006945, 10008332, 10001902, 10008561, 10008373, 10006272, 10006421, 10006431, 10007224, 10008199, 10001086, 10005684, 10001083, 10005384, 10001225, 10008458, 10008477, 10006566, 10009346, 10008425, 10000335, 10006184, 10008743, 10000908, 10001979, 10002089, 10008989, 10009516, 10001088, 10000593, 10006136, 10005628, 10007553, 10000394, 10007126, 10008798, 10002058, 10001253, 10007025, 10007407, 10008318, 10000499, 10007013, 10007501, 10007259, 10006072, 10007244, 10007535, 10005661, 10001181, 10009628, 10001908, 10008834, 10007100, 10001993, 10000101, 10000628, 10010409, 10009612, 10007039, 10001350, 10003368, 10000955, 10006794, 10001094, 10005299, 10007310, 10007911, 10000529, 10000953, 10006634, 10008378, 10001127, 10006992, 10006805, 10000007, 10009288, 10005800, 10005808, 10000425]


@celery_app.task()
def update_team_scores():
    """Task for updating all active games' teams scores per day"""

    # Task will run every 11:55 PM EST / 12:55 PM (next day) Manila time, so subtract -1 to day to get previous day since default timezone of Django is Asia/Manila
    date_query = timezone.now() - timedelta(days=1)
    date_query = date_query.strftime('%Y-%b-%d').upper()

    now = timezone.now()

    url = 'stats/json/PlayerGameStatsByDate/' + date_query

    response = requests.get(url)

    if response['status'] == settings.RESPONSE['STATUS_OK']:
        athlete_data = utils.parse_athlete_stat_data(response['response'])

        games = Game.objects.filter(Q(start_datetime__lte=now) & Q(end_datetime__gte=now))

        for game in games:
            game_teams = game.teams.all()

            for game_team in game_teams:
                total_fantasy_score = 0
                game_assets = game_team.assets.all()

                for game_asset in game_assets:
                    athlete = game_asset.game_athlete.athlete

                    if athlete:
                        # Search athlete api id if it exists in today's game athletes
                        data = next((item for item in athlete_data if item["api_id"] == athlete.api_id), None)

                        if data:
                            total_fantasy_score += data['fantasy_score']

                game_team.fantasy_score += decimal.Decimal(total_fantasy_score)
                # game_team.save()
            GameTeam.objects.bulk_update(game_teams, ['fantasy_score'])

        return len(games)
    else:
        content = {
            "message": "Failed to fetch data from Stats Perform API",
            "response": response['response']
        }

        return content


@celery_app.task()
def update_athlete_stats():
    """Task for updating all athlete stats on the current season"""

    now = timezone.now()

    season = now.strftime('%Y').upper()
    # season = '2021'
    url = 'stats/json/PlayerSeasonStats/' + season + 'PRE'

    response = requests.get(url)

    if response['status'] == settings.RESPONSE['STATUS_OK']:
        athlete_data = utils.parse_athlete_stat_data(response['response'])

        new_athlete_stats = []
        existing_athlete_stats = []

        for athlete in athlete_data:
            athlete_obj = Athlete.objects.filter(api_id=athlete.get('api_id')).first()

            if athlete_obj:
                athlete_stat_obj = GameAthleteStat.objects.filter(Q(athlete=athlete_obj) & Q(season=season)).first()

                if athlete_stat_obj is None:
                    athlete_stat_obj = GameAthleteStat(
                        season=season,
                        athlete=athlete_obj,
                        fantasy_score=athlete.get('fantasy_score'),
                        singles=athlete.get('singles'),
                        doubles=athlete.get('doubles'),
                        triples=athlete.get('triples'),
                        home_runs=athlete.get('home_runs'),
                        runs_batted_in=athlete.get('runs_batted_in'),
                        walks=athlete.get('walks'),
                        hit_by_pitch=athlete.get('hit_by_pitch'),
                        stolen_bases=athlete.get('stolen_bases'),
                        position=athlete.get('position'),
                    )

                    new_athlete_stats.append(athlete_stat_obj)
                else:
                    athlete_stat_obj.fantasy_score = athlete.get('fantasy_score')
                    athlete_stat_obj.singles = athlete.get('singles')
                    athlete_stat_obj.doubles = athlete.get('doubles')
                    athlete_stat_obj.triples = athlete.get('triples')
                    athlete_stat_obj.home_runs = athlete.get('home_runs')
                    athlete_stat_obj.runs_batted_in = athlete.get('runs_batted_in')
                    athlete_stat_obj.walks = athlete.get('walks')
                    athlete_stat_obj.hit_by_pitch = athlete.get('hit_by_pitch')
                    athlete_stat_obj.stolen_bases = athlete.get('stolen_bases')
                    athlete_stat_obj.position = athlete.get('position')

                    existing_athlete_stats.append(athlete_stat_obj)

        if len(new_athlete_stats) > 0:
            GameAthleteStat.objects.bulk_create(new_athlete_stats, 20)
        if len(existing_athlete_stats) > 0:
            GameAthleteStat.objects.bulk_update(
                existing_athlete_stats,
                ['fantasy_score', 'singles', 'doubles', 'triples', 'home_runs',
                    'runs_batted_in', 'walks', 'hit_by_pitch', 'stolen_bases', 'position'],
                20
            )

        return(len(new_athlete_stats) + len(existing_athlete_stats))


@celery_app.task()
def sync_teams_data():
    """Task for syncing all teams data from sportsdata.io"""

    response = requests.get('scores/json/teams')

    if response['status'] == settings.RESPONSE['STATUS_OK']:
        teams_data = utils.parse_team_list_data(response['response'])

        for team in teams_data:
            Team.objects.update_or_create(
                api_id=team['api_id'],
                defaults={
                    'location': team['location'],
                    'name': team['name'],
                    'key': team['key'],
                    'primary_color': team['primary_color'],
                    'secondary_color': team['secondary_color']
                }
            )

        return len(teams_data)


@celery_app.task()
def sync_athletes_data():
    """Task for syncing all athlete data from sportsdata.io"""

    response = requests.get('scores/json/Players')

    if response['status'] == settings.RESPONSE['STATUS_OK']:
        athlete_data = utils.parse_athlete_list_data(response['response'])

        for athlete in athlete_data:
            team = Team.objects.get(api_id=athlete['team_id'])

            if athlete['is_active'] == 'Active':
                athlete['is_active'] = True
            else:
                athlete['is_active'] = False

            if athlete['is_injured'] is None:
                athlete['is_injured'] = False
            else:
                athlete['is_injured'] = True

            Athlete.objects.update_or_create(
                api_id=athlete['api_id'],
                defaults={
                    'first_name': athlete['first_name'],
                    'last_name': athlete['last_name'],
                    'position': athlete['position'],
                    'salary': athlete['salary'],
                    'jersey': athlete['jersey'],
                    'is_active': athlete['is_active'],
                    'is_injured': athlete['is_injured'],
                    'team': team
                }
            )

        return len(athlete_data)


@celery_app.task()
def init_athletes_data_csv():
    """Task for initializing all athlete data based on csv file"""
    with open('athletes.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            api_id = row[0]
            first_name = row[9]
            last_name = row[10]
            position = row[7]
            salary = row[22]
            jersey = row[5]
            team_key = row[4]
            is_active = row[2]
            is_injured = row[31]

            if is_active == 'Active':
                is_active = True
            else:
                is_active = False

            if is_injured == 'null':
                is_injured = False
            else:
                is_injured = True

            if salary == 'null':
                salary = None

            if jersey == 'null':
                jersey = None

            team = Team.objects.get(key=team_key)

            Athlete.objects.update_or_create(
                api_id=api_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'position': position,
                    'salary': salary,
                    'jersey': jersey,
                    'is_active': is_active,
                    'is_injured': is_injured,
                    'team': team
                }
            )


@celery_app.task(soft_time_limit=99999999, time_limit=99999999)
def generate_athlete_images():
    output_dir = 'athlete_images/'
    file_extension = '.svg'

    athletes = Athlete.objects.filter(Q(api_id__in=athlete_ids))

    for athlete in athletes:
        athlete_id = str(athlete.id)

        file_name = output_dir + athlete_id + file_extension

        f = open(file_name, 'w')
        svg = """
            <svg viewBox="0 0 132 175" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><linearGradient id="a" gradientUnits="userSpaceOnUse" x1="-.37" x2="139.96" y1=".24" y2="169.8"><stop offset="0" stop-color="#7e7e7e"/><stop offset="1" stop-color="#a4a4a4"/></linearGradient><linearGradient id="b" gradientUnits="userSpaceOnUse" x1="66.06" x2="132" y1="99.55" y2="99.55"><stop offset="0"/><stop offset=".19" stop-color="#0a0a0a"/><stop offset=".5" stop-color="#252525"/><stop offset=".91" stop-color="#505151"/><stop offset="1" stop-color="#5a5c5c"/></linearGradient><linearGradient id="c" gradientUnits="userSpaceOnUse" x1="9.14" x2="122.67" y1="139.36" y2="25.83"><stop offset="0" stop-color="#171718"/><stop offset="1" stop-color="#373839"/></linearGradient><linearGradient id="d" gradientUnits="userSpaceOnUse" x1="58.34" x2="115.79" y1="81.63" y2="24.19"><stop offset="0" stop-color="#171718" stop-opacity="0"/><stop offset=".21" stop-color="#1e1e1f" stop-opacity=".02"/><stop offset=".43" stop-color="#333334" stop-opacity=".1"/><stop offset=".65" stop-color="#575757" stop-opacity=".22"/><stop offset=".88" stop-color="#888" stop-opacity=".39"/><stop offset="1" stop-color="#a9a9a8" stop-opacity=".5"/></linearGradient><clipPath id="e"><path d="m100.82 43.06 1.6 2.06-1.78.26-1.44-1.86-1.44.21-.1 2.09-1.66.25.38-7.48 3-.44c1.8-.27 3 .41 3.17 1.83a2.79 2.79 0 0 1 -1.73 3.08zm0-2.67c-.1-.71-.65-1-1.51-.84l-1.33.2-.14 2.6 1.44-.21c1.09-.14 1.72-.78 1.52-1.75z"/></clipPath><clipPath id="f"><path d="m106.31 37.14-.37 7.48-1.69.25.31-6.09-1.45.21.07-1.39z"/></clipPath><image id="g" height="223" width="229" xlink:href="data:image/png;base64,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"/></defs><path d="m0 24.1 66.1-24.1 65.9 24.1v98c0 23.4-17.5 35.4-26.2 38.5l-39.7 14.4c-5.2-1.9-20.6-7.6-40.7-15.2s-25.3-28.3-25.4-37.7z" fill="url(#a)"/><path d="m66.1 0v6.88l61.14 22.26 4.76-5z" fill="#434343"/><path d="m0 24.1 4.66 4.55 61.44-21.77v-6.88z" fill="#232323"/><path d="m66.06 168v7l39.74-14.4s26.2-9.28 26.2-38.5v-98l-4.76 5-.61 89c-6.31 24.69-16.35 33-23.19 36.25-1.61.77-6.37 2.49-15.81 5.9-9.08 3.32-16.55 5.95-21.57 7.75z" fill="url(#b)"/><path d="m0 24.1 4.7 4.59q30.71 70 61.39 140.07v6.24l-39.9-14.86s-26.19-8.68-26.19-38.04z" fill="#333"/><path d="m5.41 29.18 60.71-21.94 60.38 22.42v88.6s1.35 27.22-23.14 36.17-37.31 13.57-37.31 13.57l-36.43-13s-24.21-8.64-24.21-33.27z" fill="url(#c)" stroke="#1b1b1b" stroke-miterlimit="10" stroke-width="1.5"/><path d="m4.66 28.66 61.45-22.22v-.14l-61.51 22.29z" fill="#444545"/><path d="m66.11 6.44v-.14l61.2 22.77-.07.07z" fill="#686868"/><text fill="#fff" font-family="Montserrat-BoldItalic, Montserrat" font-size="10" font-style="italic" font-weight="700" transform="matrix(.98922128 -.14642834 .14642834 .98922128 18.7 57.24)">27</text><path d="m8.28 31.57 57.86-21.09 57.3 21.36v84.82z" fill="url(#d)"/><path d="m58 164.07 40-39.6a4.53 4.53 0 0 1 3-1.36h11.51a3.62 3.62 0 0 0 2.52-1c1.06-1.09 8.57-8.57 8.57-8.57v1.77l-48 48-9.77 3.51z" fill="#bf2d47"/><path d="m43.8 159.22-11.23-4 16.74-16.69a4.82 4.82 0 0 1 3.39-1.39 5.12 5.12 0 0 0 4.51-1.48c2.07-2.05 47.52-47.52 47.52-47.52h-26.89l45.7-46v38.75z" fill="#055da8"/><g fill="#fff"><text font-family="Montserrat-BoldItalic, Montserrat" font-size="12" font-style="italic" font-weight="700" transform="matrix(.98922128 -.14642834 .14642834 .98922128 18.54 74.38)">MIKE</text><text font-family="Montserrat-BoldItalic, Montserrat" font-size="12" font-style="italic" font-weight="700" transform="matrix(.98922128 -.14642834 .14642834 .98922128 17.77 88.28)">TROOUT</text><text font-family="Montserrat-BoldItalic, Montserrat" font-size="10" font-style="italic" font-weight="700" transform="matrix(.98922128 -.14642834 .14642834 .98922128 18.25 118.58)">CF</text><path d="m18.71 105.63v1.02l8.42-1.27v-1.04z"/><path d="m60.44 33.06a9.13 9.13 0 0 1 -.88-3.54v-7.13h13.33v7.34a8.18 8.18 0 0 1 -4.45 7.12l-2.26 1.15a15.86 15.86 0 0 1 -3.9-2.4l1.3-2.27h3.22l3.2-5.62-1.62-2.8h-6.5l1.66 2.82h3.26l-1.65 2.81h-3.22z"/></g><g clip-path="url(#e)"><use transform="matrix(.09 0 0 .09 87.47 31.08)" xlink:href="#g"/></g><g clip-path="url(#f)"><use transform="matrix(.09 0 0 .09 87.5 31.06)" xlink:href="#g"/></g></svg>
        """

        image_dict = xmltodict.parse(svg)

        jersey = '00'

        if athlete.jersey:
            jersey = str(athlete.jersey)

        # Change first name
        image_dict['svg']['g'][0]['text'][0]['#text'] = athlete.first_name.upper()
        # Change last name
        image_dict['svg']['g'][0]['text'][1]['#text'] = athlete.last_name.upper()
        # Change primary color
        image_dict['svg']['path'][10]['@style'] = 'fill: #' + athlete.team.primary_color  # 'fill: #000000'
        # Change secondary color
        image_dict['svg']['path'][9]['@style'] = 'fill: #' + athlete.team.secondary_color  # 'fill: #ffffff'
        # Change position
        image_dict['svg']['g'][0]['text'][2]['#text'] = athlete.position
        # Change jersey number
        image_dict['svg']['text']['#text'] = jersey

        image_xml = xmltodict.unparse(image_dict)

        f.write(image_xml)
        f.close()

        f = open(file_name, 'rb')

        file = File(f)
        athlete.nft_image.save(athlete_id + file_extension, file)

        f.close()


@celery_app.task(soft_time_limit=99999999, time_limit=99999999)
def generate_jersey_images():
    output_dir = 'jersey_images/'
    file_extension = '.svg'

    athletes = Athlete.objects.filter(Q(api_id__in=athlete_ids))

    for athlete in athletes:
        athlete_id = str(athlete.id)

        file_name = output_dir + athlete_id + file_extension

        f = open(file_name, 'w')

        svg = """
            <svg id="Jersey_number" data-name="Jersey number" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 99.37 89.14">
                <defs>
                    <style>
                    .cls-1 {
                        font-size: 69.37px;
                        fill: #fff;
                        font-family: Montserrat-BoldItalic, Montserrat;
                        font-weight: 700;
                        font-style: italic;
                    }
                    </style>
                </defs>
                <text class="cls-1" transform="translate(10.07 71.15) rotate(-8.42)">27</text>
            </svg>
        """

        image_dict = xmltodict.parse(svg)

        jersey = '00'

        if athlete.jersey:
            jersey = str(athlete.jersey)

        image_dict['svg']['text']['#text'] = jersey

        image_xml = xmltodict.unparse(image_dict)

        f.write(image_xml)
        f.close()

        f = open(file_name, 'rb')

        file = File(f)
        athlete.jersey_image.save(athlete_id + file_extension, file)

        f.close()


@celery_app.task(soft_time_limit=99999999, time_limit=99999999)
def generate_name_images():
    output_dir = 'name_images/'
    file_extension = '.svg'

    athletes = Athlete.objects.filter(Q(api_id__in=athlete_ids))

    for athlete in athletes:
        athlete_id = str(athlete.id)

        file_name = output_dir + athlete_id + file_extension

        f = open(file_name, 'w')

        svg = """
           <svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 34.16 27.35">
                <defs>
                    <style>
                    .cls-1 {
                        font-size: 7px;
                        fill: #fff;
                        font-family: Montserrat-BoldItalic, Montserrat;
                        font-weight: 700;
                        font-style: italic;
                    }

                    .cls-2 {
                        letter-spacing: -0.01em;
                    }
                    </style>
                </defs>
                <text class="cls-1" transform="translate(1.88 11.15) rotate(-8.42)">MIKE</text>
                <text class="cls-1" transform="translate(1.12 25.05) rotate(-8.42)">TROUT</text>
            </svg>
        """

        image_dict = xmltodict.parse(svg)

        # Change first name
        image_dict['svg']['text'][0]['#text'] = athlete.first_name.upper()
        # Change last name
        image_dict['svg']['text'][1]['#text'] = athlete.last_name.upper()

        image_xml = xmltodict.unparse(image_dict)

        f.write(image_xml)
        f.close()

        f = open(file_name, 'rb')

        file = File(f)
        athlete.name_image.save(athlete_id + file_extension, file)

        f.close()


@celery_app.task(soft_time_limit=99999999, time_limit=99999999)
def generate_position_images():
    output_dir = 'position_images/'
    file_extension = '.svg'

    athletes = Athlete.objects.filter(Q(api_id__in=athlete_ids))

    for athlete in athletes:
        athlete_id = str(athlete.id)

        file_name = output_dir + athlete_id + file_extension

        f = open(file_name, 'w')

        svg = """
            <svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 15.78 16.8">
                <defs>
                    <style>
                    .cls-1 {
                        font-size: 8px;
                        font-family: Montserrat-BoldItalic, Montserrat;
                        font-weight: 700;
                        font-style: italic;
                    }

                    .cls-1, .cls-2 {
                        fill: #fff;
                    }
                    </style>
                </defs>
                <text class="cls-1" transform="translate(1.24 14.23) rotate(-8.42)">CF</text>
                <polygon class="cls-2" points="1.7 1.28 1.7 2.31 10.13 1.04 10.13 0 1.7 1.28"/>
            </svg>
        """

        image_dict = xmltodict.parse(svg)

        image_dict['svg']['text']['#text'] = athlete.position.upper()

        image_xml = xmltodict.unparse(image_dict)

        f.write(image_xml)
        f.close()

        f = open(file_name, 'rb')

        file = File(f)
        athlete.position_image.save(athlete_id + file_extension, file)

        f.close()
