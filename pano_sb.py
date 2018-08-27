import RPi.GPIO as GPIO
from time import sleep
import time
GPIO.setmode(GPIO.BCM)
import subprocess
from PIL import Image
import sys
#from espeak import ESpeak
from picamera import PiCamera
import pytesseract
import preprocess
#import sys
from subprocess import call
import re

##inisialisasi gpio raspberry pi zero
GPIO.setwarnings(False)
button = [18, 15, 14]
GPIO.setup(button, GPIO.IN)
flash = 12
GPIO.setup(flash, GPIO.OUT)
buzz = 16
GPIO.setup(buzz, GPIO.OUT)

def play(txt):
	call(['espeak -p 75 -a 100 -g 10 -v id --stdout "{}" | aplay -q'.format(txt)], shell=True)

def my_callback(channel):
	print('interrupt')
	global stop
	stop = True
	#sys.exit()

def pic_voice(channel):
	print('pressed')
	global start
	start = True

def exit(channel):
	print('System Exit Detected')
	sys.exit()

GPIO.add_event_detect(button[1], GPIO.RISING, callback=my_callback, bouncetime=300) 
GPIO.add_event_detect(button[0], GPIO.RISING, callback=pic_voice, bouncetime=300)
GPIO.add_event_detect(button[2], GPIO.RISING, callback=exit, bouncetime=300)


def gabung(teks1, teks2):
	hasil = ''
	for i in range(-1, -len(teks1), -1):
		for j in range(0, len(teks2), 1):
			if teks1[i-3:i:1] == teks2[j:j+3:1]:
				hasil = teks1[0:1] + teks2[j:]
				break
			else:
				j+=1
		if hasil != '':
			break
		else:
			i+=1
	return hasil

#define variable
image_path = ["/home/pi/cam0.jpg", "/home/pi/cam1.jpg", "/home/pi/cam2.jpg", "/home/pi/cam3.jpg", "/home/pi/cam4.jpg"]
#image_path = "cam1.jpg"
camera = PiCamera()

##program dimulai
def bunyi(buzz, limit):
	a = 0
	while a<limit:
		GPIO.output(buzz, GPIO.HIGH)
		sleep(0.05)
		GPIO.output(buzz, GPIO.LOW)
		sleep(0.1)
		a += 1
	GPIO.output(buzz, GPIO.HIGH)
	sleep(0.2)
	GPIO.output(buzz, GPIO.LOW)


while True:
	print("selamat datang!!")
	play("selamat datang")
	text = ''
	#text = [[],[],[],[],[]]
	count = 0
	stop = False
	start = False

	while(not stop and count < 5):
		bunyi(buzz, 1)
		print("tekan tombol 2 untuk memulai")
		while(not stop and not start):
			sleep(0.001)
		if(stop):
			break
		else:
			print("memulai")
			GPIO.output(flash, GPIO.HIGH)
			print("mengambil gambar", count+1)
			camera.capture(image_path[count])
			print("mengambil gambar", count+1, " selesai")
			GPIO.output(flash, GPIO.LOW)
			count += 1
			start = False

	print('Mengambil gambar selesai')
	play("memulai konversi")
	bunyi(buzz, 2)
	stop = False

	waktu_mulai = time.clock()
	pic = 0
#	regex = re.compile('[^a-zA-Z]')
	text = ""
	#f = open("/home/pi/log.txt", "w")
	while pic < count:
		im = Image.open(image_path[pic])
		im = preprocess.start(im)
		#print("INFO:  Reading Text", pic+1)
		#f.write("reading text")
		temp = pytesseract.image_to_string(im, lang='ind', config='--psm 6')
		temp = temp.replace('-', ' ')
		temp = temp.replace('\n', ' ')
		temp = re.sub(r'[^a-zA-Z0-9 ]','', temp)
		#print(temp)
		#preprocess = regex.sub(' ', temp)
		text = text + temp
		#im.close()
		pic += 1
		#print(text)
		#f = open('/home/pi/log.txt', 'w')
		#f.write(text)
		#f.close()

	print(text)

	bunyi(buzz, 3)
	print("INFO:  Saying Text")
	#f.write("saying text")
	#f.close()
	print('Total huruf : ', len(text))
	selesai = time.clock() - waktu_mulai
	print("waktu : ", selesai)
#	es.say(text)
	#call(['espeak -p 75 -a 100 -g 10 -v id "{}" 2>/dev/null'.format(text)], shell=True)
	#call(['espeak -p 75 -a 100 -g 10 -v id --stdout "{}" | aplay -q'.format(text)], shell=True)
	play("memulai")
	sleep(2)
	play(text)

##loop untuk menggabungkan teks
'''
line = [[],[],[],[],[]]
hitung = 0
while text != [[],[],[],[],[]] and pic >1 and hitung<pic:
	for a in range(pic):
		line[a] = text[a].split("\n")
		print(line[a])
		print('\n')
	print(len(line[a]))
	for b in range(len(line[a])):
		for c in range(pic):
			hasil = gabung(line[c][b],line[c+1][b])
			print(hasil)
	hitung += 1
'''
print('FINISH')
