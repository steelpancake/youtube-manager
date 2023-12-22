#!/bin/python3
import yt_dlp
import sys
import time
import multiprocessing
import math

"""
This Script also works on normal playlists
usage: ./<script> <playlist url> <txt file end> <start> <end>

How it works:
     It prints an output that can be pasted into yt-dlp archive.txt
Caveat:
     Expects archive to have an extension
"""

args = sys.argv
playlist = args[1]
album_name:str = ''

# number of threads that will spawn 
# change this value accordingly
max_processes=8

ydl_opts_playlist_extractor = {}
ydl_opts = {}
#help(yt_dlp.YoutubeDL)

archive_path = args[2]
archive_file = open(archive_path, "rt")
archive_new_path = archive_path.split(".")[-2] + "_new." + archive_path.split(".")[-1]
#archive_new_file  = open(archive_new_path, "wt")

range_start = int(args[3])
range_end = int(args[4])

def main():
    ydl_opts_playlist_extractor = {
        'extract_flat': True,
        'skip_download': True,
        'no_youtube_channel_redirect': True
    }
    ydl_extractor = yt_dlp.YoutubeDL(ydl_opts_playlist_extractor)

    #exits incase an error occurs
    try:
        info_dict = ydl_extractor.extract_info(playlist, download=False, process=False)
    except:
        exit()

    playlist_entries = []
    for videos in info_dict['entries']:
        playlist_entries.append(videos)

    playlist_digits = len(str(len(playlist_entries)))

    # get the urls to perform download
    playlist_urls = []
    index = 1
    index_count = 1
    real_length = min(len(playlist_entries),range_end)
    print("max digits is {}".format(playlist_digits))
    numbering = "#{:0" + str(playlist_digits) + "d} "

    for video in playlist_entries:
        if index >= range_start and index <= range_end:
            playlist_urls.append(numbering.format(real_length - index_count + 1) + "{} '{}'".format(video["url"], truncate_string(video["title"], max_length=50)))
            index_count += 1
        index += 1

    archive_new_buffer = ""
    for url in playlist_urls:
        archive_new_buffer += url + "\n"
    archive_new_buffer += "\n"
    archive_file.close()
    archive_new_file = open(archive_path, "wt")
    archive_new_file.write(archive_new_buffer)
    archive_new_file.close()

def num_digits(n: int) -> int:
    assert n > 0
    i = int(0.30102999566398114 * (n.bit_length() - 1)) + 1
    return (10 ** i <= n) + i

def get_int_places(theNumber):
    #if theNumber <= 999999999999997:
    #    return int(math.log10(theNumber)) + 1
    #else:
        return len(str(theNumber))

def truncate_string(value, max_length=255, suffix='...'):
    string_value = str(value)
    string_truncated = string_value[:min(len(string_value), (max_length - len(suffix)))]
    suffix = (suffix if len(string_value) > max_length else '')
    return string_truncated+suffix

if __name__ == "__main__":
    main()
