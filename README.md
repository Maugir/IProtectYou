IProtectYou
===========

Python project that uses Dropbox Uploader to send Raspberry's Camera files into your Dropbox Account.
First install https://github.com/andreafabrizi/Dropbox-Uploader, so when you have activated your Dropbox directory put inside this file rasp_cam_hdd_online.py and the configuration's file config_v0.txt. At your first run the python script copies the file config_v0.txt inside your Dropbox account online, the goal is that from your Dropbox account you can control your home with your raspberry camera.

This is the structure of the configuration's file. 

board_name = xxx # board name, I use it for being different from another board, more than one Raspberry in a Dropbox account

language = 0  # 0 English, 1 Italian, 2 etc... language of the email alert (useful when your Raspberry alerts you that
inside your Dropbox account there is a new file)

quality = 10 # from 0 (low) to 100 (high) in image quality

data = 0 # 0 save data on dropbox, 1 save data on google drive, 2 save data on USB

interval = 60 # How often the Cam takes a photo in seconds - 0 =always, is a video

range_b = 00_0_0_0_0_0 # Start to take images from this date

range_e = 98_99_99_99_99_99 # End to take images

ext_int_event_a = 0 # 0 not active, 1 pin interrupt active on #GPIO 4 is 7 in Rpi.GPIO - IR detection in input for
starting to take a picture or a video 

motion_event = 0 # 0 not active, 1 take a photo/video on motion detection

amount_of_space = 1048576 # max amount of image/video saved in KB (default 1 GB)

erase_old_file	= 0		# Erase all old files saved on your account, 0=nothing to erase, 1=erase the last day, 2=erase from two days ago ...

ip = 192_168_0_2 #useful when you have to control more than one Raspberry (at the moment not used)

network = 255_255_255_0 #useful when you have to control more than one Raspberry (at the moment not used)

broadcast = 192_168_0_255 #useful when you have to control more than one Raspberry (at the moment not used)

dhcp = 0 #useful when you have to control more than one Raspberry (at the moment not used)

email_yes_no = 1 # 0 no email, 1 email to this account with a photo, 2 email to this account without photo (only url in dropbox)

email_to = xxx@gmail.com

email_user = xxx@gmail.com

email_pwd = xxx

email_smtp_name = smtp.gmail.com

email_smtp_port = 587

When there is something to upload in Dropbox your Raspberry downloads the configuration's file and applies the modifications.


More options are under development.
