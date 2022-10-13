import pandas as pd
from map_tools import get_room_map
import os

# get all the poster locations
poster_locations = []
for N in "ABC":
    room = "Posters" + N
    mapinfo = get_room_map(room)
    for obj in mapinfo['objects']:
        if obj['type'] == 2:
            poster_locations.append((room, obj['x'], obj['y'], obj['properties']['image']))

# sort poster locations so that they fill from lower left upward, room by room
poster_locations.sort(key=lambda x: (x[0], -x[2], x[1]))
# last 5 are a little janky in positioning
# poster_locations = poster_locations[:-5] + poster_locations[-2:] + poster_locations[-5:-2]

poster_info = pd.read_table("poster_names.final.txt")

print("{} places to put {} posters".format(len(poster_locations), len(poster_info)))

poster_info = poster_info.set_index("Poster Number")

poster_info['filename'] = ''
poster_info['gid'] = ''


filemap = [ln.split() for ln in open("poster_pngs/filelist.txt")]
filename_to_gid = {s[-1]: s[-2] for s in filemap}

for idx, (room, x, y, url) in enumerate(poster_locations):
    poster_num = idx + 1
    poster = poster_info.loc[poster_num]
    first_author_lastname = poster.Authors.split(',')[0].split(' ')[-1]
    first_three_words = poster.Title.split(' ')[:3]
    filename = '_'.join([first_author_lastname] + first_three_words).replace(':', '').replace('&', 'n') + '.png'
    poster_info.loc[poster_num, 'filename'] = filename
    poster_info.loc[poster_num, 'gid'] = filename_to_gid[filename]
    # os.system(f"cd poster_pngs; curl --silent -o {filename} {url}")

postertxt = open("poster.html").read()

for _, row in poster_info.iterrows():
    sub = row.Title.replace(' (video)', '')
    newtext = postertxt.replace(sub, f'<a href="https://drive.google.com/file/d/{row.gid}">{sub}</a>')
    assert newtext != postertxt
    postertxt = newtext

open("newposters.html", "w").write(postertxt)
