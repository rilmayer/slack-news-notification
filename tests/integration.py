import sys
import yaml
import logging
from news.news import daily_news
from slack.slack import make_post, post_text_to_slack

if __name__ == '__main__':    
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    contents = daily_news(logger, mock=True)
    print(contents)
    post_text = make_post(contents)
    print(post_text)

    # CONFIG_PATH = "config.yaml"
    # with open(CONFIG_PATH, 'r') as yml:
    #     config = yaml.load(yml, Loader=yaml.SafeLoader)
    # SLACK_WEBHOOK_URL = config.get('SLACK_WEBHOOK_URL', None)
    # res = post_text_to_slack(post_text, SLACK_WEBHOOK_URL)
    # print(res)
