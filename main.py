# This main.py is for Google Cloud Function
import yaml
import logging
from datetime import datetime

import functions_framework

from news.news import daily_news
from slack.slack import make_post, post_text_to_slack

logger = logging.getLogger(__name__)

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, 'r') as yml:
    config = yaml.load(yml, Loader=yaml.SafeLoader)

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event):
    # 平日（月〜金曜日）のみ実行
    if config.get('WORKDAY_OPTION', False):
        if datetime.now().weekday() in [0, 1, 2, 3, 4]:
            SLACK_WEBHOOK_URL = config.get('SLACK_WEBHOOK_URL', None)
            if SLACK_WEBHOOK_URL is None:
                return "NO SLACK_WEBHOOK_URL"
            contents = daily_news(logger)
            res = post_text_to_slack(make_post(contents), SLACK_WEBHOOK_URL)
    return 'ok'
