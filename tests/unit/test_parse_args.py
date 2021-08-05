"""
This module contains unittests for the parse_args function
"""

# Built in imports
import unittest

# Our modules
import sensu_handler_pagerduty_alternative

# Constants
TOKEN = 'abc123'
DEDUP_KEY = 'dedup_key'
SOURCE = 'the_source'
DETAILS = "these are details"


class TestParseArgs(unittest.TestCase):
    def setup_method(self, method):
        self.func = sensu_handler_pagerduty_alternative.parse_args

    def test_function_exists(self):
        assert hasattr(sensu_handler_pagerduty_alternative, 'parse_args')

    def test_fail_without_token(self):
        """
        Verify that execution fails if we don't specify a token
        """
        with self.assertRaises(SystemExit):
            self.func([])

    def test_token_set_succeed(self):
        args = ['-t', TOKEN]
        result = self.func(args)
        assert result.token == TOKEN

        args = ['--token', TOKEN]
        result = self.func(args)
        assert result.token == TOKEN

    def test_dedup_set_succeed(self):
        args = ['-k', DEDUP_KEY]
        with self.assertRaises(SystemExit):
            self.func(args)

        args = ['-k', DEDUP_KEY, '-t', TOKEN]
        result = self.func(args)
        assert result.dedup_key == DEDUP_KEY

        args = ['--dedup-key', DEDUP_KEY, '-t', TOKEN]
        result = self.func(args)
        assert result.dedup_key == DEDUP_KEY

    def test_detail_set_succeed(self):
        args = ['-d', DETAILS]
        with self.assertRaises(SystemExit):
            self.func(args)

        args = ['-d', DETAILS, '-t', TOKEN]
        result = self.func(args)
        assert result.details == DETAILS

        args = ['--details', DETAILS, '-t', TOKEN]
        result = self.func(args)
        assert result.details == DETAILS

    def test_source_set_succeed(self):
        args = ['--source', SOURCE]
        with self.assertRaises(SystemExit):
            self.func(args)

        args = ['--source', SOURCE, '-t', TOKEN]
        result = self.func(args)
        assert result.source == SOURCE

    def test_status_set_succeed(self):
        args = ['-s', '0']
        with self.assertRaises(SystemExit):
            self.func(args)

        valid_statuses = ["0", "1", "2"]
        for status in valid_statuses:
            args = ['-s', status, '-t', TOKEN]
            result = self.func(args)
            assert result.status == int(status)
            
            args = ['--status', status, '-t', TOKEN]
            result = self.func(args)
            assert result.status == int(status)
            
        invalid_statuses = ["-1", "3", "sally", ",:|"]
        for status in invalid_statuses:
            with self.assertRaises(SystemExit):
                args = ['-s', status, '-t', TOKEN]
                self.func(args)

    
