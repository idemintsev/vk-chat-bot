INTENTS = [
    {
        "name": "Дата проведения",
        "tokens": ("когда", "сколько", "дата", "дату"),
        "scenario": None,
        "answer": "Конференция проводится 1 января, регистрация начнется в 7.00"
    },
    {
        "name": "Место проведения",
        "tokens": ("где", "мест", "локация", "адрес", "метро"),
        "scenario": None,
        "answer": "Конференция пройдет в нашем офисе."
    },
    {
        "name": "Регистрация",
        "tokens": ("регистр", "добав"),
        "scenario": "registration",
        "answer": None
    }
]

SCENARIOS = {
    "registration": {
        "first_step": "step1",
        "steps": {
            "step1": {
                "text": "Чтобы зарегистрироваться, введите ваше имя.",
                "failure_text": "Имя должно состоять из 3-30 букв и может иметь дефис. Попробуйте еще раз",
                "handler": "handle_name",
                "next_step": "step2"
            },
            "step2": {
                "text": "Введите email. Мы отправим на него все данные.",
                "failure_text": "В адресе почты ошибка. Попробуйте еще раз",
                "handler": "handle_email",
                "next_step": "step3"
            },
            "step3": {
                "text": "Спасибо за регистрацию! {name}, вы успешно зарегистрированы. "
                        "Ваш билет ниже. Копия отправлена на {email}.",
                "image": "get_ticket_handler",
                "failure_text": None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

DEFAULT_ANSWER = "Привет!" \
                 "Не знаю как на это ответить." \
                 "Я могу рассказать когда и где пройдет конференция, а также зарегистрировать вас."
