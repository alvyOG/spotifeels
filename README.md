# Spotifeels - Spotify Playlist Generation based on Lyric Match and Sentiment Analysis

To set up the environment after cloning the repo, you'll need to install numpy, pandas, spotipy, lyricsgenius, and django, all of which can be installed via pip. 

To access the website used to create a playlist, run 'python manage.py runserver' in the command line from the repo directory. You may be redirected to a dummy website - paste the exact URL of this site if prompted for the redirect URL. This web app is currently unable to accept user authentication, so the Spotify account information of one of the authors has been hard-coded. You will only be able to see a list of songs and artists that are returned after the query search.

The index only consists of about 10,000 songs - if you wish to continue building this index using the Billboard Top 200 songs data we collected, simply run generateDatabase.py. An example index and lyrics file have already been provided in the repo, so running this script is unnecessary before running the search.

If you don't wish to run the code via command line, the project should already be configured to run in the IDE of your choice. Specifically, lyric_scraper.py contains code to both build the index and perform a query search.
