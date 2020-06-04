"""
    export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD
    gst-launch-1.0 videotestsrc ! gstplugin_py int-prop=100 float-prop=0.2 bool-prop=True str-prop="set" ! fakesink

"""

import logging
import timeit
import traceback
import time
import numpy as np
import cv2
import threading

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, GLib, GstBase, GstVideo  # noqa:F401,F402

FORMATS = "{BGR, RGB}"


def buffer_to_np(gst_buffer, gst_caps):
    # sample = sink.emit("pull-sample")
    # buf = sample.get_buffer()
    # caps = sample.get_caps()
    return np.ndarray(
        (gst_caps.get_structure(0).get_value('height'),
         gst_caps.get_structure(0).get_value('width'),
         3),
        buffer=gst_buffer.extract_dup(0, gst_buffer.get_size()),
        dtype='B').copy()


class SyncArrays:
    def __init__(self):
        self.arr0 = []
        self.arr1 = []
        self.arr2 = []

    def append(self, val0, val1, val2):
        self.arr0.append(val0)
        self.arr1.append(val1)
        self.arr2.append(val2)

    def pop(self, index=0):
        return self.arr0.pop(index), self.arr1.pop(index), self.arr2.pop(index)

    def get(self, index):
        return self.arr0[index], self.arr1[index], self.arr2[index]

    def __len__(self):
        return len(self.arr0)


class GstBufferProcessPy(GstBase.BaseTransform):

    GST_PLUGIN_NAME = 'gstbufferprocess_py'

    __gstmetadata__ = ("gstbufferprocess",  # Name
                       "Filter",   # Transform
                       "gstbufferprocess",  # Description
                       "none")  # Author

    __gsttemplates__ = (Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            # Set to RGB format
                                            Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")),
                        Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            # Set to RGB format
                                            Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")))

    # Explanation: https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html#GObject.GObject.__gproperties__
    # Example: https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html#properties
    __gproperties__ = {

        # Parameters from cv2.gaussian_blur
        # https://docs.opencv.org/3.0-beta/modules/imgproc/doc/filtering.html#gaussianblur
        "delay": (GObject.TYPE_INT64,  # type
                  "delay",  # nick
                  "delay",  # blurb
                  1,  # min
                  GLib.MAXINT,  # max
                  3,  # default
                  GObject.ParamFlags.READWRITE  # flags
                  ),
    }

    def __init__(self):
        super(GstBufferProcessPy, self).__init__()
        self.delay = 3
        self.set_in_place(True)
        self.set_passthrough(False)
        self.filler = None
        self.frameBuffer = SyncArrays()

        self.processThread = threading.Thread(target=self.process_loop)
        self.processThread.daemon = True
        # self.processThread.start()

    def do_get_property(self, prop: GObject.GParamSpec):
        if prop.name == 'delay':
            return self.delay
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop: GObject.GParamSpec, value):
        if prop.name == 'delay':
            self.delay = value
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def set_filler(self, caps):
        self.filler = np.zeros((caps.get_structure(0).get_value('height'),
                                caps.get_structure(0).get_value('width'),
                                3), dtype="B")

    @staticmethod
    def index_of(arr, val):
        try:
            return arr.index(val)
        except:
            return None

    # def do_transform_ip(self, inbuffer: Gst.Buffer) -> Gst.FlowReturn:
    def do_transform(self, inbuffer: Gst.Buffer, outbuffer: Gst.Buffer) -> Gst.FlowReturn:
        current_time = time.time()
        try:
            self.frameBuffer.append(buffer_to_np(inbuffer, self.sinkpad.get_current_caps()), 0, current_time)
            # print(len(self.frameBuffer))

            # if len(self.frameBuffer) > 0 and current_time - self.frameBuffer.arr2[0] >= self.delay:
            out_frame, _, _ = self.frameBuffer.pop(0)
            outbuffer.fill(0, out_frame.tobytes())
            # else:
            #     if self.filler is None:
            #         self.set_filler(self.sinkpad.get_current_caps())
            #     outbuffer.fill(0, self.filler.tobytes())
            outbuffer.pts += int(self.delay*1e9)
            print(inbuffer.pts, outbuffer.pts)

        except Exception as e:
            logging.error(e)

        return Gst.FlowReturn.OK

    def process_loop(self):
        while True:
            time.sleep(0.004)
            index = self.index_of(self.frameBuffer.arr1, 0)
            if index is not None and len(self.frameBuffer) >= index + 60:
                print("here")
                self.frameBuffer.arr1[index: index + 60] = [1] * 60
                ref_frame, _, ref_timestamp = self.frameBuffer.get(index)
                if index == 0:
                    ret_frames = self.process(self.frameBuffer.arr0[index + 59::-1].copy())
                else:
                    ret_frames = self.process(self.frameBuffer.arr0[index + 59:index - 1:-1].copy())
                print(len(ref_frame),len(ref_frame))
                index2 = self.index_of(self.frameBuffer.arr1, 1)
                if self.frameBuffer.arr2[index2] == ref_timestamp:
                    # self.frameBuffer.arr0[index2: index2 + 60] = ret_frames[-1:0:-1].copy()
                    self.frameBuffer.arr1[index2: index2 + 60] = [2] * 60
                else:
                    print("out failed.")
            # else:
            #     print("input failed.")

    def process(self, frames):
        for idx, frame in enumerate(frames):
            frames[idx] = cv2.blur(frame, (5, 5))
        return frames


GObject.type_register(GstBufferProcessPy)
__gstelementfactory__ = (GstBufferProcessPy.GST_PLUGIN_NAME,
                         Gst.Rank.NONE, GstBufferProcessPy)