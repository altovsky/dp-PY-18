# -*- coding: utf-8 -*-

import requests
import time


class VKUser:
    def __init__(self, user_id, token, sleeping_time):
        self.id = user_id
        self.token = token
        self.api_url = 'https://api.vk.com/method/'
        self.api_ver = 5.80
        self.sleeping_time = sleeping_time
        self.offset_value = 1000
        self.process_message = ''
        self.process_symbols = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']
        self.progress_output_circle = 0
        self.error_message = ''

    def progress_output(self):
        print(f'\r{self.process_message} '
              f'{self.process_symbols[self.progress_output_circle]} '
              f'{self.error_message}', end='')
        if self.progress_output_circle == len(self.process_symbols) - 1:
            self.progress_output_circle = 0
        else:
            self.progress_output_circle += 1

    def get_response_value(self, api_method, requests_parameters):
        while True:
            try:
                response_value = requests.get(
                    f'{self.api_url}{api_method}',
                    params=requests_parameters
                )

                if 'error' in response_value.json():
                    self.error_message = f'Ошибка {response_value.json()["error"]["error_msg"]}. Ожидаем...'
                    self.progress_output()
                    time.sleep(self.sleeping_time)
                    continue
                else:
                    self.error_message = ''
                    return response_value

            except Exception as Ex:
                self.error_message = f'Ошибка {Ex.args}. Ожидаем...'
                self.progress_output()
                time.sleep(self.sleeping_time)

    def get_friends(self):
        self.process_message = 'Получаем список друзей'
        self.error_message = ''
        self.progress_output()

        friends_data = self.get_response_value(
            api_method='friends.get',
            requests_parameters=dict(
                user_ids=self.id,
                fields='deactivated, type',
                access_token=self.token,
                v=self.api_ver
            )
        )

        print(f"\rСписок друзей получен. ∑ {friends_data.json()['response']['count']}.")
        return friends_data.json()['response']['items']

    def get_groups(self):
        self.process_message = 'Получаем список групп'
        self.error_message = ''
        self.progress_output()

        groups_list = []
        groups_data = self.get_response_value(
            api_method='groups.get',
            requests_parameters=dict(
                user_ids=self.id,
                extended=1,
                fields='members_count',
                access_token=self.token,
                v=self.api_ver
            )
        )

        groups_data_items = groups_data.json()['response']['items']
        for group_info in groups_data_items:
            groups_list.append(
                {
                    'name': group_info['name'],
                    'gid': group_info['id'],
                    'members_count': group_info['members_count']
                }
            )

            self.process_message = f'Получаем список групп. Получено {len(groups_list)}'
            self.progress_output()

        print(f"\rСписок групп получен. ∑ {groups_data.json()['response']['count']}.")
        return groups_list

    def get_group_info(self, group_id_num):
        self.process_message = 'Получаем информацию о группе'
        self.error_message = ''
        self.progress_output()

        group_data = self.get_response_value(
            api_method='groups.getById',
            requests_parameters=dict(
                user_ids=self.id,
                group_id=group_id_num,
                fields='name',
                access_token=self.token,
                v=self.api_ver
            )
        )

        return group_data.json()['response'][0]['name']

    def get_group_members(self, group_id_num):
        group_name = self.get_group_info(group_id_num)
        self.process_message = f'Получаем список членов группы <{group_name}.>'
        self.error_message = ''
        self.progress_output()

        offset = 0
        group_members_list = []
        while True:
            group_members_value = self.get_response_value(
                api_method='groups.getMembers',
                requests_parameters=dict(
                    group_id=group_id_num,
                    offset=offset,
                    access_token=self.token,
                    v=self.api_ver
                )
            )

            group_members_list += group_members_value.json()['response']['users']
            self.process_message = f'Получаем список членов группы <{group_name}>. Получено {len(group_members_list)}.'
            self.progress_output()

            if group_members_value.json()['response']['count'] == len(group_members_list):
                break
            else:
                offset += self.offset_value
                time.sleep(self.sleeping_time)

        print(f"\rГруппа <{group_name}> ∑ {group_members_value.json()['response']['count']}.")
        return group_members_list

    def get_correct_groups(self):
        correct_groups_list = []
        user_friends_list = self.get_friends()
        groups_list = self.get_groups()

        # time.sleep(self.sleeping_time)
        for group in groups_list:
            group_members = self.get_group_members(group['gid'])

            for friend in user_friends_list:
                if friend['id'] in group_members:
                    break

            correct_groups_list.append(
                {
                    'name': group['name'],
                    'gid': group['gid'],
                    'members_count': group['members_count']
                }
            )

            time.sleep(self.sleeping_time)

        return correct_groups_list


happy_one = VKUser(
    10579451,
    'f047c8e6863d9cc2ad0c03b140b55cf7c38a1dc5cfe66eb12e885af6f66050fcb2e68d4ad7f1fabe79b7f',
    0.34
)

correct_groups = happy_one.get_correct_groups()
print(f'Найдено групп: {len(correct_groups)}\n{correct_groups}')
