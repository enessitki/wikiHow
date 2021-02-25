import cv2
cap = cv2.VideoCapture('rtsp://127.0.0.1:5900/test')
# cap = cv2.VideoCapture('rtsp://192.168.1.90:554/axis-media/media.amp?videocodec=h264&camera=1&audio=0')

while True:
    hasFrame, frame = cap.read()
    if not hasFrame:
        break

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()