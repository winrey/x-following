from datetime import datetime
from dateutil import parser
import json
import os
import re
from typing import List, TypedDict

from client import FollowingUser
from common_cli import trials


class FollowerFiles(TypedDict):
    path: str
    user: str
    time: datetime


def list_all_followers_file():
    # list all files in cache folder
    files = os.listdir('cache')

    results = []

    pattern = re.compile(r'followers-([^\-]+)-(.+)\.json')

    for file in files:
        match = pattern.match(file)
        if match:
            user = match.group(1)
            time = parser.parse(match.group(2))
            results.append(FollowerFiles(path=file, user=user, time=time))

    return results


def compare_followers(src: List[FollowingUser], dst: List[FollowingUser]):
    src_ids = [user['screen_name'] for user in src]
    dst_ids = [user['screen_name'] for user in dst]

    src_set = set(src_ids)
    dst_set = set(dst_ids)

    result_name = src_set - dst_set

    result = list([x for x in src if x['screen_name'] in result_name])
    return result


def load_followers_file(path: str) -> List[FollowingUser]:
    with open(path, 'r') as f:
        return json.load(f)


def compare_followers_with_interact(src: List[FollowingUser], dst: List[FollowingUser]):
    diff = compare_followers(src, dst)

    print(f'Followers diff: {len(diff)}')

    for user in diff:
        print(f"{user['name']} (@{user['screen_name']}) - https://twitter.com/{user['screen_name']}")

    key = input("\n\nStart Trial? ([y]/n): ")

    if key == 'n':
        return

    trials(diff)


def main():
    files = list_all_followers_file()

    all_users = set()
    for file in files:
        all_users.add(file['user'])

    print(f'All users: {all_users}')
    name = input('Please input the screen name you want to compare: ')

    files = list(filter(lambda x: x['user'] == name, files))
    files.sort(key=lambda x: x['time'])

    src = load_followers_file("cache/" + files[-2]['path'])
    dst = load_followers_file("cache/" + files[-1]['path'])

    print('src: ' + files[-2]['path'])
    print('dst: ' + files[-1]['path'])

    print('\n')

    compare_followers_with_interact(src, dst)



if __name__ == '__main__':
    main()
