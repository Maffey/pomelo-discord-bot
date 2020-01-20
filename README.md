# Pomelo - Discord Bot
## Overview
This Discord bot was originally made for private purposes (basically, sending memes)
and was briefly imported from Repl.it, where it proved insufficient and unreliable.
The bot grew exponentially and became a group project for a class at *WWSIS Horyzont*.
## Technologies
- AWS *(distribution)*
- **discord.py**
- shelve
- plotly
- json
- zipfile
- matplotlib

##HOW TO RUN POMELO

connect to aws server via your key (encrypts the password) using shell
if you type ls you will get all files on server
enter cat pomelo.sh
pomelo.sh is a script that runs pomelo it executes the last line
    nohup python3 main.py &
    nohup - keeps open windows hidden so you can keep typing in console
    python3 - indicates language
    main.py - file to execute
    & - opens file in background, doesn't show output (like nohup)

run pomelo via script: 
    bash run_pomelo.sh
    
to stop pomelo enter ps -aux (shows active processes) then kill [process number]

crontab runs every #min hour day month week command
enter crontab -e to see what processes run at what schedule

to update pomelo enter the folder \PomeloDiscordBot and run git pull

