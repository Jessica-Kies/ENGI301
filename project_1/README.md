The code for this project was based on Franck Montano Ostrander's PocketBeagle Arcade Machine which is accessible at
https://www.hackster.io/fdm3/pocketbeagle-arcade-machine-ee661e.

Six libraries were imported to use in the code. They are os, random, time, sys, Adafruit_BBIO.PWM, and Adafruit_BBIO.GPIO

Some of the code is currently not being used for the project. This code came from the base code from Franck Montano Ostrander and will be used in later implementations. Currently 
the display is wired, but not coded to be used. In the future, the display will be utilized to tell the user if they have won or lost the game. The difficulty level will be 
displayed after the user wins. The display will say “lock” when the user loses the game and is unable to play.

The run_candy_game.sh file was created so the code could run without being connected to the computer. This is implemented using the command window. First a logs directory needs 
to be created. Then the line: “sudo crontab -e”. The next line of code is dependent on the path. For my code it was: 
“@reboot sleep 15 && sh /var/lib/cloud9/ENGI301/project_1/run_candy_game.sh >/var/lib/cloud9/ENGI301/project_1/logs/cronlog 2>&1”.

To learn more about the physical aspects of this project go to: https://www.hackster.io/jnk1/candy-game-box-using-pocket-beagle-d55049 
