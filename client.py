import requests
import json
from typing import Tuple, TypedDict, List, Dict

class MyUser(TypedDict):
    # id is the twitter user id (not the username)
    user_id: str
    # name is the display name
    name: str
    # screen_name is the twitter username
    screen_name: str
    avatar_image_url: str
    is_suspended: bool
    is_verified: bool
    is_protected: bool
    is_auth_valid: bool

class TimelineUserEntitiesDescription(TypedDict):
    urls: List[Dict[str, str]]

class TimelineUserEntitiesURL(TypedDict):
    urls: List[Dict[str, str]]

class TimelineUserEntities(TypedDict):
    description: TimelineUserEntitiesDescription
    url: TimelineUserEntitiesURL

class TimelineUserLegacy(TypedDict):
    followed_by: bool
    following: bool
    can_dm: bool
    can_media_tag: bool
    created_at: str
    default_profile: bool
    default_profile_image: bool
    description: str
    entities: TimelineUserEntities
    fast_followers_count: int
    favourites_count: int
    followers_count: int
    friends_count: int
    has_custom_timelines: bool
    is_translator: bool
    listed_count: int
    location: str
    media_count: int
    name: str
    normal_followers_count: int
    pinned_tweet_ids_str: List[str]
    possibly_sensitive: bool
    profile_banner_url: str
    profile_image_url_https: str
    profile_interstitial_type: str
    screen_name: str
    statuses_count: int
    translator_type: str
    url: str
    verified: bool
    want_retweets: bool
    withheld_in_countries: List[str]

class TimelineUser(TypedDict):
    __typename: str
    id: str
    rest_id: str
    affiliates_highlighted_label: Dict
    has_graduated_access: bool
    is_blue_verified: bool
    profile_image_shape: str
    legacy: TimelineUserLegacy


class FollowingUser(TimelineUser, TimelineUserLegacy, TypedDict):
    raw: TimelineUser


class TwitterClient:

    def __init__(self, authorization_token, cookie_value, csrf_token):
        self.authorization_token = authorization_token
        self.cookie_value = cookie_value
        # self.client_transaction_id = client_transaction_id
        self.csrf_token = csrf_token
        self.current_user_info = {}
        self.users = []
        self.session = requests.Session()

    def get_auth_headers(self, referer='https://twitter.com/'):
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh,zh-CN;q=0.9,en;q=0.8,en-US;q=0.7',
            'authorization': f'Bearer {self.authorization_token}',
            'content-type': 'application/json',
            'cookie': self.cookie_value,
            'dnt': '1',
            'referer': referer,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # 'x-client-transaction-id': self.client_transaction_id,
            'x-csrf-token': self.csrf_token,
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }

        return headers
    
    def get_multi_user_info(self) -> List[MyUser]:
        self.session.headers.update(self.get_auth_headers())
        response = self.session.get('https://api.twitter.com/1.1/account/multi/list.json')
        data = response.json()
        self.users = data['users']
        return self.users
    
    def set_current_user_info(self, user: MyUser):
        self.current_user_info = user

    def get_following_by_graphql(self, max=20, cursor="") -> Tuple[List[FollowingUser], str]:
        if not self.current_user_info:
            raise Exception('No current user info')

        variables_dict = {
            "userId": self.current_user_info["user_id"],
            "count": max,
            "includePromotedContent": False
        }

        if cursor:
            variables_dict["cursor"] = cursor

        features_dict = {
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_home_pinned_timelines_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": False,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }

        referer = f'https://twitter.com/{self.current_user_info["screen_name"]}/following'

        response = requests.get(
            'https://twitter.com/i/api/graphql/8cyc0OKedV_XD62fBjzxUw/Following',
            headers=self.get_auth_headers(referer),
            params={
                'variables': json.dumps(variables_dict),
                'features': json.dumps(features_dict)
            }
        )

        # Handle the response
        if response.ok:
            json_response = response.json()
            # Process the json_response as needed
            instructions: List = json_response["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
            # find type == "TimelineAddEntries" instruction
            instruction = next((item for item in instructions if item["type"] == "TimelineAddEntries"), None)
            entries = instruction["entries"]

            def user_valid(user) -> bool:
                return "itemContent" in user["content"]

            def map_entry_to_user(user) -> FollowingUser:
                user: TimelineUser = user["content"]["itemContent"]["user_results"]["result"]
                return {
                    **user,
                    **user["legacy"],
                    "raw": user,
                }
            
            users = list([map_entry_to_user(user) for user in entries if user_valid(user)])

            # filter cursors
            cursors = list([user["content"] for user in entries if "content" in user and user["content"]["entryType"] == "TimelineTimelineCursor"])
            # top_cursor = next((c["value"] for c in cursors if c["cursorType"] == "Top"]), None)
            bottom_cursor = next((c["value"] for c in cursors if c["cursorType"] == "Bottom"), None)

            return users, bottom_cursor

        else:
            response.raise_for_status()

    def get_all_following_by_graphql(self, singe_max=50) -> List[FollowingUser]:
        users = []
        cursor = ""
        while True:
            print(f"fetching {singe_max} users, cursor: {cursor}, total: {len(users)}")
            new_users, cursor = self.get_following_by_graphql(singe_max, cursor)
            users.extend(new_users)
            if not cursor or len(new_users) <= 1:
                break
        return users

    def unfollow(self, following: FollowingUser):
        self.session.headers.update(self.get_auth_headers())
        response = self.session.post(
            f'https://api.twitter.com/1.1/friendships/destroy.json',
            params={
                'include_profile_interstitial_type': 1,
                'include_blocking': 1,
                'include_blocked_by': 1,
                'include_followed_by': 1,
                'include_want_retweets': 1,
                'include_mute_edge': 1,
                'include_can_dm': 1,
                'include_can_media_tag': 1,
                'include_ext_has_nft_avatar': 1,
                'include_ext_is_blue_verified': 1,
                'include_ext_verified_type': 1,
                'include_ext_profile_image_shape': 1,
                'skip_status': 1,
                'user_id': following["rest_id"],
            },
        )
        return response.json()
