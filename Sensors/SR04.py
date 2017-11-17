import pyb
import time

class SR04():
	def __init__(self,pins,timeout = (100,200)):
		self.timeout = timeout
		self.trig = pyb.Pin(pins['trig'],pyb.Pin.OUT_PP,pyb.Pin.PULL_DOWN)
		self.echo = pyb.Pin(pins['echo'],pyb.Pin.IN,pyb.Pin.PULL_DOWN)
		self.trig.low()
	def getdis(self,c=25):
		self.trig.low()
		time.sleep_us(100)
		self.trig.high()
		time.sleep_us(20)
		self.trig.low() 
		tp = time.ticks_us()
		while not self.echo.value():
			if (time.ticks_us() - tp) > self.timeout[0]*1000:
				pass
			else:
				pass
		startime = time.ticks_us()
		while self.echo.value():
			if (time.ticks_us() - startime) > self.timeout[1]*1000:
				pass
			else:
				pass
		endtime = time.ticks_us()
		
		fot = time.ticks_diff(endtime,startime)
		dis_value = ((331.45 + 0.61 * c)/2000)*fot
		return dis_value
		
s = SR04({'trig':pyb.Pin.board.X2,'echo':pyb.Pin.board.X1})

def main():
	while True:
		print ("Distance: %.2f mm" % s.getdis(c=15))
		pyb.delay(1000)

if __name__ == '__main__':
	main()
