import math


def map_events(response, coordinates):
    formatted_events = []
    for venue in response:
        events = venue.get('events')
        events_data = events.get('data')
        if events and events_data:
            for event in events_data:
                event_result = dict()
                event_result['id'] = event['id']
                event_result['name'] = event['name']
                event_result['type'] = event['type']
                if event.get('cover'):
                    event_result['cover_picture'] = event['cover'].get('source')
                if event.get('picture'):
                    event_result['profile_picture'] = event['picture']['data']['url']
                event_result['description'] = event.get('description')
                if venue.get('location'):
                    venue_coordinates = {'latitude': venue['location']['latitude'],
                                         'longitude': venue['location']['longitude']}
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
    def to_rad(x):
        return x * math.pi / 100
    r = 6371  # km
    x1 = float(coord['latitude']) - float(venue_coord['latitude'])
    rad_lat = to_rad(x1)
    x2 = float(coord['longitude']) - float(venue_coord['longitude'])
    rad_long = to_rad(x2)
    a = math.sin(rad_lat / 2) ** 2 + math.cos(to_rad(venue_coord['latitude'])) + math.cos(to_rad(coord['latitude'])) * math.sin(rad_long / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c

    return d
