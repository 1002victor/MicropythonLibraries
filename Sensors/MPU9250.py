import pyb

GYRO_ADDRESS   = 0x68	  #Gyro and Accel device address
MAG_ADDRESS    = 0x0C   #compass device address
ACCEL_ADDRESS  = 0x68 

# define MPU9250 register address
SMPLRT_DIV		= 0x19	#Sample Rate Divider. Typical values:0x07(125Hz) 1KHz internal sample rate
CONFIG			= 0x1A	#Low Pass Filter.Typical values:0x06(5Hz)
GYRO_CONFIG		= 0x1B	#Gyro Full Scale Select. Typical values:0x10(1000dps)
ACCEL_CONFIG	= 0x1C	#Accel Full Scale Select. Typical values:0x01(2g)
ACCEL_CONFIG_2	= 0x1C	#Accel Full Scale Select. Typical values:0x01(2g)

ACCEL_XOUT_H	= 0x3B
ACCEL_YOUT_H	= 0x3D
ACCEL_ZOUT_H	= 0x3F

TEMP_OUT_H		= 0x41

GYRO_XOUT_H		= 0x43	
GYRO_YOUT_H		= 0x45
GYRO_ZOUT_H		= 0x47


		
MAG_XOUT_L		= 0x03
MAG_XOUT_H		= 0x04
MAG_YOUT_L		= 0x05
MAG_YOUT_H		= 0x06
MAG_ZOUT_L		= 0x07
MAG_ZOUT_H		= 0x08

INI_PIN_CFG		= 0x37
PWR_MGMT_1		= 0x6B	#Power Management. Typical values:0x00(run mode)
WHO_AM_I		= 0x75	#identity of the device

ADDRESS_AD0_LOW     = 0xD0 #address pin low (GND), default for InvenSense evaluation board
ADDRESS_AD0_HIGH    = 0xD1 #address pin high (VCC)
DEFAULT_ADDRESS     = GYRO_ADDRESS
WHO_AM_I_VAL		= 0x73 #identity of MPU9250 is 0x71. identity of MPU9255 is 0x73.




class MPU9255(object):
	def __init__(self,iicbus,address=DEFAULT_ADDRESS):
		self._address = address
		self._bus = iicbus
		self.poweron_init()
			
	def _read_byte(self,reg):
		return int(self._bus.mem_read(1,self._address,reg)[0])
		
	def _read_u16(self,reg,):
		MSB = self._read_byte(reg)
		LSB = self._read_byte(reg+1)
		return (MSB << 8) + LSB
		
	def _read_s16(self,reg):
		result = self._read_u16(reg)
		if result > 32767:result -= 65536
		return result
		
	def _write_byte(self,reg,val):
	    self._bus.mem_write(val,self._address,reg)

	def poweron_init(self):
		self._write_byte(PWR_MGMT_1, 0x00)
		self._write_byte(SMPLRT_DIV, 0x07)
		self._write_byte(CONFIG, 0x06)
		self._write_byte(GYRO_CONFIG, 0x10)
		self._write_byte(ACCEL_CONFIG, 0x01)
		self.gyrOffset_init()
		
	def check(self):
		if WHO_AM_I_VAL == self._read_byte(WHO_AM_I):
			return True
		else:
			return False
		
	def read_raw_gyro(self):
		G = [0,0,0]
		G[0] = self._read_s16(GYRO_XOUT_H)
		G[1] = self._read_s16(GYRO_YOUT_H)
		G[2] = self._read_s16(GYRO_ZOUT_H)
		return G
		
	def gyrOffset_init(self):
		Gtemp = [0,0,0]
		for i in range(0,15):
			G=self.read_raw_gyro()
			Gtemp[0] += G[0]
			Gtemp[1] += G[1]
			Gtemp[2] += G[2]
		self.GX_OFFSET = Gtemp[0] // 15
		self.GY_OFFSET = Gtemp[1] // 15
		self.GZ_OFFSET = Gtemp[2] // 15
	
	def read_gyro(self):
		G = [0,0,0]
		temp = self.read_raw_gyro()
		G[0] = temp[0] - self.GX_OFFSET
		G[1] = temp[1] - self.GY_OFFSET
		G[2] = temp[2] - self.GZ_OFFSET
		return G
		
	def read_raw_accel(self):
		A = [0,0,0]
		A[0] = self._read_s16(ACCEL_XOUT_H)
		A[1] = self._read_s16(ACCEL_YOUT_H)
		A[2] = self._read_s16(ACCEL_ZOUT_H)
		return A
		
	def read_raw_temp(self):
		T = self._read_s16(TEMP_OUT_H)
		return T
		
	def read_temp(self):
		temp = self.read_raw_temp()
		T = 21.0 + temp/333.84
		return T

	
	def read_raw_mag(self):
		M = [0,0,0]
		self._write_byte(INI_PIN_CFG,0x02)
		pyb.delay(10)
		self._bus.mem_write(0x01,MAG_ADDRESS,0x0A)
		pyb.delay(10)
		LSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_XOUT_L)[0]
		MSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_XOUT_H)[0]
		M[0] = MSB*256 + LSB
		LSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_YOUT_L)[0]
		MSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_YOUT_H)[0]
		M[1] = MSB*256 + LSB
		LSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_ZOUT_L)[0]
		MSB = self._bus.mem_read(1,MAG_ADDRESS,MAG_ZOUT_H)[0]
		M[2] = MSB*256 + LSB
		return M	



def main():
		
	iic = pyb.I2C(1,pyb.I2C.MASTER)
	m=MPU9255(iic)

	while True:
		print ("Temperature: %.2f C" % m.read_temp())
		print(m.read_raw_accel())
		print(m.read_gyro())
		print(m.read_raw_mag())
		print('---------------')
		pyb.delay(800)
	
if __name__ == '__main__':
	main()