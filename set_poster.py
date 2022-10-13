from upload_image import upload
from map_tools import get_room_map, replace_poster_images
import sys

posternum = int(sys.argv[1])
posterfile = sys.argv[2]

# get all the poster locations
poster_locations = []
for N in "ABC":
    room = "Posters" + N
    mapinfo = get_room_map(room)
    for obj in mapinfo['objects']:
        if obj['type'] == 2:
            poster_locations.append((room, obj['x'], obj['y']))

# sort poster locations so that they fill from lower left upward, room by room
poster_locations.sort(key=lambda x: (x[0], -x[2], x[1]))
# last 5 are a little janky in positioning
poster_locations = poster_locations[:-5] + poster_locations[-2:] + poster_locations[-5:-2]

print("{} places to put  posters".format(len(poster_locations)))

room, x, y = poster_locations[posternum - 1]

if posterfile.startswith('http'):
    url = posterfile
else:
    print("uploading...")
    url = upload(posterfile)
    print("    ", posterfile, url, room, posternum)


print(room, x, y, url)

replace_poster_images(room, x, y,
                      url,
                      add_number=posternum)
