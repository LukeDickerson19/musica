from backend import *



class MainWindow(QtWidgets.QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Musica") # set window title
		# self.setStyleSheet(
		#	 open(os.path.join(STYLESHEETS_PATH,
		#		 "main_window.stylesheet"), 'r').read())
		self.setGeometry(100, 150, 750, 500) # set window's location and size: (x, y, width, height)

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
			self.connection_status.move(10, 10)
			self.connection_status.setText("audio interface not connected")
			return

		# self.init_sound_wave_view()
		self.init_frequency_view()

	def init_sound_wave_view(self):

		# sound wave view
		# https://stackoverflow.com/questions/26994120/multiple-updating-plot-with-pyqtgraph-in-python # GraphicsWindow
		self.sound_wave_window = pg.GraphicsWindow(
			# title='Sound Wave%s' % (
			# 	'' if len(self.audio.channels) == 1 else 's'),
			parent=self.window)
		self.sound_wave_window.setGeometry(10, 50, 730, 440)

		self.sound_waves = {}
		x_range = 250
		y_range = 0.75
		for i in self.audio.mapping:
			p = self.sound_wave_window.addPlot()
			p.setYRange(-y_range, y_range, padding=0)
			self.sound_waves[i] = {
				"wave" : np.zeros(x_range),
				"plot" : p.plot()}

		self.timer = QtCore.QTimer()
		self.timer.setInterval(30)
		self.timer.timeout.connect(self.update_sound_wave_window)

		self.timer.start()
	def update_sound_wave_window(self):
		while True:
			try:
				data = self.audio.q.get_nowait()
			except queue.Empty:
				break
			shift = len(data)
			for i, dct in self.sound_waves.items():
				dct["wave"] = np.roll(dct["wave"], -shift, axis=0)
				dct["wave"][-shift:] = data[:, i]
				dct["plot"].setData(dct["wave"])

	def init_frequency_view(self):

		print('hi')


	# https://stackoverflow.com/questions/36555153/pyqt5-closing-terminating-application
	def closeEvent(self, event):
		self.audio.stream.stop()
		self.audio.stream.close()
		log.print('Done')


