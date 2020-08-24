import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
gi.require_version('GstVideo', '1.0')
gi.require_version('GstAudio', '1.0')
Gst.init(None)
GObject.threads_init()

import sys
import time

# python3 stream_switcher rtmp://10.128.0.42:1600/live/965199813 rtmp://10.128.0.42:1700/live/965199814 rtmp://a.rtmp.youtube.com/live2/yt2a-r43w-tfpy-f4cx-bquk

# https://git.ao2.it/experiments/gstreamer.git/blob/HEAD:/python/gst-input-selector-switch.py

class StreamSwitcher:
    def __init__(self):

        self.pipe_str = """
                        videotestsrc ! video/x-raw, width=640, height=480, framerate=30/1 ! selector.sink_0
                        videotestsrc pattern=snow ! video/x-raw, width=640, height=480, framerate=30/1 ! selector.sink_1
                        input-selector name=selector ! videoconvert ! xvimagesink
                        """

        print(self.pipe_str)
        self.pipe = Gst.parse_launch(self.pipe_str)
        self.pipe.set_state(Gst.State.PLAYING)
        self.selector = self.pipe.get_by_name("selector")
        self.mainPad = self.selector.get_static_pad("sink_0")
        self.backupPad = self.selector.get_static_pad("sink_1")
        self.selector.set_property("active-pad", self.mainPad)
        print("n-pads: %d" % self.selector.get_property("n-pads"))
        self.current_stream = "main"
        self.pipe.set_state(Gst.State.PLAYING)

        self.last_msg_time_1600 = time.time()
        self.last_msg_time_1700 = time.time()

    def switch(self, prev, next):
        if next == "main":
            self.selector.set_property("active-pad", self.mainPad)
        else:
            self.selector.set_property("active-pad", self.backupPad)

        self.current_stream = next
        print("n-pads: %d" % self.selector.get_property("n-pads"))


sw = StreamSwitcher()

while True:

    time.sleep(5)
    if sw.current_stream == "main":
        print("main to backup:", time.time() - sw.last_msg_time_1600)
        sw.switch("", "backup")

    else:
        print("backup to main:", time.time() - sw.last_msg_time_1700)
        sw.switch("", "main")
