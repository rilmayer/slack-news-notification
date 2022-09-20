import random
import slackweb

HEADER_TEXT = "*Today's Pickup News*"

def make_post(contents):
    if len(contents) == 0:
        return "今日のニュースはありません。"
    
    picked_content = random.sample(contents, 1)
    title, url = picked_content[0]["title"], picked_content[0]["url"]
    return f"{HEADER_TEXT}\n{title}\n{url}"

def post_text_to_slack(text, slack_url):
    slack = slackweb.Slack(url=slack_url)
    res = slack.notify(text=text, unfurl_links=True)
    return res
