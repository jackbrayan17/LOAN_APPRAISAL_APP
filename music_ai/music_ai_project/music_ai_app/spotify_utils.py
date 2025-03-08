import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = "f4e6d698e0804dddaac788a474c8908a"
SPOTIPY_CLIENT_SECRET = "97f136fb7b7a4dc28580646eb5905afb"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, 
    client_secret=SPOTIPY_CLIENT_SECRET
))

def search_songs(query, genre):
    results = sp.search(q=f"{query} genre:{genre}", limit=10, type='track')
    return [track['name'] for track in results['tracks']['items']]
