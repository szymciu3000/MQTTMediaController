You need to send MQTT messages with the topic "media" and payloads:
- "PAUSE" for pausing/unpausing,
- "NEXT" for next track,
- "PREV" for previous track,
- "VOL_DOWN"/"VOL_UP" for changing volume down by 10,
- "MUTE" for toggling mute,
- "SESSION_UP"/"SESSION_DOWN" for changing windows media sessions.
Change username/password for your own credentials and BROKER_IP for your MQTT broker's IP.
Designed to be used with android apps KWGT and HTTP Request Shortcuts.
KWGT Widget Template is in the directory, as well as the shortcuts.zip file ready to be imported into HTTP Request Shortcuts.
You need to change the rpi_ip, rpi_mqtt_user and rpi_mqtt_password in the HTTP Request Shortcuts app to your own. 
