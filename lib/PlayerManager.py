from threading import Thread, Timer, Event
import sublime_plugin
import sublime
import copy
import time

from .SoftwareHttp import *
from .SoftwareUtil import *
from ..Software import *
from .MusicPlaylistProvider import *
from .SoftwareMusic import *


# ACTIVE_DEVICE = {}
computer_device = {}


def checkSpotifyUser():
    if (userTypeInfo() == "premium"):
        items = [
            ("Launch Web Player", []),
            ("Launch Desktop Player", []),
        ]
    else:
    # elif (userTypeInfo() == "non-premium"):
        items = [("Launch Desktop Player", []), ]

    # else:
    #     iÐtems = []
    return items 


def getSpotifyDevice():

    api = "/v1/me/player/devices"
    getdevs = requestSpotify("GET", api)
#     print(getdevs.text)
    device_list = []

    if getdevs.status_code == 200:
        # devices = getdevs.json()['devices']
        devices = getdevs["devices"]

        for i in range(len(devices)):
            device_list.append(
                {"device_name": devices[i]['name'], "device_id": devices[i]['id'], "type": devices[i]['type']})

        if len(devices) == 0:
            device_list = []
            print("Device not found")

    return device_list


def getSpotifyActiveDevice():

    api = "/v1/me/player/devices"
    getdevs = requestSpotify("GET", api)
    ACTIVE_DEVICE = {}  # {"device_name":"","device_id":""}

    if getdevs.status_code == 200:
        # devices = getdevs.json()['devices']
        devices = getdevs["devices"]
        for i in range(len(devices)):
            if devices[i]['is_active'] == True:
                ACTIVE_DEVICE['device_name'] = devices[i]['name']
                ACTIVE_DEVICE['device_id'] = devices[i]['id']
#                 ACTIVE_DEVICE =  {"device_name":device_name,"device_id":device_id}
            # else:
            #     ACTIVE_DEVICE = {}
    print("getSpotifyActiveDevice:", ACTIVE_DEVICE)
    return ACTIVE_DEVICE


class SelectPlayer(sublime_plugin.WindowCommand):
    def run(self):
        # global ACTIVE_DEVICE
        global ACTIVE_DEVICE
        # global current_song
        # global playlist_id
        # print("current_song",current_song,"\nplaylist_id",playlist_id)
        print("ACTIVE_DEVICE", ACTIVE_DEVICE)
        # global playlist_id
        # global current_song
        # print("SelectPlayer:playlist_id",playlist_id,"\n","current_song",current_song)

        device_list = getSpotifyDevice()
        ACTIVE_DEVICE = getSpotifyActiveDevice()

        # if no device available, show generic list
        if device_list == []:
            items = checkSpotifyUser()
            print("items", items)

        # if device are available, show them
        else:
            if userTypeInfo() == "non-premium":
                items = []
                for i in device_list:
                    if i['type'] == "Computer" and "Web Player" not in i['device_name']:
                        # print(i['device_name'], i['device_id'], i['type'])
                        items.append((i['device_name'], [i['device_id']]))

                new_items = []
                if ACTIVE_DEVICE.get('device_id') is not None:
                    print("found active device")
                    active_device_id = ACTIVE_DEVICE.get('device_id')
                    active_device_name = ACTIVE_DEVICE.get('device_name')
                    print(active_device_name)

                    for i in items:
                        # print(i[0])     # get device name in string
                        # print(i[1][0])  # get device id in string
                        if i[1][0] == active_device_id:
                            new_items.append(("Listening on "+i[0], [i[1][0]]))
                        else:
                            new_items.append(("Available on "+i[0], [i[1][0]]))

                    print("new_items before\n", new_items)
                #     is_web = False
                #     is_desktop = False

                else:
                    print("when device is not active")
                    for i in items:
                        new_items.append(("Available on "+i[0], [i[1][0]]))

            else:
                items = []
                for i in device_list:
                    if i['type'] == "Computer":
                        # print(i['device_name'], i['device_id'], i['type'])
                        items.append((i['device_name'], [i['device_id']]))

                new_items = []
                is_web = False
                is_desktop = False

                if ACTIVE_DEVICE.get('device_id') is not None:
                    print("found active device")
                    active_device_id = ACTIVE_DEVICE.get('device_id')
                    active_device_name = ACTIVE_DEVICE.get('device_name')
                    print(active_device_name)

                    for i in items:
                        # print(i[0])     # get device name in string
                        # print(i[1][0])  # get device id in string
                        if i[1][0] == active_device_id:
                            new_items.append(("Listening on "+i[0], [i[1][0]]))
                        else:
                            new_items.append(("Available on "+i[0], [i[1][0]]))

                    print("new_items before\n", new_items)
                #     is_web = False
                #     is_desktop = False

                else:
                    print("when device is not active")
                    for i in items:
                        new_items.append(("Available on "+i[0], [i[1][0]]))

                # Check web/desktop player is avaiable or not
                for i in new_items:
                    if "Web Player" not in i[0]:
                        is_desktop = True
                    else:                 # "Web Player" not in i[0]:
                        is_web = True

                print("web", is_web)
                print("desk", is_desktop)

                if is_web is True and is_desktop is False:
                    new_items.append(("Launch Desktop Player", []))

                elif is_web is False and is_desktop is True:
                    new_items.append(("Launch Web Player", []))

                elif is_web is False and is_desktop is False:
                    new_items = []
                    new_items.append(("Launch Web Player", []))
                    new_items.append(("Launch Desktop Player", []))
                else:
                    # elif web is True and desk is True:
                    print("Both exist")
                    pass

            items = new_items
            # print("items update with new items")
            print("final show list\n", items)

        # select from available device
        devices = [key for key, value in items]

        # Trigger the first show panel and pass on the id of the selected item & the items
        self.window.show_quick_panel(
            devices, lambda id_1: self.on_done(id_1, items))

    def on_done(self, id_1, items):
        global ACTIVE_DEVICE
        # ACTIVE_DEVICE = {}
        print("on_done(self, id_1, items)", id_1, items)
        if id_1 >= 0:
            device_ids = items[id_1][1]
            print("device_ids", device_ids)
            print("items[id_1]", items[id_1])
            device = items[id_1][0]
            print("device", items[id_1][0])

            # If there is no device available
            if device_ids == []:
                # when desktop is selected
                if device == "Launch Desktop Player":

                    if isMac() == True:
                        launch = subprocess.Popen(
                            ["open", "-a", "spotify"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)

                    else:
                        user = os.path.expanduser('~')
                        spotify_path = os.path.join(
                            user, r"AppData\Roaming\Spotify\Spotify.exe")
                        launch = subprocess.Popen(spotify_path, shell=True,
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    err_msg = launch.communicate()[1].decode("utf-8")
                    print("launchDesktopPlayer\n", err_msg)
                    if len(err_msg) == 0:
                        print("Desktop player opened")
                    else:
                        if "The system cannot find the path specified" in err_msg:
                            msg_body = "Unable to launch Desktop player\n" + "Desktop player not found"
                        else:
                            msg_body = "Unable to launch Desktop player" + err_msg
                        sublime.error_message(msg_body)
                        msg = sublime.ok_cancel_dialog("Launching Web player ...", "Ok")
                        if msg is True:
                            print("Launching Web player ...")
                            webbrowser.open("https://open.spotify.com/")
                            time.sleep(5)

                            devices = getSpotifyDevice()
                            print("Launch Web Player:devices", devices)
                            device_id = getWebPlayerId(devices)

                            print("Launch Web Player:device_id", device_id)

                            ACTIVE_DEVICE = {}
                            ACTIVE_DEVICE['device_id'] = device_id
                            print("web player selected", ACTIVE_DEVICE)
                        else:
                            pass

                    time.sleep(5)
                    devices = getSpotifyDevice()
                    print("Launching desktop player ...2", devices)
                    # print("Launching devices")
                    try:
                        devices = getSpotifyDevice()
                        print("Launch Desktop Player: list of devices", devices)

                        device_id = getNonWebPlayerId(devices)
                        print("Launch non Web Player:device_id", device_id)

                        ACTIVE_DEVICE = {}
                        ACTIVE_DEVICE['device_id'] = device_id
                        print(ACTIVE_DEVICE)
                        # currentTrackInfo()
                    except Exception as e:
                        print("Launch Desktop Player Error", e)
                        # If desktop player didn't work. launch Web player
                        # print(
                        #     "Desktop player not found. Opening Web player ...Error:")
                        # webbrowser.open("https://open.spotify.com/")
                        # time.sleep(5)

                        # try:
                        #     devices = getSpotifyDevice()
                        #     print("Launch Web Player:devices", devices)

                        #     device_id = getWebPlayerId(devices)
                        #     print("Launch Web Player:device_id", device_id)

                        #     ACTIVE_DEVICE = {}
                        #     ACTIVE_DEVICE['device_id'] = device_id
                        #     print(ACTIVE_DEVICE)
                        #     # currentTrackInfo()
                        # except Exception as e:
                        #     print("Launch Web Player", e)

                # If user selects web player to launch
                elif device == "Launch Web Player":
                    webbrowser.open("https://open.spotify.com/")
                    time.sleep(5)

                    devices = getSpotifyDevice()
                    print("Launch Web Player:devices", devices)
                    device_id = getWebPlayerId(devices)

                    print("Launch Web Player:device_id", device_id)

                    ACTIVE_DEVICE = {}
                    ACTIVE_DEVICE['device_id'] = device_id
                    print("web player selected", ACTIVE_DEVICE)
                    # currentTrackInfo()

                else:
                    pass
                # time.sleep(5)
                # Get the device id to transfer the playback
                try:
                    transferPlayback(device_id)
                    time.sleep(1)
                    # global ACTIVE_DEVICE
                    ACTIVE_DEVICE = {}
                    ACTIVE_DEVICE = getSpotifyActiveDevice()
                    print("Got ACTIVE_DEVICE", ACTIVE_DEVICE)
                    # currentTrackInfo()
                except Exception as e:
                    print("transfer device error", e)
                currentTrackInfo()

            else:
                device_id = items[id_1][1][0]
                ACTIVE_DEVICE = {}
                ACTIVE_DEVICE['device_name'] = device
                ACTIVE_DEVICE['device_id'] = device_id
                transferPlayback(device_id)
                print("ACTIVE_DEVICE", ACTIVE_DEVICE)
                currentTrackInfo()

        # else:
        #     print("id_1",id_1)
        #     print("items[id_1]",items[id_1])
    def is_enabled(self):
        return (getValue("logged_on", True) is True)


def transferPlayback(deviceid):
    # https://api.spotify.com/v1/me/player
    payload = json.dumps({"device_ids": [deviceid], "play": True})
    print("payload for transfer device:", payload)

    api = "/v1/me/player"
    transfer = requestSpotify("PUT", api, payload)
    if transfer.status_code == 204:
        print("playback transferred to device_id", deviceid)
        # time.sleep(5)
    else:
        print(transfer.text)


def getNonWebPlayerId(device_list):
    # print('device list inside getNonWebPlayerId \n',device_list)
    for i in device_list:
        # print('getNonWebPlayerId \n',i)
        if i['type'] == "Computer" and "Web Player" not in i['device_name']:
            # print(i['device_name'])
            deviceid = i['device_id']
            # print("getNonWebPlayerId:",deviceid)
            return deviceid
    return None


def getWebPlayerId(device_list):
    for i in device_list:
        if i['type'] == "Computer" and "Web Player" in i['device_name']:
            #             print(i['device_name'])
            deviceid = i['device_id']
            # print("getWebPlayerId:",deviceid)
            return deviceid
    return None
