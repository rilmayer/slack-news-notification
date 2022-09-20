import re
import yaml
from typing import List, TypedDict
from logging import getLogger

import feedparser

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, 'r') as yml:
    config = yaml.load(yml, Loader=yaml.SafeLoader)

class Content(TypedDict):
    title: str
    url: str

def daily_news(logger, mock=False):
    rss_urls = config.get('RSS_URLS', [])
    logger.debug("RSS_URLS: {}".format(rss_urls))

    if mock:
        contents = [Content(title="This is a sample title.", url="https://example.com/")]
    else:
        contents = get_contents(rss_urls)
    logger.debug("contents: {}".format(contents))

    # Fillter by interesting words
    INTEREST_WORDS = config.get("INTEREST_WORDS", [])
    logger.debug("INTEREST_WORDS: {}".format(INTEREST_WORDS))
    if len(INTEREST_WORDS) > 0:
        filteres_contents = [content for content in contents if filter_content(content["title"], INTEREST_WORDS)]

    if len(filteres_contents) == 0:
        return contents
    else:
        return filteres_contents

def get_contents(rss_urls):
    if len(rss_urls) == 0:
        raise Exception("Please set at least one url.")

    contents = []
    n_entries = 15
    for rss_url in rss_urls:
        parse_countent = feedparser.parse(rss_url)
        for entry in parse_countent.entries[0:n_entries]:
            contents.append(
                Content(title=entry.title, url=entry.link)
            )
    return contents

def filter_content(content, keywords):
    if len(re.findall(re.compile('|'.join(keywords)), content)) > 0:
        return True
    else:
        return False
