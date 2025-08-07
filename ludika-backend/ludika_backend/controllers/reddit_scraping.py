import re

from ludika_backend.utils.config import get_config_value
import praw
from praw.models import Submission
from pydantic import BaseModel, field_validator

reddit = praw.Reddit(
    client_id=get_config_value("GenerativeAI", "reddit_client_id"),
    client_secret=get_config_value("GenerativeAI", "reddit_client_secret"),
    user_agent="Ludika/1.0 by u/Absolute_Trust",
)

SUBREDDITS = ("educationalgames", "gamebasedlearning")

SELF_POST_PATTERN = re.compile(r"^https://www\.reddit\.com/r/[a-zA-Z]*/comments")


class RedditPost(BaseModel):
    title: str
    url: str
    selftext: str

    @field_validator("url")
    def remove_self_links(cls, v):
        if SELF_POST_PATTERN.match(v):
            return None
        return v


def get_top_posts() -> list[RedditPost]:
    top_posts: list[Submission] = [
        i for sub in SUBREDDITS for i in reddit.subreddit(sub).top(limit=50, time_filter="all")
    ]

    return [RedditPost(title=post.title, url=post.url, selftext=post.selftext) for post in top_posts]
