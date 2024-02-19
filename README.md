A simple bot that sends new published houses in Holland2Stay to Telegram groups.

## Installation:
```bash
git clone https://github.com/JafarAkhondali/Holland2StayNotifier.git
cd Holland2StayNotifier/h2snotifier
python3 -m venv venv
source venv/bin/activate

cp config_example.json config.json 
cp env_example .env 
# Update config.json and .env with you desired chat group and telegram bot

pip install -r requirements.txt

# Test one-time
python main.py
```

## Demo:
Simply join the Telegram group, the bot posts new houses(Direct links removed to prevent spammer):    
The Hague, Amsterdam, Rotterdam, Zoetermeer, Capelle -> @h2notify    
Eindhoven, Helmond, Den Bosch, Tilberg -> @h2snotify_eindhoven    
Arnhem, Nijmegen  -> @h2snotify_arnhem   

## Usage:
Add a cron job to frequently run the project. Example:
```bash
crontab -e
*/5 * * * * cd /home/jef/projects/Holland2StayNotifier/h2snotifier/ && bash ./run.sh
```


## Contributors
[MHMALEK](https://github.com/MHMALEK)
