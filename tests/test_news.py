import unittest
import logging
from news.news import filter_content, get_contents, daily_news

class TestStringMethods(unittest.TestCase):

    def test_filter_content(self):
        include_kwyord = "hoge huga"
        not_include_kwyord = "huga huga"
        keywords = ["hoge"]
        is_includeing = filter_content(include_kwyord, keywords)
        self.assertEqual(is_includeing, True)
        is_includeing = filter_content(not_include_kwyord, keywords)
        self.assertEqual(is_includeing, False)

    def test_no_urls(self):
        rss_urls = []
        with self.assertRaises(Exception):
            get_contents(rss_urls)

    def test_daily_news(self):
        logger = logging.getLogger(__name__)
        contents = daily_news(logger, mock=True)
        self.assertEqual(list, type(contents))
