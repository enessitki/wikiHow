import sys
import numpy as np
import socket
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pickle
import struct
from threading import Thread


HOST='192.168.2.53'
PORT=9001

class ThermalCamera(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Termal Kamera")
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)

        # screen için size policy ekranı kaplar. # bu olmazsa el ile manuel olarak resize belirtmemiz gerekir.
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(True)

        l = QVBoxLayout()
        l.addWidget(self.scrollArea)
        self.setLayout(l)

        # ekranı maximize boyutuna set et
        self.showMaximized()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVisible(True)

        dum=Thread(target=self.getframe)
        dum.start()

    def getframe(self):
        #tcp socket aç
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(10)
        conn, addr = s.accept()

        # Gelen veriyi bayt olarak tanımla
        data = b''

        # size'ı belirle eğer boyutu küçük veri göndereceksek "H" ile değiştir.
        payload_size = struct.calcsize("L")

        while True:

            #veri boyutu kontrolleri
            while len(data) < payload_size:
                data += conn.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]

            #aldığımız veri paketini aç 0. indeks mesaj boyutu
            msg_size = struct.unpack("L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += conn.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            #pickle ile paketlenmiş veri paketini loads ile açıp frame'e tanımla
            frame = pickle.loads(frame_data)
            print(frame)

            #veri paketini qt'nin anlayabileceği şikeilde reshape et #320,240 gelen h,w değeri #np.int8 gelen değer
            frame = np.array(frame).reshape(320, 240).astype(np.int8)

            #qimage de gelen data,h,w,format şeklinde belirle
            qimage = QImage(frame, frame.shape[0], frame.shape[1], QImage.Format_Grayscale8)

            #ekrandaki imagelabel kısmına pixmap olarak her defasında gelen veriyi set et
            self.imageLabel.setPixmap(QPixmap.fromImage(qimage))
            self.imageLabel.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ThermalCamera()
    window.show()
    app.exec_()
