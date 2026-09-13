import json
import os
import sys
if getattr(sys, "frozen", False):
    current_folder_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    current_file_path = os.path.realpath(__file__)
    current_folder_path = os.path.dirname(current_file_path)

filedata = f'{current_folder_path}/data.json'
tidal_session_file = os.path.join(current_folder_path, 'tidal-session.json')

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotify2tidal import Spotify2Tidal


if os.path.exists(filedata):
    with open(filedata, 'r') as f:
        data = json.load(f)
else:
    data = {}

if data.get('CLIENT_ID') and data.get('CLIENT_SECRET') and data.get('REDIRECT_URI'):

    client_id = data['CLIENT_ID']
    client_secret = data['CLIENT_SECRET']
    redirect_uri = data['REDIRECT_URI']
else:
    client_id = input("Enter your Spotify Client ID: ")
    client_secret = input("Enter your Spotify Client Secret: ") 
    redirect_uri = "http://127.0.0.1:8888/callback"
    data = {
        "CLIENT_ID": client_id,
        "CLIENT_SECRET": client_secret,
        "REDIRECT_URI": redirect_uri
    }

with open(filedata, 'w') as f:
    json.dump(data, f)


class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify = self.authenticate()
    """def authenticate(self) -> Spotify:
        #Authenticate with the Spotify API using client credentials.
        auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        return Spotify(auth_manager=auth_manager)"""
    
    def authenticate(self):
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-public playlist-modify-private user-library-read user-library-modify",
        )
        return Spotify(auth_manager=sp_oauth)
    
    def get_client_user(self) -> dict:
        """Get the current authenticated user's profile."""
        return self.spotify.current_user()

    def get_list_of_playlists(self, user_id: str) -> list:
        """Get a list of playlists for a given user."""
        playlists = self.spotify.user_playlists(user_id)
        return playlists['items']
    
    def list_playlists(self, playlists: list) -> None:
        """Print a list of playlists."""
        for i, playlist in enumerate(playlists):
            print(f"{i + 1}. Playlist Name: {playlist['name']}, Playlist ID: {playlist['id']}")

            

class playlist_export:
    def __init__(self, playlists, user_profile):
        self.playlists = playlists
        self.num_playlist = int(input("Enter the number of playlists you want to export: "))
        self.user = user_profile


    def export_playlists(self):
            playl = self.playlists[self.num_playlist - 1]
            print(f"Exporting Playlist: {playl['name']}")
            weekly_playlist = playl['id']
            print(f"Playlist ID: {weekly_playlist}")
            tidal_playlist_name = input(
                f"Tidal playlist name [{playl['name']}]: "
            ).strip() or playl['name']
            st = Spotify2Tidal(
                tidal_session_file=tidal_session_file,
                spotify_username=self.user['id'],
                spotify_client_id=client_id,
                spotify_client_secret=client_secret,
                spotify_redirect_uri=redirect_uri,
                spotify_discover_weekly_id=weekly_playlist,  # Replace with your Discover Weekly playlist ID

	        )
            st.copy_discover_weekly(
                playlist_name=tidal_playlist_name,
                progress_callback=self.show_progress,
            )

    @staticmethod
    def show_progress(current, total, artist, track_name):
        width = 30
        completed = int(width * current / total) if total else width
        bar = "=" * completed + "-" * (width - completed)
        print(
            f"\r[{bar}] {current}/{total} {artist} - {track_name[:35]}",
            end="" if current < total else "\n",
            flush=True,
        )


if __name__ == "__main__":
    spotify_client = SpotifyClient(client_id, client_secret)
    user_profile = spotify_client.get_client_user()
    print(f"User Name: {user_profile['display_name']}, User ID: {user_profile['id']}")

    playlists = spotify_client.get_list_of_playlists(user_profile['id'])
    cantidad = len(playlists)

    spotify_client.list_playlists(playlists)

    playlist_exporter = playlist_export(playlists, user_profile)
    playlist_exporter.export_playlists()
