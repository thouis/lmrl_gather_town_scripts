from upload_image import upload
import pandas as pd
from map_tools import get_room_map, replace_poster_images
import time

poster_info = pd.read_table("poster_upload.txt", index_col=0)
print(poster_info.head())

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

print("{} places to put {} posters".format(len(poster_locations), len(poster_info)))
assert len(poster_locations) >= len(poster_info)


poster_info['poster_number'] = range(1, len(poster_info) + 1)

try:
    already_loaded = pd.read_table("UploadedPosters.txt", index_col=0)
except:
    already_loaded = poster_info.copy()
    already_loaded['gathertown_url'] = ""

already_loaded.gathertown_url = already_loaded.gathertown_url.fillna("")

# fetch all the posters, convert to png if needed
for idx, poster_row in poster_info.iterrows():
    poster_path = poster_row.image
    uid = poster_path.split("/")[0]

    # get next poster location
    room, x, y = poster_locations.pop(0)
    poster_info.loc[idx, 'room'] = room
    poster_info.loc[idx, 'x'] = x
    poster_info.loc[idx, 'y'] = y
    print(poster_info.loc[idx])
    if already_loaded.loc[idx, 'gathertown_url'] != "":
        print(poster_path, "already loaded")
        poster_info.loc[idx, 'gathertown_url'] = already_loaded.loc[idx, 'gathertown_url']
        continue

    print("uploading...", poster_path, poster_row.poster_number, len(poster_info))
    new_url = upload(poster_path)
    print("    ", new_url)
    poster_info.loc[idx, 'gathertown_url'] = new_url

    replace_poster_images(room, x, y,
                          new_url,
                          add_number=poster_row.poster_number)

    poster_info.to_csv("UploadedPosters.txt", sep="\t")
