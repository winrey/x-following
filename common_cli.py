import base64
from io import BytesIO
import os
import sys
from typing import List
import webbrowser

from colorama import init, Fore, Style
import requests
from PIL import Image

from client import FollowingUser, client
from back_white_list import save_blacklist, save_whitelist


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

# Initialize Colorama
init(autoreset=True)


def select_account():
    users = client.get_multi_user_info()
    choice = 0
    if len(users) > 1:
        print("Select Account:")
        for idx, user in enumerate(users):
            print(f"{idx+1}. {user['screen_name']}")
        choice = input("Which Account? Please input the number: ")
        choice = int(choice) - 1
    client.set_current_user_info(users[choice])

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
        os.system('clear')
        print(f"\n\t\t\t{f'Here is the {idx+1}/{length} subject:'}")
        print(f"\n\n{center_text(LINE_STR)}\n\n")
        trial_single(subject)
