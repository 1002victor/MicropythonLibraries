import pyb
from DisplayMoudle import font
'''
There is lots of DisplayMoudle drive:
Now this library is supposed blow device:
OLED-(128_64)0.96' SSD1360
OLED-(128_64)1.3'  SSD1307
'''



OLED_MODE 		=0
SIZE 			=16
XLevelL			=0x00
XLevelH			=0x10
Max_Column		=128
Max_Row			=64
Brightness		=0xFF
X_WIDTH 		=128
Y_WIDTH 		=64


# Constants
DISPLAYOFF          = 0xAE
SETCONTRAST         = 0x81
DISPLAYALLON_RESUME = 0xA4
DISPLAYALLON        = 0xA5
NORMALDISPLAY       = 0xA6
INVERTDISPLAY       = 0xA7
DISPLAYON           = 0xAF
SETDISPLAYOFFSET    = 0xD3
SETCOMPINS          = 0xDA
SETVCOMDETECT       = 0xDB
SETDISPLAYCLOCKDIV  = 0xD5
SETPRECHARGE        = 0xD9
SETMULTIPLEX        = 0xA8
SETLOWCOLUMN        = 0x00
SETHIGHCOLUMN       = 0x10
SETSTARTLINE        = 0x40
MEMORYMODE          = 0x20
COLUMNADDR          = 0x21
PAGEADDR            = 0x22
COMSCANINC          = 0xC0
COMSCANDEC          = 0xC8
SEGREMAP            = 0xA0
CHARGEPUMP          = 0x8D
EXTERNALVCC         = 0x10
SWITCHCAPVCC        = 0x20
SETPAGEADDR         = 0xB0
SETCOLADDR_LOW      = 0x00
SETCOLADDR_HIGH     = 0x10
ACTIVATE_SCROLL                      = 0x2F
DEACTIVATE_SCROLL                    = 0x2E
SET_VERTICAL_SCROLL_AREA             = 0xA3
RIGHT_HORIZONTAL_SCROLL              = 0x26
LEFT_HORIZONTAL_SCROLL               = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL  = 0x2A

# I2C devices are accessed through a Device ID. This is a 7-bit
# value but is sometimes expressed left-shifted by 1 as an 8-bit value.
# A pin on SSD1306 allows it to respond to ID 0x3C or 0x3D. The board
# I bought from ebay used a 0-ohm resistor to select between "0x78"
# (0x3c << 1) or "0x7a" (0x3d << 1). The default was set to "0x78"
DEVID = 0x3c

# I2C communication here is either <DEVID> <CTL_CMD> <command byte>
# or <DEVID> <CTL_DAT> <display buffer bytes> <> <> <> <>...
# These two values encode the Co (Continuation) bit as b7 and the
# D/C# (Data/Command Selection) bit as b6.
CTL_CMD = 0x80
CTL_DAT = 0x40



class OLED128_64(object):
	def __init__(self, pinout, height=32, external_vcc=True, i2c_devid=DEVID, spibus=2):
		self.external_vcc = external_vcc
		self.height       = 64
		self.pages        = 8
		self.columns      = 128
		rate =  8000000
		chargepump = 0x10 if self.external_vcc else 0x14
		precharge  = 0x22 if self.external_vcc else 0xf1
		multiplex  = 0x3f
		compins    = 0x12
		contrast   = 0xff # 0x8f if self.height == 32 else (0x9f if self.external_vcc else 0x9f)
		self.init_cmds = [DISPLAYOFF,
            SETDISPLAYCLOCKDIV, 0x80,
            SETMULTIPLEX, multiplex,
            SETDISPLAYOFFSET, 0x00,
            SETSTARTLINE | 0x00,
            CHARGEPUMP, chargepump,
            MEMORYMODE, 0x00,
            SEGREMAP | 0x10,
            COMSCANDEC,
            SETCOMPINS, compins,
            SETCONTRAST, contrast,
            SETPRECHARGE, precharge,
            SETVCOMDETECT, 0x40,
            DISPLAYALLON_RESUME,
            NORMALDISPLAY,
            DISPLAYON]
		self.display_cmds = [COLUMNADDR, 0, self.columns - 1, PAGEADDR, 0, self.pages-1]
		self.spi = pyb.SPI(spibus, pyb.SPI.MASTER, baudrate=rate, polarity=0, phase=0)  # SCK: Y6: MOSI: Y8
		self.dc  = pyb.Pin(pinout['dc'],  pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
		self.res = pyb.Pin(pinout['res'], pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
		self.offset = 0
		self.buffer = bytearray(self.offset + self.pages * self.columns)
		self.dis_font = font.FONT()
		#poweron
		self.res.high()
		pyb.delay(100)
		self.res.low()
		pyb.delay(200)
		self.res.high()
		pyb.delay(100)
		'''
		for cmd in self.init_cmds:
			self.write_command(cmd)
		'''
		self.write_command(0xAE)#--turn off oled panel
		self.write_command(0x00)#---set low column address
		self.write_command(0x10)#---set high column address
		self.write_command(0x40)#--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
		self.write_command(0x81)#--set contrast control register
		self.write_command(0xCF)# Set SEG Output Current Brightness
		self.write_command(0xA1)#--Set SEG/Column Mapping     0xa0×óÓÒ·´ÖÃ 0xa1Õý³£
		self.write_command(0xC8)#Set COM/Row Scan Direction   0xc0ÉÏÏÂ·´ÖÃ 0xc8Õý³£
		self.write_command(0xA6)#--set normal display
		self.write_command(0xA8)#--set multiplex ratio(1 to 64)
		self.write_command(0x3f)#--1/64 duty
		self.write_command(0xD3)#-set display offset	Shift Mapping RAM Counter (0x00~0x3F)
		self.write_command(0x00)#-not offset
		self.write_command(0xd5)#--set display clock divide ratio/oscillator frequency
		self.write_command(0x80)#--set divide ratio, Set Clock as 100 Frames/Sec
		self.write_command(0xD9)#--set pre-charge period
		self.write_command(0xF1)#Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
		self.write_command(0xDA)#--set com pins hardware configuration
		self.write_command(0x12)
		self.write_command(0xDB)#--set vcomh
		self.write_command(0x40)#Set VCOM Deselect Level
		self.write_command(0x20)#-Set Page Addressing Mode (0x00/0x01/0x02)
		self.write_command(0x02)#
		self.write_command(0x8D)#--set Charge Pump enable/disable
		self.write_command(0x14)#--set(0x10) disable
		self.write_command(0xA4)# Disable Entire Display On (0xa4/0xa5)
		self.write_command(0xA6)# Disable Inverse Display On (0xa6/a7) 
		self.write_command(0xAF)#--turn on oled panel
		self.write_command(0xAF)# /*display ON*/ 
		
		
		## clear display
		buffer = bytearray(1024)
		self.display(buffer)
	
		self.clear()
		self.set_position(0,0)
		
	def _oled_write_byte(self,cmd):
		self.spi.send(cmd)
	
	def write_command(self, command_byte):
		self.dc.low()
		self._oled_write_byte(command_byte)
	  
	def write_data(self, data_byte):
		self.dc.high()
		self._oled_write_byte(data_byte)	
	
	def display_on(self):
		self.write_command(0x8D)
		self.write_command(0x14)
		self.write_command(0xAF)
	
	def display_off(self):
		self.write_command(0x8D)
		self.write_command(0x10)
		self.write_command(0xAE)
	
	def clear(self):
		for i in range(0,8):
			self.write_command(0xB0 + i)
			self.write_command(0x00)
			self.write_command(0x10)
			for i in range(0,128):
				self.write_data(0)
			
	def fill(self):
		for i in range(0,8):
			self.write_command(0xB0 + i)
			self.write_command(0x00)
			self.write_command(0x10)
			for i in range(0,128):
				self.write_data(255)
	
	def set_position(self,x,y):
		self.write_command(0xB0+y)
		self.write_command(((x&0xf0)>>4)|0x10)
		self.write_command((x&0x0f)|0x01)
		
	def pixel(self, x, y):
		self.set_position(x,y>>3)
		data = 0x01<<(y%8)
		self.write_command(0xb0+(y>>3))
		self.write_command(((x&0xf0)>>4)|0x10)
		self.write_command((x&0x0f)|0x00)
		self.write_data(data)
		
	def RectangleDrawling(self, s_x, s_y,e_x,e_y,mode=False,gif=False):
		for y in range(s_y,e_y):
			for x in range(s_x,e_x):
				if y==s_y or y==e_y:
					self.pixel(x,y)
				else:
					if mode:
						self.pixel(x,y)
					else:
						if x==s_x or x==e_x:
							self.pixel(x,y)
		'''			
		self.set_position(s_x,s_y>>3)
		for n in range(s_x,e_x):
			self.write_data(0x01<<(s_y%8))
			if gif:
				pyb.delay(30)
		self.set_position(s_x,e_y>>3)
		for n in range(s_x,e_x):
			self.write_data(0x01<<(e_y%8))
			if gif:
				pyb.delay(30)		
		'''
	def DRAW_BATTERY(self,x,y):
		bat=[0x3C,0x3C,0xFF,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0x81,0xFF]
		self.set_position(x,y)
		for i in range(0,24):
			self.write_data(bat[i])
			
	def P6x8Str(self,x,y,str_dis):
		for item in str_dis:
			F6x8=self.dis_font.get_font6_8(item)
			if x>126:
				x=0
				y=y+1
			self.set_position(x,y)
			for i in F6x8:
				self.write_data(i)
			x=x+6
				
			
	def P8x16Str(self,x,y,str_dis):
		for item in str_dis:
			F6x8=self.dis_font.get_font8_16(item)
			if x>120:
				x=0
				y=y+2
			self.set_position(x,y)
			for i in F6x8[0:8]:
				self.write_data(i)
			self.set_position(x,y+1)
			for i in F6x8[8:16]:
				self.write_data(i)
			x=x+8
			
			
			
			
			
	def display(self,data):
		for cmd in self.display_cmds:
			self.write_command(cmd)
		self.write_data(data)