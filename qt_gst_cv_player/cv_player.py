import cv2
import numpy
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
import qimage2ndarray
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
gi.require_version('GstVideo', '1.0')
gi.require_version('GstAudio', '1.0')
from gi.repository import GstVideo, GstAudio

Gst.init(None)


class TractableLabel(QtWidgets.QLabel):
    def __init__(self, pan_values, parent=None):
        super(TractableLabel, self).__init__(parent)

        self.isPressed = False
        self.x0 = None
        self.y0 = None
        self.xShift = 0
        self.yShift = 0

        self.panValues = pan_values

        self.setMouseTracking(True)
        # print("moveable container initted")

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isPressed = True
        # print("mousePressEvent")

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isPressed = False
        self.x0 = None
        self.y0 = None
        # print("mouseReleaseEvent")

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.isPressed:
            if self.x0 is None:
                self.x0 = a0.globalX()
                self.y0 = a0.globalY()
            else:
                dx = self.geometry().x() - self.x0 + a0.globalX()
                dy = self.geometry().y() - self.y0 + a0.globalY()
                self.xShift += dx - self.geometry().x()

                # print(self.geometry().x(), dx, dx - self.geometry().x(), self.xShift)
                # self.move(dx, dy)
                self.x0 = a0.globalX()
                self.y0 = a0.globalY()

                if dx - self.geometry().x() > 0:
                    self.panValues[0] += 2
                else:
                    self.panValues[0] -= 2

                if dy - self.geometry().y() > 0:
                    self.panValues[1] += 2
                else:
                    self.panValues[1] -= 2

                # print(self.panValues)


class GstCvPlayer(QtWidgets.QWidget):
    def __init__(self, video_source_str, parent=None):
        super().__init__(parent=parent)
        self.active_window = None
        self.videoWidth = None
        self.videoHeight = None
        self.zoomCount = 1
        self.maxZoom = 10
        self.isFlipped = False
        self.panValues = [0, 0]
        self.prevPanValues = [0, 0]
        self.demandedState = "play"

        self.pipe = None
        self.appSink = None
        self.lastSample = None

        self.set_video_src(video_source_str)

        self.layout = QtWidgets.QVBoxLayout()
        self.surfaceLabel = TractableLabel(self.panValues)
        # self.surfaceLabel.setFixedWidth(980)
        # self.surfaceLabel.setFixedHeight(550)
        self.layout.addWidget(self.surfaceLabel)
        self.setLayout(self.layout)

    def update_last_sample(self, sink, data):
        sample = sink.emit("pull-sample")
        last_sample = self.get_last_sample_as_np(sample)
        self.videoHeight, self.videoWidth, depth = numpy.shape(last_sample)
        if self.active_window is None:
            self.active_window = [0, 0, self.videoWidth, self.videoHeight]
        pan_x = 0
        pan_y = 0
        if self.active_window[0] + self.panValues[0] >= 0 and \
                self.active_window[2] + self.panValues[0] <= self.videoWidth:
            pan_x = self.panValues[0]
            self.prevPanValues[0] = self.panValues[0]
        elif self.active_window[0] + self.panValues[0] < 0:
            pan_x = - self.active_window[0]
            self.panValues[0] = pan_x
            self.prevPanValues[0] = self.panValues[0]
        elif self.active_window[2] + self.panValues[0] > self.videoWidth:
            pan_x = self.videoWidth - self.active_window[2]
            self.panValues[0] = pan_x
            self.prevPanValues[0] = self.panValues[0]
        else:
            self.panValues[0] = self.prevPanValues[0]
            pan_x = self.prevPanValues[0]

        if self.active_window[1] + self.panValues[1] >= 0 and \
                self.active_window[3] + self.panValues[1] <= self.videoHeight:
            pan_y = self.panValues[1]
            self.prevPanValues[1] = self.panValues[1]
        elif self.active_window[1] + self.panValues[1] < 0:
            pan_y = - self.active_window[1]
            self.panValues[1] = pan_y
            self.prevPanValues[1] = self.panValues[1]
        elif self.active_window[3] + self.panValues[1] > self.videoHeight:
            pan_y = self.videoHeight - self.active_window[3]
            self.panValues[1] = pan_y
            self.prevPanValues[1] = self.panValues[1]
        else:
            self.panValues[1] = self.prevPanValues[1]
            pan_y = self.prevPanValues[1]

        last_sample = last_sample[
                      self.active_window[1] + pan_y: self.active_window[3] + pan_y,
                      self.active_window[0] + pan_x: self.active_window[2] + pan_x, :]

        if self.isFlipped:
            last_sample = numpy.rot90(last_sample, k=2)

        last_sample = cv2.resize(last_sample, (self.videoWidth, self.videoHeight),
                                 interpolation=cv2.INTER_CUBIC)

        # text overlay
        cv2.putText(last_sample, 'long video info location and time text', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # update surface
        qImage = qimage2ndarray.array2qimage(last_sample)
        pixmap = QtGui.QPixmap(qImage)
        self.surfaceLabel.setPixmap(pixmap)
        self.surfaceLabel.update()

        self.lastSample = last_sample

        # print(self.panValues, self.active_window)
        # print(time.time() - t0)

        return Gst.FlowReturn.OK

    @staticmethod
    def get_last_sample_as_np(sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()

        arr = numpy.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             4),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype='B')
        return arr

    def zoom_in(self):
        self.zoomCount += 1
        if self.zoomCount <= self.maxZoom:
            self.zoom()
        else:
            self.zoomCount = self.maxZoom

    def zoom_out(self):
        if self.zoomCount > 1:
            self.zoomCount -= 1
            self.zoom()

    def reset_zoom(self):
        self.zoomCount = 1
        self.active_window = [0, 0, self.videoWidth, self.videoHeight]
        self.panValues[0] = 0
        self.panValues[1] = 0

    def zoom(self):
        self.active_window = [self.videoWidth * (self.zoomCount - 1) / self.zoomCount / 2,
                              self.videoHeight * (self.zoomCount - 1) / self.zoomCount / 2,
                              self.videoWidth - self.videoWidth * (self.zoomCount - 1) / self.zoomCount / 2,
                              self.videoHeight - self.videoHeight * (self.zoomCount - 1) / self.zoomCount / 2]

        self.active_window = [int(x) for x in self.active_window]

    def flip_surface(self):
        self.isFlipped = not self.isFlipped

    def pan_image(self):
        self.panValues = [x + 10 for x in self.panValues]

    def start(self):
        self.pipe.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipe.set_state(Gst.State.PAUSED)

    def set_video_src(self, video_source_str):
        if self.pipe is not None:
            self.pipe.set_state(Gst.State.NULL)
        pipe_str = video_source_str + \
                   '! videoconvert ' \
                   '! video/x-raw, format=RGBA ' \
                   '! appsink name=asink emit-signals=1 drop=true max-buffers=5 '
        print(pipe_str)
        self.pipe = Gst.parse_launch(pipe_str)
        self.appSink = self.pipe.get_by_name('asink')
        self.appSink.connect("new-sample", self.update_last_sample, self.appSink)

        if self.demandedState is "play":
            self.start()
        else:
            self.stop()

    def screen_shot(self, dir):
        print("here")
        if self.lastSample is not None:
            cv2.imwrite(dir, cv2.cvtColor(self.lastSample, cv2.COLOR_RGBA2BGRA))

    def record(self, dir):
        print(dir)
        output_pipe_str = 'appsrc name=asrc emit-signals=true  ' \
                          '! video/x-raw, format=RGBA, width=' + \
                          str(self.videoWidth) + ', height=' + \
                          str(self.videoHeight) + ', framerate=25/1 ' \
                          '! videoconvert ' \
                          '! queue ' \
                          '! x264enc ' \
                          '! h264parse ' \
                          '! mp4mux ' \
                          '! filesink location=' + dir
        print(output_pipe_str)

        self.outputPipe = Gst.parse_launch(output_pipe_str)
        self.outputAppSink = self.outputPipe.get_by_name('asrc')
        self.outputAppSink.connect("need-data", self.output_sample)
        self.outputPipe.set_state(Gst.State.PLAYING)

    def output_sample(self, src, length):
        # print(length)
        bytes1 = memoryview(self.lastSample).tobytes()
        src.emit('push-buffer', Gst.Buffer.new_wrapped(bytes1))

    def stop_recording(self):
        print("stop record")
        self.outputPipe.send_event(Gst.Event.new_eos())


class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("qt + cv")
        self.setGeometry(0, 0, 1000, 1000)

        self.layout = QtWidgets.QVBoxLayout()
        pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=quad\&audio=0\&compression=60 ' \
                   '! rtph264depay ! avdec_h264 '
        self.player = GstCvPlayer(pipe_str)
        self.layout.addWidget(self.player)
        self.setLayout(self.layout)

        # controls
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self.player.start)
        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.clicked.connect(self.player.stop)
        self.changeVideoButton = QtWidgets.QPushButton("next cam")
        self.changeVideoButton.clicked.connect(self.change_video)
        self.zoomInButton = QtWidgets.QPushButton("zoom +")
        self.zoomInButton.clicked.connect(self.player.zoom_in)
        self.zoomOutButton = QtWidgets.QPushButton("zoom -")
        self.zoomOutButton.clicked.connect(self.player.zoom_out)
        self.resetZoomButton = QtWidgets.QPushButton("reset")
        self.resetZoomButton.clicked.connect(self.player.reset_zoom)
        self.flipButton = QtWidgets.QPushButton("rotate")
        self.flipButton.clicked.connect(self.player.flip_surface)
        self.panButton = QtWidgets.QPushButton("pan")
        self.panButton.clicked.connect(self.player.pan_image)
        self.screenShotButton = QtWidgets.QPushButton("Screen shot")
        self.screenShotButton.clicked.connect(lambda: self.player.screen_shot("/home/esetron/PycharmProjects/wikiHow/qt_gst_cv_player/test.png"))
        self.recordButton = QtWidgets.QPushButton("Record")
        self.recordButton.clicked.connect(
            lambda: self.player.record("/home/esetron/PycharmProjects/wikiHow/qt_gst_cv_player/test.mp4"))
        self.stopRecordButton = QtWidgets.QPushButton("Stop Record")
        self.stopRecordButton.clicked.connect(self.player.stop_recording)

        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.stopButton)
        self.layout.addWidget(self.changeVideoButton)
        self.layout.addWidget(self.zoomInButton)
        self.layout.addWidget(self.zoomOutButton)
        self.layout.addWidget(self.resetZoomButton)
        self.layout.addWidget(self.flipButton)
        self.layout.addWidget(self.panButton)
        self.layout.addWidget(self.screenShotButton)
        self.layout.addWidget(self.recordButton)
        self.layout.addWidget(self.stopRecordButton)

        self.count = 0
        self.show()

    def change_video(self):
        if self.count % 5 is 0:
            pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=1\&audio=0\&compression=60 ' \
                       '! rtph264depay ! avdec_h264 '
        elif self.count % 5 is 1:
            pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=2\&audio=0\&compression=60 ' \
                       '! rtph264depay ! avdec_h264 '
        elif self.count % 5 is 2:
            pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=3\&audio=0\&compression=60 ' \
                       '! rtph264depay ! avdec_h264 '
        elif self.count % 5 is 3:
            pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=4\&audio=0\&compression=60 ' \
                       '! rtph264depay ! avdec_h264 '
        elif self.count % 5 is 4:
            pipe_str = 'rtspsrc latency=0  location=rtsp://192.168.2.154/axis-media/media.amp?videocodec=h264\&camera=quad\&audio=0\&compression=60 ' \
                       '! rtph264depay ! avdec_h264 '

        self.player.set_video_src(pipe_str)
        self.count += 1


app = QtWidgets.QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()

