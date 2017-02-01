from geopy.distance import VincentyDistance
from geopy import Point
import math
from django.utils.dateparse import parse_datetime
from django.utils import timezone


def map_events(response):
    formatted_events = []
    for venue in response:
        events = response[venue].get('events')
        if not events:
            continue
        events_data = events.get('data')
        if events and events_data:
            for event in events_data:
                start_time = parse_datetime(event.get('start_time'))
                if start_time < timezone.now():
                    continue
                event_result = dict()
                event_result['fb_id'] = event['id']
                event_result['name'] = event['name']
                event_result['type'] = event['type']
                if event.get('cover'):
                    event_result['cover_picture'] = event['cover'].get('source')
                if event.get('picture'):
                    event_result['profile_picture'] = event['picture']['data']['url']
                event_result['description'] = event.get('description')
                event_result['start_time'] = event.get('start_time')
                event_result['end_time'] = event.get('end_time')
                event_result['category'] = event.get('category')
                event_result['stats'] = {
                    'attending': event.get('attending_count'),
                    'declined': event.get('declined_count'),
                    'maybe': event.get('maybe_count'),
                    'noreply': event.get('noreply_count')
                }
                event_result['venue'] = venue
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

