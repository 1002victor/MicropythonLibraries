import pyb
import time
import font
import chinese_char

RED			=0xf800
GREEN		=0x07e0
BLUE		=0x001f
PURPLE		=0xf81f
YELLOW		=0xffe0 
CYAN		=0x07ff
ORANGE		=0xfc08
BLACK		=0x0000
WHITE		=0xffff

XMAX		=128	#132	
YMAX		=160	#64

class ILI9163():
	def __init__(self,pinout,spibus):
		self.spi = pyb.SPI(spibus, pyb.SPI.MASTER, baudrate=5000000, polarity=0, phase=0)
		self.dc  = pyb.Pin(pinout['dc'],  pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
		self.res = pyb.Pin(pinout['res'], pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
		self.poweron()
		self.dis_font = font.FONT()
		self.dis_chinese = chinese_char.CHINESE_FONT()
	def _write_byte(self,b):
		self.spi.send(b)
	
	def	_write_command(self,cmd):
		self.dc.low()
		self._write_byte(cmd)
	
	def _write_data(self,dat):
		self.dc.high()
		self._write_byte(dat)
		
	def _write_16(self,dat):
		buf = 0xff&(dat>>8)
		self._write_data(buf)
		buf = 0xff&dat
		self._write_data(buf)
		
	def poweron(self):
		self.res.low()
		pyb.delay(200)
		self.res.high()
		pyb.delay(50)
		self._write_command(0x11)
		pyb.delay(100)
		self._write_command(0x3a)
		self._write_data(0x55)
		self._write_command(0x26)
		self._write_data(0x04)
		self._write_command(0xf2)
		self._write_data(0x01)
		self._write_command(0xE0)
		self._write_data(0x3F)
		self._write_data(0x25)
		self._write_data(0x1c)
		self._write_data(0x1e)
		self._write_data(0x20)
		self._write_data(0x12)
		self._write_data(0x2a)
		self._write_data(0x90)
		self._write_data(0x24)
		self._write_data(0x11)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_command(0xE1)
		self._write_data(0x20)
		self._write_data(0x20)
		self._write_data(0x20)
		self._write_data(0x20)
		self._write_data(0x05)
		self._write_data(0x00)
		self._write_data(0x15)
		self._write_data(0xa7)
		self._write_data(0x3d)
		self._write_data(0x18)
		self._write_data(0x25)
		self._write_data(0x2a)
		self._write_data(0x2b)
		self._write_data(0x2b)
		self._write_data(0x3a)
		self._write_command(0xB1)
		self._write_data(0x08)
		self._write_data(0x08)
		self._write_command(0xB4)
		self._write_data(0x07)
		self._write_command(0xC0)
		self._write_data(0x0A)
		self._write_data(0x02)
		self._write_command(0xC1)
		self._write_data(0x02)
		self._write_command(0xC5)
		self._write_data(0x4F)
		self._write_data(0x5A)
		self._write_command(0xC7)
		self._write_data(0x40)
		self._write_command(0x2A)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x7F)
		self._write_command(0x2B)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x9f)
		self._write_command(0x36)
		self._write_data(0xC0)
		self._write_command(0xB7)
		self._write_data(0x00)
		self._write_command(0x29)
		self._write_command(0x2C)
		pyb.delay(10)
		self.full_fill(BLACK)
		
	def set_pos(self,xs,ys,xe,ye):
		self._write_command(0x2A)
		self._write_data(0x00)
		self._write_data(xs)
		self._write_data(0x00)
		self._write_data(xe)
		
		self._write_command(0x2B)
		self._write_data(0x00)
		self._write_data(ys)
		self._write_data(0x00)
		self._write_data(ye)
		
		self._write_command(0x2C)
		
	def full_fill(self,color):
		self.set_pos(0,0,XMAX,YMAX)
		for i in range(0,XMAX):
			for j in range(0,YMAX):
				self._write_16(color)
			
		
	def _address_rst(self):
		self._write_command(0x2A)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x7f)
		
		self._write_command(0x2B)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x00)
		self._write_data(0x9f)
		self._write_command(0x2C)

	def clear(self):
		self.full_fill(BLACK)
		
	def draw_dot(self,x,y,color):
		self.set_pos(x,y,x,y)
		self._write_16(color)
		
	def draw_line(self,xs,ys,xe,ye,color):
		xerr = 0
		yerr = 0
		if xs == xe:
			self.set_pos(xs,ys,xe,ye)
			for i in range(0,ye-ys+1):
				self._write_16(color)
		elif ys == ye:
			self.set_pos(xs,ys,xe,ye)
			for i in range(0,xe-xs+1):
				self._write_16(color)
		else:
			dx = xe-xs
			dy = ye-ys
			if dx > 0:
				inc_x = 1
			else:
				inc_x = -1
				dx = -dx
			if dy > 0:
				inc_y = 1
			else:
				inc_y = -1
				dy = -dy
			if dx>dy:
				ds = dx
			else:
				ds = dy
			for i in range(0,ds+1+1):
				self.draw_dot(xs,ys,color)
				xerr += dx
				yerr += dy
				if xerr > ds:
					xerr -= ds
					xs += inc_x
				if yerr > ds:
					yerr -= ds
					ys += inc_y
				
		
	def draw_part(self,xs,ys,xe,ye,color):
		self.set_pos(xs,ys,xe,ye)
		for i in range(0,ye-ys+1):
			for i in range(0,xe-xs+1):
				self._write_16(color)
				
	def draw_rectangle(self,xs,ys,xe,ye,color):
		self.draw_line(xs,ys,xs,ye,color)
		self.draw_line(xe,ys,xe,ye,color)
		self.draw_line(xs,ys,xe,ys,color)
		self.draw_line(xs,ye,xe,ye,color)

	def draw_circle(self,x,y,r,color):
		dx = r
		dy = r
		if ((x>=r) and((XMAX-x)>=r) and (y>=r) and ((YMAX-y)>=r)):
			for dx in range(0,r+1):
				while((r * r + 1 - dx * dx) < (dy * dy)):
					dy = dy - 1
				self.draw_dot(x + dx, y - dy, color)
				self.draw_dot(x - dx, y - dy, color)
				self.draw_dot(x - dx, y + dy, color)
				self.draw_dot(x + dx, y + dy, color)

				self.draw_dot(x + dy, y - dx, color)
				self.draw_dot(x - dy, y - dx, color)
				self.draw_dot(x - dy, y + dx, color)
				self.draw_dot(x + dy, y + dx, color)
							
	
	def P6x8char(self,x,y,char_dis,word_color,back_color):
		self.set_pos(x*6,y*8,(x+1)*6-1,(y+1)*8-1)
		F6x8 = self.dis_font.get_font6_8(char_dis)
		for i in range(0,8):
			for item in F6x8:
				if (item & (0x01<<i)):
					self._write_16(word_color)
				else:
					self._write_16(back_color)
			
	def P6x8str(self,x,y,str_dis,word_color,back_color):
		for item in str_dis:
			self.P6x8char(x,y,item,word_color,back_color)
			x = x+1
			if x>20:
				x=0
				y = y+1
			
	def P8x16char(self,x,y,char_dis,word_color,back_color):
		F = self.dis_font.get_font8_16(char_dis)
		self.set_pos(x*8,y*16,(x+1)*8-1,(y+1)*16-1)
		for item in F:
			for i in range(0,8):
				if (item & (0x01<<i)):
					self._write_16(word_color)
				else:
					self._write_16(back_color)

	def P8x16str(self,x,y,str_dis,word_color,back_color):
		for item in str_dis:
			self.P8x16char(x,y,item,word_color,back_color)
			x = x+1
			if x>15:
				x=0
				y = y+1		
				
	def P16x16char(self,x,y,char_dis,word_color,back_color):
		F16x16 = self.dis_chinese.F16x16[char_dis]
		self.set_pos(x*8,y*16,(x+1)*8-1,(y+1)*16-1)
		for item in F16x16[0:16]:
			for i in range(0,8):
				if (item & (0x01<<i)):
					self._write_16(word_color)
				else:
					self._write_16(back_color)
		self.set_pos((x+1)*8,y*16,(x+2)*8-1,(y+1)*16-1)
		for item in F16x16[16:]:
			for i in range(0,8):
				if (item & (0x01<<i)):
					self._write_16(word_color)
				else:
					self._write_16(back_color)
	def P16x16str(self,x,y,str_dis,word_color,back_color):
		for item in str_dis:
			self.P16x16char(x,y,item,word_color,back_color)
			x = x+2
			if x>14:
				x=0
				y = y+1	

def main():				
	s = ILI9163({'dc':pyb.Pin.board.X4,'res':pyb.Pin.board.X3},1)
	rtc = pyb.RTC()
	s.draw_line(0,6,32,6,YELLOW)
	s.draw_line(0,9,32,9,YELLOW)
	s.draw_line(97,6,128,6,YELLOW)
	s.draw_line(97,9,128,9,YELLOW)
	s.P16x16str(4,0,'系统信息',YELLOW,BLACK)
	s.P16x16str(0,1,'电流',GREEN,BLACK)
	s.draw_rectangle(33,16,127,81,GREEN)
	s.P16x16str(0,5,'温度',RED,BLACK)
	s.draw_rectangle(33,82,127,143,RED)
	s.P16x16str(0,9,'时间',BLUE,BLACK)
	dot = True
	while True:
		t1 = time.ticks_us()
		timetup = rtc.datetime()
		dot = not dot
		if dot:
			sd = ":{:0>2}-{:0>2} {:0>2}:{:0>2}".format(timetup[1],timetup[2],timetup[4],timetup[5])
		else:
			sd = ":{:0>2}-{:0>2} {:0>2} {:0>2}".format(timetup[1],timetup[2],timetup[4],timetup[5])
		s.P8x16str(4,9,sd,BLUE,BLACK)
		pyb.delay(500)

if __name__ == '__main__':
		main()
	
	