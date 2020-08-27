import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
gi.require_version('GstVideo', '1.0')
gi.require_version('GstAudio', '1.0')
import logging, os
GObject.threads_init()
Gst.init(None)
Gst.init_check(None)
print(Gst.version_string(), Gst.version())
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(4)
Gst.debug_set_colored(True)
Gst.debug_set_default_threshold(Gst.DebugLevel.WARNING)
Gst.debug_print_stack_trace()
logger = logging.getLogger("gst-gtklaunch-1.0")


try:
    assert os.environ.get("GST_DEBUG_DUMP_DOT_DIR", None)
except (NameError, AssertionError):
    os.environ["GST_DEBUG_DUMP_DOT_DIR"] = os.getcwd()

import sys
import time

# python3 stream-manager-main.py rtmp://10.128.0.42:1600/live/965199813 rtmp://10.128.0.42:1700/live/965199814 rtmp://a.rtmp.youtube.com/live2/yt2a-r43w-tfpy-f4cx-bquk

# https://git.ao2.it/experiments/gstreamer.git/blob/HEAD:/python/gst-input-selector-switch.py
# http://lifestyletransfer.com/how-to-use-gstreamer-appsrc-in-python/


class StreamSwitcher:
    def __init__(self):
        self.active_input = 1
        self.is_caps_set = False

        self.src_url_main = sys.argv[1]
        self.src_url_backup = sys.argv[2]
        self.sink_url = sys.argv[3]

        # self.video_caps = " video/x-raw, width=1920, height=1080, framerate=60/1, format=I420 "
        # self.video_caps = " video/x-raw, format=(string)I420, width=(int)1920, height=(int)1080, interlace-mode=(string)progressive, multiview-mode=(string)mono, multiview-flags=(GstVideoMultiviewFlagsSet)0:ffffffff:/right-view-first/left-flipped/left-flopped/right-flipped/right-flopped/half-aspect/mixed-mono, pixel-aspect-ratio=(fraction)1/1, chroma-site=(string)mpeg2, colorimetry=(string)bt709, framerate=(fraction)60/1 "
        self.video_caps = " video/x-raw, format=(string)I420, width=(int)1920, height=(int)1080, interlace-mode=(string)progressive, multiview-mode=(string)mono, multiview-flags=(GstVideoMultiviewFlagsSet)0:ffffffff:/right-view-first/left-flipped/left-flopped/right-flipped/right-flopped/half-aspect/mixed-mono, pixel-aspect-ratio=(fraction)1/1, chroma-site=(string)mpeg2, colorimetry=(string)bt709, framerate=(fraction)60/1 "
        self.audio_caps = " audio/x-raw, format=F32LE, layout=interleaved, rate=44100, channels=2, channel-mask=(bitmask)0x0000000000000003 "

        pipe_str_filler = "videotestsrc pattern=snow ! " + self.video_caps + " ! appsink name=video_filler drop=true max-buffers=5 emit-signals=1 "
        pipe_str_filler += "audiotestsrc volume=0.2 ! " + self.audio_caps + " ! appsink name=audio_filler drop=true max-buffers=5 emit-signals=1 "

        pipe_str_main = "rtmpsrc location="+self.src_url_main+"   name=src do-timestamp=true ! flvdemux name=demux "
        pipe_str_main += "demux.video ! queue ! h264parse ! avdec_h264 ! videoconvert ! videorate ! " + self.video_caps + " ! appsink name=video_main drop=true max-buffers=5 emit-signals=1 "
        pipe_str_main += "demux.audio ! queue ! aacparse ! decodebin ! audioconvert ! " + self.audio_caps + " ! appsink name=audio_main drop=true max-buffers=5 emit-signals=1 "

        pipe_str_backup = pipe_str_main.replace(self.src_url_main, self.src_url_backup).replace("video_main", "video_backup").replace("audio_main", "audio_backup")
        print()
        print(pipe_str_main)
        print()
        print(pipe_str_backup)
        print()
        print(pipe_str_filler)
        print()
        self.filler_pipe = Gst.parse_launch(pipe_str_filler)
        self.main_pipe = Gst.parse_launch(pipe_str_main)
        self.backup_pipe = Gst.parse_launch(pipe_str_backup)

        self.video_filler_sink = self.filler_pipe.get_by_name("video_filler")
        self.video_main_sink = self.main_pipe.get_by_name("video_main")
        self.video_backup_sink = self.backup_pipe.get_by_name("video_backup")

        self.audio_filler_sink = self.filler_pipe.get_by_name("audio_filler")
        self.audio_main_sink = self.main_pipe.get_by_name("audio_main")
        self.audio_backup_sink = self.backup_pipe.get_by_name("audio_backup")

        self.video_filler_sink.connect("new-sample", self.update_video_filler, self.video_filler_sink)
        self.video_main_sink.connect("new-sample", self.update_video_main, self.video_main_sink)
        self.video_backup_sink.connect("new-sample", self.update_video_backup, self.video_backup_sink)

        self.audio_filler_sink.connect("new-sample", self.update_audio_filler, self.audio_filler_sink)
        self.audio_main_sink.connect("new-sample", self.update_audio_main, self.audio_main_sink)
        self.audio_backup_sink.connect("new-sample", self.update_audio_backup, self.audio_backup_sink)

        pipe_str_out = "appsrc emit-signals=True is-live=true stream-type=0 name=video_out ! " + self.video_caps + " ! "
        pipe_str_out += " queue ! nvh264enc bitrate=20000 preset=2 rc-mode=3 !  h264parse ! queue ! flvmux name=mux streamable=true ! queue ! rtmpsink sync=true location=" + self.sink_url + " "
        pipe_str_out += "appsrc emit-signals=True is-live=true stream-type=0 name=audio_out ! " + self.audio_caps + " ! audioconvert ! voaacenc perfect-timestamp=true ! aacparse ! queue ! mux. "
        print(pipe_str_out)
        self.out_pipe = Gst.parse_launch(pipe_str_out)
        self.video_out_src = self.out_pipe.get_by_name("video_out")
        self.video_out_src.set_property("format", Gst.Format.TIME)
        self.audio_out_src = self.out_pipe.get_by_name("audio_out")
        self.audio_out_src.set_property("format", Gst.Format.TIME)
        # self.out_src.connect("need-data", self.update_out, self.out_src)

        self.out_pipe.set_state(Gst.State.PLAYING)
        self.filler_pipe.set_state(Gst.State.PLAYING)
        self.main_pipe.set_state(Gst.State.PLAYING)
        self.backup_pipe.set_state(Gst.State.PLAYING)

    def update_video_filler(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        print()
        print("filler")
        print(caps)
        print()
        if self.active_input == 0:
            self.video_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_video_main(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        print()
        print("main")
        print(caps)
        print()
        if self.active_input == 1:
            # if not self.is_caps_set:
            #     self.is_caps_set = True
            #     self.video_out_src.set_caps(caps)
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
        print()
        print("filler")
        print(caps)
        print()
        if self.active_input == 0:
            self.audio_out_src.emit("push-buffer", buf)
        return Gst.FlowReturn.OK

    def update_audio_main(self, sink, data):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        print()
        print("main")
        print(caps)
        print()
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
    # if sw.active_input < 2:
    #     sw.active_input += 1
    # else:
    #     sw.active_input = 0
    # print(sw.active_input)