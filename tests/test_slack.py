import unittest
import logging
from slack.slack import make_post

class TestStringMethods(unittest.TestCase):

    def test_make_post(self):
        expected = "*Today's Pickup News*\nThis is a sample title.\nhttps://example.com/"
        input_contents = [{"title": "This is a sample title.", "url": "https://example.com/"}]
        post_text = make_post(input_contents)
        self.assertEqual(expected, post_text)
