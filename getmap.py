from secrets import API_KEY, SPACE_ID
import json
import requests


def get_room_map(room):
    data = {"apiKey": API_KEY,
            "spaceId": SPACE_ID.replace("/", "\\"),
            "mapId": room}
    response = requests.get("https://gather.town/api/getMap",
                            params=data)
    response.raise_for_status()
    return json.loads(response.text)


def set_room_map(room, new_map):
    data = {"apiKey": API_KEY,
            "spaceId": SPACE_ID.replace("/", "\\"),
            "mapId": room,
            "mapContent": new_map}

    response = requests.post("https://gather.town/api/setMap",
                             json=data)
    response.raise_for_status()
    return response.text


def replace_poster_images(room,
                          poster_x, poster_y,
                          image_url):
    room_data = get_room_map(room)

    # find the poster by location
    poster = [obj for obj in room_data['objects']
              if (obj['type'] == 2 and
                  obj['x'] == poster_x and
                  obj['y'] == poster_y)]
    assert len(poster) == 1, "Couldn't find poster at {},{} in {}".format(
        poster_x, poster_y, room)

    poster = poster[0]
    poster['properties']['image'] = image_url
    poster['properties']['preview'] = image_url

    print("Replacing")
    print(set_room_map(room, room_data))
