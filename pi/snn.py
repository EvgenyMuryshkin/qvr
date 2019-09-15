# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

# https://randomnerdtutorials.com/video-streaming-with-raspberry-pi-camera/

import io
import picamera
import logging
import socketserver

from http import server

import cv2 as cv
import numpy as np

import os
from time import sleep

import static
from cameraThead import CameraThread
from lib import uptime

import json

print("uptime(sec) = ", uptime())

import serial
port = serial.Serial("/dev/serial0", baudrate=115200, timeout=3.0)

cameraThread = CameraThread()
cameraThread.start()

class Vector3(object):
    def __init__(self, data = "{}"):
        self.__dict__ = json.loads(data)
        if not "x" in self.__dict__.keys():
            self.x = 0
        if not "y" in self.__dict__.keys():
            self.y = 0
        if not "z" in self.__dict__.keys():
            self.z = 0

class StreamingHandler(server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def toServoValue(self, value):
        value = max(-90, min(value, 90))
        return value + 90

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = str(self.headers['Content-Type'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
        
        rotations = Vector3(body)

        # translate to servo parameters
        port.write(bytes([255, self.toServoValue(rotations.x), self.toServoValue(rotations.y), self.toServoValue(rotations.z)]))
        
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = static.load("index.html")
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.jpg':
            frame = cameraThread.frame
            if len(frame) == 0:
                self.send_response(204)
                return

            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(frame))
            self.end_headers()
            self.wfile.write(frame)
            self.wfile.write(b'\r\n')
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = cameraThread.frame
                    if len(frame) == 0:
                        continue

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    # throttle responses
                    sleep(0.1)

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

print("Camera streaming server starting")
# with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
#     output = StreamingOutput()
#     #Uncomment the next line to change your Pi's Camera rotation (in degrees)
#     #camera.rotation = 90
#     camera.start_recording(output, format='mjpeg')
#     try:
#         address = ('', 8000)
#         server = StreamingServer(address, StreamingHandler)
#         server.serve_forever()
#     finally:
#         camera.stop_recording()

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print("Shutdown requested")
    server.shutdown()
except Exception as e:
    logging.error("Server exception: %s", str(e))
finally:
    print("Closing")
    cameraThread.stop()
    #camera.stop_recording()