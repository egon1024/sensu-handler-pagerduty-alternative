#!/usr/bin/env python

"""
This module provides a handler for use with Sensu Go (https://sensu.io/)

The intent of this module was to provide a mechanism for being able to pass a data structure
(not just a string) through to the details of a PagerDuty alert.

While similar to the PagerDuty handler from the folks as Sensu, there are some differences in the
interface and attention should be paid to the documentation when using it.
"""

# pylint disable=c0103

# Built in imports
import argparse
import json
import os
import re
import socket
import sys

# 3rd party imports
from pdpyras import EventsAPISession

TEMPLATE_RE = re.compile(r"^\s*{{\s*([a-zA-Z0-9._\ ]+)\s*}}\s*$")


def main():
    """
    Main execution flow
    """

    args = parse_args(sys.argv[1:])
    event = json.loads(sys.stdin.read())
    set_default_args(args, event)
    send_to_pd(args)


def parse_args(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        description="sensu-go handler for sending data to pagerduty"
    )

    # Will check os.environ['PAGERDUTY_DEDUP_KEY'] if not defined
    parser.add_argument(
        "-k", "--dedup-key",
        type=str,
        help="String to use to identify the alert, for deduplication purposes. Can be set with "
             "PAGERDUTY_DEDUP_KEY env var. Defaults to \"{namespace}_{host}_{check name}\".",
    )

    # Will check os.environ['PAGERDUTY_DETAILS'] if not defined
    parser.add_argument(
        "-d", "--details",
        type=str,
        help="String of details to send - will attempt to convert from json.  Can be set with "
             "PAGERDUTY_DETAILS env var.  Defaults to full event data."
    )

    # Will check os.environ['PAGERDUTY_SUMMARY'] if not defined
    parser.add_argument(
        "-S", "--summary",
        type=str,
        help="String for alert summary.  Can be set with PAGERDUTY_SUMMARY env var.  Defaults "
             "to \"{namespace/{entity name}/{check name} : {check output}\"",
    )

    # Will check os.environ['PAGERDUTY_SOURCE'] if not defined
    parser.add_argument(
        "--source",
        type=str,
        help="Define the 'source' field for the alert, to indicate where this alert is coming "
             "from.  Can be set with PAGERDUTY_SOURCE env var. Defaults to the local host's FQDN",
    )

    # Will check os.environ['PAGERDUTY_STATUS'] if not defined
    parser.add_argument(
        "-s", "--status",
        type=int,
        help="Status of the check.  Can be set with PAGERDUTY_STATUS env var.  Defaults to "
             "value of check status.  Valid values: 0 (Ok), 1 (Warning), 2 (Critical)",
        choices=[0, 1, 2],
    )

    # Will check os.environ['PAGERDUTY_TOKEN'] if not defined
    parser.add_argument(
        "-t", "--token",
        required=True,
        type=str,
        help="The authentication token.  Can be set with PAGERDUTY_TOKEN env var."
    )

    parsed = parser.parse_args(args)
    return parsed


def set_default_args(args, event):
    """
    Set default vaules for arguments.
    """

    if args.dedup_key is None:
        default = "{}_{}_{}".format(
            event['entity']['metadata']['namespace'],
            event['entity']['metadata']['name'],
            event['check']['metadata']['name'],
        )
        args.dedup_key = os.environ.get('PAGERDUTY_DEDUP_KEY', default)

    if args.summary is None:
        default = "{}/{}/{} : {}".format(
            event['entity']['metadata']['namespace'],
            event['entity']['metadata']['name'],
            event['check']['metadata']['name'],
            event['check']['output'],
        )
        args.summary = os.environ.get('PAGERDUTY_SUMMARY', default)

    if args.status is None:
        default = event['check']['status']
        args.status = int(os.environ.get('PAGERDUTY_STATUS', default))

    if args.source is None:
        default = socket.getfqdn()
        args.source = os.environ.get('PAGERDUTY_SOURCE', default)

    # Figure out the details data to use
    if args.details is None:
        default = event
        args.details = os.environ.get('PAGERDUTY_DETAILS', default)

    # If it's a template, process it
    if isinstance(args.details, str) and TEMPLATE_RE.search(args.details):
        args.details = parse_template(args.details, event)

    # Convert from JSON, if needed
    if isinstance(args.details, str):
        try:
            args.details = json.loads(args.details)
        except json.decoder.JSONDecodeError:
            pass


def parse_template(templ_str, event):
    """
    Parses a template string and find the corresponding element in an event data structure.

    This is a highly simplified version of the templating that is supported by
    the Golang template code - it supports only a single reference to a sub
    element of the event structure.
    """

    matches = TEMPLATE_RE.search(templ_str)
    tokens = matches.group(1).split('.')

    ref = event
    loc = []
    for token in tokens:
        token = token.strip()

        # Skip the blank tokens
        if not token:
            continue

        if token not in ref:
            disp_loc = "event" + ''.join(["['{}']".format(_) for _ in loc])
            err = "Could not find '{}' in {}".format(token, disp_loc)
            raise RuntimeError(err)

        ref = ref[token]
        loc.append(token)

    return ref


def send_to_pd(args):
    """
    Take the curated argument data and use it to generate a message to PagerDuty.
    """

    session = EventsAPISession(args.token)
    source = args.source

    payload = {
        "summary": args.summary,
        "source": source,
        "custom_details": args.details,
    }

    if args.status in (1, 2):
        session.trigger(
            summary=args.summary,
            source=source,
            dedup_key=args.dedup_key,
            payload=payload,
        )
    else:
        session.resolve(dedup_key=args.dedup_key)


if __name__ == "__main__":
    main()
