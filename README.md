# dobby18bot
telegram bot for dobby's learning

## Assumption
- User: `pi`
- virtualenv: `/home/pi/dobby-bot/venv/bin/python`
- python script to launch: `/home/pi/dobby-bot/dobby-bot.py`

## Create the service script
location: /etc/systemd/system/multi-user.target.wants/dobby-bot.service
```
[Unit]
Description=Telegram Bot Daemon for Dobby
After=network.target sshd.service

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/dobby-bot
ExecStart=/home/pi/dobby-bot/venv/bin/python dobby-bot.py
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```
## Enable the service
```sudo systemctl enable dobby-bot.service```

## Reload and start
```
sudo systemctl daemon-reload
sudo systemctl restart service.service
```
