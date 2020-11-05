#!/usr/bin/env python3

"""
Handler - функция, которая принимает на вход text (текстовое сообщение) и content (dict), а возвращает bool:
True если шаг пройден, False если данные введены некорректно.
"""

import re

from ticket_painter import get_ticket

re_name = re.compile(r'^[\w\-\s]{3,30}$')
re_email = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def get_ticket_handler(text, context):
    return get_ticket(name=context['name'], email=context['email'])
