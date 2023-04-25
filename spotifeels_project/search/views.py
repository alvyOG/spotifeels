from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    # Test function
    #s = sum(1,3)

    # Get user input field from form on HTML page
    user_input = request.POST.get('user_input')

    # Parse user input as playlist query
    playlist_query = parseUserInput(user_input)

    # Generate playlist from query
    playlist_output = generatePlaylistFromQuery(playlist_query)

    # Pass in data to the html page (sum and user input)
    #return render(request, "index.html", {"sum": s, "user_input": user_input})
    return render(request, "index.html", {
        "user_input": user_input,
        "playlist_output": playlist_output
    })

# Test function, shows how to use other functions within view
def sum(num1, num2):
    return num1 + num2

# Parse a given input to create a valid playlist query
def parseUserInput(input):
    output = []
    return output

# Generate a playlist from a valid query (list)
def generatePlaylistFromQuery(query):
    playlist = []
    s1 = "Test Song 1"
    s2 = "Test Song 2"
    playlist.append(s1)
    playlist.append(s2)
    return playlist