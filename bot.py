#!/user/bin/env python3

import logging
import logging.config
import random

import requests
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import handlers
from intents_scenarios import SCENARIOS, INTENTS, DEFAULT_ANSWER
from logger_settings import get_logger
from models import UserState, Registration

try:
    from settings import _TOKEN, GROUP_ID
except ImportError:
    exit('Do cp settings.py.default settings.py and set token')


class Bot:
    """
    Сценарий регистрации на конференцию "My conference" через vk.com.
    Use python3.7

    Поддерживает ответы на вопросы про дату, место проведения и сценарий регистрации:
    - спрашиваем имя;
    - спрашиваем email;
    - говорим об успешной регистрации
    Если шаг не пройден, задаем уточняющий вопрос, пока шаг не будет пройден.
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из vk.com.
        :param token: секретный токен.
        """
        self.group_id = group_id
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.long_poll = VkBotLongPoll(vk=self.vk_session, group_id=self.group_id)
        self.api = self.vk_session.get_api()
        self.bot_log = logging.getLogger(__name__)

    def run(self):
        """
        Запускает бота.
        """
        for event in self.long_poll.listen():
            try:
                self.event_handling(event)
            except Exception:
                self.bot_log.exception('ошибка в обработке события')

    @db_session
    def event_handling(self, event):
        """
        Отправляет сообщение назад, если оно имеет текстовый формат.
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            self.bot_log.info(f'Мы пока не умеем обрабатывать событие такого типа - {event.type}')
            return

        user_id = event.message.peer_id
        text = event.message.text
        state = UserState.get(user_id=str(user_id))

        if state is not None:
            self.continue_scenario(text=text, state=state, user_id=user_id)
        else:
            # search intent
            for intent in INTENTS:
                self.bot_log.debug(f'Пользователь получил {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(text_to_send=intent['answer'], user_id=user_id)
                    else:
                        self.start_scenario(user_id=user_id, scenario_name=intent['scenario'], text=text)
                    break
            else:
                self.send_text(text_to_send=DEFAULT_ANSWER, user_id=user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            peer_id=user_id,
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20))

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = \
            requests.post(url=upload_url, files={'photo': ('ticket_to_the_conferense.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            peer_id=user_id,
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20))

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(text_to_send=step['text'].format(**context), user_id=user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step=step, user_id=user_id, text=text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            self.send_step(step=next_step, user_id=user_id, text=text, context=state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                self.bot_log.info('Зарегистрирован: {name}  {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send=text_to_send, user_id=user_id)


if __name__ == '__main__':

    get_logger(log_level='ERROR')
    vk_bot = Bot(group_id=GROUP_ID, token=_TOKEN)
    try:
        vk_bot.run()
    except Exception as exc:
        print(exc)
