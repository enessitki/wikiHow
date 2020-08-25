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
# http://lifestyletransfer.com/how-to-use-gstreamer-appsrc-in-python/


class StreamSwitcher:
    def __init__(self):
        pipe_str_filler = "videotestsrc ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=filler drop=true max-buffers=5 emit-signals=1"
        pipe_str_main = "videotestsrc pattern=snow ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=main drop=true max-buffers=5 emit-signals=1"
        pipe_str_backup = "videotestsrc pattern=ball ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=backup drop=true max-buffers=5 emit-signals=1"

        self.filler_pipe = Gst.parse_launch(pipe_str_filler)
        self.main_pipe = Gst.parse_launch(pipe_str_main)
        self.backup_pipe = Gst.parse_launch(pipe_str_backup)

        self.filler_sink = self.filler_pipe.get_by_name("filler")
        self.main_sink = self.main_pipe.get_by_name("main")
        self.backup_sink = self.backup_pipe.get_by_name("backup")

        self.filler_sink.connect("new-sample", self.update_filler, self.filler_sink)
        self.main_sink.connect("new-sample", self.update_main, self.main_sink)
        self.backup_sink.connect("new-sample", self.update_backup, self.backup_sink)

        pipe_str_out = "appsrc emit-signals=True is-live=True name=out ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! xvimagesink"
        self.out_pipe = Gst.parse_launch(pipe_str_out)
        self.out_src = self.out_pipe.get_by_name("out")
        self.out_src.set_property("format", Gst.Format.TIME)
        # self.out_src.connect("need-data", self.update_out, self.out_src)

        self.filler_pipe.set_state(Gst.State.PLAYING)
        self.main_pipe.set_state(Gst.State.PLAYING)
        self.backup_pipe.set_state(Gst.State.PLAYING)
        self.out_pipe.set_state(Gst.State.PLAYING)

        self.active_input = 0
        self.is_caps_set = False

    def update_filler(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 0:
            self.out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_main(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 1:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_backup(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 2:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    # def update_out(self, source, length):
    #     # Attempt to read data from the stream
    #     try:
    #         data = self.fd.read(length)
    #     except IOError as err:
    #         self.exit("Failed to read data from stream: {0}".format(err))
    #
    #     # If data is empty it's the end of stream
    #     if not data:
    #         source.emit("end-of-stream")
    #         return

        # Convert the Python bytes into a GStreamer Buffer
        # and then push it to the appsrc
        # buf = Gst.Buffer.new_wrapped(data)
        # source.emit("push-buffer", buf)


sw = StreamSwitcher()
while True:
    time.sleep(1)
    if sw.active_input < 2:
        sw.active_input += 1
    else:
        sw.active_input = 0
