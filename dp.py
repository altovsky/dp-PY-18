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
        self.progress_symbols = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']
        self.progress_output_cycle = 0
        self.progress_percent = 0
        self.error_message = ''
        # self.max_member_ids_request = 1
        self.max_member_ids_request = 500

    def progress_output(self):
        print(f'\r{self.progress_symbols[self.progress_output_cycle]} '
              f'{self.progress_percent}% '
              f'{self.process_message} '
              f'{self.error_message}', end='')
        if self.progress_output_cycle == len(self.progress_symbols) - 1:
            self.progress_output_cycle = 0
        else:
            self.progress_output_cycle += 1

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

        print(f"\rДрузья ∑ {friends_data.json()['response']['count']}")
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

        print(f"\rГруппы ∑ {groups_data.json()['response']['count']}")
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

    def is_member_of_group(self, user_group, user_friends):
        user_friends_ids_list = set()
        max_member_counter = 0
        user_friends_number = len(user_friends)
        for counter, friend in enumerate(user_friends):

            user_friends_ids_list.add(friend['id'])
            max_member_counter += 1

            if max_member_counter == self.max_member_ids_request \
                    or \
                    counter + 1 == user_friends_number:

                self.process_message = f'Проверяем группу <{user_group["name"]}.>'
                self.error_message = ''
                self.progress_output()

                is_member = self.get_response_value(
                    api_method='groups.isMember',
                    requests_parameters=dict(
                        group_id=user_group['gid'],
                        user_ids=user_friends_ids_list,
                        access_token=self.token,
                        v=self.api_ver
                    )
                )

                for each in is_member.json()['response']:
                    if each['member']:
                        return True

                time.sleep(self.sleeping_time)
                user_friends_ids_list = []

        return False

    def get_correct_groups(self):
        correct_groups_list = []
        user_friends_list = self.get_friends()
        groups_list = self.get_groups()

        for count, group in enumerate(groups_list):
            self.process_message = f'Проверяем группу <{group["name"]}.>'
            self.progress_percent = int(round(1/(len(groups_list)/100)*(count+1), 0))
            self.error_message = ''
            self.progress_output()

            if not self.is_member_of_group(group, user_friends_list):
                correct_groups_list.append(
                    {
                        'name': group['name'],
                        'gid': group['gid'],
                        'members_count': group['members_count']
                    }
                )

        return correct_groups_list


happy_one = VKUser(
    10579451,
    # 171691064,
    'eef6370405d8b09233cdebc90e5d149096ab9a3d0c94d17d510387226f1e87b300bcfd7118615c5e6d255',
    # 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae',
    0.3,
    # 0.0,
)

correct_groups = happy_one.get_correct_groups()
# print(f'\rНайдено групп, в которых нет друзей: {len(correct_groups)}\n{correct_groups}\n')
print(f'\rНайдено групп, в которых нет друзей: {len(correct_groups)}')
