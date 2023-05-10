# id5_verifier
Python script to check which imgur id5 urls are valid. 
Multi threaded and low bandwidth! Begins checking at either 0 or a number specified and will continue till it reaches ~1billion attempts 
The only thing you need to install is pybase62 which you can get by running python.exe -m pip install pybase62 

This was quickly hacked together so it isn’t totally perfect but it kind of works, be sure to read code comments. This is intended to be ran twice, once forwards and once in reverse just to be 100% sure all possible products are calculated. You need to un comment some lines to do this.

This program could be modified to work with larger or smaller imgur id’s easily. 
Be aware it is really easy to hit imgur’s rate limiter! 

This script does not download data from the images, it just gets the first 10 bytes of the http response for max bandwidth effectiveness. 

Included are my two output files, last_id.txt and working_id5.txt, you can modify last_id.txt to start at a higher number if you want. working_id5.txt is the result of checking the first nearly 100K urls, each one of these should be a valid image id, there may be duplicates in this list as I just kept it going as I fixed issues in the script. 

