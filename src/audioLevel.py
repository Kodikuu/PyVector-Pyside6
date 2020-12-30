from PySide6.QtCore import QThread

import numpy as np
import soundcard as sc


def get_device(samplerate=48000, name=None):
    if name:
        device = sc.get_microphone(name, include_loopback=True)
    else:
        output = sc.default_speaker()
        device = sc.get_microphone(output.name, include_loopback=True)

    return device.recorder(samplerate)

def capture_generator(device, capturesize):
    with device:
        while True:
            tmpdata = device.record(numframes=capturesize).T  # Capture
            data = sum(tmpdata)  # Merge L+R
            yield data

class audioLevel(QThread):
    def __init__(self, parent, samplerate, buffersize, capturesize, devname=None):
        QThread.__init__(self, parent)
        self.exiting = False

        self.buffer = np.zeros(buffersize)
        self.fft_filtered = np.zeros(buffersize)

        self.device = get_device(samplerate, devname)
        self.capture = capture_generator(self.device, capturesize)
        self.newdata = 0
    
    def run(self):
        while not self.exiting:
            self.capture()

            if self.newdata:
                pass
    
    def capture(self):
        data = next(self.capture)
        self.newdata += data.size
        self.buffer = np.append(self.buffer[data.size:], data)