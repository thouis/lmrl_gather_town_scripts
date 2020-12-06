import requests
import json
from upload_image import upload
from secrets import API_KEY, SPACE_ID
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


default_poster_map = upload("poster_default.png")
highlighted_poster_map = upload("poster_highlighted.png")


def numbered_poster_urls(number):
    kbd = ImageFont.truetype("AmericanTypewriter.ttc", 38, 2)

    def drawon(im):
        image = Image.open(im)
        draw = ImageDraw.Draw(image)
        draw.text((15, 12), str(number), font=kbd, fill=(0, 0, 0, 255))
        image.save("/tmp/tmp_numbered.png")
        return upload("/tmp/tmp_numbered.png")

    return [drawon(im) for im in["poster_default.png", "poster_highlighted.png"]]


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
                          image_url,
                          map_image=default_poster_map,
                          map_image_highlighted=highlighted_poster_map,
                          add_number=None):
    room_data = get_room_map(room)

    if add_number is not None:
        print("enumerating")
        map_image, map_image_highlighted = numbered_poster_urls(add_number)
        print(map_image)

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
    poster['normal'] = map_image
    poster['highlighted'] = map_image_highlighted

    print("Replacing")
    print(set_room_map(room, room_data))




#             "height": 2,
#             "highlighted": "https://cdn.gather.town/v0/b/gather-town.appspot.com/o/internal-dashboard-upload%2Fm9FGNtWDzoKBHHEf?alt=media&token=6bb224da-50e5-45a5-b020-6aa4f9e3b2c7",
#             "normal": "https://cdn.gather.town/v0/b/gather-town.appspot.com/o/internal-dashboard-upload%2FoENQMnkAVRb54S0Z?alt=media&token=52ad427d-558f-4835-a83f-afa4504d700d",
#             "properties": {
#                 "image": "https://cdn.gather.town/v0/b/gather-town-dev.appspot.com/o/assets%2F46a007a2-d124-47a7-a1f9-0b771393eac4?alt=media&token=350e542e-a4a9-4951-b5a9-742f226c0d96",
#                 "preview": "https://cdn.gather.town/v0/b/gather-town-dev.appspot.com/o/assets%2F46a007a2-d124-47a7-a1f9-0b771393eac4?alt=media&token=350e542e-a4a9-4951-b5a9-742f226c0d96"
#             },
#             "scale": 1,
#             "type": 2,
#             "width": 3,
#             "x": 36,
#             "y": 5
#         },
# 
