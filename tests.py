from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

import intents_scenarios
from bot import Bot
from ticket_painter import get_ticket


def isolate_bd(test_func):
    def wrapper(*arqs, **kwargs):
        with db_session():
            test_func(*arqs, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'message':
                       {'date': 1601658838,
                        'from_id': 179096999,
                        'id': 190, 'out': 0,
                        'peer_id': 179096999,
                        'text': 'test',
                        'conversation_message_id': 190,
                        'fwd_messages': [],
                        'important': False,
                        'random_id': 0,
                        'attachments': [],
                        'is_hidden': False},
                   'client_info':
                       {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link'],
                        'keyboard': True,
                        'inline_keyboard': True,
                        'carousel': False,
                        'lang_id': 0}
                   },
        'group_id': 198864592,
        'event_id': 'e92108559b255648c097a2fd71e1a16e8b876034'
    }

    def test_run(self):
        count = 5
        events = [{}] * count
        long_poll_mock = Mock(return_value=events)
        long_poll_listen_mock = Mock()
        long_poll_listen_mock.listen = long_poll_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poll_listen_mock):
                bot = Bot('', '')
                bot.event_handling = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.event_handling.assert_called()
                bot.event_handling.assert_any_call({})
                assert bot.event_handling.call_count == count

    INPUTS = [
        'Привет',
        'А когда?',
        'Где будет конференция?',
        'Зарегистрируй меня',
        'Игорь',
        'мой адрес email@email',
        'email@email.ru',
    ]
    EXPECTED_OUTPUTS = [
        intents_scenarios.DEFAULT_ANSWER,
        intents_scenarios.INTENTS[0]['answer'],
        intents_scenarios.INTENTS[1]['answer'],
        intents_scenarios.SCENARIOS['registration']['steps']['step1']['text'],
        intents_scenarios.SCENARIOS['registration']['steps']['step2']['text'],
        intents_scenarios.SCENARIOS['registration']['steps']['step2']['failure_text'],
        intents_scenarios.SCENARIOS['registration']['steps']['step3']['text'].format(name='Игорь', email='email@email.ru')
    ]

    @isolate_bd
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))
        long_poll_mock = Mock()
        long_poll_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poll_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()
        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_get_ticket(self):
        ticket_file = get_ticket('Oleg', 'oleg@gmail.com')
        with open('files/ticket_example.png', 'rb') as expected_picture:
            ticket_bytes = expected_picture.read()

        assert ticket_file.read() == ticket_bytes