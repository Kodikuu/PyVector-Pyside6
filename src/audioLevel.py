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

def apply_binning(fft_filtered, bands, freq_min, freq_max, samplerate):
    df = samplerate / fft_filtered.size
    scalar = 2 / samplerate

    out = np.zeros(bands)
    bandFreqs = calculate_bands_freqs(bands, freq_min, freq_max)

    iBin = 0
    iBand = 0
    f0 = 0.0
    while iBin < fft_filtered.size and iBand < bands:
        fLin1 = (iBin+0.5)*df
        fLog1 = bandFreqs[iBand]
        x = fft_filtered[iBin]

        if fLin1 <= fLog1:
            out[iBand] += (fLin1-f0) * x * scalar
            f0 = fLin1
            iBin += 1
        else:
            out[iBand] += (fLog1-f0) * x * scalar
            f0 = fLog1
            iBand += 1

    return out

def calculate_bands_freqs(bands, freq_min, freq_max):
    step = (log(freq_max/freq_min) / bands) / log(2)

    bandFreq = [freq_min*2**(step/2), ]
    for i in range(1, bands):
        bandFreq.append(bandFreq[i-1]*2**step)

    return bandFreq

class audioLevel(QThread):
    def __init__(self, parent, samplerate, buffersize, capturesize, devname=None, attack=1, decay=1):
        QThread.__init__(self, parent)
        self.exiting = False

        self.buffer = np.zeros(buffersize)
        self.fft_filtered = np.zeros(buffersize)

        self.device = get_device(samplerate, devname)
        self.capture = capture_generator(self.device, capturesize)

        self.samplerate = samplerate
        self.attack = attack
        self.decay = decay
    
    def run(self):
        while not self.exiting:
            newdata = self.nextCapture()

            if newdata:
                fft_raw = run_fft(self.buffer)
                self.fft_filtered = apply_filter(fft_raw, self.fft_filtered, newdata, self.samplerate, self.attack, self.decay)
                self.newdata = 0
    
    def nextCapture(self):
        data = next(self.capture)
        self.buffer = np.append(self.buffer[data.size:], data)
        return data.size
    
    def createPoints(self, width, height, originY, bands, sensitivity=35, freq_min=20, freq_max=20000):
        rawbins = apply_binning(self.fft_filtered, bands, freq_min, freq_max, self.samplerate)
        if max(rawbins) > 0:
            scaledbins = rawbins / 10
            unclippedbins = ((10/sensitivity)*np.log10(scaledbins))+1
            bins = np.clip(unclippedbins, 0, 1)
        else:
            bins = [0 for i in range(bands)]

        partpoints = [height*val for val in bins]

        return [[width*pos/(bands-1), originY-partpoints[pos]] for pos in range(bands)]