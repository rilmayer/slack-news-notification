import re
import os
import sys
import json
import random
import logging
import urllib.request
from datetime import datetime, timedelta

# import 3rd party modules
sys.path.append('./lib')

import slackweb
import feedparser
from bs4 import BeautifulSoup


logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def lambda_handler(event, context):
    """This function call in AWS Lambda
    """
    res_list = []

    # daily news notify(weekday only)
    if datetime.now().weekday() in [0, 1, 2, 3, 4]:
        res = notify_daily_news()
        res_list.append(res)

    # Monday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 0:
        text, attachments = get_github_trends()
        res = notify_slack(text, attachments)
        res_list.append(res)

    # Tuseday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 1:
        text, attachments = get_amazon_trends()
        res = notify_slack(text, attachments)
        res_list.append(res)

    # Wednesday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 2:
        text, attachments = get_hacker_news_trends()
        res = notify_slack(text, attachments)
        res_list.append(res)

    # Thursday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 3:
        text, attachments = get_ivents()
        res = notify_slack(text, attachments)
        res_list.append(res)

    # Friday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 4:
        text, attachments = get_arxiv_papers()
        res = notify_slack(text, attachments)
        res_list.append(res)

    return str(res_list)


def notify_daily_news():
    """Notify daily news

    Only "daily news" is notify function, 
    because want to use unfurl_links option.
    Other getting infomation functions(bellow) dosen't notify.

    Parameters
    ----------
    None
    
    Returns
    -------
    res : str
       slack notify response(if notification success, return 'ok')
    """

    n_picked_news = 1 # only "1" is able to set
    header_text = f"*今日の Pickup News*"

    # URL(Add your favrite RSS)
    rss_urls = [
        # 'http://gihyo.jp/dev/feed/rss2',
        # 'https://www.infoq.com/jp/feed',
        # 'http://rss.rssad.jp/rss/codezine/new/20/index.xml',
        # 'http://it.impressbm.co.jp/list/feed/rss',
        'http://b.hatena.ne.jp/hotentry/it.rss',
        'https://news.yahoo.co.jp/pickup/computer/rss.xml',
        'http://feeds.japan.cnet.com/rss/cnet/all.rdf'
    ]

    contents = []
    for rss_url in rss_urls:
        parse_countent = feedparser.parse(rss_url)

        # max 20 contents because Hatena Bookmark has many contents
        if rss_url == 'http://b.hatena.ne.jp/hotentry/it.rss':
            n_entries = 20
        else:
            n_entries = 7

        for entry in parse_countent.entries[0:n_entries]:
            content = entry.title + "\n" + entry.link
            contents.append(content)

    # filltering by picking word (Engineering words)
    words = ['データ', 'アルゴリズム', 'SQL', 'tensorflow', '分析', '機械学習',
             'Python', 'DB', '検索', '統計', '計算', '言語処理', 'パーソナライズ']

    filltered_contents = []
    for content in contents:
        if len(re.findall(re.compile('|'.join(words)), content)) > 0:
            filltered_contents.append(content)
        
    attachments = []
    if len(filltered_contents) > 0:
        attachments = random.sample(filltered_contents, n_picked_news)
    else:
        attachments = random.sample(contents, n_picked_news)

    text = header_text + "\n" + "\n".join(attachments)
    res = notify_slack(text=text, attachments=[], unfurl_links=True)
    return res


def notify_slack(text, attachments, **keywords):
    """Notify slack
    Depends on http://github-trends.ryotarai.info

    Parameters
    ----------
    header_text : str
        slack notification header
    attachments : dict
        slackweb's attachments(see https://api.slack.com/docs/message-attachments)
    **keywords : dict
        slack notification options
        (see https://github.com/satoshi03/slack-python-webhook)

    Returns
    -------
    res : str
       slack notify response(if notification success, return 'ok')
    """

    # initialize slack notify
    slack_url = os.environ['CHANNEL_URL']
    slack = slackweb.Slack(url=slack_url)
    res = slack.notify(text=text, attachments=attachments, **keywords)
    return res


# < Get info from several sources >
# functions under this line has all same param, return
#     params 
#     -------
#     None
#    
#     Returns
#     -------
#     header_text : str
#         slack notification header
#     attachments : dict
#         slackweb's attachments(see https://api.slack.com/docs/message-attachments)

# Github Trends
def get_github_trends():
    top_n = 5 # MAX is 5
    header_text = f"*Github Trends TOP{top_n}*"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]

    rss_url = 'http://github-trends.ryotarai.info/rss/github_trends_all_weekly.rss'
    parse_countent = feedparser.parse(rss_url)
    attachments = []
    for i, entry in enumerate(parse_countent.entries[0:top_n]):
        attachment = {
            "title": f"#{i + 1} " + entry.title.split(' (')[0],
            "title_link": entry.link,
            "text": entry.description,
            "mrkdwn_in": ["text"],
            "color": color_map[i]
        }
        attachments.append(attachment)
    return header_text, attachments

# Amazon Trends
#   Depends on https://am-tb.tk/amaranrss/
def get_amazon_trends():
    top_n = 5 # MAX is 5
    header_text = f"*Amzonベストセラー（IT） TOP{top_n}*"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]
    # IT, Computer category
    rss_url = 'https://am-tb.tk/amaranrss/get/?url=https://www.amazon.co.jp/gp/bestsellers/books/466298/ref=zg_bs_nav_b_1_b'
    
    # Books all
    # rss_url = 'https://am-tb.tk/amaranrss/get/?url=https%3A%2F%2Fwww.amazon.co.jp%2Fgp%2Ftop-sellers%2Fbooks%2F'
    parse_countent = feedparser.parse(rss_url)
    attachments = []
    for i, entry in enumerate(parse_countent.entries[0:top_n]):
        attachment = {
            "title": f"#{i + 1} " + entry.title,
            "title_link": entry.link,
            "mrkdwn_in": ["text"],
            "color": color_map[i]
        }
        attachments.append(attachment)
    return header_text, attachments


# Hacker News trend
#   Depends on https://hnrss.org/newest
def get_hacker_news_trends():
    top_n = 5 # MAX is 5
    header_text = f"*Hacker News Trends Top {top_n}*"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]
    rss_url = 'https://hnrss.org/newest'
    parse_countent = feedparser.parse(rss_url)
    attachments = []
    for i, entry in enumerate(parse_countent.entries[0:top_n]):
        attachment = {
            "title": f"#{i + 1} " + entry.title,
            "title_link": entry.link,
            "color": color_map[i]
        }
        attachments.append(attachment)
    return header_text, attachments

# Connpass ivents
#   Depends on connpass
#   [TODO] filltering interesting words
def get_ivents():
    top_n = 5 # MAX is 5
    header_text = f"*勉強会・イベント情報*"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]

    RSS_URL = 'https://connpass.com/explore/ja.atom'
    parse_countent = feedparser.parse(RSS_URL)

    attachments = []

    i = 0
    for entry in parse_countent.entries:
        if  i >= top_n:
            break
        if not entry.get('summary', 0) == 0:
            summary = entry.summary.split('<br />')[0] + '\n' + entry.summary.split('<br />')[1]
            if '東京都' in summary:
                attachment = {
                    "title": f"#{i + 1} " + entry.title,
                    "title_link": entry.link,
                    "text": summary,
                    "color": color_map[i]
                }
                attachments.append(attachment)
                i += 1

    if attachments == 0:
        return '今週東京で開催されるめぼしいイベントは特にないようです…。', []
    else:
        return header_text, attachments

# Arxiv papers(pickup from published in a last 1 week)
#   [TOD0] ranking by population
def get_arxiv_papers():
    top_n = 5 # MAX is 5
    days_search_range = 7
    header_text = f"*Arxiv Paper Pickup!*"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]

    with open("config.json", "r") as f:
        config = json.load(f)
    arxiv_cstag_dict = config.get('arxiv_cstag')

    search_from_day = datetime.now() - timedelta(days=days_search_range)
    search_to_day = datetime.now()

    arxiv_search_query = "https://arxiv.org/search/advanced?advanced=" \
                        + "&terms-0-operator=AND" \
                        + "&terms-0-term=" \
                        + "&terms-0-field=title" \
                        + "&classification-computer_science=y" \
                        + "&classification-physics_archives=all" \
                        + "&classification-include_cross_list=exclude" \
                        + "&date-year=" \
                        + "&date-filter_by=date_range" \
                        + "&date-from_date=" + search_from_day.strftime('%Y-%m-%d') \
                        + "&date-to_date=" + search_to_day.strftime('%Y-%m-%d') \
                        + "&date-date_type=submitted_date_first" \
                        + "&abstracts=hide" \
                        + "&size=200" \
                        + "&order=-announced_date_first"

    # [TODO] speed up this line
    contents = urllib.request.urlopen(arxiv_search_query).read()
    
    arxiv_soup = BeautifulSoup(contents, "html.parser")

    title_list = [title.text.strip() for title in arxiv_soup.find_all('p', class_="title is-5 mathjax")]
    url_list = [url.a.attrs['href'] for url in arxiv_soup.find_all('p', class_="list-title is-inline-block")]
    tag_list = [tag.text for tag in arxiv_soup.find_all(class_="tag is-small is-link tooltip is-tooltip-top")]
    author_list = [tag.text for tag in arxiv_soup.find_all(class_="authors")]

    # arxiv paper index list
    index_list = []

    # filltering by Arxiv tags(optional)
    
    # filltering_tags = ["cs.IR"]
    # for i, tag in tag_list:
    #     if tag in filltering_tags:
    #         index_list.append(content)

    n_pickup = top_n - len(index_list)
    pickuped_indexes = random.sample(range(0, n_pickup), n_pickup)
    index_list.extend(pickuped_indexes)

    attachments = []
    for i, paper_index in enumerate(index_list):
        tag = tag_list[paper_index]
        arxiv_cstag = arxiv_cstag_dict.get(tag)
        plane_author_name = author_list[paper_index]
        author_name = plane_author_name.replace("\n", "").replace(" ", "").replace(",", ", ").replace("Authors:", "")
        attachment = {
            "title": f"#{i + 1} " + title_list[paper_index],
            "title_link": url_list[paper_index],
            "author_name": author_name,
            "text": f"Tags: {tag}（{arxiv_cstag}）",
            "mrkdwn_in": ["text"],
            "color": color_map[i]
        }
        attachments.append(attachment)
    return header_text, attachments
    