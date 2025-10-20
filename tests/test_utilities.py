"""Unit test for utility functinos"""

from unittest import TestCase

from sb4dfritzlib.utilities.logging import StatusLogger

class TestStatusLogger(TestCase):

    def setUp(self):
        self.logger = StatusLogger()
    
    def test_add_log(self):
        self.assertEqual(len(self.logger.data), 0)
        self.logger.add_log("This is a test", "Out of nowhere")
        self.assertEqual(len(self.logger.data), 1)

    def test_clear_log(self):
        self.logger.add_log("This is a test", "Out of nowhere")
        self.logger.clear()
        self.assertEqual(len(self.logger.data), 0)

    def test_get_log(self):
        from datetime import datetime
        latest = self.logger.get_log()
        self.assertFalse(latest)
        self.logger.add_log("Doesn't matter", "Not it")
        self.logger.add_log("This is a test", "Out of nowhere")
        self.logger.get_log()
        first = self.logger.get_log(0)
        latest = self.logger.get_log()
        time_diff = latest['date'] - datetime.now()
        self.assertAlmostEqual(time_diff.total_seconds(), 0, places=3)
        self.assertEqual(first['message'], "Doesn't matter")
        self.assertEqual(first['source'], "Not it")
        self.assertEqual(latest['message'], "This is a test")
        self.assertEqual(latest['source'], "Out of nowhere")
