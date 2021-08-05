"""
This module contains unittests for the set_default_args function
"""

# Built in imports
import json
import os
import socket
import unittest
from unittest.mock import MagicMock, patch

# Our modules
import sensu_handler_pagerduty_alternative

# Constants
TOKEN = 'abc123'
EVENT = {
    'entity': {
        'metadata': {
            'namespace': 'entity-namespace',
            'name': 'entity-name',
        },
    },
    'check': {
        'metadata': {
            'name': 'check-name',
        },
        'output': 'check-output',
        'status': 1,
    }
}

class TestSetDefaultArgs(unittest.TestCase):
    def setup_method(self, method):
        self.func = sensu_handler_pagerduty_alternative.set_default_args
        self.args = MagicMock()
        self.args.details = None



    def test_function_exists(self):
        assert hasattr(sensu_handler_pagerduty_alternative, 'set_default_args')

    def test_default_dedup_key(self):
        self.args.dedup_key = None

        self.func(self.args, EVENT)

        assert self.args.dedup_key == 'entity-namespace_entity-name_check-name'

    def test_env_dedup_key(self):
        val = "env_key"
        os.environ["PAGERDUTY_DEDUP_KEY"] = val
        self.args.dedup_key = None

        self.func(self.args, EVENT)

        assert self.args.dedup_key == val

    def test_default_summary(self):
        self.args.summary = None

        self.func(self.args, EVENT)

        assert self.args.summary == 'entity-namespace/entity-name/check-name : check-output'

    def test_env_summary(self):
        val = "env_summary"
        os.environ["PAGERDUTY_SUMMARY"] = val
        self.args.summary = None

        self.func(self.args, EVENT)

        assert self.args.summary == val

    def test_default_status(self):
        self.args.status = None

        self.func(self.args, EVENT)

        assert self.args.status == 1

    def test_env_status(self):
        val = 2
        os.environ["PAGERDUTY_STATUS"] = str(val)
        self.args.status = None

        self.func(self.args, EVENT)

        assert self.args.status == val

    @patch('sensu_handler_pagerduty_alternative.socket.getfqdn')
    def test_default_source(self, getfqdn):
        val = 'myhost'
        getfqdn.return_value = val

        self.args.source = None

        self.func(self.args, EVENT)

        assert self.args.source == val

    def test_env_source(self):
        val = "env_source"
        os.environ["PAGERDUTY_SOURCE"] = val
        self.args.source = None

        self.func(self.args, EVENT)

        assert self.args.source == val

    def test_default_details(self):
        self.args.details = None

        self.func(self.args, EVENT)

        assert self.args.details is EVENT

    def test_env_details(self):
        val = "env_details"
        os.environ["PAGERDUTY_DETAILS"] = val
        self.args.details = None

        self.func(self.args, EVENT)

        assert self.args.details == val

    @patch('sensu_handler_pagerduty_alternative.parse_template')
    def test_details_template(self, parse_template):
        val = "template_parse_val"
        parse_template.return_value = val
        self.args.details = "{{ .check.something }}"

        self.func(self.args, EVENT)

        assert self.args.details is val
        assert parse_template.called

    def test_details_json(self):
        val = ['a', 'b', 'c']
        str_val = json.dumps(val)
        self.args.details = str_val

        self.func(self.args, EVENT)

        assert self.args.details == val
