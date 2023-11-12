import base64
from io import BytesIO
import json
from os import system
import os
import sys
from typing import List

from PIL import Image
import requests
import webbrowser
from colorama import init, Fore, Style

from client import client, FollowingUser
from common_cli import select_account

# Initialize Colorama
init(autoreset=True)

FOLLOWING_CACHE_PATH = 'cache/followings.json'
WHITELIST_PATH = 'cache/whitelist.json'
BLACKLIST_PATH = 'cache/blacklist.json'

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


BOLD = Style.BRIGHT
NORMAL = Style.NORMAL
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
RESET = Style.RESET_ALL

LINE_STR = "-------------------------"

# Function to center the text based on the terminal width
def center_text(text):
    term_width = os.get_terminal_size().columns
    return text.center(term_width)

def print_centered_description(description):
    term_width = os.get_terminal_size().columns
    max_line_length = term_width // 3  # Maximum length of the line is half the width of the terminal

    # Split the description into words
    words = description.split()

    # Initialize an empty line and list of lines
    line = ''
    lines = []

    # Build lines of appropriate length
    for word in words:
        # Check if adding the next word would exceed the max line length
        if len(line) + len(word) + 1 > max_line_length:
            lines.append(line)
            line = word
        else:
            line += ' ' + word if line else word

    # Add the last line if it's not empty
    if line:
        lines.append(line)

    # Print each line centered
    for line in lines:
        print(YELLOW + line.center(term_width) + RESET)


def display_image_iterm2_from_url(image_url, scale=0.1):
    response = requests.get(image_url)
    if response.status_code == 200:
        # 获取原始图片数据
        image_data = BytesIO(response.content)
        # 使用Pillow来加载图像
        image = Image.open(image_data)
        # 计算缩放后的新尺寸
        term_width = os.get_terminal_size().columns
        new_width = term_width * scale
        aspect_ratio = image.height / image.width
        new_height = aspect_ratio * new_width
        # 转换图片大小为整数
        new_width, new_height = int(new_width), int(new_height)
        # 缩放图像并再次编码为base64
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        buffered = BytesIO()
        resized_image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 使用 iTerm2 的专有转义序列来显示图片
        # 添加 padding 来尝试居中图片（这将不完全准确）
        padding = " " * ((term_width - new_width) // 2)
        print(padding + f'\x1b]1337;File=inline=1;width={new_width};preserveAspectRatio=1:{encoded_image}\a\n')
    else:
        print(f"Error: Unable to download image. Status code: {response.status_code}")


def print_following_info(following: FollowingUser):
    is_verify = following.get('is_blue_verified', None) or following.get('is_verified', None)
    personal_site = following.get('legacy', {}).get('entities', {}).get('url', {}).get('urls', [{}])[0].get('expanded_url', None)
    is_following = following.get('following', False)
    follow_by = following.get('followed_by', False)
    relation = '❤' if is_following and follow_by else '←' if follow_by else '→' if is_following else 'x'
    
    # Bold the name and handle, and add a checkmark or cross emoji based on verification status
    # Centered and styled text output
    display_image_iterm2_from_url(following['profile_image_url_https'])
    print(center_text(f"{BOLD}{following['name']}{RESET} (@{following['screen_name']}) {GREEN+'✅' if is_verify else RED+''}\n"))
    print_centered_description(following['description'])
    print()
    if personal_site:
        print(center_text(f"{CYAN}{personal_site}{RESET}"))
        print()
    print(center_text(f"{MAGENTA}{following.get('friends_count', 'x')} following, {following.get('followers_count', 'x')} followers"))
    print()
    print(center_text(f"DM: {following.get('can_dm', False) and '✅' or '❌'} | You {relation} 👤"))
    print(center_text(f"{BLUE}https://twitter.com/{following['screen_name']}{RESET}"))


def trial_single(following: FollowingUser):
    print_following_info(following)
    
    while True:
        print(f"\n\n{GREEN}{center_text(LINE_STR)}{RESET}\n\n")
        print(f"\t\t\tGuilty or not Guilty?")
        print(f"\t\t\t( {RED}[g]{RESET}uilty / {BLUE}[n]{RESET}ot guilty / {CYAN}[w]{RESET}hitelist / open {MAGENTA}[p]{RESET}rofile / {YELLOW}[q]{RESET}uit )")
        choice = input(f"\t\t\tYour Choice: ")
        choice = choice.lower()

        print()
        
        if choice == 'g':
            print(center_text(f"{RED}Guilty! {following['name']} (@{following['screen_name']}) Unfollowed!{RESET}"))
            client.unfollow(following)  # Uncomment this when you integrate with Twitter API
            save_blacklist(following)
            break
        elif choice == 'n':
            print(center_text(f"{BLUE}Not Guilty! {following['name']} (@{following['screen_name']}) Keep Following (for now...){RESET}"))
            break
        elif choice == 'w':
            print(center_text(f"{GREEN}Whitelisted! {following['name']} (@{following['screen_name']}){RESET}"))
            save_whitelist(following)  # Uncomment this when you integrate with Twitter API
            break
        elif choice == 'p':
            print(center_text(f"{CYAN}Opening Profile... {following['name']} (@{following['screen_name']}){RESET}"))
            webbrowser.open(f"https://twitter.com/{following['screen_name']}")
        elif choice == 'q':
            print(center_text(f"{YELLOW}Quit! {following['name']} (@{following['screen_name']}){RESET}"))
            sys.exit(0)
            break

    print()
    input(center_text("Press Enter to continue..."))


def trials(subjects: List[FollowingUser]):
    length = len(subjects)
    for idx, subject in enumerate(subjects):
        # clear screen
        system('clear')
        print(f"\n\t\t\t{f'Here is the {idx+1}/{length} subject:'}")
        print(f"\n\n{center_text(LINE_STR)}\n\n")
        trial_single(subject)


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

