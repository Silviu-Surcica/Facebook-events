from celery import group
from geopy.distance import VincentyDistance
from geopy import Point
from news.tasks import get_venues
import math


def map_events(response, coordinates):
    formatted_events = []
    for venue in response:
        events = response[venue].get('events')
        if not events:
            continue
        events_data = events.get('data')
        if events and events_data:
            for event in events_data:
                event_result = dict()
                event_result['fb_id'] = event['id']
                event_result['name'] = event['name']
                event_result['type'] = event['type']
                if event.get('cover'):
                    event_result['cover_picture'] = event['cover'].get('source')
                if event.get('picture'):
                    event_result['profile_picture'] = event['picture']['data']['url']
                event_result['description'] = event.get('description')
                if response[venue].get('location'):
                    venue_coordinates = {'latitude': response[venue]['location']['latitude'],
                                         'longitude': response[venue]['location']['longitude']}
                    event_result['distance'] = calculate_distance(venue_coordinates, coordinates)
                event_result['start_time'] = event.get('start_time')
                event_result['end_time'] = event.get('end_time')
                event_result['category'] = event.get('category')
                event_result['stats'] = {
                    'attending': event.get('attending_count'),
                    'declined': event.get('declined_count'),
                    'maybe': event.get('maybe_count'),
                    'noreply': event.get('noreply_count')
                }
                formatted_events.append(event_result)

    return formatted_events


def calculate_distance(venue_coord, coord):

    lat1, lon1 = float(venue_coord['latitude']), float(venue_coord['longitude'])
    lat2, lon2 = float(coord['latitude']), float(coord['longitude'])
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def map_bucharest():
    starting_point = (44.529723, 25.969094)
    origin = Point(*starting_point)
    total_distance = 20  # km
    destination_points = []
    for i in range(0, total_distance * 2 + 1):
        d = float(i)/2
        new_origin = VincentyDistance(kilometers=d).destination(point=origin, bearing=180)
        for j in range(0, total_distance * 2 + 6):
            d = float(j)/2
            destination = VincentyDistance(kilometers=d).destination(point=new_origin, bearing=90)
            destination_points.append((destination.latitude, destination.longitude))

    return destination_points


def ingest_venues(access_token):
    coords = map_bucharest()
    maxim_chunks = 30
    f = lambda array, n=maxim_chunks: [array[i:i + n] for i in range(0, len(array), n)]
    grouped_coords = f(coords)
    for chunk in grouped_coords:
        lazy_group = group([get_venues.s(access_token, *coordinates) for coordinates in chunk])
        promise = lazy_group()
        results = promise.get()
        print results
