from __future__ import absolute_import, unicode_literals
from celery import task, shared_task, group
from news.models import Event, Venue
from news.utils import map_bucharest, map_events
import requests
import time


@task
def add(x, y):
    time.sleep(5)
    return x+y


@task
def ingest_venues(access_token):
    coords = map_bucharest()
    maxim_chunks = 30
    f = lambda array, n=maxim_chunks: [array[i:i + n] for i in range(0, len(array), n)]
    grouped_coords = f(coords)
    for chunk in grouped_coords:
        lazy_group = group([get_venues.s(access_token, *coordinates) for coordinates in chunk])
        promise = lazy_group()
        results = promise.get()
        for result in results:
            for venues in result:
                for venue_data in venues:
                    Venue.objects.get_or_create(fb_id=venue_data[0], name=venue_data[1])
    print 'Finished ingesting venues'


@task
def ingest_events(access_token):
    venues = Venue.objects.values_list('fb_id', flat=True)
    id_limit, tmp, ids = 50, [], []
    for venue in venues:
        tmp.append(venue)
        if len(tmp) == id_limit:
            ids.append(tmp)
            tmp = []
    lazy_group = group([get_events.s(access_token, v) for v in ids])
    promise = lazy_group()
    results = promise.get()
    if results:
        print 'Finished ingesting events'


@task(rate_limit='5/s')
def get_venues(access_token, latitude, longitude):
    id_limit, ids = 50, []
    place_url = 'https://graph.facebook.com/v2.8/search?type=place&q=' \
                '&center={},{}&fields=id,name&distance=500&limit=1000&access_token={}&after='.format(latitude, longitude,
                                                                                                     access_token)
    r = requests.get(place_url)
    response = r.json()
    paging = response.get('paging')
    while paging:
        tmp = []
        for venue in response['data']:
            tmp.append((venue['id'], venue['name']))
            if len(tmp) == id_limit:
                ids.append(tmp)
                tmp = []
        if len(tmp):
            ids.append(tmp)
        after = paging['cursors']['after']
        place_url = 'https://graph.facebook.com/v2.8/search?type=place&q=&center={},{}&fields=id,name&' \
                    'distance=1000&limit=1000&access_token={}&after={}'.format(latitude, longitude, access_token, after)
        r = requests.get(place_url)
        response = r.json()
        paging = response.get('paging')

    return ids


@task
def get_events(access_token, venues):
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
    events = map_events(response)
    for event in events:
        venue = Venue.objects.get(fb_id=event['venue'])
        event['venue'] = venue
        Event.objects.get_or_create(**event)


