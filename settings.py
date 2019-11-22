''' Configuration file for the program '''
from types import SimpleNamespace


def get_settings():
    ''' Parses the settings locally or from the server according to the debug value '''
    settings_ = {
        'region': 'EUW',
        'locale': 'en_GB',
        'log_time_format': '%H:%M:%S',
        'summoner_icon_id': 23,
        'riot_client_services_path': 'E:/Riot Games/Riot Client/RiotClientServices.exe',
        'league_client_path': 'E:/Riot Games/League of Legends/LeagueClient.exe',
        'league_client_process': 'LeagueClient.exe',
        'riot_client_process': 'RiotClientServices.exe',
        'riot_client_config': '~/AppData/Local/Riot Games/Riot Client/Config',
        'game_process': 'League of Legends.exe',
        'bug_splat_process': 'BsSndRpt.exe',
        'connection_retry_count': 180,
        'heartbeat_send_interval': 20,
        'champions': [51, 22, 15, 17, 18, 21],
        'buy_list': [22, 15, 17, 18],
        'rewards_groups': {
            'npe_rewards_login_v1_step1': {
                'choice': 'caitlyn_group',
                'name': 'Caitlyn',
                'disabled': False
            },
            'npe_rewards_login_v1_step2': {
                'choice': 'illaoi_group',
                'name': 'Illaoi',
                'disabled': False
            },
            'npe_rewards_login_v1_step3': {
                'choice': 'brand_group',
                'name': 'Brand',
                'disabled': False
            },
            'npe_rewards_login_v1_step4': {
                'choice': 'thresh_group',
                'name': 'Thresh',
                'disabled': False
            },
            'npe_rewards_login_v1_step5': {
                'choice': 'ekko_group',
                'name': 'Ekko',
                'disabled': False
            },
            'prestige_02_v3': {
                'choice': 'missfortune_group',
                'name': 'Miss Fortune',
                'disabled': False
            }
        },
        "level_x": 170,
        "level_y": 465,
        "level_search_thresh": 95.00,
        "event_search_thresh": 90.00,
        "obj_search_thresh": 99.96,
        "map_search_thresh": 95.00,
        "buy_wait_interval": 1,
    }
    return SimpleNamespace(**settings_)
