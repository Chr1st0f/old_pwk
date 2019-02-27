#!../venvkali/bin/python3
# !--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

''' 
Role :  Do a CSRF

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
