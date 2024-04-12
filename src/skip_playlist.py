#!/bin/python3 import yt_dlp
import sys
import time
import multiprocessing

"""
This Script also works on normal playlists
usage: ./<script> <playlist url> <start> <end>

How it works:
     It prints an output that can be pasted into yt-dlp archive.txt
"""

args = sys.argv
playlist = args[1]
album_name:str = ''

# number of threads that will spawn 
# change this value accordingly
max_processes=8

ydl_opts_playlist_extractor = {}
ydl_opts = {}

range_start = int(args[2])
range_end = int(args[3])

def main():
    ydl_opts_playlist_extractor = {
        'extract_flat': True,
        'skip_download': True,
    }
    ydl_extractor = yt_dlp.YoutubeDL(ydl_opts_playlist_extractor)

    #exits incase an error occurs
    try:
        info_dict = ydl_extractor.extract_info(playlist, download=False, process=False)
    except:
        exit()

    # remove 'Album - ' from playlist name
    global album_name
    album_name = info_dict['title'].replace('Album - ', '')

    playlist_entries = []
    for videos in info_dict['entries']:
        playlist_entries.append(videos)

    playlist_digits = len(str(len(playlist_entries)))

    # get the urls to perform download
    playlist_urls = []
    index = 1
    for video in playlist_entries:
        if index >= range_start and index <= range_end:
            print("youtube "+video["id"])
        index += 1

if __name__ == "__main__":
    main()
