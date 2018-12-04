# dobby18bot
telegram bot for dobby's learning
```
[Unit]
Description=Bot Daemon for Dobby
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/dobby-bot
ExecStart=/home/pi/ocv/bin/python dobby-bot.py
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target
```
