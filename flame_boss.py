import paho.mqtt.client as mqtt
import cudf
import os
import cv2
import time
import json

username = os.getenv('FLAMEBOSS_USERNAME')
password = os.getenv('FLAMEBOSS_PASSWORD')
device_id = os.getenv('FLAMEBOSS_DEVICE_ID')
rtsp_username = os.getenv('RTSP_USERNAME')
rtsp_password = os.getenv('RTSP_PASSWORD')

frame = None

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(f"flameboss/" + device_id + "/send/open")
    else:
        print(f'An error occurred while connecting to MQTT broker. Error Code: ' + rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = json.loads(msg.payload)
    prob1_temp = (9/50) * data['temps'][0] + 32
    prob2_temp = (9/50) * data['temps'][1] + 32

    # Format to 2 decimal places
    prob1_temp = "{:.2f}".format(prob1_temp)
    prob2_temp = "{:.2f}".format(prob2_temp)

    butt_text = f'Butt: ' + str(prob1_temp)
    egg_text = f'Egg:  ' + str(prob2_temp)  
    position = (1500, 1900)
    egg_position = (1500, 2000)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 3
    color = (255, 255, 255)
    thickness = 3

    cv2.putText(frame, butt_text, position, font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(frame, egg_text, egg_position, font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.imwrite('/home/jdyer/Desktop/FlameBoss.jpg', frame)
    print('Updated image created. Maybe publish to websocket here???')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=username, password=password)
client.connect_async("s7.myflameboss.com", 1883, 60)

if __name__ == '__main__':
    vdo = cv2.VideoCapture(f'rtsp://' + rtsp_username + ':' + rtsp_password + '@192.168.0.195:554/cam/realmonitor?channel=2&subtype=0')
    status, frame = None, None
    if vdo.isOpened():
        client.loop_start()
        while True:
            (status, frame) = vdo.read()
            time.sleep(1)
