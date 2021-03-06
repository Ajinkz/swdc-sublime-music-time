'''
 The player functions for Spotify (like play, pause, etc. - everything that is 
 in Cody Music for Javascript), as well as the AppleScript commands, could be 
 in a separate file (MusicControlManager).
'''
import os
import sublime_plugin
import sublime
from threading import Thread, Timer, Event
import webbrowser

from ..Constants import *
from .MusicPlaylistProvider import *
from .SoftwareMusic import *
from .SocialShareManager import *
from .PlayerManager import *
from .SoftwareHttp import *


# Song's Controls: Play
def playSong():
    global active_device

    # getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium": 
        playPlayer()
        currentTrackInfo()
        print("desktop player Working")
    else:
        active_device = getSpotifyActiveDevice()

        if active_device == {}:
            current_window = sublime.active_window()
            current_window.run_command("select_player")

        api = "/v1/me/player/play?" + ACTIVE_DEVICE.get('device_id')
        plays = requestSpotify("PUT", api, None, getItem('spotify_access_token'))
        # print(plays["status"])
        print("Web player Working | Playing ... ", plays["status"], "|",plays)
    currentTrackInfo()


# Song's Controls: Pause
def pauseSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        print(isMac())
        pausePlayer()
        currentTrackInfo()
        print("desktop player Working")
    else:
        api = "/v1/me/player/pause?" + ACTIVE_DEVICE.get('device_id')
        pause = requestSpotify("PUT", api, None, getItem('spotify_access_token'))
        print("Web player Working | Paused ...", pause["status"], "|",pause)
    currentTrackInfo()


# Song's Controls: Next
def nextSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        nextTrack()
        currentTrackInfo()
        print("desktop player Working")
    else:
        api = "/v1/me/player/next?" + ACTIVE_DEVICE.get('device_id')
        nxt = requestSpotify("POST", api, None, getItem('spotify_access_token'))
        print("Web player Working | Next ...", nxt["status"], "|",nxt)
    currentTrackInfo()

# Song's Controls: Previous
def previousSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        previousTrack()
        currentTrackInfo()
        print("desktop player Working")
    else:
        api = "/v1/me/player/previous?" + ACTIVE_DEVICE.get('device_id')
        nxt = requestSpotify("POST", api, None, getItem('spotify_access_token'))
        print("Web player Working | previous ...", prev["status"], "|",prev)
        # showStatus("▶️ "+currentTrackInfo()[0])# if currentTrackInfo()[1] is True else print("Paused",currentTrackInfo()[0])
    currentTrackInfo()

# Launch Spotify player
def startPlayer():
    args = "open -a Spotify"
    os.system(args)

# Song's Controls: Play from Desktop
def playPlayer():
    play = '''
    osascript -e 'tell application "Spotify" to play'
    '''
    os.system(play)


# Song's Controls: Pause from Desktop
def pausePlayer():
    pause = '''
    osascript -e 'tell application "Spotify" to pause'  
    '''
    os.system(pause)
    # args = { "osascript", "-e", "tell application \""+ playerName + "\" to pause" }
    # return runCommand(args, None)

# Song's Controls: Previous from Desktop
def previousTrack():
    prev = '''
    osascript -e 'tell application "Spotify" to play (previous track)'
    ''' 
    os.system(prev)

# Song's Controls: Next from Desktop
def nextTrack():
    nxt = '''
    osascript -e 'tell application "Spotify" to play (next track)'
    '''
    os.system(nxt)


def openDesktopPlayer():
    msg = subprocess.Popen(["open", "-a", "spotify"], stdout=subprocess.PIPE)
    print(msg)
    if msg == "Unable to find application named 'spotify'":
        return False
    else:
        return True


def likeSong(track_id):
    try:

        payload_data1 = {'ids': [track_id]}
        print("payload_data1",payload_data1)
        payload1 = json.dumps(payload_data1)
        print("payload1",payload1)

        api = "/v1/me/tracks"
        put_like_url = requestSpotify("PUT", api, payload1, getItem('spotify_access_token'))
        print("put_like_url",put_like_url)
        if put_like_url["status"] == 200:
            
            #  call the software API PUT `/music/liked/track/${trackId}?type=${type}` with a payload of 

            payload_data2 = {"liked": True}
            print("payload_data2",payload_data2)
            payload2 = json.dumps(payload_data2)
            print("payload2",payload2)

            api = "/music/liked/track/"+ track_id +"?type=spotify"
            swdc_put_like_url = requestIt("PUT", api, payload2, getItem("jwt"))
            print("swdc_put_like_url",swdc_put_like_url)
            if swdc_put_like_url is not None and swdc_put_like_url["status"] == 200:
                print("Music Time: Song Liked !")
        #     else:
        #         print("Try later",swdc_put_like_url.json())
        # else:
        #     print("Unable to like track at this moment",put_like_url.json())
    except Exception as e:
        print("Likesong",e)


def unLikeSong(track_id):
    try:

        payload_data1 = {'ids': [track_id]}
        print("payload_data1",payload_data1)
        payload1 = json.dumps(payload_data1)
        print("payload1",payload1)

        api = "/v1/me/tracks"
        put_unlike_url = requestSpotify("DELETE", api, payload1, getItem('spotify_access_token'))
        print("put_unlike_url",put_unlike_url)
        if put_unlike_url is not None and put_unlike_url["status"] == 200:
            #  call the software API PUT `/music/liked/track/${trackId}?type=${type}` with a payload of 

            payload_data2 = {"liked": False}
            print("payload_data2",payload_data2)
            payload2 = json.dumps(payload_data2)
            print("payload2",payload2)

            api = "/music/liked/track/"+ track_id +"?type=spotify"
            swdc_put_unlike_url = requestIt("PUT", api, payload2, getItem("jwt"))
            print("swdc_put_unlike_url",swdc_put_unlike_url)
            if swdc_put_unlike_url is not None and swdc_put_unlike_url["status"] == 200:
                print("Music Time: Song Unliked !")
        #     else:
        #         print("Try later",swdc_put_unlike_url.json())
        # else:
        #     print("Unable to unlike track at this moment",put_unlike_url.json())
    except Exception as e:
        print("unLikesong",e)


def checkLikedSong():
    track_id = getSpotifyTrackId()[0]
    Liked_songs_ids = getLikedSongsIds()#getLikedSongs()
    print("checkLikedSong Liked_songs_ids",Liked_songs_ids)
    if track_id:
        if track_id in Liked_songs_ids:
            print("Unliking a Song ",track_id)
            unLikeSong(track_id)
        else:
            print("Liking a Song ",track_id)
            likeSong(track_id)
        getUserPlaylists()
    else:
        message_dialog = sublime.message_dialog("No song currently being played.\nPlease play a song from playlist.")


class LikeUnlikeSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            checkLikedSong()
        except Exception as E:
            print("checkLikedSong:", E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)