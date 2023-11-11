import json
from os import system
from typing import List
from client import FollowingUser, TwitterClient
from secret import AUTHORIZATION_TOKEN, COOKIE_VALUE, CSRF_TOKEN
import webbrowser

FOLLOWING_CACHE_PATH = 'cache/followings.json'
WHITELIST_PATH = 'cache/whitelist.json'

client = TwitterClient(
    authorization_token=AUTHORIZATION_TOKEN,
    cookie_value=COOKIE_VALUE,
    csrf_token=CSRF_TOKEN,
)

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

    users = client.get_multi_user_info()
    client.set_current_user_info(users[0])

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


def load_whitelist() -> List[FollowingUser]:
    try:
        with open(WHITELIST_PATH, 'r') as f:
            return [json.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return []


def save_whitelist(following: FollowingUser):
    with open(WHITELIST_PATH, 'a') as f:
        f.write(json.dumps(following) + '\n')


def filter_not_in_white_list(followings: List[FollowingUser]):
    white_list = load_whitelist()
    hash_screen_name = {following['screen_name']: following for following in white_list}
    hash_id = {following['id']: following for following in white_list}
    def is_in_whitelist(following: FollowingUser):
        return following['screen_name'] in hash_screen_name or following['id'] in hash_id
    return [following for following in followings if not is_in_whitelist(following)]


LINE_STR = "-------------------------"

def trial_single(following: FollowingUser):
    is_verify = following.get('is_blue_verified', None) or following.get('is_verified', None)
    print(f"{following['name']} (@{following['screen_name']}) {'✅' if is_verify else ''}")
    print(f"{following['description']}")
    print(f"{following.get('friends_count', 'x')} following, {following.get('followers_count', 'x')} followers")
    print(f"https://twitter.com/{following['screen_name']}")
    while True:
        print(f"\n\n{LINE_STR}\n\nGuilty or not Guilty?")
        print(f"( [g]uilty / [n]ot guilty / [w]hitelist / open [p]rofile / [q]uit )")
        choice = input(f"Your Choice: ")
        choice = choice.lower()
        if choice == 'g':
            print(f"Guilty! {following['name']} (@{following['screen_name']}) Unfollowed!")
            client.unfollow(following)
            break
        elif choice == 'n':
            print(f"Not Guilty! {following['name']} (@{following['screen_name']}) Keep Following (for now...)")
            break
        elif choice == 'w':
            print(f"Whitelisted! {following['name']} (@{following['screen_name']})")
            save_whitelist(following)
            break
        elif choice == 'p':
            print(f"Opening Profile... {following['name']} (@{following['screen_name']})")
            webbrowser.open(f"https://twitter.com/{following['screen_name']}")
        elif choice == 'q':
            print(f"Quit! {following['name']} (@{following['screen_name']})")
            system.exit(0)
            break

    input("Press Enter to continue...")

def trials(subjects: List[FollowingUser]):
    length = len(subjects)
    for idx, subject in enumerate(subjects):
        # clear screen
        system('clear')
        print(f"Here is the {idx+1}/{length} subject:\n\n{LINE_STR}\n\n")
        trial_single(subject)


def main():
    followings = get_all_followings()
    subjects = filter_one_way_followings(followings)
    subjects = filter_not_public_accounts(subjects)
    subjects = filter_not_in_white_list(subjects)

    trials(subjects)


if __name__ == '__main__':
    main()

