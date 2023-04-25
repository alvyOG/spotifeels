import lyricsgenius as lg
import re, string, operator, math

import pandas as pd
import requests.exceptions

import PorterStemmer
import json
from wordcloud import STOPWORDS
import ast
import geniusAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from nltk.corpus import stopwords

api_key = "fnLpxVmCwp7oOq3QwWB-u_NssokWTV19wG16IZjSBbR02YhYgfaJtVzEbHddeThk"

genius = geniusAPI.Genius(api_key)
#genius = lg.Genius(api_key)

# Turn on status messages
genius.verbose = False

# Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.remove_section_headers = True

genius.skip_non_songs = True

def tokenize(text):
    p = list(string.punctuation) + ['\u201c', '\u201d', '\u2026', '\u2014', '\u2013', '\u200b', '\u200f']
    #p.remove('\'')
    for i in p:
        text = text.replace(i, ' ').lower()
    tokens = text.split()
    return tokens

def stemming(tokens):
    stemmed_tokens = []
    stemmer = PorterStemmer.PorterStemmer()
    for x in tokens:

        stemmed_tokens.append(stemmer.stem(x, 0, len(x) - 1))
    return stemmed_tokens

def delete_embed(s):
    if s.endswith('Embed'):
        s = s[:-5]
    #print(s)

    while len(s) > 0 and s[-1].isnumeric():
        s = s[:-1]
    return s


def build_index(song_artist_id_list):
    song_artist_id_set = set()
    try:
        # Opening JSON file
        with open(r'index.json') as json_file:
            index = json.load(json_file)
    except FileNotFoundError:
        index = {}
    for x in index:
        for song_artist_id in index[x]:
            song_artist_id_set.add(song_artist_id)
    song_artist_id_list = [s for s in song_artist_id_list if not str(s[0]) + ', ' + str(s[1]) + ', ' + str(s[2]) in song_artist_id_set]

    ### OLD CODE ####
    # for s in song_artist_id_list:
    #     song_artist_id_string = str(s[0]) + ', ' + str(s[1]) + ', ' + str(s[2])
    #     #print(song_artist_string)
    #     if song_artist_id_string in song_artist_id_set:
    #         song_artist_id_list.remove(s)
    #print(song_artist_id_set)
    #print(song_artist_id_list)

    try:
        song_artist_id_lyrics = pd.read_csv('lyrics.csv')
    except FileNotFoundError:
        song_artist_id_lyrics = pd.DataFrame(columns=['song', 'artist', 'id', 'lyrics'])

    # Begin building dictionary
    for (song_name, artist, id) in song_artist_id_list: #ex: [('Red', 'Taylor Swift'), ('Yellow', 'Coldplay'), ('Green Light', 'Lorde')]:

        #song_name = song_name.replace((' & ', ' and ')) #moved to source code

        try:
            song = genius.search_song(song_name, artist)
        except requests.exceptions.Timeout:
            continue

        try:
            lyrics = song.lyrics
        except AttributeError:
            print("AttributeError: " + str(song_name) + " - trying to fix")
            song_name = song_name.split(' - ')[0]
            if str(song_name) + ', '+str(artist)+', '+str(id) not in song_artist_id_set:
                try:
                    song = genius.search_song(song_name, artist)
                    lyrics = song.lyrics
                    print('fixed!')
                except AttributeError:
                    print("couldn't fix")
                    continue
                except requests.exceptions.Timeout:
                    continue
            else:
                continue
        except requests.exceptions.Timeout:
            continue

        if 'https://genius.com/Genius' in song.url.split('-'): # or song.url.split('-')[len(song.url.split('-'))-2].lower() != song_name.split(' ')[len(song_name.split(' '))-1].lower():
            print('true')
            artist = artist.split(' and ')[0]
            song_name = song_name.split(' (')[0]
            if str(song_name) +', '+ str(artist) +', '+ str(id) not in song_artist_id_set:

                try:
                    song = genius.search_song(song_name, artist)
                except requests.exceptions.Timeout:
                    continue

                try:
                    lyrics = song.lyrics
                except AttributeError:
                    print("AttributeError: " + str(song_name) + " - trying to fix")
                    if str(song_name.split(' - ')[0]) + ', ' + str(artist) + ', ' + str(id) not in song_artist_id_set:
                        try:
                            song_name = song_name.split(' - ')[0]
                            song = genius.search_song(song_name, artist)
                            lyrics = song.lyrics
                            print('fixed!')
                        except AttributeError:
                            print("couldn't fix")
                            continue
                        except requests.exceptions.Timeout:
                            continue
                except requests.exceptions.Timeout:
                    continue
            else:
                continue

        q = lyrics.split('\n')
        for l in q:
            if l.startswith('See') and l.endswith('like') and '$' in l:
                q.remove(l)

        n = q[0].find('Lyrics')
        if n != -1:
            q[0] = q[0][n+6:]
        if q[0].strip(' ') == '':
            q.remove(q[0])

        k = q[len(q)-1].find('You may also like')
        if k != -1:
            q[len(q)-1] = q[len(q)-1][:k+1]
        if q[len(q)-1].strip(' ') == '':
            q.remove(q[len(q)-1])

        if len(q) - 1 > 0:
            q[len(q) - 1] = delete_embed(q[len(q) - 1])
        lyrics = ""
        for l in q:
            lyrics = lyrics + l + " "

        song_artist_id_lyrics.loc[len(song_artist_id_lyrics)] = [song_name, artist, id, lyrics]
        tokens = tokenize(lyrics)
        tokens_without_sw = [word for word in tokens if not word in tokenize(' '.join(list(STOPWORDS) + ['\'cause']))]
        stems = stemming(tokens_without_sw)
        for s in stems:
            if s in index:
                if str(song_name) + ", " + str(artist) + ', '+ str(id) not in index[s]:
                    index[s][str(song_name) + ", " + str(artist) + ', '+ str(id)] = 1
                else:
                    index[s][str(song_name) + ", " + str(artist) + ', '+ str(id)] += 1
            else:
                index[s] = {str(song_name) + ", " + str(artist) + ', '+ str(id): 1}
    with open("index.json", "w") as outfile:
        json.dump(index, outfile)
    song_artist_id_lyrics.to_csv('lyrics.csv', index=False)

def search(query, top_k):
    l = {}
    lyric_term_tfidfs = {}
    song_artist_set = set()
    search_stems = stemming(tokenize(query))
    with open('index.json') as json_file:
        index = json.load(json_file)
    for x in index:
        for song_artist in index[x]:
            song_artist_set.add(song_artist)
    N = len(song_artist_set)
    for stem in search_stems:
        if stem in index:
            for song_artist in index[stem]:
                tf = index[stem][song_artist]

                # if stem not in l:
                #     l[stem] = str(song_artist) + "TF: " + str(tf) + "    "
                # else:
                #     l[stem] += str(song_artist) + "TF: " + str(tf) + "    "
                df = len(index[stem])
                tf_idf = tf * math.log(N/df)
                if song_artist not in lyric_term_tfidfs:
                    lyric_term_tfidfs[song_artist] = tf_idf
                else:
                    lyric_term_tfidfs[song_artist] += tf_idf
                sorted_dict = dict(sorted(lyric_term_tfidfs.items(), key=lambda item: item[1], reverse=True))
                song_list = [x for x in sorted_dict]

    #print(l)
    sorted_list = []
    for x in sorted_dict:
        sorted_list.append((x, sorted_dict[x]))


    print(sorted_list[:top_k])
    print(song_list[:top_k])
    return song_list[:top_k]

def create_playlist(query, top_k):

    song_list = search(query, top_k)
    tracks = []

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='1e2a8192043a4d45a0d7de6104e8ca36',
                                                   client_secret='ebccd4a75315480397803bef2fc33fab',
                                                   redirect_uri='https://users.wpi.edu/~mrsuyer/index.html',
                                                   username='msuyer508',
                                                   scope='playlist-modify-private'))

    playlist = sp.user_playlist_create(user='msuyer508', name=query, public=False)
    for song_artist_id in song_list:
        id = song_artist_id.split(', ')[2]
        tracks.append('spotify:track:'+str(id))
    sp.playlist_add_items(playlist_id=playlist['id'], items=tracks)


if __name__ == '__main__':


    # df = pd.read_csv('raw.csv', low_memory=False)
    # for x in range(3417):
    #     ind = []
    #     lower_bound = x*10 + 15830
    #     for y in range(10):
    #         q = df['artists'][lower_bound]
    #         # if type(q) == 'float':
    #         #     print(q)
    #         artist_name = ""
    #         for y in ast.literal_eval(str(q).replace('\n', ',')):
    #             # print(y['name'])
    #             artist_name += y['name'] + ' and '
    #         artist_name = artist_name[:-5]
    #         #print(artist_name)
    #         ind.append((df['name'][lower_bound], artist_name, df['id'][lower_bound]))
    #         #song_artist_id_genre.loc[len(song_artist_id_genre)] = [df['name'][x], artist_name, df['id'][x], df['genre'][x]]
    #         #print(x)
    #         lower_bound += 1
    #         #song_artist_id_genre.to_csv('song_artist_id_genre.csv')
    #         # print(ast.literal_eval(df['artists'][3])[0])
    #         # print(df['artists'][2].replace('\n', ''))
    #     print("building index, iteration "+str(x+1))
    #     build_index(ind)

    # df = pd.read_csv('TrackFeaturesDatabase - Copy.csv', low_memory=False)
    # for x in range(3360):
    #     ind = []
    #     lower_bound = x*10 + 1400
    #     for y in range(10):
    #         # q = df['artists'][lower_bound]
    #         # # if type(q) == 'float':
    #         # #     print(q)
    #         # artist_name = ""
    #         # for y in ast.literal_eval(str(q).replace('\n', ',')):
    #         #     # print(y['name'])
    #         #     artist_name += y['track_name'] + ' and '
    #         # artist_name = artist_name[:-5]
    #         #print(artist_name)
    #         ind.append((df['track_name'][lower_bound], df['artist'][lower_bound], df['track_id'][lower_bound]))
    #         #song_artist_id_genre.loc[len(song_artist_id_genre)] = [df['name'][x], artist_name, df['id'][x], df['genre'][x]]
    #         #print(x)
    #         lower_bound += 1
    #         #song_artist_id_genre.to_csv('song_artist_id_genre.csv')
    #         # print(ast.literal_eval(df['artists'][3])[0])
    #         # print(df['artists'][2].replace('\n', ''))
    #     print("building index, iteration "+str(x+1))
    #     build_index(ind)

    # genius.skip_non_songs = True
    # genius.verbose = True
    # song = genius.search_song('Come and See Me (feat. Drake)', 'PARTYNEXTDOOR and Drake')
    # lyrics = song.lyrics
    # print(lyrics)
    # song2 = genius.search_song('Love Is The Seventh Wave', 'Sting and Stephen Fitzmaurice')
    # lyrics2 = song2.lyrics
    # print(lyrics2)
    # song3 = genius.search_song('Die For You (with Ariana Grande) - Remix', 'The Weeknd and Ariana Grande')
    # lyrics3 = song3.lyrics
    # print(lyrics3)
    # song4 = genius.search_song('Who Says', 'Selena Gomez & the Scene')
    # lyrics4 = song4.lyrics
    # print(lyrics4)
    # song5 = genius.search_song('Hit \'Em Up - Single Version', '2Pac and Outlawz')
    # lyrics5 = song5.lyrics
    # print(lyrics5)
    # song6 = genius.search_song('Some Nights', 'Like Moths to Flames')
    # lyrics6 = song6.lyrics
    # print(lyrics6)
    # song7 = genius.search_song('Renegade', 'Big Red Machine')
    # lyrics7 = song7.lyrics
    # print(lyrics7)
    # song8 = genius.search_song('Vegas (From the Original Motion Picture Soundtrack ELVIS)', 'Doja Cat')
    # lyrics8 = song8.lyrics
    # print(lyrics8)
    # song9 = genius.search_song('Midnight Rain', 'Taylor Swift')
    # lyrics9 = song9.lyrics
    # print(lyrics9)

    # build_index([('oops!', 'Yung Gravy', 6)])


    create_playlist("I am nailing this presentation!", 10)