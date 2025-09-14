import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("dba006a65be04444aa7e47f445cf27ca")
client_secret = os.getenv("54d00fbdf26f44149f3d2ec0f08473bb")

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
