from client import client


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
