import json
import logging
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from unidecode import unidecode

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# Path to the JSON file containing the list of songs
json_file_path = "./songs.json"

# Path to the folder where the songs will be downloaded
target_folder = "../pikaraoke-songs/"

playlist_id = "https://open.spotify.com/playlist/65iZh65XeiApbnb4ef9LZ4"

def download():
    logging.info("Searching for songs in " + str(playlist_id))

    # Read the client ID and secret from the file
    with open('.secrets', 'r') as file:
        credentials = file.read().splitlines()

    # Authenticate with Spotify
    client_credentials_manager = SpotifyClientCredentials(
        client_id = credentials[0],
        client_secret = credentials[1]
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    spotify_songs = []

    # Read the JSON file
    with open(json_file_path, "r") as json_file:
        json_songs = json.load(json_file)

    for song in json_songs:
        spotify_songs.append(song["spotify"])

    logging.info("Found " + str(len(spotify_songs)) + " songs in the JSON file.")
    # Get spotify URLs from playlist
    i = 100
    results = sp.playlist_tracks(playlist_id, offset=0)

    limit = results["total"]

    playlist_track = results["items"]

    while i <= limit:
        results = sp.playlist_tracks(playlist_id, offset=i)
        playlist_track.extend(results["items"])
        i += 100

    logging.info("Found " + str(len(playlist_track)) + " songs in the playlist.")

    for song in playlist_track:
        logging.info("Processing " + str(song["track"]["name"]))

        if song["track"]["external_urls"]["spotify"] not in spotify_songs:
            logging.info(str(song["track"]["name"]) + " not downloaded yet. Downloading...")

            command = f'yt-dlp -j --no-playlist --flat-playlist ytsearch1:"{song["track"]["name"]} lyrics"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            if result.returncode == 0:
                output = result.stdout.strip()
                data = json.loads(output)
                if data:
                    video_url = data['webpage_url']
                else:
                    logging.error("No video found.")
            else:
                logging.error("Error executing the command.")

            cmd = f'yt-dlp -f bestvideo[ext!=webm][height<=1080]+bestaudio[ext!=webm]/best[ext!=webm] -o \"../pikaraoke-songs/{unidecode(song["track"]["artists"][0]["name"])} - {unidecode(song["track"]["name"])}.mp4\" {video_url}'
            
            rc = subprocess.call(cmd)
            if rc != 0:
                logging.error("Error code while downloading, retrying once...")
                rc = subprocess.call(cmd)

            if rc == 0:
                logging.info("Song successfully downloaded: " + str(video_url))
                filename = f'{song["track"]["artists"][0]["name"]} - {song["track"]["name"]}.mp4'
            else:
                logging.error("Error downloading song: " + video_url)

            json_songs.append({
                "songName": song["track"]["name"],
                "spotify": song["track"]["external_urls"]["spotify"],
                "youtube": video_url,
                "filename": filename
            })

            with open(json_file_path, 'w') as json_file:
                json.dump(json_songs, json_file)

if __name__ == '__main__':
    download()
    logging.info("Done.")