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

        input_pipe_str = 'videotestsrc pattern=ball '\
                '! video/x-raw, format=BGRA, width=640, height=480, framerate=30/1 '\
                '! queue '\
                '! appsink name=asink emit-signals=1 '\

        self.inputPipe = Gst.parse_launch(input_pipe_str)
        self.inputAppSink = self.inputPipe.get_by_name('asink')
        self.inputAppSink.connect("new-sample", self.update_last_sample, self.inputAppSink)

        output_pipe_str = 'appsrc name=asrc ' \
                          '! video/x-raw, format=BGRA, width=640, height=480, framerate=30/1 ' \
                          '! videoconvert ' \
                          '! xvimagesink '

        self.outputPipe = Gst.parse_launch(output_pipe_str)
        self.outputAppSink = self.outputPipe.get_by_name('asrc')
        self.outputAppSink.connect("need-data", self.output_sample)

        self.inputPipe.set_state(Gst.State.PLAYING)
        time.sleep(1)
        self.outputPipe.set_state(Gst.State.PLAYING)

        # self.overlayImage = cv2.imread("image/video-play-4-48.png", cv2.IMREAD_UNCHANGED)

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

    def output_sample(self, src, length):
        # print(self.lastSample.size)
        bytes1 = memoryview(self.lastSample).tobytes()
        # buf = Gst.Buffer()
        # print(dir(buf))
        #['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__gtype__', '__hash__', '__info__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_clear_boxed', 'add_meta', 'add_parent_buffer_meta', 'add_protection_meta', 'add_reference_timestamp_meta', 'append', 'append_memory', 'append_region', 'copy', 'copy_deep', 'copy_into', 'copy_region', 'dts', 'duration', 'extract', 'extract_dup', 'fill', 'find_memory', 'foreach_meta', 'get_all_memory', 'get_flags', 'get_max_memory', 'get_memory', 'get_memory_range', 'get_meta', 'get_n_meta', 'get_reference_timestamp_meta', 'get_size', 'get_sizes', 'get_sizes_range', 'has_flags', 'insert_memory', 'is_all_memory_writable', 'is_memory_range_writable', 'map', 'map_range', 'memcmp', 'memset', 'mini_object', 'n_memory', 'new', 'new_allocate', 'new_wrapped', 'new_wrapped_full', 'offset', 'offset_end', 'peek_memory', 'pool', 'prepend_memory', 'pts', 'remove_all_memory', 'remove_memory', 'remove_memory_range', 'remove_meta', 'replace_all_memory', 'replace_memory', 'replace_memory_range', 'resize', 'resize_range', 'set_flags', 'set_size', 'unmap', 'unset_flags']

        # buf.fill(0, bytes1)
        buf = Gst.Buffer.new()
        buf.new_wrapped(bytes1)
        print(buf.get_sizes())
        ret, map_info = buf.map(Gst.MapFlags.READ | Gst.MapFlags.WRITE)
        print(map_info.data)

        ##bytes1 = memoryview(self.lastSample).tobytes()
        ##src.emit('push-buffer', Gst.Buffer.new_wrapped(bytes1))

        src.emit('push-buffer', buf)
        # return Gst.FlowReturn.OK





    # def on_draw(self, _overlay, context, _timestamp, _duration):
    #     shape = np.shape(self.overlayImage)
    #     surface = cairo.ImageSurface.create_for_data(
    #         self.overlayImage, cairo.FORMAT_ARGB32, shape[0], shape[1])
    #
    #     context.set_source_surface(surface)
    #     context.rectangle(0, 0, shape[0], shape[1])
    #     context.fill()
    #     context.stroke()
    #
    # def set_overlay_image(self, image):
    #     self.overlayImage = image
    #
    # def get_last_sample(self):
    #     return self.lastSample


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
