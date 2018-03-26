#coding: utf-8

import smtplib
from email.mime.text import MIMEText

import config

message_greetings = u"""
I found {} new flats!

"""

message_flat = u"""
Address: {addr}
Kiez: {kiez}

Cold rent: €{kalt}
Warm rent: €{total}

Size: {sqm} m²

Link: {link}
"""

section = u"""
===
"""


def create_email_body(flats):
    flatmsgs = section.join([message_flat.format(**a) for a in flats])
    msg = message_greetings.format(len(flats)) + section + flatmsgs
    return msg


def create_email(flats):
    msg = MIMEText(create_email_body(flats))

    msg['Subject'] = "Found {} new flats".format(len(flats))
    msg["From"] = config.email_from
    msg["To"] = config.email_to

def send_email(flats):
    msg = create_email(flats)
    s = smtplib.SMTP(config.smtp_server)
    s.sendmail(config.email_from, config.email_to, msg.as_string())
    s.quit()
