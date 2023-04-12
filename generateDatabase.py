import requests
from bs4 import BeautifulSoup


class DatabaseGenerator:
    startYear = 2002
    endYear = 2023

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

def main():
    generator = DatabaseGenerator()
    album_year_list = generator.generate_albums_list(2002, 2023)
    print(album_year_list)

main()