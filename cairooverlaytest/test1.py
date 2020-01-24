import gi
gi.require_version('Gst', '1.0')
import sys
from gi.repository import Gst, GObject
gi.require_version('GstVideo', '1.0')
gi.require_version('GstAudio', '1.0')
from gi.repository import GstVideo, GstAudio
import time
import cairo
import numpy as np
import cv2


Gst.init(None)

im = cv2.imread("image/video-play-4-48.png")



class SimpleOverlay(object):

    def __init__(self):

        pipe_str = 'videotestsrc '\
                '! video/x-raw, format=RGB16, width=640, height=480, framerate=30/1 '\
                '! cairooverlay name=overlay '\
                '! videoconvert '\
                '! xvimagesink '

        print(pipe_str)

        self.pipe = Gst.parse_launch(pipe_str)
        self.overlay = self.pipe.get_by_name('overlay')
        self.overlay.connect('draw', self.on_draw)
        self.pipe.set_state(Gst.State.PLAYING)

    @staticmethod
    def on_draw(_overlay, context, _timestamp, _duration):
        # context.select_font_face('Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        # context.set_font_size(40)
        # context.move_to(100, 100)
        # context.text_path('HELLO')
        # context.set_source_rgb(0.5, 0.5, 1)
        # context.fill_preserve()
        # context.set_source_rgb(0, 0, 0)
        # context.set_line_width(1)
        # context.stroke()
        width, height = 50, 50
        data = np.ndarray(shape=(height, width), dtype=np.uint32)
        surface = cairo.ImageSurface.create_for_data(
            data, cairo.FORMAT_ARGB32, width, height)
        # context = cairo.Context(surface)

        context.rectangle(0, 0, 50, 50)
        # context.set_source_rgb(0,0,0)
        context.set_source_surface(surface)
        context.fill()
        # context.set_source_rgb(0, 0, 0)
        context.stroke()

        print(dir(context))
        # print(dir(_overlay))
        # ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'append_path', 'arc', 'arc_negative', 'clip', 'clip_extents', 'clip_preserve', 'close_path', 'copy_clip_rectangle_list', 'copy_page', 'copy_path', 'copy_path_flat', 'curve_to', 'device_to_user', 'device_to_user_distance', 'fill', 'fill_extents', 'fill_preserve', 'font_extents', 'get_antialias', 'get_current_point', 'get_dash', 'get_dash_count', 'get_fill_rule', 'get_font_face', 'get_font_matrix', 'get_font_options', 'get_group_target', 'get_line_cap', 'get_line_join', 'get_line_width', 'get_matrix', 'get_miter_limit', 'get_operator', 'get_scaled_font', 'get_source', 'get_target', 'get_tolerance', 'glyph_extents', 'glyph_path', 'has_current_point', 'identity_matrix', 'in_clip', 'in_fill', 'in_stroke', 'line_to', 'mask', 'mask_surface', 'move_to', 'new_path', 'new_sub_path', 'paint', 'paint_with_alpha', 'path_extents', 'pop_group', 'pop_group_to_source', 'push_group', 'push_group_with_content', 'rectangle', 'rel_curve_to', 'rel_line_to', 'rel_move_to', 'reset_clip', 'restore', 'rotate', 'save', 'scale', 'select_font_face', 'set_antialias', 'set_dash', 'set_fill_rule', 'set_font_face', 'set_font_matrix', 'set_font_options', 'set_font_size', 'set_line_cap', 'set_line_join', 'set_line_width', 'set_matrix', 'set_miter_limit', 'set_operator', 'set_scaled_font', 'set_source', 'set_source_rgb', 'set_source_rgba', 'set_source_surface', 'set_tolerance', 'show_glyphs', 'show_page', 'show_text', 'show_text_glyphs', 'stroke', 'stroke_extents', 'stroke_preserve', 'tag_begin', 'tag_end', 'text_extents', 'text_path', 'transform', 'translate', 'user_to_device', 'user_to_device_distance']

    #     self.bus = self.pipe.get_bus()
    #     self.bus.add_signal_watch()
    #     self.bus.enable_sync_message_emission()
    #     self.bus.connect("sync-message", self.on_message)
    #
    # def on_message(self, bus, message, src):
    #     pass



s = SimpleOverlay()

while True:
    time.sleep(1)
