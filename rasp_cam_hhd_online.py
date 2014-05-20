import os
import datetime
import RPi.GPIO as GPIO
import string
import re
import time
import thread
import smtplib import SMTP
import smtplib import SMTP_SSL
import smtplib import SMTPException

class Config_data:
	board_name		= None		# board name, I use it for being different from another board
	language		= 0			# 0 English, 1 Italian, 2 etc...
	quality         = 10		# from 0 (low) to 100 (high) in image quality
	# with range_b = 00_0_0_0_0_0 and range_e = 101_99_99_99_99_99 infinity time
	range_b         = [] 		# begin -multiple intervals - list cannot be inizialized here!
	range_e         = [] 		# end - multiple intervals - list cannot be initialized here!
	interval        = 60   		# every seconds - 0 =always, is a video
	ext_int_event_a = 0 		# 0 not active, 1 pin interrupt active on #GPIO 4 is 7 in Rpi.GPIO - IR detection in input for starting to take a picture or a video 
	#at the moment only one interrupt pin
	motion_event	= 0			# 0 not active, 1 take a photo/video on motion detection
	data	        = 0  		# 0 save data on dropbox, 1 save data on google drive, 2 save data on USB
	erase_old_file	= 0			# Erase all old files saved on your account, 0=nothing to erase, 1=erase the last day, 2=erase from two days ago ...
	amount_of_space	= 1048576	# max amount of image/video saved in KB (default 1 GB)
	ip	            = [] 		# some other boring network stuff
	network         = [] 		# some other boring network stuff
	broadcast       = [] 		# some other boring network stuff
	dhcp            = 0 		# 0 without DHCP, 1 with DHCP 
	email_yes_no	= 0 		# 0 no email, 1 email to this account with a photo, 2 email to this account without photo (only url in dropbox)
	email_to 		= None		# Who I send this email alert ?
	email_user		= None		# email account info: user
	email_pwd		= None  	# email account info: pwd
	email_smtp_name = None		# email account info: smtp server name
	email_smtp_port = 0			# email account info: smtp server port
	check_others	= 0			# to control others raspberries or others ips in the security system 0=none, >1 time in sec
	ip0_to_c        = []		# the first ip to check 
	ip1_to_c        = []
	ip2_to_c        = []
	ip3_to_c        = []
	ip4_to_c        = []
	ip5_to_c        = []
	ip6_to_c        = []
	ip7_to_c        = []
	ip8_to_c        = []
	ip9_to_c        = []		# the last ip to check 
	
space = -1
USB_DIRECTORY_PATH="/media/usb_security"
USB_EXE_PATH="/home/pi/Dropbox-Uploader"
#Remember to attach usb on the high connector, the connector more distance from the back
def take_a_video_picture_movement(channel):
	global config_data
	global space
	#GPIO 4 is 7 in Rpi.GPIO - IR detection - ext_int_event_a 
	while space<config_data.amount_of_space:	#while 1
		reload_config()
		comparison = check_config()	
		if comparison:
			#print "Movement!"
			time.sleep(0.3) #confirm the movement by waiting 1.5 sec
			if GPIO.input(7): #and check again the input
				print "Movement after 0.3 sec!"
				take_the_moment()
				os.system("sync")
			#else:
				#print "NO - Movement after 0.3 sec!"
		else:
			print "Change settings"

def take_the_moment():
	global config_data
	global space
	today  = datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S")
	#today = "14_02_14_18_26_04"
	os.system("/usr/bin/raspistill -v -q "+str(config_data.quality)+" -o "+USB_EXE_PATH+"/"+today+".jpg") 
	print "OK_2a"
	if config_data.data==2:#USB
		if os.path.isdir(USB_DIRECTORY_PATH):
			os.system("mv "+USB_EXE_PATH+"/"+today+".jpg "+USB_DIRECTORY_PATH+"/"+today+".jpg")	
		else:
			if os.path.isdir(USB_DIRECTORY_PATH):
				print "OK_3"
			else:
				print "OK_4"
				os.system("mv "+USB_EXE_PATH+"/"+today+".jpg "+USB_DIRECTORY_PATH+"/"+today+".jpg")					
	elif config_data.data==0:		
		isalive = os.popen('ping -c 2 www.google.it | grep -o "64 bytes"').read()
		if isalive:
			if isalive[0:2]=='64': #if network is on
				print("Network is up and running")
				os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh upload "+USB_EXE_PATH+"/"+today+".jpg") #Send a recently image
			else:
				print("Network is down - save the image in USB, send it in another moment")
		else:
			print("Network is down - save the image in USB, send it in another moment")				
		#At every send, you have to control if the file was sended
		isalive = os.popen(". "+USB_EXE_PATH+"/dropbox_uploader.sh list | grep -o "+today+".jpg").read()
		isalive = isalive.strip('\n')
		if isalive:
			if os.path.isfile(USB_EXE_PATH+"/"+isalive):
				if os.path.isfile(USB_EXE_PATH+"/"+isalive):
					print "The image was correctly sended to Dropbox"
					os.system("rm -f "+USB_EXE_PATH+"/"+today+".jpg") #erase the image sended to Dropbox
					#Send an email to confirm
					send_email()
					#Are there another images that weren't sended? Send it immediately TODO...check if it works
					if os.system("ls "+USB_EXE_PATH+" | grep -o "+".jpg"):	#if there is an image or more
						os.system("./dropbox_uploader.sh upload *.jpg") #send all images
						os.system("rm -f "+USB_EXE_PATH+"/*.jpg") #TODO check if the images sended are in Dropbox
						os.system("rm -f "+USB_EXE_PATH+"/images_not_sended.txt") 
				else:
					print "Error: the image wasn't correctly sended to Dropbox" #Save it to a queue of images that weren't sended, that are inside this work's directory
					if os.path.isfile("images_not_sended.txt"):
						queue_file=open(USB_EXE_PATH+"/images_not_sended.txt","a") #append
					else:
						queue_file=open(USB_EXE_PATH+"/images_not_sended.txt","w") #create it
					queue_file.write(today+".jpg \n")
					queue_file.close()
		else:
			print "Error: the image wasn't correctly sended to Dropbox" #Save it to a queue of images that weren't sended, that are inside this work's directory
			if os.path.isfile(USB_EXE_PATH+"/images_not_sended.txt"):
				queue_file=open(USB_EXE_PATH+"/images_not_sended.txt","a") #append
			else:
				queue_file=open(USB_EXE_PATH+"/images_not_sended.txt","w") #create it
			queue_file.write(today+".jpg \n")
			queue_file.close()	
	if config_data.data==2:#USB	
		print "USB_1"
	elif config_data.data==0:
		#At every send, control if there is a configuration file
		isalive = os.popen(". "+USB_EXE_PATH+"/dropbox_uploader.sh list | grep -o config_v.*").read()
		isalive = isalive.strip('\n')
		if isalive:
			if isalive[0:8]=='config_v':
				print "In Dropbox account there is a configuration file" #if this file has the same name not download it
				#old_config_value=int(isalive[8:10])	
				if os.path.isfile(USB_EXE_PATH+"/"+isalive):
					print "The file in the Dropbox account is like this file inside the Raspberry"
				else:
					print isalive			
					print "The file in the Dropbox account is not like this file inside the Raspberry. Download it and reconfig the system."
					os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh download "+isalive)
					#Now reload the new configuration 
					reload_config()
			else:
				print("There isn't configiguration file-now I create one")
				os.system("rm -f "+USB_EXE_PATH+"/config_v*") #erase all old config file, crate a default file
				config_file=open(USB_EXE_PATH+"/config_v0.txt","w")
				config_file.write("board_name = abc_security \n")
				config_file.write("language = 0 \n")
				config_file.write("quality = 10 \n")
				config_file.write("range_b = 00_0_0_0_0_0 \n") #yy_m_d_h_m_s
				config_file.write("range_e = 101_99_99_99_99_99 \n")
				config_file.write("interval = 60 \n")
				config_file.write("ext_int_event_a = 0\n")
				config_file.write("motion_event = 0\n")
				config_file.write("data = 0 \n")
				config_file.write("erase_old_file = 0 \n")
				config_file.write("amount_of_space	= 1048576 \n")
				config_file.write("ip = 192_168_0_2 \n")
				config_file.write("network = 255_255_255_0 \n")
				config_file.write("broadcast = 192_168_0_255 \n")
				config_file.write("dhcp = 0 \n")
				config_file.write("email_yes_no = 0 \n")
				config_file.write("email_to = 0 \n")
				config_file.write("email_user = 0 \n")
				config_file.write("email_pwd = 0 \n")
				config_file.write("email_smtp_name = 0 \n")
				config_file.write("email_smtp_port = 0 \n")
				config_file.close()
				os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh upload config_v0.txt") #Only one shot, without check Internet connection		
	if config_data.erase_old_file:
		today  = datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S")
		today_re = 	re.findall(r'\d+',today)	#today_re[0]+"_"+today_re[1]+"_"+today_re[2] %y_%m_%d
		if today_re[2]>config_data.erase_old_file :
			today_re[2] = today_re[2]-config_data.erase_old_file
		else: #28/29 Febrary (2)- 30 November(11) April(4) June(6) September (9) - 31 January (1)(3)(5)(7)(8)(10)(12)
			if today_re[1]==1:
				today_re[1]=12
				if today_re[0]>0:
					today_re[0]=today_re[0]-1
				else:
					today_re[0]=99	
			else:
				today_re[1]=today_re[1]-1
			if today_re[1]==1 or today_re[1]==3 or today_re[1]==5 or today_re[1]==7 or today_re[1]==8 or today_re[1]==10 or today_re[1]==12:
				today_re[2]=31-(config_data.erase_old_file-today_re[2])			
			elif today_re[1]==4 or today_re[1]==6 or today_re[1]==9 or today_re[1]==11:
				today_re[2]=30-(config_data.erase_old_file-today_re[2])
			elif today_re[1]==2:
				if today_re[0]%4==0:#year with a day in more 
					today_re[2]=29-(config_data.erase_old_file-today_re[2])
				else:#normal year
					today_re[2]=28-(config_data.erase_old_file-today_re[2])
		#Erase old images on USB card
		if config_data.data==2:
			if os.path.isdir(USB_DIRECTORY_PATH) and os.path.isdir("/dev/sda1"): #if exist the usb device
				print "OK_1"
			else:
				print "OK_2"
				
			if os.system("ls "+USB_DIRECTORY_PATH+" | grep -o "+today_re[0]+"_"+today_re[1]+"_"+today_re[2]+"_.*.jpg"):	#if there is an image or more
				os.system("rm -f "+USB_DIRECTORY_PATH+"/"+today_re[0]+"_"+today_re[1]+"_"+today_re[2]+"_.*.jpg")				
		if config_data.data==0:
			isalive = os.popen(". "+USB_EXE_PATH+"/dropbox_uploader.sh list | grep -o "+today_re[0]+"_"+today_re[1]+"_"+today_re[2]+"_.*.jpg").read()
			isalive = isalive.strip('\n')
			print isalive
			if isalive:
				print "OK_2"
				isalive=isalive.replace('\n',' ') 
				isalive=isalive.split(' ') #convert a string in a list 
				#os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh remove "+isalive)
				for item in isalive:
					os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh delete "+item) #one item at once
			else:
				print "Empty_1"
	else:
		print "Empty_2" #nothing to do	
	if config_data.data==2:	
		#if os.path.isdir("/dev/sda1"):
		space = sum([os.path.getsize(USB_DIRECTORY_PATH+"/"+f) for f in os.listdir(USB_DIRECTORY_PATH+"/") if os.path.isfile(USB_DIRECTORY_PATH+"/"+f)])/1024 #directory size without subdirectories KB
		print "Space amount occupy by this dir "+str(space)+" KB"
		#else:
		#	print "No usb inserted"
	elif config_data.data==0:
		isalive = os.popen(". "+USB_EXE_PATH+"/dropbox_uploader.sh info | grep -o Used:.*Mb").read()
		isalive = isalive.strip('\n')
		space = int(re.search(r'\d+',isalive).group())
		print "Space amount occupy by this dir "+str(space)+" KB"
		
def send_email():
	global config_data
	#print "Sending Email"
	smtpserver = smtplib.SMTP(config_data.email_smtp_name,config_data.email_smtp_port)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(config_data.email_user, config_data.email_pwd)
	header = 'To:' + config_data.email_to + '\n' + 'From: ' + config_data.email_user
	header = header + '\n' + 'Subject: Nuova immagine su Dropbox \n'
	print header
	msg = header + '\n Prova riuscita \n\n'
	smtpserver.sendmail(config_data.email_user, config_data.email_to, msg)
	smtpserver.close()

def send_email_ssl():
	global config_data
	if config_data.email_user!=0 and config_data.email_pwd !=0 and config_data.email_to!=0:
		print "Sending Email"
		try:
			smtpserver = smtplib.SMTP_SSL(config_data.email_smtp_name,config_data.email_smtp_port)
			smtpserver.login(config_data.email_user, config_data.email_pwd)
			if config_data.language==1 : #italian
				header = 'To:' + config_data.email_to + '\n' + 'From: ' + config_data.email_user
				header = header + '\n' + 'Subject: cambio impostazioni avvenuto con successo \n'			
				msg = header + '\n Prova riuscita \n\n'
			else : #at the moment only two languages
				header = 'To:' + config_data.email_to + '\n' + 'From: ' + config_data.email_user
				header = header + '\n' + 'Subject: settings changed \n'			
				msg = header + '\n Settings changed successfully \n\n'		
			smtpserver.sendmail(config_data.email_user, config_data.email_to, msg)
			smtpserver.quit()
		except SMTPException:
			print "Unable to send email"	
	
def check_config(): #Check the configuration file if is right return 1 value
	global config_data
	global space
	#print("Check config")	
	return_value = 0
	#if config_data.ext_int_event_a and config_data.motion_event:
	#	return_value = 1 # not consider the interval time but only the interrupt
	#else :
	today  = datetime.datetime.now().strftime("%y_%m_%d_%H_%M_%S")
	space = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))/1024 #directory size without subdirectories KB
	today_re = 	re.findall(r'\d+',today)	
	#print "Date time now: Year 20"+str(today_re[0])+" Month "+str(today_re[1])+" Day "+str(today_re[2])
	if config_data.range_b[0] < today_re[0] < config_data.range_e[0] :
		#print "OK Year"
		if config_data.range_b[1] < today_re[1] < config_data.range_e[1] :
			#print "OK Month"
			if config_data.range_b[2] < today_re[2] < config_data.range_e[2] :
				#print "OK Day"
				if config_data.range_b[3] < today_re[3] < config_data.range_e[3] :
					#print "OK Hour"
					if config_data.range_b[4] < today_re[4] < config_data.range_e[4] :
						#print "OK Minute"
						if config_data.range_b[5] < today_re[5] < config_data.range_e[5] :
							#print "OK Second"
							return_value = 1
							
	if space<config_data.amount_of_space:
		return_value = 1
	else:
		return_value = 0
		
	if return_value:
		return 1
	else:	
		return 0
	
def reload_config(): #Load config from the configuration file
	global config_data
	isalive = os.popen("ls "+USB_EXE_PATH+"| grep -zo config_v.*").read()
	isalive = isalive.strip('\n')	
	if isalive:
		if os.path.isfile(USB_EXE_PATH+"/"+isalive):
			with open(USB_EXE_PATH+"/"+isalive) as f:
				for line in f:
					if 'board_name =' in line :
						#print line
						config_data.board_name=str(re.search(r'\d+',line).group())
					if 'language =' in line :
						#print line
						config_data.language=int(re.search(r'\d+',line).group())	
					if 'quality =' in line :
						#print line
						config_data.quality=int(re.search(r'\d+',line).group())	#to check the value use this expression: print int(re.search(r'\d+',line).group())
					if 'data =' in line :
						#print line
						config_data.data=int(re.search(r'\d+',line).group())					
					if 'interval =' in line :
						#print line
						config_data.interval=int(re.search(r'\d+',line).group())	
					if 'range_b =' in line :
						#print line
						config_data.range_b = re.findall(r'\d+',line) #List with: year, month,day,hour,minute,second											
					if 'range_e =' in line :
						#print line
						config_data.range_e = re.findall(r'\d+',line) #List with: year, month,day,hour,minute,second
					if 'ext_int_event_a =' in line:
						#print line
						config_data.ext_int_event_a = int(re.search(r'\d+',line).group())
					if 'motion_event =' in line:
						#print line
						config_data.motion_event = int(re.search(r'\d+',line).group())	
					if 'erase_old_file =' in line:	
						#print line
						config_data.erase_old_file = int(re.search(r'\d+',line).group())					
					if 'amount_of_space =' in line:	
						#print line
						config_data.amount_of_space = int(re.search(r'\d+',line).group())
					if 'ip =' in line :
						#print line
						config_data.ip = re.findall(r'\d+',line)
					if 'network =' in line :
						#print line
						config_data.network = re.findall(r'\d+',line)
					if 'broadcast =' in line :
						#print line
						config_data.broadcast = re.findall(r'\d+',line)
					if 'dhcp =' in line :
						#print line
						config_data.dhcp=int(re.search(r'\d+',line).group())
					if 'email_yes_no =' in line :
						#print line
						config_data.email_yes_no=int(re.search(r'\d+',line).group())
					if 'email_to =' in line :
						#print line
						config_data.email_to=str(re.search(r'\d+',line).group())
					if 'email_user =' in line :
						#print line
						config_data.email_user=str(re.search(r'\d+',line).group())	
					if 'email_pwd =' in line :
						#print line
						config_data.email_pwd=str(re.search(r'\d+',line).group())	
					if 'email_smtp_name =' in line :
						#print line
						config_data.email_smtp_name=str(re.search(r'\d+',line).group())	
					if 'email_smtp_port =' in line :
						#print line
						config_data.email_smtp_port=int(re.search(r'\d+',line).group())		

	
def take_a_video_picture_interval(string,sleeptime,*args):
	global config_data
	global space
	while space<config_data.amount_of_space:	#while 1
		print string
		reload_config()
		comparison = check_config()	
		GPIO.setwarnings(False) #to remove Rpi.GPIO's warning
		if comparison:
			take_the_moment()			
			if config_data.motion_event and config_data.ext_int_event_a:					
				GPIO.setmode(GPIO.BOARD) 
				#GPIO.gpio_function(7) check if gpio is already setted as input or other
				GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #pull-up input ,pull_up_down=GPIO.PUD_DOWN
				# dimensione della directory
				#print os.path.getsize("nomefile")
				#print os.stat(".").st_size
				#print sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f)) #directory size without subdirectories
				print ("Debug 1: input value ")
				print GPIO.input(7)	
				GPIO.add_event_detect(7,GPIO.RISING,callback=take_a_video_picture_movement,bouncetime=3000) #bouncetime tempo inibizione tra un evento e un altro 3000=3s			
				thread.exit()
			else:
				GPIO.cleanup()
				time.sleep(sleeptime)
						
		else:
			print "The date/time range is not valid"
		
		
	print "There isn't space available - Max amount_of_space reached: "+str(config_data.amount_of_space)+" KB" 	

def control_config_file(string,sleeptime,*args):
	while 1:
		print string
		isalive = os.popen(". "+USB_EXE_PATH+"/dropbox_uploader.sh list | grep -o config_v.*").read()
		isalive = isalive.strip('\n')
		if isalive:
			if isalive[0:8]=='config_v':
				print("In Dropbox account there is a configuration file") #if this file has the same name not download it
				#old_config_value=int(isalive[8:10])	
				if os.path.isfile(USB_EXE_PATH+"/"+isalive):
					print "The configuration file is in the Dropbox account, now I download it"
					os.system(". "+USB_EXE_PATH+"/dropbox_uploader.sh download "+isalive)			
			
if __name__=="__main__": 
	try:
		#if os.path.isdir(USB_DIRECTORY_PATH):
		#	os.system("rm -r "+USB_DIRECTORY_PATH)
		config_data = Config_data()	
		reload_config()
		comparison = check_config()	
	
		
		if comparison:
			if config_data.data==2:			
				os.system("umount /dev/sda1")
				if os.path.isdir(USB_DIRECTORY_PATH)==0:
					os.system("mkdir "+USB_DIRECTORY_PATH)
				os.system("mount /dev/sda1 "+USB_DIRECTORY_PATH)
				
			thread.start_new_thread(take_a_video_picture_interval,("Thread No:1",config_data.interval))
			while 1:pass
		else:
			print "The date/time range is not valid" #	Start the process, to check if in Dropbox there is another configuration file
			thread.start_new_thread(control_config_file,("Thread No:2",config_data.interval))
			while 1:pass
			
	except KeyboardInterrupt:
		# Reset GPIO settings
		GPIO.cleanup()
# Change to your own account information
# to = 'xxx'
# gmail_user = 'xxx'
# gmail_password = 'xxx'
# smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
# smtpserver.ehlo()
# smtpserver.starttls()
# smtpserver.ehlo
# smtpserver.login(gmail_user, gmail_password)
# today = datetime.date.today()
# # Very Linux Specific
# arg='ip route list'
# p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
# data = p.communicate()
# split_data = data[0].split()
# ipaddr = split_data[split_data.index('src')+1]
# my_ip = 'Your ip is %s' %  ipaddr
# msg = MIMEText(my_ip)
# msg['Subject'] = 'IP For RaspberryPi on %s' % today.strftime('%b %d %Y')
# msg['From'] = gmail_user
# msg['To'] = to
# smtpserver.sendmail(gmail_user, [to], msg.as_string())
# smtpserver.quit()	
	
