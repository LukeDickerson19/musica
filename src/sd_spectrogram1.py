import math
import numpy as np
import shutil
import sounddevice as sd



block_duration = 50
try:
    columns, _ = shutil.get_terminal_size()
except AttributeError:
    columns = 80
gain = 10
low, high = 100, 2000

# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))

samplerate = sd.query_devices(4, 'input')['default_samplerate']

delta_f = (high - low) / (columns - 1)
fftsize = math.ceil(samplerate / delta_f)
low_bin = math.floor(low / delta_f)


def callback(indata, frames, time, status):
    if status:
        text = ' ' + str(status) + ' '
        print('\x1b[34;40m', text.center(columns, '#'),
              '\x1b[0m', sep='')
    if any(indata):
        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        magnitude *= gain / fftsize
        line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                for x in magnitude[low_bin:low_bin + columns])
        print(*line, sep='', end='\x1b[0m\n')
    else:
        print('no input')

with sd.InputStream(
	device=4,
	channels=1,
	callback=callback,
    blocksize=int(samplerate * block_duration / 1000),
    samplerate=samplerate):

    while True:
        response = input()
        if response in ('', 'q', 'Q'):
            break
        for ch in response:
            if ch == '+':
                args.gain *= 2
            elif ch == '-':
                args.gain /= 2
            else:
                print('\x1b[31;40m', usage_line.center(args.columns, '#'),
                      '\x1b[0m', sep='')
                break

