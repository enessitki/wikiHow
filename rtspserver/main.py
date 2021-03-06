#! /usr/bin/python

# pyrtsp - RTSP test server hack
# Copyright (C) 2013  Robert Swain <robert.swain@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GObject, Gst, GstVideo, GstRtspServer

Gst.init(None)


def fn(x,y=5):
    pass

fn(y=10, x=10)


mainloop = GObject.MainLoop()

server = GstRtspServer.RTSPServer()
server.set_service("5900")

mounts = server.get_mount_points()

factory = GstRtspServer.RTSPMediaFactory()
# factory.set_launch('( videotestsrc is-live=1 ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )')
#factory.set_launch('(v4l2src device=/dev/video0 ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! video/x-raw, format=I420 '
#                   '! jpegenc ! rtpjpegpay name=pay0 )')

factory.set_launch('(ximagesrc ! videoconvert '
                   '! jpegenc ! rtpjpegpay name=pay0 )')

# '! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 )')

# gst-launch-1.0 -v rtspsrc name=kgmsrc location="rtsp://127.0.0.1:8554/test" latency=0 protocols=GST_RTSP_LOWER_TRANS_UDP async-handling=true timeout=0 udp-reconnect=0 ! rtpjpegdepay ! jpegdec ! xvimagesink


mounts.add_factory("/test", factory)


server.attach(None)

print("stream ready at rtsp://127.0.0.1:5900/test")
mainloop.run()
