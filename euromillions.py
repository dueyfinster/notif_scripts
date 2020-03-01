#!/usr/bin/env python3
"""
euromillions.py by Neil Grogan, 2020

A script to email you when the Euromillions lottery is over a threshold
"""
import logging
from logging.config import fileConfig
import sys
import configparser
from pathlib import Path
from urllib import request
import re
import datetime
import calendar
import smtplib
from email.mime.text import MIMEText

file_name = Path(__file__).stem
config_path = str(Path(file_name + ".ini").resolve())
fileConfig(config_path, defaults={'logfilename': Path(file_name + ".log").resolve() })
log = logging.getLogger(__name__)


def config(dic='DEFAULT'):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config[dic]

def get_html(url, user_agent):
    """
    Get raw HTML from a webpage URL
    """
    log.debug('Getting HTML from {url} with UA as {ua}'.format(url=url, ua=user_agent))
    req = request.Request(url, data=None, headers={ 'User-Agent': user_agent})
    html = request.urlopen(req).read().decode('utf-8').strip()
    log.debug('Retrieved HTML from {url} as {html}'.format(url=url, html=html))
    return html

def get_jackpot_value(html, regex):
    """
    Use regex to extract jackpotvalue from HTML
    """
    log.debug('Getting Jackpot value from HTML using regex: '.format(regex=regex))
    jackpot_value = re.search(regex, html).group(1)
    log.debug('Jackpot value retrieved from HTML: {jv}'.format(jv=jackpot_value))
    return jackpot_value

def jackpot_playable(jackpot_limit, jackpot_value):
    """
    If jackpot is above or equal to our limit we can play
    """
    num_jack = int(jackpot_value.replace(',',''))
    if num_jack >= jackpot_limit:
        log.info("Play the Euromillions! It's " + jackpot_value + "!")
        return True
    else:
        log.info("No point playing Euromillions, it's only " + jackpot_value)
        return False

def correct_weekday():
    """
    Checks if today is a Tuesday or Friday (as these are draw days)
    """
    num_wd = datetime.datetime.today().weekday()
    if num_wd == 1 or num_wd == 4:
        log.debug("Today is a draw day!")
        return True
    else:
        log.debug("Not a draw day - it's " + calendar.day_name[num_wd] + "!")
        return False

def get_smtp_config():
    cf = config('SMTP')
    return  cf.get("host"), \
            cf.get("port"), \
            cf.get("username"), \
            cf.get("password"), \
            cf.get("from"), \
            cf.get("to")


def send_email(num_jack):
    """
    Sends email notification
    """
    host, port, user, passw, fro, to = get_smtp_config()

    title = 'Euromillions is ready to play!'
    msg_content = '<h2>{title} </h2> <font color="green">PLAY OK!</font></h2>\n'.format(title=title)
    message = MIMEText(msg_content, 'html')

    message['From'] = 'Euromillions ' + fro
    message['To'] = 'Euromillions ' + to
    message['Subject'] = 'Euromillions Jackpot is €{num_jack}'.format(num_jack=num_jack)

    msg_full = message.as_string()

    server = smtplib.SMTP_SSL('{host}:{port}'.format(host=host, port=port))
    server.login(user, passw)
    server.sendmail(fro, [to], msg_full)
    server.quit()

def main():
    conf = config()

    url = conf.get('url')
    user_agent = conf.get('useragent')
    html = get_html(url, user_agent)

    regex = conf.get('regex')
    jackpot_value = get_jackpot_value(html, regex)

    jackpot_limit = conf.getint('limit')
    if jackpot_playable(jackpot_limit, jackpot_value) and correct_weekday():
        send_email(jackpot_value)

    

if __name__ == '__main__':
    main()
