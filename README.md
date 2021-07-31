# Alternative Sensu PagerDuty Handler


## Table of Contents

 - [Overview](#overview)
 - [Usage examples](#usage-examples)
   - [Help output](#help-output)
   - [Deduplication key](#deduplication-key)
   - [Summary](#summary)
   - [Source](#source)
   - [Status](#status)
   - [Details](#details)
 - [Configuration](#configuration)
   - [Installation](#installation)
   - [Handler definition](#handler-definition)
 - [Environment variables](#environment-variables)

## Overview

This Python package provides an alternative [Sensu Go](https://sensu.io/) [handler](https://docs.sensu.io/sensu-go/latest/observability-pipeline/observe-process/handlers/) for communicating with [PagerDuty](https://pagerduty.com/).  Originally authored under the auspices of my day job at [DigitalOcean](https://www.digitalocean.com/) and released as open source with their gracious permission.

While there is a [handler](https://github.com/sensu/sensu-pagerduty-handler) released by the good folks at [Sensu](https://sensu.io/), there was one piece of functionality it did not have that I needed.  Specifically, I had the need to be able to customize the data structure that is sent to [PagerDuty](https://pagerduty.com/) in the customer details section of an incident.

I want to be clear that this handler is **far** inferior to [the one provided](https://github.com/sensu/sensu-pagerduty-handler) and that unless you have the same specific need that I have, you are almost definitely better off using theirs instead.

## Usage examples

### Help output

```
usage: sensu_handler_pagerduty_alternative.py [-h] [-k DEDUP_KEY] [-d DETAILS] [-S SUMMARY]
                                              [--source SOURCE] [-s {0,1,2}] -t TOKEN

sensu-go handler for sending data to pagerduty

optional arguments:
  -h, --help            show this help message and exit
  -k DEDUP_KEY, --dedup-key DEDUP_KEY
                        String to use to identify the alert, for deduplication purposes. Can be
                        set with PAGERDUTY_DEDUP_KEY env var. Defaults to
                        "{namespace}_{host}_{check name}".
  -d DETAILS, --details DETAILS
                        String of details to send - will attempt to convert from json. Can be set
                        with PAGERDUTY_DETAILS env var. Defaults to full event data.
  -S SUMMARY, --summary SUMMARY
                        String for alert summary. Can be set with PAGERDUTY_SUMMARY env var.
                        Defaults to "{namespace/{entity name}/{check name} : {check output}"
  --source SOURCE       Define the 'source' field for the alert, to indicate where this alert is
                        coming from. Can be set with PAGERDUTY_SOURCE env var. Defaults to the
                        local host's FQDN
  -s {0,1,2}, --status {0,1,2}
                        Status of the check. Can be set with PAGERDUTY_STATUS env var. Defaults to
                        value of check status. Valid values: 0 (Ok), 1 (Warning), 2 (Critical)
  -t TOKEN, --token TOKEN
                        The authentication token. Can be set with PAGERDUTY_TOKEN env var.
```

### Deduplication key

The deduplication key, unlike [the official handler]((https://github.com/sensu/sensu-pagerduty-handler)), does not accept a template string and no interpolation will be performed on the value.  A simple string can be passed in.  If none is defined, the environment variable `PAGERDUTY_DEDUP_KEY` will be looked at for a value.  If that is also unavailable/unset, a dedup key will be generated by looking at the event data and combining the values of the {entity namespace}/{entity name}/{check name} fields.

### Summary

The incident summary (only relevant for incident creation), much like the [Deduplication key](#Deduplication-key) field, supports only a non-template string value.  If none is defined, the environment variable `PAGERDUTY_SUMMARY` will be sourced for a value.  If this is also unavailable, the default value will be generated from the event data, by combining {entity namespace}/{entity name}/{check name} and the {check output}.

### Source

The source field defined for the alert is a simple, non-templated string, as with the [Deduplication key](#Deduplication-key) field.  If none is defined, the environment variable `PAGERDUTY_SOURCE` will be examined for a value.  If this is also unavailable, the default value will be generated by looking up the FQDN of the host executing the handler.

### Status

This field allows one to explicitly define the status of the check for the handler, overriding the value defined in the event.  In the case of a `Warning` (1) or `Critical` (2), an incident will be triggered where as a value of `Ok` (0) will trigger a resolve of an incident.  If this field is not defined, the handler will read the value from the event data in the {check status} field.

### Details

The function of this field is largely the driver for the creation of this module.  The desire was to be able to provide a customized data structure to [PagerDuty](https://pagerduty.com/).  This field supports a couple of options:

  1. A normal string.  Example: `This is some text that matters to me.`
  2. A string that is JSON encoded (it will be decoded to be sent to [PagerDuty](https://pagerduty.com/).  Example: `"{\"field\": \"value\", \"something\": \"else\"}"`
  3. A super simplified template reference. Example: `"{{ .check.metadata.annotations }}"`

Number 1 is as described, a simple string value.  Number 2 is similar except that if the string value that is provided is a JSON encoded data structure, the handler will attempt to decode it and use the resulting data structure. 

Number 3 is a VERY simplified version of the templating employed by the [original handler](https://github.com/sensu/sensu-pagerduty-handler).  This allows the value to contain a single reference to a field within the event data structure.

## Configuration

### Installation

At this time, this plugin is NOT yet available as a Sensu asset.  It is recommended to be installed using a local virtualenv.

### Handler definition

```
type: Handler
api_version: core/v2
metadata:
  name: pagerduty
  namespace: default
spec:
  type: pipe
  command: >-
    /path/to/pd-handler.py 
    --token "<token_value>"
    --details "{{ .check.metadata.annotations }}"
  filters:
    - is_incident
  timeout: 10
```

## Environment variables

Much like the [original handler](https://github.com/sensu/sensu-pagerduty-handler), this handler allows most fields to be defined via environment variables rather than commandline arguments.  A commandline argument will override these values though.

| Argument    | Environment Variable |
|-------------|----------------------|
| --dedup-key | PAGERDUTY_DEDUP_KEY  |
| --details   | PAGERDUTY_DETAILS    |
| --source    | PAGERDUTY_SOURCE     |
| --status    | PAGERDUTY_STATUS     |
| --summary   | PAGERDUTY_SUMMARY    |
| --token     | PAGERDUTY_TOKEN      |
