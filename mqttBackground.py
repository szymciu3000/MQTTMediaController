import paho.mqtt.client as mqtt
import logging
import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, VK_MEDIA_NEXT_TRACK, VK_MEDIA_PREV_TRACK, VK_VOLUME_MUTE, VK_VOLUME_UP, VK_VOLUME_DOWN, KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP 
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

broker = "BROKER_IP"
port = 1883
topics = ["media"]
client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2) 

def handle_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logging.info("Connected")
        for topic in topics:
            client.subscribe(topic)
            logging.info(f"Subscribed to topic: {topic}")
    else:
        logging.info(f"Connect failed rc={reason_code}")
        
async def get_sessions_manager():
    sessions_manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    return sessions_manager

def handle_message(client,userdata,msg):
    payload = msg.payload.decode()
    logging.info(f"topic: {msg.topic}, message: {payload}")
    if msg.topic == "media":
        if payload == "PAUSE":
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)

        elif payload == "NEXT":
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)

        elif payload == "PREV":
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)

        elif payload == "VOL_DOWN":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = max(current_volume-0.08,0.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            win32api.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_EXTENDEDKEY, 0) #this is so that the media overlay shows up

        elif payload == "VOL_UP":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = min(current_volume+0.08,1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            win32api.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_EXTENDEDKEY, 0) #this is so that the media overlay shows up

        elif payload == "MUTE":
            win32api.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_EXTENDEDKEY, 0) 

        elif payload == "SESSIONS":
            sessions_manager = asyncio.run(get_sessions_manager())
            current_session = sessions_manager.get_current_session().source_app_user_model_id
            sessions_sorted = sorted(
                sessions_manager.get_sessions(),
                key = lambda a: a.source_app_user_model_id.lower()
            )
            print(f"Current session: {current_session}")
            for x in sessions_sorted:
                print(x.source_app_user_model_id)
                
        elif payload == "SESSION_UP":
            sessions_manager = asyncio.run(get_sessions_manager())
            current_session = sessions_manager.get_current_session().source_app_user_model_id
            sessions_sorted = sorted(
                sessions_manager.get_sessions(),
                key = lambda a: a.source_app_user_model_id.lower()
            )
            for x in range(len(sessions_sorted)):
                if sessions_sorted[x].source_app_user_model_id == current_session:
                    sessions_sorted[x].try_pause_async()
                    sessions_sorted[(x+1)%len(sessions_sorted)].try_play_async()
            win32api.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_EXTENDEDKEY, 0)
            win32api.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_EXTENDEDKEY, 0) #this is so that the media overlay shows up

        elif payload == "SESSION_DOWN":
            sessions_manager = asyncio.run(get_sessions_manager())
            current_session = sessions_manager.get_current_session().source_app_user_model_id
            sessions_sorted = sorted(
                sessions_manager.get_sessions(),
                key = lambda a: a.source_app_user_model_id.lower()
            )
            for x in range(len(sessions_sorted)):
                if sessions_sorted[x].source_app_user_model_id == current_session:
                    sessions_sorted[x].try_pause_async()
                    sessions_sorted[x-1].try_play_async()
            win32api.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_EXTENDEDKEY, 0)
            win32api.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_EXTENDEDKEY, 0) #this is so that the media overlay shows up
            
            

        
client.username_pw_set("USERNAME","PASSWORD")
client.on_connect = handle_connect
client.on_message = handle_message
try:
    client.connect(broker,port,60)        
except Exception as e:
    logging.info(f"Connect error: {e} (retrying)")
client.loop_forever()
