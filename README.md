# X Following

Check your following list & review whether they are worth to be followed.

If you think it's useful, please star it. I will develop more features if I find out it's help you :).

## Features

What's the difference between this and directly check the following list on Twitter?

- It will help you to filter the public account, and only show you the private account.
- When it comes to the second time, you'll find it will remember your choice for whitelist and reduce your work.
- You can backup your followers list to a local file, and find out who unfollowed you.
- If you are banned by Twitter, your following list or followers list will be lost. But if you use this tool, at least you can backup them.
- If other people use this tool, more features will be added or we'll consider to make it a twitter app.

## Usage

install dependencies

```bash
pip install -r requirements.txt
```

copy secrets.py
  
```bash
cp secrets.example.py secrets.py
```

go to [Twitter](https://x.com/) and login, then open the developer tools and copy the cookie, authorization and x-csrf-token to secrets.py

> we will develop a better way to get these values if we find out if it's useful.

Backup your followers list

```bash
python backup_followers.py
```

Check your following list

```bash
python check_following.py
```

It will show you the following list, and you can choose:

- Guilty: It'll help you to unfollow the account and add it to the backlist.
- Not Guilty: It'll pass the account(for now😈).
- Whitelist: It'll add the account to the whitelist, and it'll not show up again.
- Profile: It'll open the profile page in browser.

***It's better to use iterm2 that can show the avatar of the user***

## TODO

[ ] Show latest tweet

[ ] Print who is unfollow you between backups
