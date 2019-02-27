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
    
###    2_csrf_dvwa_medium.py :
    
   In this mode, it is not possible to do it because there is a referer 
   when you try to change the password in get mode.
   It is to prevent you to send a link on other website site. 
   In this case when you click on the link the referer will be your 
   attacking machine and it'll not be the DVWA. 
     
   This python script log in to the DVWA platform 
   ( it is a docker machine but can be anything else )
   Change the security to medium mode 
   Go to CSRF menu 
   Change the password in modifying the referer and providing cookie 
   generated before. 
   You would need to download bs4 , requests, termcolor
   In python3 -> pip3 install ... 
   
   This script is adaptable to your DVWA test plaform. Just change the 
   IP address and should work if you don't have change the default passwords
   