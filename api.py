import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import logging
logging.basicConfig(filename="api.log", level=logging.INFO)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import traceback
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import pandas as pd
cid = '56333853e8064d9c95e1067d8d90b76c'
secret = '52d71e473eb641b3af44c9fe9b960374'

import sys

if len(sys.argv) != 2:
    print("Usage: python example.py <argument>")
    argument = "90day"
else:
    argument = sys.argv[1]
    print(f"Received argument: {argument}")

if argument == "2025":
    print("2025")
    url = 'https://www.metacritic.com/browse/albums/score/metascore/year?sort=desc&year_selected=2025'
    the_playlist = '78IDU0bUwB0O0Q2fyCvUAK' # metacritic 2025
else:
    print("90 day")
    url = 'https://www.metacritic.com/browse/albums/score/metascore/90day/filtered'
    the_playlist = '1wciSk2nWiRIVHFNdK4rJu' # metacritic 90 day


def meta_scrape(url):


    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers = user_agent)

    soup = BeautifulSoup(response.text, 'html.parser')

    album_df = pd.DataFrame(columns=['artist', 'album'])
    table_df = pd.DataFrame(columns=['pos','artist', 'album','score'])

    # for name in soup.find_all('div', class_='clamp-details'): 
    #     print(name.text)
    
    for name in soup.find_all("td", class_="clamp-summary-wrap"):        
        for score in name.find_all("div", class_="metascore_w large release positive"):
            score_text = score.text
        for pos in name.find_all("span", class_="title numbered"):     
            pos_text = pos.text.strip().replace('.','')
        for album in name.find('h3'):
            album_text = album.text
        for artist in name.find_all("div", class_="artist"):
            artist_text = artist.text.split('by')[1].strip()

        result = {'pos': pos_text, 'artist': artist_text, 'album': album_text, 'score': score_text}
        print(result)
        
        # Use pd.concat instead of append
        table_df = pd.concat([table_df, pd.DataFrame([result])], ignore_index=True)
    
    table_df.to_csv('table.csv')

    return table_df

try:
    secret
    print ("Secret set")
except:
    print ("Secret not set")
    sys.exit(0)


username = 'paulmcevoy@gmail.com' 
userid='895268bd5d614308'

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

import spotipy.util as util
token = util.prompt_for_user_token(
    username=username,  
    scope='playlist-modify-public', 
    client_id=cid, 
    client_secret=secret, 
    redirect_uri="http://localhost:8888/callback"
)
sp = spotipy.Spotify(auth=token)

# sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

try:
    table_df = meta_scrape(url=url)
except Exception as e:
    logging.info(f'Could not scrape due to: ',{e})

table_df = table_df.head(20)
# first remove all tracks
playlist_has_tracks = True
while(playlist_has_tracks):
    tracks_in_playlist = sp.playlist_tracks(playlist_id=the_playlist, fields=None, limit=100, offset=0, market=None)
    if (tracks_in_playlist['total'] != 0):
        tracks_to_delete = []
        for each_track in tracks_in_playlist['items']:
            tracks_to_delete.append(each_track['track']['id'])
        sp.user_playlist_remove_all_occurrences_of_tracks(user='895268bd5d614308', playlist_id=the_playlist, tracks=tracks_to_delete)

    else:
        playlist_has_tracks = False


total_track_count = 0
limit_reached = False
for index, row in table_df.iterrows():
    track_id_list = []
    res = sp.search(q="artist:" + row['artist'] + " album:" + row['album'], type="album", limit = 1)

    if res['albums']['items']:
        album = res['albums']['items'][0]

        table_df.loc[index, 'returned_album'] = album['name']
        table_df.loc[index, 'album_length'] = album['total_tracks']
        total_track_count += album['total_tracks']
        if total_track_count > 199:
            logging.info("Playlist has reached 200 tracks, stopping.")
            limit_reached = True
        if not limit_reached:
            table_df.loc[index, 'id'] = album['id']
            track_list = sp.album_tracks(album['id'], limit=50, offset=0, market=None)
            for each_track in track_list['items']:
                track_id_list.append(each_track['id'])
            try:
                sp.user_playlist_add_tracks(user='895268bd5d614308', playlist_id=the_playlist, tracks=track_id_list, position=None)
            except Exception as e:
                print(f'Could not add tracks due to: ', {e})
    else:
        logging.info("No results")

table_df.to_csv('results.csv')
