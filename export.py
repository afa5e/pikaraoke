import os
import json
import requests
import spotipy
import logging
import re
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.ERROR,
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

        logging.info(f'Processing {name}')

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
        
        # Create a dictionary object for each file
        file_object = {
            'songName': text,
            'filename': filename,
            'youtube': '',
            'spotify': spotify_url
        }
        
        # Append the file object to the list
        file_names.append(file_object)

# Save the list as a JSON file
json_file_path = './songs.json'
with open(json_file_path, 'w') as json_file:
    json.dump(file_names, json_file)
