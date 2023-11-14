import json
from typing import List

from client import client, FollowingUser
from common_cli import select_account, trials
from back_white_list import filter_not_in_whitelist, filter_not_in_blacklist


FOLLOWING_CACHE_PATH = 'cache/followings.json'

def load_followings():
    try:
        with open(FOLLOWING_CACHE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return False


def get_all_followings(force_update=False):

    followings = load_followings()

    if followings and not force_update:
        return followings

    followings = client.get_all_following_by_graphql(50)

    print("saving followings...")

    with open('cache/followings.json', 'w') as f:
        json.dump(followings, f)

    return followings


def filter_one_way_followings(followings: List[FollowingUser]):
    one_way_followings = []
    for following in followings:
        if "followed_by" not in following or not following["followed_by"]:
            one_way_followings.append(following)
    return one_way_followings


def is_public_account(following: FollowingUser):
    if following["verified"]:
        return True
    followers_count = following.get("followers_count", 0)
    following_count = following.get("following_count", 0)
    if following_count < 100 and followers_count > 2000:
        return True
    if following_count == 0:
        return False
    return followers_count / following_count > 30


def filter_not_public_accounts(followings: List[FollowingUser]):
    return [following for following in followings if not is_public_account(following)]


def main_trails():
    select_account()
    followings = get_all_followings()
    subjects = filter_one_way_followings(followings)
    subjects = filter_not_public_accounts(subjects)
    subjects = filter_not_in_whitelist(subjects)
    subjects = filter_not_in_blacklist(subjects)

    trials(subjects)


if __name__ == '__main__':
    main_trails()

