import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import apiData
import csv
import datetime
import math


# Step 1: Gather albums from Billboard
# Step 2: Gather songs per album from Spotify
# Step 3: Write songs (features) to database?

class DatabaseGenerator:
    startYear = 2002
    endYear = 2023
    cid = apiData.SPOTIFY_CLIENT_ID
    secret = apiData.SPOTIFY_CLIENT_SECRET

    def generate_albums_list(self, start_year, end_year):
        """Generates and returns a list of album data for albums between given start and end years."""
        albums_year_list = []
        url_p1 = "https://www.billboard.com/charts/year-end/"  # add year after
        url_p2 = "/top-billboard-200-albums/"  # add p2 after year
        for year in range(start_year, end_year):
            # Get URLs for each year in range
            url = url_p1 + str(year) + url_p2
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # Get all albums on page
            albums_list = []
            albums = soup.find_all("h3", id="title-of-a-story")
            count = 1
            # For each album found, make sure it exists and parse artist info
            for album in albums:
                if count < 201:
                    if album:
                        album_text = album.get_text(separator='\n', strip=True)
                        artist = album.parent.find("span")
                        if artist:
                            artist_text = artist.get_text(separator='\n', strip=True)
                            albums_list.append({
                                "album": album_text,
                                "artist": artist_text,
                            })
                    count += 1
            # Update albums_year_list with all info on albums from the curr year in range
            albums_year_list.append({
                "year": year,
                "num_albums": len(albums_list),
                "url": url,
                "albums_list": albums_list
            })
        return albums_year_list

    def get_spotify_client(self, cid, secret):
        """Accesses secret credentials and returns Spotify client object."""
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp

    def get_spotify_album_id(self, spotify_client, name, artist):
        """Given the name and artist of an album, use the spotify client to search for the album and return its id."""
        sp = spotify_client
        if not artist == "Soundtrack":
            q_string = "album:" + str(name) + " artist:" + str(artist)
        else:
            q_string = "album:" + str(name)
        try:
            response = sp.search(q_string, 20, 0, "album", "US")
        except requests.exceptions.HTTPError:
            response = None
        if response and response["albums"]["items"]:
            album_id = str(response["albums"]["items"][0]["id"])
        else:
            album_id = 0
        return album_id

    def get_spotify_album_tracks_features(self, spotify_client, album_id):
        """Search for the provided album id and return a list of info on all tracks within that album."""
        sp = spotify_client
        tracks = []

        # If album_id does not exist, or an HTTP error occurs, return empty list
        if album_id == 0:
            return tracks
        try:
            response = sp.album_tracks(album_id, 50, 0, "US")
        except requests.exceptions.HTTPError:
            return tracks
        
        # For each track in the album, record track data and append to track list
        for i in response["items"]:
            track_id = i["id"]
            track_name = i["name"]
            try:
                features = sp.audio_features(track_id)[0]
            except requests.exceptions.HTTPError:
                continue
            if not features:
                continue
            track_data = {
                "track_id": track_id,
                "track_name": track_name,
                "danceability": features["danceability"],
                "energy": features["energy"],
                "loudness": features["loudness"],
                "speechiness": features["speechiness"],
                "acousticness": features["acousticness"],
                "instrumentalness": features["instrumentalness"],
                "liveness": features["liveness"],
                "valence": features["valence"],
                "tempo": features["tempo"]
            }
            tracks.append(track_data)
        return tracks

    def generate_albums_tracks_features_list(self, album_year_list, start_year, end_year):
        """Write all ablum and track info to csv."""
        with open("TrackFeaturesDatabase.csv", "a", newline="", encoding='utf-8') as csv_file:
            field_names = [
                "track_id", "track_name", "album", "artist", "album_id", "danceability",
                "energy", "loudness", "speechiness", "acousticness", "instrumentalness",
                "liveness", "valence", "tempo"
            ]
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            if start_year == 0:
                writer.writeheader()
            for year in range(start_year, end_year):
                print([datetime.datetime.now(), year])
                albums_in_year = album_year_list[year]["num_albums"]
                sp = self.get_spotify_client(self.cid, self.secret)
                for a_num in range(albums_in_year):
                    album = album_year_list[year]["albums_list"][a_num]["album"]
                    artist = album_year_list[year]["albums_list"][a_num]["artist"]
                    album_id = self.get_spotify_album_id(sp, album, artist)
                    if album_id == 0:
                        continue
                    tracks_features = self.get_spotify_album_tracks_features(sp, album_id)
                    if len(tracks_features) == 0 or len(tracks_features[0]) == 0:
                        continue
                    for track in tracks_features:
                        track_dict = {
                            "track_id": track["track_id"],
                            "track_name": track["track_name"],
                            "album": album,
                            "artist": artist,
                            "album_id": album_id,
                            "danceability": track["danceability"],
                            "energy": track["energy"],
                            "loudness": track["loudness"],
                            "speechiness": track["speechiness"],
                            "acousticness": track["acousticness"],
                            "instrumentalness": track["instrumentalness"],
                            "liveness": track["liveness"],
                            "valence": track["valence"],
                            "tempo": track["tempo"]
                        }
                        writer.writerow(track_dict)


def main():
    # Step 1
    generator = DatabaseGenerator()
    album_year_list = generator.generate_albums_list(2002, 2023)
    # Step 2/3 - need to split up years to avoid Spotify timeout
    for year in range(len(album_year_list)):
        generator.generate_albums_tracks_features_list(album_year_list, year, year+1)


main()
