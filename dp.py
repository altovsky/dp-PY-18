# -*- coding: utf-8 -*-

import requests
import time

# USER_ID = 171691064
# TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
USER_ID = 10579451
TOKEN = '4293b67c340ee16f434ae2b4a7f3470efd5c82169ed92bb594b8d04fce9005454fb628de498fcd88c779b'

VK_API_URL = 'https://api.vk.com/method/'

VK_SLEEPING_TIME = 0.9
VK_OFFSET_VALUE = 1000

progress_output_curcle = 0
# PROCESS_SYMBOLS = ['|', '/', '-', '=', '-', '\\']
PROCESS_SYMBOLS = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']


def get_groups_info(token, user_id):

    while True:
        progress_output('Получаем список групп')
        groups_info_list = []
        groups_info_response = requests.get(
            f'{VK_API_URL}groups.get',
            params=dict(
                user_ids=user_id,
                extended=1,
                fields='members_count',
                access_token=token,
                v=5.80
            )
        )

        if 'error' in groups_info_response.json():
            progress_output(
                'Получаем список групп ',
                f'Ошибка {groups_info_response.json()["error"]["error_msg"]}. Ожидаем...'
            )
            time.sleep(VK_SLEEPING_TIME)
            continue
        else:
            for group_info in groups_info_response.json()['response']['items']:

                groups_info_list.append(
                    {
                        'name': group_info['name'],
                        'gid': group_info['id'],
                        'members_count': group_info['members_count']
                    }
                )
            print(f"\rСписок групп получен. ∑ {groups_info_response.json()['response']['count']}.")
            return groups_info_list


def get_group_members(token, group_id_num):
    offset = 0
    group_members_list = []

    while True:
        try:
            progress_output(f'Получаем список членов группы. Получено {len(group_members_list)}')
            group_members_response = requests.get(
                f'{VK_API_URL}groups.getMembers',
                params=dict(
                    group_id=group_id_num,
                    offset=offset,
                    access_token=token,
                    v=5.80
                )
            )
            if 'error' in group_members_response.json():
                progress_output(
                    f'Получаем список членов группы. Получено {len(group_members_list)} ',
                    f'Ошибка {group_members_response.json()["error"]["error_msg"]}. Ожидаем...'
                )
                time.sleep(VK_SLEEPING_TIME)
                continue
            else:
                group_members_list += group_members_response.json()['response']['users']
                if group_members_response.json()['response']['count'] == len(group_members_list):
                    break
                else:
                    offset += VK_OFFSET_VALUE
                    time.sleep(VK_SLEEPING_TIME)
        except Exception as Ex:
            print(Ex.args)
            time.sleep(VK_SLEEPING_TIME)
            continue

    print(f"\rСписок членов группы получен. ∑ {group_members_response.json()['response']['count']}.")
    return group_members_list


def progress_output(process_name, more_info=''):
    global progress_output_curcle

    print(f'\r{process_name} {PROCESS_SYMBOLS[progress_output_curcle]} {more_info}', end='')
    if progress_output_curcle == len(PROCESS_SYMBOLS)-1:
        progress_output_curcle = 0
    else:
        progress_output_curcle += 1


def get_user_friends(token, user_id):

    while True:
        progress_output('Получаем список друзей')
        response_user_friends = requests.get(
            f'{VK_API_URL}friends.get',
            params=dict(
                user_ids=user_id,
                # extended=1,
                fields='deactivated, type',
                access_token=token,
                v=5.80
            )
        )

        if 'error' in response_user_friends.json():
            progress_output(
                'Получаем список друзей',
                f"Ошибка - {response_user_friends.json()['error']['error_msg']} Повторяем попытку."
            )
            time.sleep(VK_SLEEPING_TIME)
            continue
        else:
            print(f"\rСписок друзей получен. ∑ {response_user_friends.json()['response']['count']}.")
            return response_user_friends.json()['response']['items']


valid_groups_list = []
user_friends_list = get_user_friends(TOKEN, USER_ID)
groups_info = get_groups_info(TOKEN, USER_ID)

time.sleep(VK_SLEEPING_TIME)

for group in groups_info:
    if group['members_count'] < 400:
        group_members = get_group_members(TOKEN, group['gid'])

        for friend in user_friends_list:
            if friend['id'] in group_members:
                break

        valid_groups_list.append(
            {
                'name': group['name'],
                'gid': group['gid'],
                'members_count': group['members_count']
            }
        )

        time.sleep(VK_SLEEPING_TIME)

print('valid_groups_list', '\n', valid_groups_list)
