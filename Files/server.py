import os
import json

from flask import Flask, render_template, request, json, jsonify
from pilib import Pilib

lib = Pilib()

app = Flask(__name__)

@app.route('/')
@app.route('/index.htm')
def index():
	return render_template('index.htm')

@app.route('/home.htm')
def home():
	if not lib._isAuto():
		lib.setSpeed(2.65)
		lib.home()
		lib.clean()
	return render_template('index.htm')

@app.route('/auto_on.htm')
def auto_on():
	file = open("auto.txt", "wt")
	file.seek(0)
	file.truncate()
	file.write(str(1))
	file.close()
	return render_template('index.htm')

@app.route('/auto_off.htm')
def auto_off():
	if lib._isAuto():
		lib.que = ["", "home", "clear"]
	lib.auto = 0
	file = open("auto.txt", "wt")
	file.seek(0)
	file.truncate()
	file.write(str(0))
	file.close()
	return render_template('index.htm')

@app.route('/quit.htm')
def quit():
	lib.quit = 1
	file = open("quit.txt", "wt")
	file.seek(0)
	file.truncate()
	file.write(str(1))
	file.close()
	
	lib.wait()
	
	file = open("quit.txt", "wt")
	file.seek(0)
	file.truncate()
	file.write(str(0))
	file.close()
	lib.que = [""]
	return render_template('index.htm')

@app.route('/xpos.htm')
def xpos():
	return str(lib.getRackX())

@app.route('/ypos.htm')
def ypos():
	return str(lib.getRackY())
	
@app.route('/shutdown.htm')
def shutdown():
	os.system("sudo shutdown -h now")
	return '{"shutdown":"true"}';

@app.route('/reboot.htm')
def reboot():
	os.system("sudo reboot")

@app.route('/reload.htm')
def reload():
	global lib
	lib.stop()
	lib = Pilib()
	return render_template('index.htm')

@app.route('/up.htm')
def up():
	if not lib._isAuto():
		lib.setSpeed(2.65)
		stapUp = request.args.get('steps')
		if stapUp is None or not stapUp:
			lib.up(1)
		else:
			lib.up(int(stapUp))
		lib.clean()
	return render_template('index.htm')
	
@app.route('/down.htm')
def down():
	if not lib._isAuto():
		lib.setSpeed(2.65)
		stapDown = request.args.get('steps')
		if stapDown is None or not stapDown:
			lib.down(1)
		else:
			lib.down(int(stapDown))
		lib.clean()
	return render_template('index.htm')
	
@app.route('/startself.htm')
def startAnimatieSelf():
	if not lib._isAuto():
		lib.aniself()
	return render_template('index.htm')

@app.route('/start.htm')
def startAnimatie():
	if not lib._isAuto():
		lib.ani()
	return render_template('index.htm')

@app.route('/code.htm')
def codepage():
	code = request.args.get('code')
	if code is None:
		return("{'error':'Geen argument'}")
	else:
		ret = os.popen(code).read().replace('\n','<br />')
		return('{"code":"' + code + '", "ret":"' + ret + '"}')

if __name__ == '__main__':
 	app.run(host='0.0.0.0', port = 5000, debug=True, use_reloader=False)