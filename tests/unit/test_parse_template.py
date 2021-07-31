"""
This module contains unittests for the parse_template function
"""

# Built in imports
import unittest
from unittest.mock import MagicMock, patch

# Our modules
import sensu_handler_pagerduty_alternative

# Constants
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
    },
    'some_list_thingo': [
        'a', 'b', 'c',
    ],
}

class TestParseTemplate(unittest.TestCase):
    def setup_method(self, method):
        self.func = sensu_handler_pagerduty_alternative.parse_template

    def test_function_exists(self):
        assert hasattr(sensu_handler_pagerduty_alternative, 'parse_template')

    def test_retrieve_string(self):
        templ = '{{ .entity.metadata.namespace }}'
        expected = EVENT['entity']['metadata']['namespace']

        ret_val = self.func(templ, EVENT)

        assert ret_val == expected

    def test_retrieve_dict(self):
        templ = '{{ .entity.metadata }}'
        expected = EVENT['entity']['metadata']

        ret_val = self.func(templ, EVENT)

        assert ret_val == expected

    def test_retrieve_list(self):
        templ = '{{ .some_list_thingo }}'
        expected = EVENT['some_list_thingo']

        ret_val = self.func(templ, EVENT)

        assert ret_val == expected

    def test_valid_formats(self):
        expected = EVENT['entity']['metadata']['namespace']

        templs = [
            '{{ .entity.metadata.namespace }}',
            '{{ .entity.metadata.namespace. }}',
            '{{ . entity . metadata . namespace . }}',
            '    {{ .entity.metadata.namespace }}   ',
            '{{.entity.metadata.namespace}}',
            ' {{ entity.metadata.namespace }} ',
        ]

        for templ in templs:
            ret_val = self.func(templ, EVENT)
            assert ret_val == expected, "Failure with '{}'".format(templ)

    def test_invalid_formats(self):
        templs = [
            '{{ bob }}',
            '{{ entity.not_here }}',
            '{{ entity.metadata.0 }}',
        ]

        for templ in templs:
            with self.assertRaises(RuntimeError):
                self.func(templ, EVENT)
