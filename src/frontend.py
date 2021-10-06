from backend import *



class MainWindow(QtWidgets.QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Musica") # set window title
		# self.setStyleSheet(
		#	 open(os.path.join(STYLESHEETS_PATH,
		#		 "main_window.stylesheet"), 'r').read())
		# self.setGeometry(70, 90, 800, 600)#1100, 685) # set window's location and size: (x, y, width, height)
		self.showMaximized()


		# set background color
		self.palette = self.palette()
		self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor('black')) # QtGui.QColor(155, 155, 155))
		self.setPalette(self.palette)

		self.state = {
			'view' : view.SOUND_WAVE
		}

		# Central Component Settings
		self.window = QtWidgets.QWidget()
		self.setCentralWidget(self.window)

		# connection to raw audio input
		self.audio = AudioInput(
			num_indents=0,
			new_line_start=True)
		if not self.audio.connected:
			self.connection_status = QtWidgets.QLabel(self.window)
			self.connection_status.setStyleSheet("QLabel { color : gray }")
			self.connection_status.move(10, 10)
			self.connection_status.setText("audio interface not connected")
			return

		# uncomment piantEvent() to show static fretboard
		# ... the function itself ... its getting called by the PyQt lib by default
		# self.init_sound_wave_view()
		# self.init_frequency_view2()



	def paintEvent(self, event):
		p = QtGui.QPainter()
		p.begin(self)
		self.draw_scale(p,
			reference_note={'string': 6, 'fret' : 5, 'note_number' : 1},
			note_colors='white', # valid values: 'white', 'rainbow', 'triad 1', 'triad 2', ... 'triad 7'
			draw_note_numbers=True,
			draw_fret_numbers=True,
			draw_string_tuning=True,
			draw_scale_name=True)
		p.end()
	def draw_scale(self, p,
		reference_note={'string': 6, 'fret' : 5, 'note_number' : 1},
		note_colors='white',
		draw_note_numbers=True,
		draw_fret_numbers=True,
		draw_string_tuning=True,
		draw_scale_name=True):

		full_scale, scale_name = self.get_scale_on_fretboard(reference_note)

		# F# minor / A major
		self.draw_scale_notes(p, 80,  250, full_scale,
			note_colors=note_colors,
			draw_note_numbers=draw_note_numbers,
			draw_fret_numbers=draw_fret_numbers,
			draw_string_tuning=draw_string_tuning,
			draw_scale_name=draw_scale_name,
			scale_name=scale_name)
	def get_scale_on_fretboard(self, ref_note):
		scale = A_MAJOR
		scale_name_index = 0
		while True:
			if scale[ref_note['string']][ref_note['fret']] == ref_note['note_number']:
				return scale, SCALE_NAMES[scale_name_index]
			else:
				scale = {
					string_number : notes[1:] + [notes[1]] \
					for string_number, notes in scale.items()}
				# "+ [notes[1]]" instead of "+ [notes[0]]" because the last fret
				# of the guitar string shows the same thing as the first fret
				scale_name_index += 1
				if scale == A_MAJOR:
					break
	def draw_scale_notes(self, p, x0, y0, scale_notes,
		note_colors='white',
		draw_note_numbers=True,
		draw_fret_numbers=True,
		draw_string_tuning=True,
		draw_scale_name=True,
		scale_name=None):

		# get triad number, notes, and name if note_color starts with "triad"
		triad_info = None
		if note_colors.startswith('triad'):
			triad_number = int(note_colors.split(' ')[-1])
			triad_notes  = [
				triad_number,
				(triad_number + 2) % 7,
				(triad_number + 4) % 7]
			triad_notes = [7 if tn == 0 else tn for tn in triad_notes]
			triad_name  = MODE_NAMES[triad_number - 1]
			triad_info = {'number' : triad_number, 'name' : triad_name}

		# draw fretboard
		center_fret_coordinates = self.draw_fretboard(
			p, x0, y0,
			draw_fret_numbers=draw_fret_numbers,
			draw_string_tuning=draw_string_tuning,
			draw_scale_name=draw_scale_name,
			scale_name=scale_name,
			triad_info=triad_info)

		# draw notes in scale
		r = 11 # r = circle radius
		for string_number, notes in scale_notes.items():
			for fret_number, note_number in enumerate(notes):
				if note_number == None: continue

				x, y = center_fret_coordinates[string_number][fret_number]

				# cc = circle color
				if note_colors == 'white':
					cc = QtCore.Qt.white
				elif note_colors == 'rainbow':
					if   note_number == 1: cc = QtCore.Qt.yellow
					elif note_number == 2: cc = QtCore.Qt.green
					elif note_number == 3: cc = QtCore.Qt.blue
					elif note_number == 4: cc = QtCore.Qt.magenta
					elif note_number == 5: cc = QtCore.Qt.white
					elif note_number == 6: cc = QtCore.Qt.red
					elif note_number == 7: cc = QtGui.QColor(255,165,0) # orange # cc = circle color
				elif note_colors.startswith('triad'):
					if note_number == triad_notes[0]:   cc = QtCore.Qt.red
					elif note_number == triad_notes[1]: cc = QtCore.Qt.blue
					elif note_number == triad_notes[2]: cc = QtCore.Qt.yellow
					else:                               cc = QtCore.Qt.white
				p.setPen(QtGui.QPen(cc))
				p.setBrush(QtGui.QBrush(cc, QtCore.Qt.SolidPattern))
				p.drawEllipse(QtCore.QPoint(x, y), r, r)

				# draw note_number
				if draw_note_numbers:
					p.setPen(QtGui.QColor(0, 0, 0))
					p.setFont(QtGui.QFont('Decorative', 1.4*r))
					p.drawText(QtCore.QPoint(x-r/2, y+4*r/5), str(note_number))
	def draw_fretboard(self, p, x0, y0,
		string_tuning=['e', 'B', 'G', 'D', 'A', 'E'],
		num_frets=24,
		num_strings=6,
		draw_fret_numbers=True,
		draw_string_tuning=True,
		draw_scale_name=True,
		scale_name=None,
		triad_info=None):

		center_fret_coordinates = {
			string_number : {fret_number : (None, None)
			for fret_number in range(num_frets)}
		for string_number in range(1, num_strings + 1)}

		# constants
		# the frets will start wide on the left and get shorter the farther
		# right you go, just like on a real guitar fretboard
		fwl = 66 # 50  # fdl = fret width left [measured in pixels]
		fwr = 33 # 26  # fdr = fret width right [measured in pixels]
		fl  = 180 # fl  = fret length (vertically) [measured in pixels]
		ft  = 3   # ft  = fret thickness [measured in pixels] = the line of the fret
		fc  = QtGui.QColor(50, 50, 50) # fc = fret color
		sg  = fl / (num_strings - 1) # sg = string gap [measured in pixels]
		st  = 3   # st = string thickness [measured in pixels]
		sc  = QtGui.QColor(50, 50, 50) # QtCore.Qt.gray # sc = string color

		# draw the frets
		x = x0
		for fret_number, fw in enumerate(np.linspace(fwl, fwr, num_frets)):
			x += fw
			p.setPen(QtGui.QPen(fc, ft))
			p.drawLine(x, y0, x, y0 + fl)

			# calculate center_fret_coordinates values
			_y = y0
			cx = round(x - (fw / 2))
			for string_number in range(1, num_strings + 1):
				center_fret_coordinates[string_number][fret_number] = (
					cx, round(_y))
				_y += sg

			# draw fret numbers
			if draw_fret_numbers:
				p.setPen(QtGui.QColor(50, 50, 50)) # grey
				p.setFont(QtGui.QFont('Decorative', 12))
				p.drawText(QtCore.QPoint(cx-8, y0 + fl + 1.25*sg), str(fret_number))

		# draw key and mode name
		fbw = x + fwr # fbw = fret board width
		p.setPen(QtGui.QColor(50, 50, 50))
		p.setFont(QtGui.QFont('Decorative', 20))
		if draw_scale_name:
			legend_string = 'Key: %s' % scale_name
			p.drawText(QtCore.QPoint(x0, y0 - 3.5*sg), legend_string)
		if triad_info != None:
			legend_string = 'Mode %d: %s' % (triad_info['number'], triad_info['name'])
			p.drawText(QtCore.QPoint(x0, y0 - 2.5*sg), legend_string)


		# draw last fret number
		if draw_fret_numbers:
			cx = round(x + (fw / 2))
			p.setPen(QtGui.QColor(50, 50, 50)) # grey
			p.setFont(QtGui.QFont('Decorative', 12))
			p.drawText(QtCore.QPoint(cx-8, y0 + fl + 1.25*sg), str(num_frets))

		fret_number = num_frets
		_y = y0
		for string_number in range(1, num_strings + 1):
			center_fret_coordinates[string_number][fret_number] = (
				round(x + (fw / 2)), round(_y))
			_y += sg

		# # print out center_fret_coordinates
		# for k, v in center_fret_coordinates.items():
		# 	print(k, v)
		# print()

		# draw the strings
		y = y0
		for i in range(num_strings):
			p.setPen(QtGui.QPen(sc, st))
			p.drawLine(x0, y, x + fwr, y)

			# draw string tuning
			if draw_string_tuning:
				p.setPen(QtGui.QColor(50, 50, 50)) # grey
				p.setFont(QtGui.QFont('Decorative', 12))
				p.drawText(QtCore.QPoint(x0 - 1.3*fwr, y + 6), str(string_tuning[i]))

			y += sg

		return center_fret_coordinates
	

	def init_sound_wave_view(self):

		self.sound_wave_window = self.init_graph()

		self.sound_wave_channels = {}
		x_range = 2500 // properties.get('audio', 'downsample')
		y_range = 0.75
		self.p = self.sound_wave_window.addPlot(
			title='Sound Wave%s' % (
				'' if len(self.audio.channels) == 1 else 's'))
		self.p.setYRange(-y_range, y_range, padding=0)
		for i in self.audio.mapping:
			self.sound_wave_channels[i] = {
				"wave"  : np.zeros(x_range),
				"curve" : self.p.plot()}

		self.timer = QtCore.QTimer()
		self.timer.setInterval(30) # measured in milliseconds
		self.timer.timeout.connect(self.update_sound_wave_window)

		self.timer.start()
	def update_sound_wave_window(self):
		while True:
			try:
				data = self.audio.q.get_nowait()
			except queue.Empty:
				break
			shift = len(data)
			for channel_index, dct in self.sound_wave_channels.items():
				dct["wave"] = np.roll(dct["wave"], -shift, axis=0)
				dct["wave"][-shift:] = data[:, channel_index]
				dct["curve"].setData(dct["wave"])


	def init_frequency_view2(self):

		self.frequency_window = self.init_graph()

		self.frequency_channels = {}
		self.t_range = 4096#2048#1024 # number of samples used to calculate fourier transform, must be power of 2: https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch04.html
		self.p = self.frequency_window.addPlot(
			title="Frequency Spectrum",
			left="Amplitude (aka Volume) [dB]",
			bottom="Frequency (aka Pitch) [Hz]")
		self.p.setYRange(-100, 100, padding=0)
		self.p.setXRange(0, 1000, padding=0)
		# self.p.setYRange(-0.01, 0.1, padding=0)
		for i in self.audio.mapping:
			self.frequency_channels[i] = {
				"wave"  : np.zeros(self.t_range),
				"curve" : self.p.plot()}

		self.min_amplitude_threshold = 20 # measured in dB
		self.frequencies = [self.audio.samplerate * k / (self.t_range * 1) for k in range(self.t_range // 2 + 1)] # self.t_range*2 for rfft, self.t_range for fft
		# frequencies = self.audio.samplerate * np.fft.fftfreq(self.t_range)[:self.t_range // 2 + 1]
		# print(frequencies)#.tolist())
		# print(frequencies.size)
		# sys.exit()
		self.xs=np.arange(self.t_range/2,dtype=float)


		self.timer = QtCore.QTimer()
		self.timer.setInterval(30) # measured in milliseconds
		self.timer.timeout.connect(self.update_frequency_window2)

		self.timer.start()
	def update_frequency_window2(self):
		while True:
			try:
				data = self.audio.q.get_nowait()
			except queue.Empty:
				break
			shift = len(data)
			for channel_index, dct in self.frequency_channels.items():
				if channel_index == 1: continue # just vocals for testing

				dct["wave"] = np.roll(dct["wave"], -shift, axis=0)
				dct["wave"][-shift:] = data[:, channel_index]

				# left, right = np.split(np.abs(np.fft.fft(dct["wave"])), 2)
				# print(dct["wave"].shape, left.shape, right.shape)
				# ys = np.add(left, right[::-1])
				# ys = np.multiply(20, np.log10(ys))
				# dct["curve"].setData(self.xs, ys)

				spectrum = np.fft.rfft(dct["wave"], axis=0)
				amplitudes = 20 * np.log10(np.abs(spectrum))
				# print(amplitudes)
				# sys.exit()
				dct["curve"].setData(self.frequencies, amplitudes)

				# spectrum = np.fft.rfft(dct["wave"], axis=0)
				# frequencies = np.fft.fftfreq(len(spectrum), 1.0 / self.audio.samplerate)
				# amplitudes = 20 * np.log10(np.abs(spectrum))
				# dct["curve"].setData(frequencies, amplitudes)

				# # https://makersportal.com/blog/2018/9/13/audio-processing-in-python-part-i-sampling-and-the-fast-fourier-transform
				# Y_k = np.fft.fft(dct["wave"])[0:int(self.t_range/2)]/self.t_range
				# Y_k[1:] = 2*Y_k[1:]
				# Pxx = np.abs(Y_k)
				# f = self.audio.samplerate*np.arange((self.t_range/2))/self.t_range
				# # f = np.fft.fftfreq(self.t_range, 1/self.audio.samplerate)[0:int(self.t_range/2)]
				# dct["curve"].setData(f, Pxx)

			# print('\n')


	def init_frequency_view(self):

		self.frequency_window = pg.GraphicsWindow(parent=self.window)
		self.frequency_window.setGeometry(10, 50, 730, 440)

		self.frequency_channels = {}
		self.t_range = 1024 # number of samples used to calculate fourier transform, 1024 is fastest: https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch04.html
		self.t_display_range = 10000 # number of samples displayed on the screen (trailing window)
		frequency_range = (100, 2000) # measured in Hz
		df = 1 # measured in Hz
		self.f_samples = (frequency_range[1] - frequency_range[0]) // df # frequency range
		for i in self.audio.mapping:
			self.frequency_channels[i] = {
				"wave" : np.zeros(self.t_range),
				"freq" : np.zeros((self.t_display_range))}

		self.timer = QtCore.QTimer()
		self.timer.setInterval(30) # measured in milliseconds
		self.timer.timeout.connect(self.update_frequency_window)

		self.timer.start()
	def update_frequency_window(self):
		min_amplitude_threshold = 20 # measured in dB
		while True:
			try:
				data = self.audio.q.get_nowait()
			except queue.Empty:
				break
			shift = len(data)
			for channel_index, dct in self.frequency_channels.items():
				dct["wave"] = np.roll(dct["wave"], -shift, axis=0)
				dct["wave"][-shift:] = data[:, channel_index]
				
				spectrum = np.fft.rfft(dct["wave"], axis=0)
				# freqs = np.fft.fftfreq(len(spectrum), 1.0/self.audio.samplerate)

				# # Find the peak in the coefficients
				# idx = np.argmax(np.abs(spectrum)) # index of strongest amplitude
				# strongest_freq = abs(freqs[idx] * self.audio.samplerate) # measured in Hz
				# amplitude = 20 * np.log10(2 * np.abs(spectrum) / spectrum.size) # measured in dB
				# if amplitude > min_amplitude_threshold:
				# 	print('%.6f Hz\t%.6f dB' % (strongest_freq, amplitude))

				dct["plot"].setData(np.abs(spectrum))

				# freqs = scipy.signal.spectrogram(
				# 	dct["wave"],
				# 	fs=self.audio.samplerate,
				# 	)
				# spectrum = np.fft.fft(dct["wave"], axis=0)
				# ampls = np.log10(np.abs(spectrum)) # measured in dB
				# freqs = 
				# freq = np.fft.fft(dct["wave"], axis=0)#[:self.t_range // 2 + 1:-1] # real component is amplitude, imaginary component is frequency
				# freq = np.max(np.abs(np.fft.fft(dct["wave"], axis=0))) # np.abs() takes the sqrt(sum of the squares) of the real and imaginary components of the complex number
				# freq = freq if freq > min_amplitude_threshold else 0
				# print(freq.tolist(), '\n')#np.max(freq))
				# print(np.abs(freq))
				# min_amplitude_threshold = 100 # measured in dB
				# dct["freq"] = dct["freq"] if dct["freq"] > min_amplitude_threshold:


				# dct["plot"].setData(dct["wave"])
			print('\n')


	def init_graph(self):

		screen_width  = QtGui.QDesktopWidget().screenGeometry().width()
		screen_height = QtGui.QDesktopWidget().screenGeometry().height()
		margin = 0.05 # margin = percentage of screen width or height
		# print(self.frameGeometry().width(), self.frameGeometry().height()) # coodinates of self don't work with showMaximized()
		# print(screen_width, screen_height)
	
		# sound wave view
		# https://stackoverflow.com/questions/26994120/multiple-updating-plot-with-pyqtgraph-in-python # GraphicsWindow
		graph = pg.GraphicsWindow(parent=self.window)
		graph.setGeometry(
			screen_width  * 0.25 * margin,
			screen_height * 0.25 * margin,
			screen_width  * (1 - 1.50 * margin),
			screen_height * (1 - 2.25 * margin))
		# self.sound_wave_window.setGeometry(10, 50, 730, 440)

		return graph

	# https://stackoverflow.com/questions/36555153/pyqt5-closing-terminating-application
	def closeEvent(self, event):
		if self.audio.connected:
			self.audio.stream.stop()
			self.audio.stream.close()
		log.print('Done')


