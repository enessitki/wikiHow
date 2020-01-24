import time
import cairo
import numpy as np
import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
gi.require_version('GstVideo', '1.0')
gi.require_version('GstAudio', '1.0')
from gi.repository import GstVideo, GstAudio


Gst.init(None)


class SimpleOverlay(object):

    def __init__(self):
        self.lastSample = None

        pipe_str = 'videotestsrc pattern=ball '\
                '! video/x-raw, format=BGRA, width=640, height=480, framerate=30/1 '\
                '! tee name=t1 '\
                '! queue '\
                '! appsink name=asink emit-signals=1 t1. '\
                '! queue '\
                '! cairooverlay name=overlay '\
                '! videoconvert '\
                '! xvimagesink '

        print(pipe_str)

        self.overlayImage = cv2.imread("image/video-play-4-48.png", cv2.IMREAD_UNCHANGED)

        self.pipe = Gst.parse_launch(pipe_str)
        self.appSink = self.pipe.get_by_name('asink')
        self.appSink.connect("new-sample", self.update_last_sample, self.appSink)
        self.overlay = self.pipe.get_by_name('overlay')
        self.overlay.connect('draw', self.on_draw)
        self.pipe.set_state(Gst.State.PLAYING)

    def update_last_sample(self, sink, data):
        sample = sink.emit("pull-sample")
        arr = self.get_last_sample_as_np(sample)
        self.lastSample = arr
        cv2.imshow("last-sample", arr)
        cv2.waitKey(10)
        return Gst.FlowReturn.OK

    @staticmethod
    def get_last_sample_as_np(sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()

        arr = np.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             4),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype='B')
        return arr

    def on_draw(self, _overlay, context, _timestamp, _duration):
        shape = np.shape(self.overlayImage)
        surface = cairo.ImageSurface.create_for_data(
            self.overlayImage, cairo.FORMAT_ARGB32, shape[0], shape[1])

        context.set_source_surface(surface)
        context.rectangle(0, 0, shape[0], shape[1])
        context.fill()
        context.stroke()

    def set_overlay_image(self, image):
        self.overlayImage = image

    def get_last_sample(self):
        return self.lastSample


s = SimpleOverlay()

while True:
    time.sleep(1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (0, 48)
    fontScale = 1
    fontColor = (0, 0, 0)
    lineType = 2

    cv2.putText(s.lastSample, 'Hello World!',
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                lineType)
