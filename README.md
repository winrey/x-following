# X Following

Check your following list and assess if they're worth your attention.

If you find this tool helpful, give it a star. Your feedback is valuable, and with enough interest, I’ll develop more features.

## Features

Why use this instead of checking your following list on Twitter?

- Filters out public accounts to focus on private ones.
- Remembers your whitelist choices, saving you time on subsequent uses.
- Allows you to back up your following list locally to track unfollowers.
- In case of a Twitter ban, you won't lose your lists if they're backed up here.
- With wider use, more features will be considered, including a dedicated Twitter app.

## How to Use

Install dependencies:

```bash
pip install -r requirements.txt
```

Prepare your configuration file:

```bash
cp secrets.example.py secrets.py
```

Go to [Twitter](https://x.com/), sign in, then use the developer tools to copy your cookie, authorization, and x-csrf-token into `secrets.py`

> We're exploring better methods for obtaining these values if the tool proves useful.

Back up your followers list:

```bash
python backup_followers.py
```

Compare your followers list from the last backup to your current following list:

```bash
python compare_followers.py
```

Review your following list:

```bash
python check_following.py
```

You'll be presented with options for each account:

- **Guilty**: Unfollows the account and adds it to the blacklist.
- **Not Guilty**: Keeps the account as is for now.
- **Whitelist**: Adds the account to your whitelist so it won't appear again.
- **Profile**: Opens the user's profile page in your browser.

*Note: For an enhanced experience with user avatars, try using iTerm2.*

## Upcoming Features

- [ ] Display the latest tweet from each user.
- [ ] Notify you about who has unfollowed you since your last backup.
- [ ] Summarize your following accounts by LLM.
