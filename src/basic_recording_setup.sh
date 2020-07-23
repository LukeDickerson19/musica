

# check if the scarlett is plugged in
python3.8 - << EOF
import sys
import subprocess
ret = subprocess.check_output(['lsusb'])
for s in ret.decode("utf-8").split('\n'):
	if 'Focusrite-Novation' in s:
		sys.exit(0)
sys.exit(1)
EOF
if [ $? -ne 0 ]; then
	notify-send 'ERROR' 'Plug in Scarlett Focusrite Interface before starting JACK'

else

	# start jack
	# sources:
	#		http://write.flossmanuals.net/ardour/starting-jack-on-ubuntu/
	# 		https://qjackctl.sourceforge.io/
	# '&' starts a different subprocess, this is required so this script can continue as jack runs
	#		source: https://stackoverflow.com/questions/13338870/what-does-at-the-end-of-a-linux-command-mean
	qjackctl &

	guitarix & # open guitarix for guitar
	guitarix & # open guitarix for vocals

	# pause so jack has time to setup connections
	sleep 3

	# update the connections of jack
	# source: https://linuxmusicians.com/viewtopic.php?f=27&t=19208
	jack_disconnect -s default system:capture_2 gx_head_amp-01:in_0 &

	# pause 1 second ten open ardour DAW 
	sleep 1
	ardour6 &

fi

# exit this script so the terminal can continue to be used
exit

