class Auto:
	def __init__(self, lib):
		lib._lock()
		prerand = [1.6, 0.9, 1.4, 1.0, 1.5, 0.9, 1.3, 0.8, 1.6, 0.9]

		lib.setSpeed(2.65)
		lib.setPos(100)
		lib.sendLight(True)
		lib.setPos(500)
		lib.sendLight(False)

		i = 0
		j = 0

		while j < 20:
			i += 1
			j += 1
			i %= len(prerand)
			lib.setSpeed(prerand[i] * 1.7285)
			lib.up(int(prerand[i] * 150))
			lib.down(int(prerand[i] * 150))
		lib.home()
		lib.clean()