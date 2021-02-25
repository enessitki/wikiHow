import os
#os.system("ffmpeg -threads 6 -video_size 1024x760 -framerate 30 -f x11grab -i :0.0 -preset ultrafast -tune zerolatency -f mpegts udp://192.168.2.55:6666?pkt_size=2000")
#ffmpeg -threads 6 -video_size 1024x760 -framerate 60 -f x11grab -i :0.0 -preset ultrafast -tune zerolatency -f mpegts udp://192.168.2.55:6666?pkt_size=2000
class kill:
    os.system("killall ffmpeg")
class screen:
    os.system("ffmpeg -f x11grab -s 1024x768 -framerate 50 -i :0.0 -preset ultrafast -tune zerolatency -f mpegts udp://192.168.2.55:6666?pkt_size=2000")
screen()
