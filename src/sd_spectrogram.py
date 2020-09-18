#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
import argparse
import math
import numpy as np
import shutil

usage_line = ' press <enter> to quit, +<enter> or -<enter> to change scaling '


'''

    TO DO

        figure out how to specify the channel and get the guitar input or the vocal input

        connect it to pyqt5

        make gui option to do vocals or guitar
            OR both simultaniously

        make it able to record audio and save it to a wav file
        then make it so it can play the wav file back
        do this to hear what its actually recording
            is it capturing the change in pitch in my voice
            the waveform graph looks the same whether i sing high or low
            it would be cool if it was expanded to show the difference
            and it changed color depending on the frequency and selected scale
            and it moved slowly accrose the time axis

        figure out basic PyQt stuff
            how to plot a line
            how to do a scatter plot
            a bar plot
            maybe put the file in coding_tutorials

            also you can use the video for this stuff too

        if its capturing the frequency
            figure out how to display the frequency in the spectogram
                https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch04.html
                    need to determine sample rate (number of samples per second)
                        shouldn't it be RATE?
            make it move slowly over time
            make option to show
                notes or frequency Hz

        it would also be nice to have the graph just be a part of the GUI
        and other parts could have
            text
            buttons
            images

        make a drop down button to select a Key
        make a drop down button to select numbers / letters
        and then display horizontal bars of the minor scale (ex. A minor)
            1 - A - red
            2 - B - orange
            3 - C - yellow
            4 - D - green
            5 - E - blue
            6 - F - violet
            7 - G - white

        make it so you can separate the signal of the vocals and guitar
            scarlett input 1 vs input 2
                https://stackoverflow.com/questions/45039072/how-do-i-use-an-external-microphone-for-pyaudio-instead-of-the-in-built-micropho
                https://stackoverflow.com/questions/20760589/list-all-audio-devices-with-pythons-pyaudio-portaudio-binding
                https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.PyAudio.open

                    if you go to settings > Sound and set the Input and Output to the Scarlett
                        you can specify input_device_index=4, however it gets an over flow error
                        when it calls read(). I need to find the right chunk size for the scarlett

                        however I need to use Jack Sink/Source Input and Output anyway ...

        then move into guitar ML stuff


    SOURCES
        https://www.youtube.com/watch?v=RHmTgapLu4s
        https://github.com/markjay4k/Audio-Spectrum-Analyzer-in-Python/blob/master/audio_spectrumQT.py

        https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch04.html

        Real-Time Text-Mode Spectrogram (aka THIS CODE)
        https://python-sounddevice.readthedocs.io/en/0.3.7/examples.html

    '''




def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

try:
    columns, _ = shutil.get_terminal_size()
except AttributeError:
    columns = 80

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-l', '--list-devices', action='store_true',
                    help='list audio devices and exit')
parser.add_argument('-b', '--block-duration', type=float,
                    metavar='DURATION', default=50,
                    help='block size (default %(default)s milliseconds)')
parser.add_argument('-c', '--columns', type=int, default=columns,
                    help='width of spectrogram')
parser.add_argument('-d', '--device', type=int_or_str,
                    help='input device (numeric ID or substring)')
parser.add_argument('-g', '--gain', type=float, default=10,
                    help='initial gain factor (default %(default)s)')
parser.add_argument('-r', '--range', type=float, nargs=2,
                    metavar=('LOW', 'HIGH'), default=[100, 2000],
                    help='frequency range (default %(default)s Hz)')
args = parser.parse_args()

low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

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

try:
    import sounddevice as sd

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    def callback(indata, frames, time, status):
        if status:
            text = ' ' + str(status) + ' '
            print('\x1b[34;40m', text.center(args.columns, '#'),
                  '\x1b[0m', sep='')
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize
            line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin:low_bin + args.columns])
            print(*line, sep='', end='\x1b[0m\n')
        else:
            print('no input')

    with sd.InputStream(device=4, channels=1, callback=callback,
                        blocksize=int(samplerate * args.block_duration / 1000),
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
except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
