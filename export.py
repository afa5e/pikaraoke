import os
import json
import requests
import spotipy
import logging
import re
import yt_dlp
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# Specify the folder path
folder_path = '../pikaraoke-songs'

# Create an empty list to store the file names
file_names = []

# Read the client ID and secret from the file
with open('.secrets', 'r') as file:
    credentials = file.read().splitlines()

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(
    client_id = credentials[0],
    client_secret = credentials[1]
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Iterate over the files in the folder
for filename in os.listdir(folder_path):
    # Check if the file is a song (you can modify this condition based on your file naming convention)
    if filename.endswith('.mp4'):
        # Get the filename without extension
        name = os.path.splitext(filename)[0]

        logging.info(f'Processing {filename}')

        if name.find('---') != -1:
            logging.error(f'{name} is not formatted correctly')
            pass
        
        try:
            # Get the text after any type of dash
            text = re.split(r'\s[-–—‒]\s', name)[1]
        except:
            logging.error(f'Could not process {name}')
            pass

        
        # Search for the song on Spotify
        results = sp.search(q=text, type='track', limit=1)
        if results['tracks']['items']:
            # Get the Spotify URL for the first search result
            spotify_url = results['tracks']['items'][0]['external_urls']['spotify']
        else:
            spotify_url = ''
            logging.error(f'Could not find {text} on Spotify')


        # Search for the song on YouTube
        ydl_opts = {
            'default_search': 'ytsearch1',
            'format': 'bestaudio/best',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                search_results = ydl.extract_info(f"ytsearch:{text} lyrics", download=False)
                if search_results['entries']:
                    # Get the YouTube URL for the first search result
                    youtube_url = search_results['entries'][0]['webpage_url']
                else:
                    logging.error(f'Could not find {text} on YouTube')
            except yt_dlp.DownloadError:
                logging.error(f'Could not search for {text} on YouTube')
                youtube_url = ''


        # Create a dictionary object for each file
        file_object = {
            'songName': text,
            'filename': filename,
            'youtube': youtube_url,
            'spotify': spotify_url
        }

        # Append the file object to the list
        file_names.append(file_object)

        json_file_path = './songs.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(file_names, json_file)

        with open('spotify.txt', 'a+') as spotify_file:
            existing_file_names = spotify_file.read().splitlines()

            url_exists = False
            for file_name in existing_file_names:
                if file_name == spotify_url:
                    url_exists = True
                    logging.warning(f'{name} already exists in the file')
                    break

            if not url_exists:
                spotify_file.write(spotify_url + '\n')
