#!/usr/bin/python2


import sys, os
#sys.path.append("/home/biegbart/ort/paramiko-master/")
#sys.path.append("/home/biegbart/ort/cryptography-master/src")
#sys.path.append("/home/biegbart/ort/enum34-1.1.6")
#sys.path.append("/home/biegbart/ort/six-1.10.0")
#sys.path.append("/home/biegbart/ort/pexpect-4.2.1")
#sys.path.append(os.path.abspath("pexpect-4.2.1"))

import sys, os, glob

for i in glob.glob("/home/biegbart/libs/*"):
	sys.path.append(os.path.abspath(i))


# csv, file
# TODO wifi controllers: User: prompt, problem with exiting


#import paramiko
import pexpect 
from pexpect import EOF
#import pxssh
from openpyxl import Workbook

import getpass, re
from datetime import datetime

'''
	Finds system username, full name and user ID.
	
	return:
		(username, full name, uid)
		None - if not found
'''

def findUserFullNameAndID():
	username = getpass.getuser()
	
	with open('/etc/passwd', 'r') as file:
		for line in file:
			if re.match('^%s:.*' % username, line):
				l = re.split(':', line)
				return (username, l[4], l[2])
	
	return (None, None, None)

	
	

# ask for input file
if len(sys.argv) > 1:
	infile = sys.argv[1]
else:
	infile = "dev_to_check.txt"
	infile = raw_input("Input file [%s]: " % infile) or infile

print('')
print('Choosed file: %s.' % infile)
print('')

print('')

uid, fullName, username = findUserFullNameAndID()

username = raw_input("login [%s]: " % username) or username
password = getpass.getpass('password: ')

print('')

# ==============================
# select NCM jumphost
#ncm_jumphost=''

menu = {}
menu['1'] = ["####"]
menu['2'] = ["####"]
menu['3'] = ["####"]
menu['4'] = ["####"]
menu['5'] = ["####"]
menu['6'] = ["####"]
menu['7'] = ["####"]
menu['8'] = ["####"]
menu['9'] = ["####"]

while True:
	options = menu.keys()
	options.sort()
	
	for i in options:
		print("%s\t%s" % (i, menu[i][0]))
	
	selection = raw_input("Select NCM jumphost: ")
	
	if selection in options:
		ncm_jumphost = menu[selection][1]
		break

		
# ==============================
# connect to NCM

print("\nConnecting to %s..." % ncm_jumphost)
child = pexpect.spawn('ssh -p 8022 -o StrictHostKeyChecking=no -l %s %s' % (username, ncm_jumphost), timeout=60)
try:
	child.expect('Password:')
except (pexpect.EOF, pexpect.TIMEOUT) as e:
	# connection refused, other errors
	print("Cannot connect to NCM jumphost. Exiting.")
	print(child.before)
	child.close()
	exit(1)
	
child.sendline(password)

index = child.expect(['Password:', 'NA>'])

if index == 0:
	print('Bad password. Exiting.')
	exit(1)
elif index == 1:
	print('Connected to NCM.')




outfilename = "%s.txt" % datetime.now().strftime("%Y%m%d%H%M%S")

print('Output files prefix: %s' % outfilename)
	
# ==============================
# go through all IP addresses

with open(infile) as f:
	with open(outfilename + '.txt', 'w') as outfile:
		outfile.write("ip,icmp,reachable,tacacs,location,comment\n")
		outfile.flush()
		
		outfileexcel = Workbook()
		outfileexcelws = outfileexcel.active
		outfileexcelws.title = infile
		
		outfileexcelws.append(['ip', 'icmp', 'reachable', 'tacacs', 'location', 'comment'])

		for ip in f:
			ip = ip.rstrip('\n').rstrip('\r')
			
			# check if line contains valid IP address
			if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip) is None:
				continue
			
			comment = ''
			icmp = ''
			reachable = ''
			tacacs = ''
			location = ''
			
			print('%s ...' % ip)

			
			try:
				# ping
				child.sendline('os ping %s -c 10' % ip)
				index = child.expect(['10 packets transmitted', 'NA>'])
				
				if index != 0:
					icmp = 'unknown'
				else:
					index = child.expect(['0 received', '1 received', '2 received', '3 received', '4 received', '5 received', '6 received', '7 received', '8 received', '9 received', '10 received'])
					
					if index == 0:
						icmp = 'no'
					elif index == 1:
						icmp = 'received 1/10 packet loss'
					elif index == 2:
						icmp = 'received 2/10 packet loss'
					elif index == 3:
						icmp = 'received 3/10 packet loss'
					elif index == 4:
						icmp = 'received 4/10 packet loss'
					elif index == 5:
						icmp = 'received 5/10 packet loss'
					elif index == 6:
						icmp = 'received 6/10 packet loss'
					elif index == 7:
						icmp = 'received 7/10 packey loss'
					elif index == 8:
						icmp = 'received 8/10 packet loss'
					elif index == 9:
						icmp = 'received 9/10 packet loss'
					elif index == 10:
						icmp = 'yes'
					
					child.expect('NA>')
				
				

					
				outfile.write("%s,%s,%s,%s,%s,%s\n" % (ip, icmp, reachable, tacacs, location, comment))
				outfile.flush()
				
				outfileexcelws.append([ip, icmp, reachable, tacacs, location, comment])
				outfileexcel.save(outfilename + ".xlsx")


				
			except pexpect.TIMEOUT:
				# check 164.52.138.37
				print("TIMEOUT")
				print(child.before)
				reachable = 'no/timeout'
				tacacs = 'no/timeout'
				icmp = 'no/timeout'
				outfile.write("%s,%s,%s,%s,%s,%s\n" % (ip, icmp, reachable, tacacs, location, comment))
				outfile.flush()
				
				outfileexcelws.append([ip, icmp, reachable, tacacs, location, comment])
				outfileexcel.save(outfilename + ".xlsx")

				#child.close()
				#print(str(child))
			
			#print("\n\n")
			#exit(1)



		
	# ==============================
	# exit NCM jumphost
	print("Exiting NCM jumphost.")
	child.sendline('quit')
	child.close()
	#exit(1)

