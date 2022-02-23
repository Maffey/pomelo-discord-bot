# Pomelo Discord Bot

Sassy Discord bot with multiple small functionalities, used mostly for fun and learning.

# How to run Pomelo

1. Clone the repository.
2. Set the working directory as the root directory of the repository (/pomelo-discord-bot by default).
3. Get the necessary API tokens and set them up as environmental variables:
   1. Discord bot token
   2. Google Maps API token
   3. MongoDB's connection token (full identifier)
4. Run main.py. You're done!

Pomelo currently is deployed using Heroku. To deploy it to Heroku, see the relevant guides.

## How to run Pomelo on AWS \[depracated\]

In the past, Pomelo was deployed on multiple things, including repl.it and AWS.
This guide refers to running Pomelo on AWS, although it hadn't been updated in quite a while.

Connect to AWS server via your key (encrypts the password) using shell. if you type `ls` you will get all files listed
on the server. Enter the folder with the *pomelo-discord-bot* and enter following command:
`nohup python3 main.py &`
nohup - runs given piece of software in the background, by attaching it to virtual terminal. python3 - indicates which
language you want to use to run the script. main.py - file to execute. & - opens file in background, doesn't show
output (like nohup)

To stop pomelo enter `ps -aux` (shows active processes) then `kill [process_number]`

Crontab allows us to automate some tasks, in this case daily. Enter `crontab -e` to see what processes run at what
schedule. Here, add the command above and `sudo reboot` to allow for a machine restart every day.

To update pomelo enter the folder \pomelo-discord-bot and run `git pull`.

