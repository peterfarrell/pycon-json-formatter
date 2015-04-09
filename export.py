#!/usr/bin/env python
"""PyCon JSON to HTML Exporter
Usage:
    ./export.py group <group>
    ./export.py group 'day1_group1'
    ./export.py group '__all__'
Options:
    -h --help              Show this screen
"""

from datetime import datetime
import urllib
import json

from babel import dates
from docopt import docopt
from jinja2 import Environment, PackageLoader


def convert_date_to_native(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')


def format_datetime(value, format='medium'):
    if format == 'full':
        _format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        _format = "EE MMM d. HH:mm"
    return dates.format_datetime(convert_date_to_native(value), _format)


FEED_URL = 'https://us.pycon.org/2015/schedule/conference.json'

JINJA_ENV = Environment(loader=PackageLoader('export', 'templates'))
JINJA_ENV.filters['datetime'] = format_datetime


SESSION_GROUPS = {
    'day1_group1': (convert_date_to_native('2015-04-10T10:50:00'), convert_date_to_native('2015-04-10T12:55:00'),),
    'day1_group2': (convert_date_to_native('2015-04-10T13:40:00'), convert_date_to_native('2015-04-10T16:00:00'),),
    'day1_group3': (convert_date_to_native('2015-04-10T16:15:00'), convert_date_to_native('2015-04-10T17:40:00'),),
    'day2_group1': (convert_date_to_native('2015-04-11T10:50:00'), convert_date_to_native('2015-04-11T12:55:00'),),
    'day2_group2': (convert_date_to_native('2015-04-11T13:40:00'), convert_date_to_native('2015-04-11T16:00:00'),),
    'day2_group3': (convert_date_to_native('2015-04-11T16:15:00'), convert_date_to_native('2015-04-11T17:40:00'),),
    'day3_group1': (convert_date_to_native('2015-04-11T13:10:00'), convert_date_to_native('2015-04-12T15:10:00'),),
}


def parse_json(feed_url=FEED_URL):
    response = urllib.urlopen(feed_url)
    data = json.loads(response.read())
    return data


def build_room_list(data):
    room_list = []

    for item in data:
        room = item['room']
        if room not in room_list:
            room_list.append(room)

    return room_list


def build_room_sessions(data, room, date_start, date_end):
    sessions = []

    for item in data:
        if item['room'] == room and convert_date_to_native(item['start']) >= date_start and convert_date_to_native(item['end']) <= date_end:
            sessions.append(item)

    return sessions


def build_sessions(data, date_start, date_end):
    room_list = build_room_list(data)
    sessions = {}

    for room in room_list:
        room_sessions = build_room_sessions(data, room, date_start, date_end)
        if room_sessions:
            sessions[room] = room_sessions

    return sessions


def make_html(sessions):
    template = JINJA_ENV.get_template('schedule.html')
    return template.render(sessions=sessions)


def run(group):
    data = parse_json()

    if group == '__all__':
        group = SESSION_GROUPS.keys()

    for g in group:
        print 'Building group: %s' % (g, )
        sessions = build_sessions(data, SESSION_GROUPS[g][0], SESSION_GROUPS[g][1])
        html = make_html(sessions)

        with open("./schedules/schedule_%s.html" % g, "wb") as f:
            f.write(html.encode('utf8'))


if __name__ == '__main__':
    arguments = docopt(__doc__, version='PyCon JSON to HTML Exporter')

    run(arguments['<group>'])