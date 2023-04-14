import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import apiData

# Step 1: Gather albums from Billboard
# Step 2: Gather songs per album from Spotify
# Step 3: Write songs (features) to database?

class DatabaseGenerator:
    startYear = 2002
    endYear = 2023
    cid = apiData.SPOTIFY_CLIENT_ID
    secret = apiData.SPOTIFY_CLIENT_SECRET

    def generate_albums_list(self, start_year, end_year):
        albums_year_list = []
        url_p1 = "https://www.billboard.com/charts/year-end/"  # add year after
        url_p2 = "/top-billboard-200-albums/"  # add p2 after year
        for year in range(start_year, end_year):
            url = url_p1 + str(year) + url_p2
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            albums_list = []
            albums = soup.find_all("h3", id="title-of-a-story")
            count = 1
            for album in albums:
                if count < 201:
                    if album:
                        album_text = album.get_text(separator='\n', strip=True)
                        artist = album.parent.find("span")
                        if artist:
                            artistText = artist.get_text(separator='\n', strip=True)
                            albums_list.append({
                                "album": album_text,
                                "artist": artistText,
                            })
                    count += 1
            albums_year_list.append({
                "year": year,
                "numAlbums": len(albums_list),
                "url": url,
                "albumsList": albums_list
            })
        return albums_year_list

    def get_spotify_client(self, cid, secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp

def main():
    # Step 1
    generator = DatabaseGenerator()
    album_year_list = generator.generate_albums_list(2002, 2023)
    print(album_year_list)
    # Step 2
    spotify_client = generator.get_spotify_client(generator.cid, generator.secret)
    print(spotify_client.available_markets())
    spotify_client.search()

main()