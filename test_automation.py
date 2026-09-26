import unittest
from unittest.mock import patch

from Backend.Automation import OpenApp


class OpenAppYoutubeTests(unittest.TestCase):
    @patch("Backend.Automation.webbrowser.open")
    def test_open_youtube_with_query_uses_search_url(self, mock_open):
        result = OpenApp("youtube hello world")
        self.assertTrue(result)
        mock_open.assert_called_once_with("https://www.youtube.com/results?search_query=hello+world")

    @patch("Backend.Automation.webbrowser.open")
    def test_open_youtube_without_query_opens_homepage(self, mock_open):
        result = OpenApp("youtube")
        self.assertTrue(result)
        mock_open.assert_called_once_with("https://www.youtube.com")

    @patch("Backend.Automation.PlayYoutube")
    @patch("Backend.Automation.webbrowser.open")
    def test_open_youtube_and_play_uses_direct_play(self, mock_open, mock_play):
        result = OpenApp("youtube and play rabah")
        self.assertTrue(result)
        mock_play.assert_called_once_with("rabah")
        mock_open.assert_not_called()

    @patch("Backend.Automation.appopen")
    @patch("Backend.Automation.webbrowser.open")
    def test_google_photos_prefers_website_over_local_app(self, mock_open, mock_appopen):
        result = OpenApp("google photos")
        self.assertTrue(result)
        mock_open.assert_called_once_with("https://photos.google.com/")
        mock_appopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
