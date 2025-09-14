import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("1c0fbafab5b344ecbf155b4e719cc9f2")
client_secret = os.getenv("9c8b72d1c6cb42df87402634641e2631")

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_track_name(url_or_query):
    if "open.spotify.com/track/" in url_or_query:
        track_id = url_or_query.split("/")[-1].split("?")[0]
        result = sp.track(track_id)
        return result['name'] + " " + result['artists'][0]['name']
    else:
        results = sp.search(q=url_or_query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return track['name'] + " " + track['artists'][0]['name']
    return None
