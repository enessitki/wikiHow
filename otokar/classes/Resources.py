# -*- coding: windows-1254 -*-
import xml.etree.ElementTree as ET
import os
from PyQt5.QtGui import QColor, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, QRectF
from classes import UKBParams

dirname = os.path.dirname(__file__)

constPathTR = UKBParams.dirResources + "consts_tr.xml"
constPathENG = UKBParams.dirResources + "consts.xml"
constPath = UKBParams.dirResources + "consts.xml"


class Resources:
    selectedLanguage = []
    # primaryColor = "#007769"
    # primaryColorDark = "#004a3f"
    # primaryColorLight = "#48a697"
    # secondaryColor = "#00acc1"
    # secondaryColorDark = "#007c91"
    # secondaryColorLight = "#5ddef4"
    # primaryColor = "#000000FF"
    # primaryColorDark = "#000000FF"
    # primaryColorLight = "#000000FF"
    # secondaryColor = "#F4F7FCFF"
    # secondaryColorDark = "#A9A9A9FF"
    # secondaryColorDeepDark = "#808080FF"
    # # secondaryColorDark = "#c2c2c2"
    # secondaryColorLight = "#F4F7FCFF"

    primaryColor = "#000000"
    primaryColorDark = "#000000"
    primaryColorLight = "#000000"
    secondaryColor = "#F4F7FC"
    secondaryColorDark = "#A9A9A9"
    secondaryColorDeepDark = "#808080"
    # secondaryColorDark = "#c2c2c2"
    secondaryColorLight = "#F4F7FC"

    # primaryColor = "#263238"
    # primaryColorDark = "#000a12"
    # primaryColorLight = "#4f5b62"
    # secondaryColor = "#03a9f4"
    # secondaryColorDark = "#007ac1"
    # secondaryColorLight = "#67daff"
    lightText = "#ffffffff"
    darkText = "#000000"
    disabled = 'grey'
    warning = "#8e4700"
    error = "#8B0000"
    # error = "#ff000c"
    info = "#004266"

    def __init__(self):
        if constPath is not None:
            self.tree = ET.parse(constPath)
            self.root = self.tree.getroot()
        else:
            self.treeTr = ET.parse(constPathTR)
            self.rootTr = self.treeTr.getroot()

            self.treeEng = ET.parse(constPathENG)
            self.rootEng = self.treeEng.getroot()

    def set_language(self, lan):
        self.selectedLanguage.append(lan)

        if len(self.selectedLanguage) > 1:
            self.selectedLanguage.pop(0)

    def get(self, tag):
        if constPath is not None:
            for item in self.root.iter(tag):
                return item.get('value')

        elif self.selectedLanguage[0] == "eng":
            for item in self.rootEng.iter(tag):
                return item.get('value')
        else:
            for item in self.rootTr.iter(tag):
                return item.get('value')

        return 0

    def get_primary_color(self):
        [r, g, b] = self.color_code_converter(self.primaryColor)
        return QColor(r, g, b)

    def get_primary_color_dark(self):
        [r, g, b] = self.color_code_converter(self.primaryColorDark)
        return QColor(r, g, b)

    def get_primary_color_light(self):
        [r, g, b] = self.color_code_converter(self.primaryColorLight)
        return QColor(r, g, b)

    def get_secondary_color(self):
        [r, g, b] = self.color_code_converter(self.secondaryColor)
        return QColor(r, g, b)

    def get_secondary_color_dark(self):
        [r, g, b] = self.color_code_converter(self.secondaryColorDark)
        return QColor(r, g, b)

    def get_secondary_color_light(self):
        [r, g, b] = self.color_code_converter(self.secondaryColorLight)
        return QColor(r, g, b)

    def getQColor(self, color):
        [r, g, b] = self.color_code_converter(color)
        return QColor(r, g, b)

    @staticmethod
    def set_color(w, color):
        w.setAutoFillBackground(True)
        pal = w.palette()
        pal.setColor(w.backgroundRole(), color)
        w.setPalette(pal)

    def paintEvent(self, w):
        painter = QPainter(w)
        painter.begin(w)
        gradient = QLinearGradient(QRectF(w.rect()).topLeft(), QRectF(w.rect()).bottomLeft())
        gradient.setColorAt(0.0, Qt.black)
        gradient.setColorAt(0.4, Qt.gray)
        gradient.setColorAt(0.7, Qt.black)
        painter.setBrush(gradient)
        painter.drawRoundedRect(w.rect(), 10.0, 10.0)
        painter.end()

    def styleSheet(self):
        font = 'bold 24px '
        height = '30px'

        styeSheet = " QTabBar::tab:selected  {border: 2px solid black; border-radius: 2px; width: 250; font : "+font+"; background-color :" + self.secondaryColor + "; color: " + self.lightText + "; }" +\
            " QTabBar::tab:!selected {border: 2px solid black; border-radius: 2px; width: 250; font : "+font+"; background-color :" + self.secondaryColorDark + "; color: " + self.lightText + "; }" +\
            " QTabBar::tab:!enabled  {border: 2px solid black; border-radius: 2px; width: 250; font : "+font+"; background-color :" + self.primaryColorDark + "; color: " + self.disabled + "; }" +\
            " QListWidget{border: 2px solid black;font : "+font+"; background-color :" + self.secondaryColorDark + "; color: " + self.lightText + "; }" +\
            " QListWidget::item:alternate{background-color :" + self.secondaryColor +";}"+\
            " QListWidget::item:hover{background-color :" + self.secondaryColorLight +"; color: " + self.darkText + "; }"+\
            " QListWidget::item:selected{background-color :" + self.secondaryColorLight +"; color: " + self.darkText + "; }"+ \
            " QPushButton{height: "+height+"; font : "+font+"; background-color :" + self.secondaryColor + "; color: " + self.darkText + "; }" +\
            " QPushButton:pressed{background-color :" + self.secondaryColor + "}" +\
            " QPushButton:hover{background-color :" + self.secondaryColor + "}" +\
            " QLineEdit{height: "+height+"; font : "+font+";}" +\
            " QLabel{border: None; font : "+font+"; color: "+self.lightText+";}" +\
            " QComboBox{height: "+height+"; font : "+font+"; background-color :" + self.lightText +"; color: " + self.darkText + ";}" +\
            " QComboBox::item{height: "+height+"; font : "+font+"; background-color :" + self.lightText +"; color: " + self.darkText + ";}" + \
            " QComboBox::item:hover{background-color :" + self.secondaryColor + "; color: " + self.darkText + "; }" + \
            " QComboBox::item:selected{background-color :" + self.secondaryColor + "; color: " + self.darkText + "; }" + \
            " QComboBox::drop-down{width: 100px; height: 100px;}" + \
            " QPlainTextEdit{border: None; font : "+font+";}" +\
            " QRadioButton{font : "+font+"; color:"+self.lightText+";}"\
            " QRadioButton::indicator{width:24; height:24;}" +\
            " QRadioButton::indicator:checked{image: url(" + UKBParams.dirResources + "checked.png" + ");}" +\
            " QRadioButton::indicator:unchecked{image: url(" + UKBParams.dirResources + "unchecked.png" + ");}" +\
            " QGroupBox{font : "+font+"; color:"+self.lightText+";}"\
            " QLCDNumber{font : "+font+"; color:"+self.lightText+";}"\
            " QCheckBox{font : "+font+"; color:"+self.lightText+";}" \
            " QCheckBox::indicator{width:24; height:24;}"\
            " QCheckBox::indicator:checked{image: url("+UKBParams.dirResources+"checked.png"+");}" \
            " QGroupBox{border: 2px solid white; margin-top: 1em;}"\
            " QLCDNumber{border: 0px;}"\

        return styeSheet

    @staticmethod
    def color_code_converter(text):
        r = int(text[1:3], 16)
        g = int(text[3:5], 16)
        b = int(text[5:7], 16)

        return [r, g, b]
