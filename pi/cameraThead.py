import threading
from threading import Condition, Event
from lib import uptime
import picamera
import io
import logging
import cv2 as cv
import numpy as np

# python3 test.py
# Load the model.
net = cv.dnn.readNet('nets/face-detection-adas-0001.xml',
                     'nets/face-detection-adas-0001.bin')
# Specify target device.
net.setPreferableTarget(cv.dnn.DNN_TARGET_MYRIAD)


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                # TODO: some logic error here
                if len(self.frame) != 0:
                    self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class CameraThread(threading.Thread, object):
    lastTime = uptime()
    initialized = 0
    # WTF is AttributeError: __enter__?
    shutdown = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.frame = []

    def logInitialized(self):
        if self.initialized == 0:
            print("Camera ready")
            self.initialized = 1

    def stop(self):
        self.shutdown = 1

    def run(self):
        print("Started streaming")
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            output = StreamingOutput()
            #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            #camera.rotation = -90
            camera.start_recording(output, format='mjpeg')

            try:
                logged = 0
                while self.shutdown == 0:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                    source = cv.imdecode(np.frombuffer(frame, np.uint8), -1)

                    blob = cv.dnn.blobFromImage(source, size=(672, 384), ddepth=cv.CV_8U)
                    net.setInput(blob)
                    out = net.forward()

                    # Draw detected faces on the frame.
                    for detection in out.reshape(-1, 7):
                        confidence = float(detection[2])
                        xmin = int(detection[3] * source.shape[1])
                        ymin = int(detection[4] * source.shape[0])
                        xmax = int(detection[5] * source.shape[1])
                        ymax = int(detection[6] * source.shape[0])
                        if confidence > 0.5:
                            cv.rectangle(source, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))
        
                    timeStamp = uptime()
                    frameRate = round(1 / (timeStamp - self.lastTime), 2)
                    cv.putText(source, str(frameRate) + " fps", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, 255)
                    self.lastTime = timeStamp

                    (ret, frame) = cv.imencode(".jpg", source)
                    
                    self.logInitialized()
                    self.frame = frame
            except Exception as e:
                if self.shutdown == 0:
                    logging.error("Streaming failed %s", str(e))
            finally:
                camera.stop_recording()
