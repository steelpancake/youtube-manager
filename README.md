## youtube-manager
a project to help in managing the scraping of youtube channels (at risk of deletion)  

# usage
[![asciicast](https://asciinema.org/a/628776.svg)](https://asciinema.org/a/628776)
```
python <path to __init__.py>
```
currently the project has the following commands:  

- ### no command
	- when run with no command, it does the scraping
- ### --ac  --add-channel
	- add a channel to me monitored
- ### --lc  --list-channels
	- i think you know what it does
- ### --rf  --reset-formats
	- resets the formats in config.json and replaces with built in ones from the script

# while scraping
if the scraper find a new video, it will open that link in your default browser and ask you what to do:
```
y   / n  / i      / ia         / skip
yes / no / ignore / ignore all / skip
```
- yes  will download the video and then ask you what format you want to download it in

- no  will skip only one video (will ask next time)

- ignore  will add the video to the archive (will not ask next time)

- ignore all  will add the entire channel/playlist to the archive (will not ask until a new video is added)

- skip  same as no but for entire channel/playlist
