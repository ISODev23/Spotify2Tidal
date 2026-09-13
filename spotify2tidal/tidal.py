import logging
from pathlib import Path
import requests
import tidalapi


class Tidal:
    """Provide a search-based adding of new favorites to Tidal.

    Add new artists/albums/tracks/albums by searching for them with
    save_artist(), save_album(), and save_track().

    Authentication uses the OAuth device flow provided by tidalapi. The session
    is stored locally so the browser login is only required when the token expires.
    """
    def __init__(self, session_file):
        self.tidal_session = self._connect(Path(session_file))

    @property
    def own_playlists(self):
        """All playlists of the current user."""
        return self.tidal_session.user.playlists()

    def add_track_to_playlist(self, playlist_id, name, artist):
        """Search tidal for a track and add it to a playlist.

        Parameters
        ----------
        playlist_id:
            Playlist to add track to
        name: str
            Name of the track
        artist: str
            Artist of the track
        """
        track_id = self._search_track(name, artist)

        if track_id:
            playlist = self.tidal_session.playlist(playlist_id)
            try:
                playlist.add([track_id])
            except requests.exceptions.HTTPError as error:
                if error.response is None or error.response.status_code != 412:
                    raise
                logging.getLogger(__name__).warning(
                    "Tidal rejected the playlist ETag; retrying track add."
                )
                playlist._etag = "*"
                playlist.add([track_id])
            logging.getLogger(__name__).info("Added: %s - %s", artist, name)

        else:
            logging.getLogger(__name__).warning(
                "Could not find track: %s - %s", artist, name
            )

    def delete_existing_playlist(self, playlist_name):
        """Delete any existing playlist with a given name.

        Parameters
        ----------
        playlist_name: str
            Playlist name to delete
        """
        for playlist in self.own_playlists:
            if playlist.name == playlist_name:
                self._delete_playlist(playlist.id)

    def save_album(self, name, artist_name):
        """Find an album and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the album
        artist_name: str
            Name of the artist
        """
        album = self._search_album(name, artist_name)

        if album:
            self.tidal_session.user.favorites.add_album(album.id)
            logging.getLogger(__name__).warning(
                "Added album: %s from %s", name, artist_name
            )
        else:
            logging.getLogger(__name__).warning(
                "Could not find album: %s from %s", name, artist_name
            )

    def save_artist(self, name):
        """Find an artist by name and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the artist
        """
        artist = self._search_artist(name)

        if artist:
            self.tidal_session.user.favorites.add_artist(artist.id)
            logging.getLogger(__name__).warning("Added artist: %s", name)
        else:
            logging.getLogger(__name__).warning(
                "Could not find artist: %s", name
            )

    def save_track(self, name, artist_name):
        """Find a track and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the track
        artist_name: str
            Name of the artist
        """
        track = self._search_track(name, artist_name)

        if track:
            self.tidal_session.user.favorites.add_track(track.id)
            logging.getLogger(__name__).warning(
                "Added track: %s from %s", name, artist_name
            )
        else:
            logging.getLogger(__name__).warning(
                "Could not find track: %s from %s", name, artist_name
            )

    def _create_playlist(self, playlist_name, delete_existing=False):
        """Create a tidal playlist and return its ID.

        Parameters
        ----------
        playlist_name: str
            Name of the playlist to create
        delete_existing: str
            Delete any existing playlist with the same name
        """
        if delete_existing is True:
            self.delete_existing_playlist(playlist_name)

        logging.getLogger(__name__).debug(
            "Created playlist: %s", playlist_name
        )

        playlist = self.tidal_session.user.create_playlist(playlist_name, "")
        return playlist.id

    def _connect(self, session_file):
        """Load an OAuth session or start the Tidal device authorization flow."""
        tidal_session = tidalapi.Session()
        if not tidal_session.login_session_file(session_file):
            raise RuntimeError("No se pudo autenticar con Tidal mediante OAuth.")
        return tidal_session

    def _delete_playlist(self, playlist_id):
        """Delete a playlist.

        Parameters
        ----------
        playlist_id: str
            Playlist ID to delete
        """
        self.tidal_session.playlist(playlist_id).delete()

    def _search_track(self, name, artist):
        """Search tidal and return the track ID.

        Parameters
        ----------
        name: str
            Name of the track
        artist: str
            Artist of the track
        """
        tracks = self._search_results(
            name, tidalapi.Track, "tracks", fallback=f"{name} {artist}"
        )

        for t in tracks:
            if t.artist.name.lower() == artist.lower():
                return t.id

    def _search_album(self, name, artist):
        """Search tidal and return the album ID.

        Parameters
        ----------
        name: str
            Name of the album
        artist: str
            Artist of the album
        """
        albums = self._search_results(
            name, tidalapi.Album, "albums", fallback=f"{name} {artist}"
        )

        for a in albums:
            if a.artist.name.lower() == artist.lower():
                return a.id

    def _search_artist(self, name):
        """Search tidal and return the artist ID.

        Parameters
        ----------
        name: str
            Name of the artist
        """
        artists = self._search_results(name, tidalapi.Artist, "artists")

        for a in artists:
            if a.name.lower() == name.lower():
                return a.id

    def _search_results(self, query, model, result_key, fallback=None):
        """Search Tidal and tolerate transient server errors."""
        queries = [query]
        if fallback and fallback != query:
            queries.append(fallback)

        for current_query in queries:
            try:
                return self.tidal_session.search(
                    current_query, models=[model]
                )[result_key]
            except requests.exceptions.HTTPError as error:
                logging.getLogger(__name__).warning(
                    "Tidal search failed for %r: %s", current_query, error
                )

        return []
