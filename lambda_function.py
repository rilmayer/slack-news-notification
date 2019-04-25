import re
import os
import sys
import json
import random
from datetime import datetime

# import 3rd party modules
sys.path.append('./lib')

import slackweb
import feedparser


# get info from several sources
# functions under this line has all same return valiable
#   input: None
#   return: 
#     text(str): slack notification header
#     attachments(object): slackweb's attachment object

# Github Trends
def get_github_trends():
    top_n = 5 # MAX is 5
    header_text = f"Github Trends TOP{top_n}"
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
    header_text = f"Amzonベストセラー TOP{top_n}"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]
    # IT, omputer category
    #rss_url = 'https://am-tb.tk/amaranrss/get/?url=https://www.amazon.co.jp/gp/bestsellers/books/466298/ref=zg_bs_nav_b_1_b'
    
    # Books all
    rss_url = 'https://am-tb.tk/amaranrss/get/?url=https%3A%2F%2Fwww.amazon.co.jp%2Fgp%2Ftop-sellers%2Fbooks%2F'
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
    header_text = f"Hacker News {top_n}"
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
# [TODO] filltering interesting words
def get_ivents():
    top_n = 5 # MAX is 5
    header_text = f"勉強会・イベント情報 {top_n}"
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

# [TODO] get Arxiv papers function


# notify daily news
#   Only "daily news fonction" is notify function, 
#   because want to use unfurl_links option
def notify_daily_news():
    n_picked_news = 1 # only "1" is able to set
    header_text = f"今日の Pickup News"
    color_map = ["#800000", "#008000", "#000080", "#808000", "#800080", "#008080"]

    # URL(add your favrite RSS)
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
        
    post_contents = []
    if len(filltered_contents) > 0:
        attachments = random.sample(filltered_contents, n_picked_news)
    else:
        attachments = random.sample(contents, n_picked_news)

    text = "*" + header_text + "*\n" + "\n".join(attachments)
    res = notify_slack(text=text, attachments=[], unfurl_links=True)
    return res


# Notify slack
def notify_slack(text, attachments, **keywords):
    # initialize slack notify
    slack_url = os.environ['CHANNEL_URL']
    slack = slackweb.Slack(url=slack_url)
    res = slack.notify(text=text, attachments=attachments, **keywords)
    return res


def lambda_handler(event, context):
    res_list = []

    # daily news notify
    res = notify_daily_news()
    res_list.append(res)

    # Monday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 0:
        res = get_github_trends()
        res_list.append(res)

    # Tuseday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 1:
        res = get_amazon_trends()
        res_list.append(res)

    # Wednesday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 2:
        res = get_hacker_news_trends()
        res_list.append(res)

    # Thursday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 3:
        res_list.append(res)

    # Friday Morning special
    if datetime.now().strftime('%H') == "00" and datetime.now().weekday() == 3:
        pass

    return str(res_list)
