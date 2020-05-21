import sys, os
from itertools import cycle
import shutil
import PyQt5.QtMultimedia as M
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)
#import moviepy.editor as mp
from pathlib import Path


class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.soundPlayer = QMediaPlayer()

        btn_size = QSize(16, 16)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setFixedSize(640, 480)
        self.videoLayout = QtWidgets.QHBoxLayout()

        self.imageLabel = QLabel(self)
        self.imageLabel.resize(640, 480)

        self.videoLayout.addWidget(self.imageLabel)
        self.videoLayout.addWidget(self.videoWidget)

        self.viewWidget = QtWidgets.QWidget()
        self.viewWidget.setLayout(self.videoLayout)
        self.viewWidget.setFixedSize(640, 480)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        #self.scroll.setWidget(self.imageLabel)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btn_size)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.stretchButton = QPushButton('Dosyalar')
        self.stretchButton.setFixedHeight(24)
        self.stretchButton.clicked.connect(self.stretch)

        self.nextButton = QPushButton('Sonraki')
        self.nextButton.setFixedHeight(24)
        self.nextButton.setIconSize(btn_size)
        self.nextButton.clicked.connect(self.next_file)

        self.previousButton = QPushButton('Önceki')
        self.previousButton.setFixedHeight(24)
        self.previousButton.setIconSize(btn_size)
        self.previousButton.clicked.connect(self.prev_file)

        self.extractButton = QPushButton('Aktar')
        self.extractButton.setFixedHeight(24)
        self.extractButton.clicked.connect(self.extract_file)

        self.removeButton = QPushButton('Sil')
        self.removeButton.setFixedHeight(24)
        self.removeButton.clicked.connect(self.remove)

        # self.zoomButton = QPushButton('Yakınlaştır')
        # self.zoomButton.setFixedHeight(24)
        # self.zoomButton.clicked.connect(self.zoom_in)
        #
        # self.zoomOutButton = QPushButton('Uzaklaştır')
        # self.zoomOutButton.setFixedHeight(24)
        # self.zoomOutButton.clicked.connect(self.zoom_out)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.stretchButton)
        control_layout.addWidget(self.playButton)
        # control_layout.addWidget(self.zoomButton)
        # control_layout.addWidget(self.zoomOutButton)
        control_layout.addWidget(self.previousButton)
        control_layout.addWidget(self.nextButton)
        control_layout.addWidget(self.extractButton)
        control_layout.addWidget(self.removeButton)

        control_layout.addWidget(self.positionSlider)

        self.listLayout = QVBoxLayout()

        self.treeview = QTreeView()
        self.treeview.setFixedWidth(200)
        self.listLayout.addWidget(self.treeview)

        self.workspace = '/home/esetron/PycharmProjects/Gstreamer-demo/media/'

        filters = ["*.png", "*.mp4"]
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(self.workspace)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.dirModel.setNameFilters(filters)
        self.dirModel.setNameFilterDisables(0)

        self.treeview.setModel(self.dirModel)

        self.treeview.setRootIndex(self.dirModel.index(self.dirModel.rootPath()))

        self.treeview.doubleClicked.connect(self.list_clicked)

        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.treeview)
        top_layout.addWidget(self.viewWidget)
        layout.addLayout(top_layout)
        layout.addLayout(control_layout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.soundPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    def list_clicked(self, index):
        self.set_media(index)

    def next_file(self):
        index = self.treeview.indexBelow(self.treeview.currentIndex())
        if str(index.data()).find(".") > -1 and str(self.treeview.currentIndex().data()).find(".") > -1:
            self.treeview.setCurrentIndex(index)
            self.set_media(index)

    def prev_file(self):
        index = self.treeview.indexAbove(self.treeview.currentIndex())
        if str(index.data()).find(".") > -1 and str(self.treeview.currentIndex().data()).find(".") > -1:
            self.treeview.setCurrentIndex(index)
            self.set_media(index)

    def set_media(self, index):
        # self.videoLayout.removeWidget(self.videoWidget)
        # self.videoLayout.removeWidget(self.imageLabel)
        index_item = self.dirModel.index(index.row(), 0, index.parent())

        file_name = self.dirModel.fileName(index_item)
        file_path = self.dirModel.filePath(index_item)
        print(file_path)
        if file_name.find(".") == -1:  # a folder
            pass
            # self.filesFullPathList = os.listdir(self.workspace + clicked_name)
            # self.currentFolder = clicked_name + "/"
        else:
            split = file_name.split(".")
            base_name = split[0]
            extension = split[1]

            if extension == "png":
                #self.videoLayout.removeWidget(self.videoWidget)
                #self.videoLayout.removeWidget(self.imageLabel)
                # self.videoLayout.addWidget(self.imageLabel)
                # self.selectedFileFullPath = file_path
                # self.imageLabel.resize(640, 480)
                self.play(force="pause")
                pixmap = QPixmap(file_path)
                self.imageLabel.setPixmap(pixmap)
                self.imageLabel.setVisible(True)
                self.videoWidget.setVisible(False)
            else:
                # self.videoLayout.removeWidget(self.imageLabel)
                # self.videoLayout.addWidget(self.videoWidget)
                audio_file_name = base_name + '.wav'
                audio_file_path = file_path.replace(file_name, audio_file_name)
                self.soundPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(audio_file_path)))

                # self.selectedFileFullPath = file_path
                self.mediaPlayer.setMedia(
                        QMediaContent(QUrl.fromLocalFile(file_path)))
                self.playButton.setEnabled(True)
                # folder = os.path.dirname(self.selectedFileFullPath)
                # print("-" + folder)
                self.statusBar.showMessage(file_path)

                self.imageLabel.setVisible(False)
                self.videoWidget.setVisible(True)

                self.play(force="play")

    def play(self, force=None):
        if force is None:
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.soundPlayer.pause()
                self.mediaPlayer.pause()
            else:
                self.soundPlayer.play()
                self.mediaPlayer.play()
        elif force == "pause":
            self.soundPlayer.pause()
            self.mediaPlayer.pause()
        elif force == "play":
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

    def remove(self):
        index = self.treeview.currentIndex()
        index_item = self.dirModel.index(index.row(), 0, index.parent())

        file_name = self.dirModel.fileName(index_item)
        file_path = self.dirModel.filePath(index_item)

        if file_name.find(".") > -1:
            file_path = file_path.replace(file_name, "")

        qmRemove = QtWidgets.QMessageBox
        choise = qmRemove.question(self, '', "Emin misiniz ?", qmRemove.Yes | qmRemove.No)

        if choise == qmRemove.Yes:
            print(file_path)
            os.system("rm -r " + file_path)
        else:
            print("Cancelled")

    def extract_file(self, index):
        # find usb
        mnt_root = "/media/esetron"
        usb_list = os.listdir(mnt_root)
        if len(usb_list) == 0:
            # todo add popup
            print("usb not found popup")
        else:
            target_folder = mnt_root + "/" + usb_list[0] + "/"


            #findusbname
            #usbPath = os.listdir.(/home/pi/media)
            #
            #/home/pi/media/***
            #self.sound = '/home/esetron/PycharmProjects/Gstreamer-demo/media/sound/' + sound
            #onlyName =str(index.data())


            qmExtract = QtWidgets.QMessageBox
            choise = qmExtract.question(self, '', "Dosyaları aktarmak istiyor musunuz?", qmExtract.Yes | QMessageBox.No)
            if choise == qmExtract.Yes:
                index = self.treeview.currentIndex()
                index_item = self.dirModel.index(index.row(), 0, index.parent())

                file_name = self.dirModel.fileName(index_item)
                file_path = self.dirModel.filePath(index_item)

                if file_name.find(".") > -1:
                    file_path = file_path.replace(file_name, "")
                    file_path = file_path[:-1]
                folder_name = file_path.split("/")[-1]
                source_folder = file_path + "/"
                target_folder += folder_name
                print("target_folder", target_folder)
                os.mkdir(target_folder)
                target_folder += "/"

                file_list = os.listdir(file_path)
                print("file_list", file_list)
                for name in file_list:
                    #splitter = str(index.data)
                    onlyName = name.split('.')[0]
                    ext = name.split('.')[1]
                    if ext == "mp4":
                        video = (source_folder + name)
                        sound = (source_folder + onlyName + ".wav")
                        #os.system("cp -r /home/esetron/PycharmProjects/Gstreamer-demo/media/op1 /home/esetron/PycharmProjects/Gstreamer-demo/")
                        os.system("gst-launch-1.0 -v mp4mux name=mux1 ! filesink location=" + '"' + target_folder + name + '"' + " filesrc location=" + video + " ! decodebin ! queue ! x264enc ! h264parse ! mux1. filesrc location=" + sound + " ! decodebin ! opusenc ! mux1.")
                    elif ext == "png":
                        os.system("cp " + source_folder + name + " " + target_folder)
                        #os.system("cp " + '"' + source_folder + '"' + name + '"' + target_folder + '"')  #usb path
            else:
                print("Canceller")
            #shutil.copytree(src,dest)

    def stretch(self):
        self.treeview.setVisible(not self.treeview.isVisible())
        self.treeview.update()

    # def zoom_in(self):
    #     self.imageLabel.resize(800, 600)
    #     #self._displayed_pixmap.scaled(self.width(), self.height(), QtCore.Qt.SmoothTransformation)
    #
    # def zoom_out(self):
    #     #self.imageLabel.setFixedWidth(self.imageLabel.width*1.25)
    #     self.scaleImage(0.8)
    #     pass
    #
    # def normal_size(self):
    #     #self.imageLabel.adjustSize()
    #     #self.ScaleFactor = 1.0
    #     pass

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.setFixedSize(800, 600)
    #player.resize(600, 400)
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
