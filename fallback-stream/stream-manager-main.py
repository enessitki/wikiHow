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
        self.active_input = 0

        pipe_str_filler = "videotestsrc ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=video_filler drop=true max-buffers=5 emit-signals=1 "
        pipe_str_filler += "audiotestsrc volume=0.3 ! audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int)44100, channels=(int)1 ! appsink name=audio_filler drop=true max-buffers=5 emit-signals=1 "

        pipe_str_main = "videotestsrc pattern=snow ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=video_main drop=true max-buffers=5 emit-signals=1 "
        pipe_str_main += "audiotestsrc volume=0.2 ! audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int)44100, channels=(int)1 ! appsink name=audio_main drop=true max-buffers=5 emit-signals=1 "

        pipe_str_backup = "videotestsrc pattern=ball ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! appsink name=video_backup drop=true max-buffers=5 emit-signals=1 "
        pipe_str_backup += "audiotestsrc volume=0.1 ! audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int)44100, channels=(int)1 ! appsink name=audio_backup drop=true max-buffers=5 emit-signals=1 "

        self.filler_pipe = Gst.parse_launch(pipe_str_filler)
        self.main_pipe = Gst.parse_launch(pipe_str_main)
        self.backup_pipe = Gst.parse_launch(pipe_str_backup)

        self.video_filler_sink = self.filler_pipe.get_by_name("video_filler")
        self.video_main_sink = self.main_pipe.get_by_name("video_main")
        self.video_backup_sink = self.backup_pipe.get_by_name("video_backup")

        self.audio_filler_sink = self.filler_pipe.get_by_name("audio_filler")
        self.audio_main_sink = self.main_pipe.get_by_name("audio_main")
        self.audio_backup_sink = self.backup_pipe.get_by_name("audio_backup")
        print(self.audio_backup_sink)

        self.video_filler_sink.connect("new-sample", self.update_video_filler, self.video_filler_sink)
        self.video_main_sink.connect("new-sample", self.update_video_main, self.video_main_sink)
        self.video_backup_sink.connect("new-sample", self.update_video_backup, self.video_backup_sink)

        self.audio_filler_sink.connect("new-sample", self.update_audio_filler, self.audio_filler_sink)
        self.audio_main_sink.connect("new-sample", self.update_audio_main, self.audio_main_sink)
        self.audio_backup_sink.connect("new-sample", self.update_audio_backup, self.audio_backup_sink)

        pipe_str_out = "appsrc emit-signals=True is-live=True name=video_out ! video/x-raw, width=640, height=480, framerate=30/1, format=I420 ! xvimagesink "
        pipe_str_out += "appsrc emit-signals=True is-live=True name=audio_out ! audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int)44100, channels=(int)1 ! audioconvert ! autoaudiosink "

        self.out_pipe = Gst.parse_launch(pipe_str_out)
        self.video_out_src = self.out_pipe.get_by_name("video_out")
        self.video_out_src.set_property("format", Gst.Format.TIME)
        self.audio_out_src = self.out_pipe.get_by_name("audio_out")
        self.audio_out_src.set_property("format", Gst.Format.TIME)
        # self.out_src.connect("need-data", self.update_out, self.out_src)

        self.filler_pipe.set_state(Gst.State.PLAYING)
        self.main_pipe.set_state(Gst.State.PLAYING)
        self.backup_pipe.set_state(Gst.State.PLAYING)
        self.out_pipe.set_state(Gst.State.PLAYING)

        self.is_caps_set = False

    def update_video_filler(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 0:
            self.video_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_video_main(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 1:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.video_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_video_backup(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 2:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.video_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_audio_filler(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 0:
            self.audio_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_audio_main(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 1:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.audio_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_audio_backup(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if self.active_input == 2:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.out_src.set_caps(caps)
            self.audio_out_src.emit("push-buffer", buf)
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
