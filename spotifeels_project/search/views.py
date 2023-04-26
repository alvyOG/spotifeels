from django.http import HttpResponse
from django.shortcuts import render
from .Utils import lyric_scraper
import re

def index(request):

    # Get user input field from form on HTML page
    user_input = request.POST.get('user_input')

    # Parse user input as playlist query
    # playlist_query = parseUserInput(user_input)

    # Generate playlist from query
    # playlist_output = generatePlaylistFromQuery(playlist_query)
    playlist_output = ""
    if user_input:
        playlist_output = lyric_scraper.create_playlist(user_input, 10)

    # Pass in data to the html page (sum and user input)
    #return render(request, "index.html", {"sum": s, "user_input": user_input})
    return render(request, "index.html", {
        "user_input": user_input,
        "playlist_output": playlist_output
    })

# Probably don't need this since tokenize function handles parsing input
# Parse a given input to create a valid playlist query
# def parseUserInput(input):
#     output = [input]
#     # # Remove all non-letter characters and convert to lowercase
#     # output = re.sub(r'[^a-zA-Z]', '', output)
#     # output = output.lower()
#     return output

# Generate a playlist from a valid query (list)
# def generatePlaylistFromQuery(query):
#     playlist = []
#     s1 = "Test Song 1"
#     s2 = "Test Song 2"
#     playlist.append(s1)
#     playlist.append(s2)
#     return playlist