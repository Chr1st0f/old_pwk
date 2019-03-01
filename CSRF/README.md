# PWK /OSCP
### Created by Chr1st0f 27/02/19
Christophe Cazin -> admin@cyber-secu.com
##
    This repo is composed of 2 scripts : 
    
###    1_csrf_dvwa_low.html :
    
   In low security mode in DVWA CRSF menu, if someone is logged in 
   to DVWA in admin, you send this html file and when the image will
   be loaded, the password will be changed in GET mode 
   
   <a href=http://172.16.13.1:81/vulnerabilities/csrf/?password_new=weakpass&password_conf=weakpass&Change=Change#>
    
   Once the client has loaded the html file, the password is changed. 
   There is also a 2nd example with a link in this file 
    
###    2_csrf_dvwa_v1_10_high.py :
    
   Change the password in the CSRF menu in high security level
   
   In this mode, it is not possible to do the same as low/medium mode
   because there is a referer in the header when you try to change 
   the password in get mode.
   It is to prevent you to send a link on other website site. 
   In this case when you click on the link the referer will be your 
   attacking machine and it'll not be the DVWA. 
     
   This script allow you to crack DVWA CSRF (Cross-Site Request Forgery ) platform 
        
   Connect to DVWA interface 
    Go to DVWA Security menu and Setup the high level 
    Go to CSRF menu and launch a changing of password
    To be able to do it we have to send a GET request in : 
        modifying the REFERER ( give the IP of source DVWA and not the default ) in the header
        Give a hiiden field call user_tkoken 
        Fill the form and validate 
    All is done with requests and Beautiful soup library
        
   Work only in DVWA Version 1.10 *Development* (Release date: 2015-10-08
   else you should adapt the soup filters ( response could be a bit different with other versions )
   I have used a docker image of DVWA for my tests.
   You would need to download bs4 , requests, termcolor
   In python3 -> pip3 install ... 
   
   This script is adaptable to your DVWA test plaform. Just change the 
   IP address and should work if you don't have change the default passwords
   
   If you have questions or requests, please send me an email.