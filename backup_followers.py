from datetime import datetime
import json

from colorama import init

from common_cli import select_account
from client import client
from compare_followers import compare_followers_with_interact, list_all_followers_file, load_followers_file

# Initialize Colorama
init(autoreset=True)

def save_followers():
    select_account()
    followers = client.get_all_followers_by_graphql(50)
    now = datetime.now()
    name = client.get_current_user_info()['screen_name']
    with open(f'cache/followers-{name}-{now}.json', 'w') as f:
        json.dump(followers, f)

    print("\n\ncompare followers...\n")
    files = list_all_followers_file()
    files = list(filter(lambda x: x['user'] == name, files))
    files.sort(key=lambda x: x['time'])

    if len(files) < 1:
        print("No enough files to compare")
        return

    print("last file: " + files[-1]['path'])
    last_followers = load_followers_file("cache/" + files[-1]['path'])

    compare_followers_with_interact(last_followers, followers)


if __name__ == '__main__':
    save_followers()

