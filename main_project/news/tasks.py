from __future__ import absolute_import, unicode_literals
from celery import task, shared_task
import requests
from news.models import Event
import time


@task
def add(x, y):
    time.sleep(5)
    return x+y


@task(rate_limit='5/s')
def get_venues(access_token, latitude, longitude):
    id_limit, ids = 50, []
    place_url = 'https://graph.facebook.com/v2.8/search?type=place&q=' \
                '&center={},{}&fields=id&distance=500&limit=1000&access_token={}&after='.format(latitude, longitude,
                                                                                                 access_token)
    r = requests.get(place_url)
    response = r.json()
    paging = response.get('paging')
    while paging:
        tmp = []
        for venue in response['data']:
            tmp.append(venue['id'])
            if len(tmp) == id_limit:
                ids.append(tmp)
                tmp = []
        if len(tmp):
            ids.append(tmp)
        after = paging['cursors']['after']
        place_url = 'https://graph.facebook.com/v2.8/search?type=place&q=&center={},{}&fields=id&distance=1000&limit=' \
                    '1000&access_token={}&after={}'.format(latitude, longitude, access_token, after)
        r = requests.get(place_url)
        response = r.json()
        paging = response.get('paging')

    return ids


@task
def get_events(access_token, venues, coordinates):
    events_fields = [
        "id",
        "type",
        "name",
        "cover.fields(id,source)",
        "picture.type(large)",
        "description",
        "start_time",
        "end_time",
        "category",
        "attending_count",
        "declined_count",
        "maybe_count",
        "noreply_count"
    ]
    fields = [
        "id",
        "name",
        "about",
        "emails",
        "cover.fields(id,source)",
        "picture.type(large)",
        "location",
        "events.fields({})".format(','.join(events_fields))
    ]
    events_url = 'https://graph.facebook.com/v2.8/?ids={}&fields={}&access_token={}'.format(
        ','.join(venues), ','.join(fields), access_token)
    r = requests.get(events_url)
    response = r.json()
    from news.utils import map_events
    events = map_events(response, coordinates)
    for event in events:
        Event.objects.create(**event)
    return events

