import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import logging
logging.basicConfig(filename="api.log", level=logging.INFO)

import traceback
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
#To get the url, and scrap the html page  
import requests
from bs4 import BeautifulSoup
from scraper import meta_scrape
#To save the reviews in a dataframe 
import pandas as pd
cid = '56333853e8064d9c95e1067d8d90b76c'
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
    meta_scrape()
    table_df = pd.read_csv('table.csv')
except Exception as e:
    logging.info(f'Could not scrape due to: ',{e})

table_df = table_df.head(20)

# first remove all tracks
playlist_has_tracks = True
while(playlist_has_tracks):
    tracks_in_playlist = sp.playlist_tracks(playlist_id='1wciSk2nWiRIVHFNdK4rJu', fields=None, limit=100, offset=0, market=None)
    if (tracks_in_playlist['total'] != 0):
        tracks_to_delete = []
        for each_track in tracks_in_playlist['items']:
            tracks_to_delete.append(each_track['track']['id'])
        sp.user_playlist_remove_all_occurrences_of_tracks(user='895268bd5d614308', playlist_id='1wciSk2nWiRIVHFNdK4rJu', tracks=tracks_to_delete)

    else:
        playlist_has_tracks = False



for index, row in table_df.iterrows():
    track_id_list = []
    res = sp.search(q="artist:" + row['artist'] + " album:" + row['album'], type="album", limit = 1)
    if res['albums']['items']:
        album = res['albums']['items'][0]

        table_df.loc[index, 'returned_album'] = album['name']
        table_df.loc[index, 'album_length'] = album['total_tracks']
        table_df.loc[index, 'id'] = album['id']
        track_list = sp.album_tracks(album['id'], limit=50, offset=0, market=None)
        for each_track in track_list['items']:
            track_id_list.append(each_track['id'])
        try:
            sp.user_playlist_add_tracks(user='895268bd5d614308', playlist_id='1wciSk2nWiRIVHFNdK4rJu', tracks=track_id_list, position=None)
        except Exception as e:
            print(f'Could not add tracks due to: ', {e})
    else:
        logging.info("No results")

table_df.to_csv('results.csv')
