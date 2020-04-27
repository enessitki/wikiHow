import sys, os
from itertools import cycle
import shutil
import PyQt5.QtMultimedia as M
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)
#import moviepy.editor as mp


class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.soundPlayer = QMediaPlayer()

        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        videoWidget.setFixedSize(300, 400)
        videoLayout = QtWidgets.QHBoxLayout()
        videoLayout.addWidget(videoWidget)
        viewWidget = QtWidgets.QWidget()
        viewWidget.setLayout(videoLayout)
        viewWidget.setFixedSize(640, 480)

        openButton = QPushButton("Open Video")
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.abrir)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.nextButton = QPushButton('next')
        self.nextButton.setFixedHeight(24)
        self.nextButton.setIconSize(btnSize)
        self.nextButton.clicked.connect(self.next_file)

        self.previousButton = QPushButton('prev')
        self.previousButton.setFixedHeight(24)
        self.previousButton.setIconSize(btnSize)
        self.previousButton.clicked.connect(self.prev_file)

        self.extractButton = QPushButton('Extreact')
        self.extractButton.setFixedHeight(24)
        self.extractButton.clicked.connect(self.extract_file)

        self.removeButton = QPushButton('Remove')
        self.removeButton.setFixedHeight(24)
        self.removeButton.clicked.connect(self.remove)

        self.zoomButton = QPushButton('zoom in')
        self.zoomButton.setFixedHeight(24)
        self.zoomButton.clicked.connect(self.zoom_in)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.zoomButton)
        controlLayout.addWidget(self.previousButton)
        controlLayout.addWidget(self.nextButton)
        controlLayout.addWidget(self.extractButton)
        controlLayout.addWidget(self.removeButton)

        controlLayout.addWidget(self.positionSlider)

        listLayout = QHBoxLayout()
        self.treeview = QTreeView()
        self.listview = QListView()
        #self.listWidget = QListWidget()
        listLayout.addWidget(self.treeview)
        #listLayout.addWidget(self.listview)
        #listLayout.addWidget(self.listWidget)

        self.root = '/home/esetron/PycharmProjects/Gstreamer-demo/media/'

        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        #self.fileModel2 = QFileSystemModel()
        #self.fileModel2.setFilter(QDir.NoDotAndDotDot | QDir.Files)

        self.treeview.setModel(self.dirModel)
        self.listview.setModel(self.fileModel)
        #self.listWidget.setModel(self.fileModel2)

        self.treeview.setRootIndex(self.dirModel.index(self.root))
        self.listview.setRootIndex(self.fileModel.index(self.root))
        #self.listWidget.setRootIndex(self.fileModel2.index(path))

        self.treeview.clicked.connect(self.on_clicked)
        self.treeview.doubleClicked.connect(self.list_clicked)
        #self.listview.doubleClicked.connect(self.list_clicked)

        layout = QVBoxLayout()
        topLayout = QHBoxLayout()
        topLayout.addLayout(listLayout)
        topLayout.addWidget(viewWidget)
        #layout.addLayout(listLayout)
        #layout.addWidget(viewWidget)
        layout.addLayout(topLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.soundPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")


    def list_clicked(self, index):
        print(index.data())
        splitter = str(index.data())
        basename = splitter.split('.')[0]
        ext = splitter.split('.')[1]
        sound = basename + '.wav'
        self.sound = '/home/esetron/PycharmProjects/Gstreamer-demo/media/sound/' + sound
        self.soundPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.sound)))

        self.filename = '/home/esetron/PycharmProjects/Gstreamer-demo/media/video/' + splitter
        self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.filename)))
        self.playButton.setEnabled(True)
        folder = os.path.dirname(self.filename)
        print("-" + folder)
        self.statusBar.showMessage(self.filename)

        self.play
        # item = self.listview.currentIndex()
        # print(item)

    def on_clicked(self, index):
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))


    def abrir(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a media file",
                ".", "Video Files (*png *.wav *.mp4)")
        print(fileName)

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.soundPlayer.pause()
            self.mediaPlayer.pause()
        else:
            self.soundPlayer.play()
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
        self.soundPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def next_file(self):
        dirPath = os.path.dirname(self.filename)
        filelist = os.listdir(dirPath)
        for name in filelist:
            if (dirPath + "/" + name) == self.filename:
                if filelist.index(name) != len(filelist) -1:
                    nextFile = filelist.index(name) +1
                else:
                    nextFile = filelist[0]

        print(filelist[nextFile])
        self.filename = (dirPath + "/" + filelist[nextFile])
        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(self.filename)))
        self.play()

    def prev_file(self):
        dirPath = os.path.dirname(self.filename)
        filelist = os.listdir(dirPath)
        for name in filelist:
            if (dirPath + "/" + name) == self.filename:
                if filelist.index(name) != len(filelist):
                    prevFile = filelist.index(name) -1
                else:
                    prevFile = filelist[len(filelist) -1]


        print(filelist[prevFile])
        self.filename = (dirPath + "/" + filelist[prevFile])
        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(self.filename)))
        self.play()

    def remove(self):
        folder = os.path.dirname(self.filename)
        print(folder)
        #os.system("rm -r " + folder)
        pass

    def extract_file(self, index):
        #findusbname
        #usbPath = os.listdir.(/home/pi/media)
        #
        #/home/pi/media/***
        #self.sound = '/home/esetron/PycharmProjects/Gstreamer-demo/media/sound/' + sound
        #onlyName =str(index.data())
        dirPath = os.path.dirname(self.filename)
        fileList = os.listdir(dirPath)
        for name in fileList:
            splitter = str(index.data())
            onlyName = splitter.split('.')[0]
            ext = splitter.split('.')[1]
            if ext == "mp4":
                video = fileList[name]
                sound = (onlyName + ".wav")
                #os.system("cp -r /home/esetron/PycharmProjects/Gstreamer-demo/media/op1 /home/esetron/PycharmProjects/Gstreamer-demo/")
                os.system("gst-launch-1.0 -v mp4mux name=mux1 ! filesink location=out.mp4 filesrc location=" + video + " ! decodebin ! queue ! x264enc ! h264parse ! mux1. filesrc location=" + sound + " ! decodebin ! opusenc ! mux1.")
            elif ext == "png":
                os.system("cp " + name + "usbPath[0]")  #usb path

        #shutil.copytree(src,dest)

    def zoom_in(self):
        #self.scaleImage(1.25)
        pass

    def zoom_out(self):
        #self.scaleImage(0.8)
        pass

    def normal_size(self):
        #self.imageLabel.adjustSize()
        #self.ScaleFactor = 1.0
        pass

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(600, 400)
    player.show()
    sys.exit(app.exec_())



#----------------
# import os
# partitionsFile = open("/proc/partitions")
# lines = partitionsFile.readlines()[2:]#Skips the header lines
# for line in lines:
#     words = [x.strip() for x in line.split()]
#     minorNumber = int(words[1])
#     deviceName = words[3]
#     if minorNumber % 16 == 0:
#         path = "/sys/class/block/" + deviceName
#         if os.path.islink(path):
#             if os.path.realpath(path).find("/usb") > 0:
#                 print "/dev/%s" % deviceName


#'C:\\gstreamer\\1.0\\x86_64\\bin\\gst-launch-1.0.exe -v mp4mux name=mux1 ! filesink location=outputFile852 ' +
#            'filesrc location=inputAudioFile852 ! decodebin ! opusenc ! mux1. ' +
#            'filesrc location=inputVideoFile852 ! decodebin ! videoconvert ! videoscale !' +
#            ' video/x-raw, format=I420, width=1280, height=720, interlace-mode=progressive, multiview-mode=mono,' +
#            ' multiview-flags=0:ffffffff:/right-view-first/left-flipped/left-flopped/right-flipped/right-flopped/half-aspect/mixed-mono,' +
#            ' pixel-aspect-ratio=1/1, chroma-site=mpeg2, colorimetry=1:4:0:0, framerate=25/1 ! x264enc ! mux1.';


#gst-launch-1.0 -v mp4mux name=mux1 ! filesink location=out.mp4 filesrc location=v.mp4 ! decodebin ! queue ! x264enc ! h264parse ! mux1. filesrc location=a.wav ! decodebin ! opusenc ! mux1.^C
