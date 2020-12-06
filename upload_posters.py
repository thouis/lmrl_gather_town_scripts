from upload_image import upload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd
import os
import subprocess
from map_tools import get_room_map, replace_poster_images

poster_info = pd.read_csv("LMRL 2020 Poster Upload.csv")
poster_info.columns = "timestamp email authors title abstract videolink poster_image".split()
poster_info = poster_info[~ poster_info['authors title'.split()].duplicated(keep='last')]
poster_info['poster_number'] = range(1, len(poster_info) + 1)

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
# last 4 are a little janky in positioning
poster_locations = poster_locations[:-4] + poster_locations[-2:] + poster_locations[-4:-2]
print("{} places to put {} posters".format(len(poster_locations), len(poster_info)))
assert len(poster_locations) == len(poster_info)


gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# fetch all the posters, convert to png if needed
for idx, poster_row in poster_info.iterrows():
    poster_path = poster_row.poster_image
    file_id = poster_path.split('id=')[1]
    file = drive.CreateFile({'id': file_id})
    name = file['title']
    print("fetching", name)
    outpath = os.path.join("poster_images", name)
    if not os.path.exists(outpath):
        print("downloading", outpath)
        file.GetContentFile(outpath)
    if name.lower().endswith('.pdf'):
        newpath = outpath[:-3] + 'png'
    else:
        assert outpath.endswith('.png')
        # make sure it's small enough
        newpath = outpath[:-3] + '.reduced.png'
    if not os.path.exists(newpath):
        print("converting {} to {}".format(outpath, newpath))
        subprocess.run("sips -Z 2500 -s format png".split() +
                       [outpath] +
                       ["--out"] +
                       [newpath])
        subprocess.run("mogrify -alpha remove -background white".split() + [newpath])
    outpath = newpath

    poster_info.loc[idx, 'png'] = outpath

    print("uploading...", outpath)
    new_url = upload(outpath)
    print("    ", new_url)
    poster_info.loc[idx, 'gathertown_url'] = new_url

    # get next poster location
    room, x, y = poster_locations.pop(0)
    poster_info.loc[idx, 'room'] = room
    poster_info.loc[idx, 'x'] = x
    poster_info.loc[idx, 'y'] = y

    replace_poster_images(room, x, y,
                          new_url,
                          add_number=poster_row.poster_number)

poster_info.to_csv("UploadedPosters.txt", sep="\t", index=None)
