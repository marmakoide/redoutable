# redoutable

This script automatically maintains an area of r/place, using a PNG picture as
a template. The more people runs the script to cover the same area with the same
template, the harder it will be to grief that area.


Quick instructions
------------------

On Linux, Ubuntu distribution

* Install Python : *sudo apt-get install python python-setuptools*
* Install the required dependencies : *sudo easy_install requests*
* Download the archive at *https://github.com/marmakoide/redoutable/archive/master.zip*
* Uncompress the archive on your desktop. This should creates a *redoutable-master* folder
* Open a shell window and type : *cd ~/Desktop/redoutable-master*
* Still in that shell window : *python redoutable.py -u username -p password -x x -y y image.png*

* *image.png* is the picture to maintain
* *x* and *y* are the coordinates of the upper left corner of the picture in r/place.
* *username* and *password* is your login/password for Reddit.

To stop the script : Ctrl+c in the shell window 

On Windows

* Install Python : *https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi*
* Download the archive at *https://github.com/marmakoide/redoutable/archive/master.zip*
* Uncompress the archive on your desktop. This should creates a *redoutable-master* folder
* Open a terminal window (Windows key + R) then type *cmd* and click *OK*
* In the terminal, type *CD C:\Users\VotreNomUtilisateur\Desktop\redoutable-master*
* Type *easy_install requests*
* Still in that terminal : *python redoutable.py -u username -p password -x x -y y image.png*

* *image.png* is the picture to maintain
* *x* and *y* are the coordinates of the upper left corner of the picture in r/place.
* *username* and *password* is your login/password for Reddit.

To stop the script : Ctrl+c in the terminal


