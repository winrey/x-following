
import json
from typing import List

from client import FollowingUser


WHITELIST_PATH = 'cache/whitelist.json'
BLACKLIST_PATH = 'cache/blacklist.json'

def use_list(path: str):
    def load_list() -> List[FollowingUser]:
        try:
            with open(path, 'r') as f:
                return [json.loads(line) for line in f.readlines()]
        except FileNotFoundError:
            return []


    def save_list(following: FollowingUser):
        with open(path, 'a') as f:
            f.write(json.dumps(following) + '\n')


    def filter_not_in_list(followings: List[FollowingUser]):
        white_list = load_list()
        hash_screen_name = {following['screen_name']: following for following in white_list}
        hash_id = {following['id']: following for following in white_list}
        def is_in_whitelist(following: FollowingUser):
            return following['screen_name'] in hash_screen_name or following['id'] in hash_id
        return [following for following in followings if not is_in_whitelist(following)]

    return load_list, save_list, filter_not_in_list


_, save_whitelist, filter_not_in_whitelist = use_list(WHITELIST_PATH)
_, save_blacklist, filter_not_in_blacklist = use_list(BLACKLIST_PATH)

