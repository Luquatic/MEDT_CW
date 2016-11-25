import RPi.GPIO as GPIO
from multiprocessing import Queue
from auto import Auto
from autoself import AutoSelf
import threading
import time
import math

class Pilib:
	auto = 0
	_auto = True
	quit = False
	loop = True
	shouldClean = False
	xPos = 0
	que = []
	speed = 1
	light = 0
	seq = [ [1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1],
			[1,0,0,1] ]
	pins = [11,12,13,15]

	def __init__(self):
		print('# init pilib')
		GPIO.setwarnings(False)
		file = open("quit.txt", "wt")
		file.seek(0)
		file.truncate()
		file.write(str(0))
		file.close()
		file = open("xPos.txt")
		try:
			self.xPos = int(file.readlines()[0])
		except IndexError:
			self.xPos = 0
			print("xPos.txt no line")
		file.close()
		GPIO.setmode(GPIO.BOARD)
		#Motor
		for pin in self.pins:
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,0)
		#Led
		GPIO.setup(7, GPIO.OUT)
		GPIO.output(7, 0)
		#Swtich
		GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		t = threading.Thread(target=self.threaded)
		t.daemon = True
		t.start()
		lib = self
	
	def ani(self):
		Auto(self)
	
	def aniself(self):
		AutoSelf(self)
	
	def clean(self):
		self.que.append("clean")
	
	def wait(self):
		while self.que:
			time.sleep(0.01)
	
	def stop(self):
		time.sleep(0.01)
		while self.auto == 1:
			time.sleep(0.01)
		self.wait()
		self.loop = False
		self._clean()
		time.sleep(0.02)
		GPIO.cleanup()

	def home(self):
		self.que.append("home")
		
	def printPos(self):
		self.que.append("printPos")
	
	def printStr(self, str):
		self.que.append("print " + str)

	def printEval(self, str):
		self.que.append("eval " + str)
	
	def quit(self, arg):
		file = open("quit.txt", "wt")
		file.seek(0)
		file.truncate()
		file.write(str(arg))
		file.close()
	
	def waitOnLight(self):
		self.que.append("waitlight")
	
	def sendLight(self, doSend):
		if doSend:
			self.que.append("light")
		else:
			self.que.append("dark")

	def sleep(self, time):
		self.que.append("sleep " + str(time))

	def up(self, amount):
		self.que.append("up " + str(amount))

	def down(self, amount):
		self.que.append("down " + str(amount))
	
	def setPos(self, pos):
		self.que.append("setpos " + str(pos))

	def getRackX(self):
		file = open("/boot/x.txt")
		ret = int(file.readlines()[0])
		file.close()
		return ret

	def getRackY(self):
		file = open("/boot/y.txt")
		ret = int(file.readlines()[0])
		file.close()
		return ret
		
	def getPos(self):
		return self.xPos

	def setSpeed(self, speed):
		self.que.append("speed " + str(speed))

	def getSpeed(self):
		return self.speed
	
	def getLight(self):
		return self.light
	
	def _isAuto(self):
		self._updateFiles()
		return self.auto == 1
	
	def _clean(self):
		self.shouldClean = True
		for pin in self.pins:
			GPIO.output(pin,0)

	def _detectLight(self):
		return GPIO.input(18) == 1
	
	def _home(self):
		self._rotateN(50000)

	def _lock(self):
		self._auto = False

	def _rotate(self, times):
		for i in range(times):
			for half in range(8):
				for pin in range(4):
					GPIO.output(self.pins[pin], self.seq[half][pin])
					self.xPos += 0.03125
					if self.quit == 1:
						break;
				time.sleep(0.003 / self.speed)
				if self.quit == 1:
					break;
			if self.quit == 1:
				break;
	
	def _rotateN(self, times):
		end = False
		for i in range(times):
			for half in reversed(range(8)):
				for pin in reversed(range(4)):
					if GPIO.input(16) == 1:
						GPIO.output(self.pins[pin], self.seq[half][pin])
						self.xPos -= 0.03125
					else:
						end = True
				if end or self.quit == 1:
					break
				time.sleep(0.0025 / self.speed)
			if end or self.quit == 1:
				break
		if end:
			self._rotate(6)
			self.xPos = 0

	def _stop(self):
		file = open("quit.txt")
		ret = int(file.readlines()[0])
		file.close()
		return ret
	
	def _updateFiles(self):
		self.xPos = int(math.floor(self.xPos))
		file = open("xPos.txt", "wt")
		file.seek(0)
		file.truncate()
		file.write(str(self.xPos))
		file.close()
		file = open("quit.txt")
		try:
			self.quit = int(file.readlines()[0])
		except IndexError:
			self.xPos = 0
			print("quit.txt no line")
		file.close()
		file = open("xSpeed.txt", "wt")
		file.seek(0)
		file.truncate()
		file.write(str(self.speed))
		file.close()
		file = open("auto.txt")
		try:
			self.auto = int(file.readlines()[0])
		except IndexError:
			self.auto = 0
			print("auto.txt no line")
		file.close()
	
	def threaded(self):
		while self.loop:
			self._updateFiles()
			if self.auto == 1 and self._auto == True:
				i = 0
				while self._detectLight() == 1 and i < 10 and self.getRackX() != 0:
					time.sleep(0.01)
					i += 1
				if(i != 10):
					self.ani()
			if not self.que:
				time.sleep(0.01)
				self._auto = True
				continue
			current = self.que[0]
			print("AS: " + current)
			if current == "home":
				self._home()
			elif current.startswith("clean"):
				time.sleep(0.01)
				self._clean()
			elif current.startswith("up "):
				self._rotateN(int(current.split(" ")[1]))
			elif current.startswith("down "):
				self._rotate(int(current.split(" ")[1])) 
			elif current.startswith("printPos"):
				print(str(self.xPos))
			elif current.startswith("eval "):
				print(eval(current.replace("eval ", "")))
			elif current.startswith("print "):
				print(current.replace("print ", ""))
			elif current.startswith("speed "):
				self.speed = float(current.split(" ")[1])
			elif current.startswith("light"):
				GPIO.output(7, True)
				self.light = 1
			elif current.startswith("dark"):
				GPIO.output(7, False)
				self.light = 0
			elif current.startswith("waitlight"):
				while self._detectLight() == 1:
					time.sleep(0.01)
			elif current.startswith("sleep "):
				time.sleep(float(current.split(" ")[1]))
			elif current.startswith("setpos "):
				pos = int(current.split(" ")[1])
				if self.xPos < pos:
					self._rotate(int(pos - self.xPos))
				elif self.xPos > pos:
					self._rotateN(int(self.xPos - pos))
			del self.que[0]
			if self.shouldClean:
				self._clean()
				self.shouldClean = False
