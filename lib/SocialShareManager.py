
import urllib.parse
import webbrowser
import requests

from ..Constants import *
from .SoftwareUtil import *
from .SoftwareSettings import *
from .SoftwareMusic import *
from .SlackConnectionManager import *


def encodeUrl(url):
    return urllib.parse.quote(url)

def getSpotifyTrackId():
    try:
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}
        trackstr = SPOTIFY_API + "/v1/me/player/currently-playing?" + \
            ACTIVE_DEVICE.get('device_id')  # getActiveDeviceInfo()
        track = requests.get(trackstr, headers=headers)

        if track.status_code == 200:
            trackinfo = track.json()['item']['name']
            trackstate = track.json()['is_playing']
            track_id = track.json()['item']['id']
            return track_id
    except Exception as e:
        print("getSpotifyTrackId",e)
        pass

    return ""

# current_track_id = "2Svje8vKEM4VCKxoRyAvA4"
# current_track_id = ""

# class ShareSong(sublime_plugin.WindowCommand):

#     def run(self):
#         items = ["Facebook", "Slack", "Tumblr",
#             "Twitter", "Whatsapp", "Copy Song Link"]
#         self.window.show_quick_panel(items, lambda id: self.on_done(id, items))

#     def on_done(self, id, items):
#         current_track_id = getSpotifyTrackId()
#         print("current_track_id",current_track_id)
#         if current_track_id:
#             # current_track_id = current_song
#             if id >= 0 and items[id] == "Facebook":
#                 '''
#                 "https://www.facebook.com/sharer/sharer.php?u=
#                 https%3A%2F%2Fopen.spotify.com%2Ftrack%2F5O932cZmzOZGOGZz9RHx20
#                 &hashtag=%23MusicTime"
#                 '''
#                 fb_Url = "https://www.facebook.com/sharer/sharer.php?u="
#                 EncodedURL = encodeUrl("https://open.spotify.com/album/"+ current_track_id)
#                 Endcoded_hashtag = encodeUrl("MusicTime")
#                 fb_shareUrl = fb_Url+EncodedURL+"&hashtags="+Endcoded_hashtag
#                 webbrowser.open(fb_shareUrl)
#                 print("Facebook:",fb_shareUrl)

#             elif items[id] == "Slack":
#                 print("Slack")

#             elif items[id] == "Tumblr":
#                 '''
#                 https://www.tumblr.com/widgets/share/tool?
#                 canonicalUrl=https%3A%2F%2Fopen.spotify.com%2Ftrack%2F5O932cZmzOZGOGZz9RHx20
#                 &content=https%3A%2F%2Fopen.spotify.com%2Ftrack%2F5O932cZmzOZGOGZz9RHx20
#                 &posttype=link&title=Check%20out%20this%20Song
#                 &caption=Software%20Audio%20Share&tags=MusicTime
#                 '''
#                 tumblr_Url = "https://www.tumblr.com/widgets/share/tool?canonicalUrl=" 
#                 EncodedURL = encodeUrl("https://open.spotify.com/album/"+ current_track_id)
#                 Endcoded_msg = encodeUrl("Check out this Song")
#                 Encoded_caption = encodeUrl("Software Audio Share")
#                 tumblr_shareUrl = tumblr_Url+EncodedURL+"&content="+EncodedURL+"&posttype=link&title="+Endcoded_msg+"&caption="+Encoded_caption+"&tags=MusicTime"
#                 webbrowser.open(tumblr_shareUrl)
#                 print("Tumblr:",tumblr_shareUrl)


#             elif items[id] == "Twitter":
#                 '''
#                 https://twitter.com/intent/tweet/?text=Check%20out%20this%20Song
#                 &url=https%3A%2F%2Fopen.spotify.com%2Ftrack%2F5O932cZmzOZGOGZz9RHx20
#                 &hashtags=MusicTime
#                 '''
#                 twitter_Url = "https://twitter.com/intent/tweet/?text="
#                 Endcoded_msg = encodeUrl("Check out this Song ")
#                 EncodedURL = encodeUrl("https://open.spotify.com/album/"+ current_track_id)
#                 twitter_shareUrl = twitter_Url + Endcoded_msg +"&url="+ EncodedURL +"&hashtags=MusicTime"
#                 webbrowser.open(twitter_shareUrl)
#                 print("Twitter:",twitter_shareUrl)

#             elif items[id] == "Whatsapp":
#                 '''
#                 https://api.whatsapp.com/send?text=
#                 Check%20out%20this%20Song%3A%20https%3A%2F%2Fopen.spotify.com%2Ftrack%2F5O932cZmzOZGOGZz9RHx20

#                 '''
#                 whatsapp_Url = "https://api.whatsapp.com/send?text="
#                 Endcoded_msg = encodeUrl("Check out this Song ")
#                 EncodedURL = encodeUrl("https://open.spotify.com/album/"+ current_track_id)
#                 whatsapp_shareUrl = whatsapp_Url + Endcoded_msg +EncodedURL
#                 webbrowser.open(whatsapp_shareUrl)
#                 print("Whatsapp: ",whatsapp_shareUrl)

#             else:
#                 track_url = "https://open.spotify.com/album/"+ current_track_id
#                 sublime.set_clipboard(track_url)
#                 print(track_url)
#         else:
#             message_dialog = sublime.message_dialog("No track found. Please play some track before sharing.")


slack_channel_names = []
slack_channel = {}


class ShareSong(sublime_plugin.WindowCommand):

    def run(self):
        global slack_channel_names
        global slack_channel


        isSlackAvailable = getValue("slack_logged_on", True)
        print("isSlackAvailable",isSlackAvailable)
        if isSlackAvailable is True:
            slack_channel = getSlackChannels()
            print("slack_channel:",slack_channel)
            slack_channel_names = list(slack_channel)
            print("slack_channel_names:",slack_channel_names)

            items = [
                ("Facebook", []),
                ("Slack", slack_channel_names),
                ("Tumblr", []),
                ("Twitter", []),
                ("Whatsapp", []),
                ("Copy Song Link", []),
            ]
        else:
            items = [
                ("Facebook", []),
                ("Tumblr", []),
                ("Twitter", []),
                ("Whatsapp", []),
                ("Copy Song Link", []),
            ]

        # select social media platform
        social_media = [key for key, value in items]

        # Trigger the first show panel and pass on the id of the selected item & the items
        self.window.show_quick_panel(social_media, lambda id_1: self.on_done(id_1, items))

    def on_done(self, id_1, items):
        if id_1 >= 0:

            # Trigger the second show panel (with the second item of the selected tuple as the list) & pass on both id's with the list.
            self.window.show_quick_panel(items[id_1][1], lambda id_2: self.on_done2(id_2, id_1, items))

    def on_done2(self, id_2, id_1, items):

        current_track_id = getSpotifyTrackId()
        print("current_track_id",current_track_id)
        if current_track_id:
            # Slack
            if id_2 >= 0:

                try:
                    print(items[id_1][1][id_2])
                    channel_name = items[id_1][1][id_2]
                    channel_id = slack_channel.get(channel_name)
                    print("channel_id",channel_id,"\nchannel_name",channel_name)
                    sendSlackMessage(channel_id,current_track_id)
                except Exception as e:
                    print("slack post msg",e)

            # other social media platforms
            else:
                print(items[id_1][0])
                share_id = items[id_1][0]

                if share_id == "Facebook":

                    fb_Url = "https://www.facebook.com/sharer/sharer.php?u="
                    EncodedURL = encodeUrl("https://open.spotify.com/track/"+ current_track_id)
                    Endcoded_hashtag = encodeUrl("MusicTime")
                    fb_shareUrl = fb_Url+EncodedURL+"&hashtags="+Endcoded_hashtag
                    webbrowser.open(fb_shareUrl)
                    print("Facebook:",fb_shareUrl)

                elif share_id == "Tumblr":

                    tumblr_Url = "https://www.tumblr.com/widgets/share/tool?canonicalUrl=" 
                    EncodedURL = encodeUrl("https://open.spotify.com/track/"+ current_track_id)
                    Endcoded_msg = encodeUrl("Check out this Song")
                    Encoded_caption = encodeUrl("Software Audio Share")
                    tumblr_shareUrl = tumblr_Url+EncodedURL+"&content="+EncodedURL+"&posttype=link&title="+Endcoded_msg+"&caption="+Encoded_caption+"&tags=MusicTime"
                    webbrowser.open(tumblr_shareUrl)
                    print("Tumblr:",tumblr_shareUrl)

                elif share_id == "Twitter":

                    twitter_Url = "https://twitter.com/intent/tweet/?text="
                    Endcoded_msg = encodeUrl("Check out this Song ")
                    EncodedURL = encodeUrl("https://open.spotify.com/track/"+ current_track_id)
                    twitter_shareUrl = twitter_Url + Endcoded_msg +"&url="+ EncodedURL +"&hashtags=MusicTime"
                    webbrowser.open(twitter_shareUrl)
                    print("Twitter:",twitter_shareUrl)

                elif share_id == "Whatsapp":

                    whatsapp_Url = "https://api.whatsapp.com/send?text="
                    Endcoded_msg = encodeUrl("Check out this Song ")
                    EncodedURL = encodeUrl("https://open.spotify.com/track/"+ current_track_id)
                    whatsapp_shareUrl = whatsapp_Url + Endcoded_msg +EncodedURL
                    webbrowser.open(whatsapp_shareUrl)
                    print("Whatsapp: ",whatsapp_shareUrl)

                elif share_id == "Copy Song Link": 
                    '''Copy link to clipboard'''
                    track_url = "https://open.spotify.com/track/"+ current_track_id
                    sublime.set_clipboard(track_url)
                    print(track_url)
                    message_dialog = sublime.message_dialog("Spotify track link copied to clipboard.")

                else:
                    pass
                    
        else:
            '''If no current track found'''
            message_dialog = sublime.message_dialog("No track found. Please play some track before sharing.")

    def is_enabled(self):
        return (getValue("logged_on", True) is True)
