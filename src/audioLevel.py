from PySide6.QtCore import QThread

import numpy as np
import soundcard as sc

from math import sqrt, exp, log


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

def run_fft(buffer):
    buffer = buffer * np.hanning(buffer.size)
    raw = np.fft.rfft(buffer)
    absolute = np.abs(raw[1:])
    return absolute

def apply_filter(fft_raw, fft_filtered, newsize, samplerate, attack, decay):
    kfft = (exp((-2) / (samplerate/(newsize) * attack * 0.001)),
            exp((-2) / (samplerate/(newsize) * decay * 0.001)))

    scalar = 1 / sqrt(4096)
    for iBin in range(fft_raw.size):
        x0 = fft_filtered[iBin]
        x1 = (fft_raw[iBin].real**2) * scalar
        x0 = x1 + kfft[int(x1 < x0)] * (x0 - x1)
        fft_filtered[iBin] = x0

    return fft_filtered

class audioLevel(QThread):
    def __init__(self, parent, samplerate, buffersize, capturesize, devname=None, attack=1, decay=1):
        QThread.__init__(self, parent)
        self.exiting = False

        self.buffer = np.zeros(buffersize)
        self.fft_filtered = np.zeros(buffersize)

        self.device = get_device(samplerate, devname)
        self.capture = capture_generator(self.device, capturesize)
        self.newdata = 0

        self.samplerate = samplerate
        self.attack = attack
        self.decay = decay
    
    def run(self):
        while not self.exiting:
            self.capture()

            if self.newdata:
                fft_raw = run_fft(self.buffer)
                self.fft_filtered = apply_filter(fft_raw, self.fft_filtered, self.newdata, self.samplerate, self.attack, self.decay)
                self.newdata = 0
    
    def capture(self):
        data = next(self.capture)
        self.newdata += data.size
        self.buffer = np.append(self.buffer[data.size:], data)