import machine
import time
import micropython

micropython.alloc_emergency_exception_buf(100)

d0 = machine.Pin('X5',machine.Pin.IN) 

def callback(p):
	global d0
	irm_rec_flag = 0
	data = [0,0,0,0]
	downtime = time.ticks_us()
	while(not d0.value()):
		if (time.ticks_us()-downtime)>10000:
			return
		else:
			pass
	uptime = time.ticks_us()
	while(d0.value()):
		if (time.ticks_us()-uptime)>5000:
			return
		else:
			pass
	downtime = time.ticks_us()
	for i in range(0,4):
		for j in range(0,8):	
			while( not d0.value()):
				if (time.ticks_us()-downtime)>800:
					return
				else:
					pass
			uptime = time.ticks_us()
			while(d0.value()):
				if(time.ticks_us()-uptime)>2000:
					return
				else:
					pass
			downtime = time.ticks_us()
			data[i] = data[i]>>1
			if (downtime-uptime) > 800:
				data[i] = data[i] | 0x80
	if ((data[2]+data[3]) == 255):
		print(data)
	else:
		print('error')
	
d0.irq(trigger=machine.Pin.IRQ_FALLING , handler=callback)

