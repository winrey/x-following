from datetime import datetime
from dateutil import parser
import json
import os
import re
from typing import List, TypedDict

from client import FollowingUser


class FollowerFiles(TypedDict):
    path: str
    user: str
    time: datetime


def list_all_followers_file():
    # list all files in cache folder
    files = os.listdir('cache')

    results = []

    pattern = re.compile(r'followers-(.+)-(.+)\.json')

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

    return src_set - dst_set


def load_followers_file(path: str) -> List[FollowingUser]:
    with open(path, 'r') as f:
        return json.load(f)

def main():
    files = list_all_followers_file()
    files.sort(key=lambda x: x['time'])

    src = load_followers_file("cache/" + files[-2]['path'])
    dst = load_followers_file("cache/" + files[-1]['path'])

    diff = compare_followers(src, dst)

    print(f'Followers diff: {len(diff)}')

    for user_id in diff:
        print(user_id)


if __name__ == '__main__':
    main()
