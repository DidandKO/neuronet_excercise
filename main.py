from __future__ import annotations
from abc import ABC, abstractmethod


class Context:
    _state = None
    _user_id = None

    def __init__(self, state: State) -> None:
        self.set_state(state)

    def set_state(self, state: State):
        print(f"Context: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def get_state(self):
        return self._state

    def set_user_id(self, user_id):
        print(f'Общение с пользоваетелем {user_id}')
        self._user_id = user_id

    def send_message(self, text_message):
        self._state.send_message(text_message, self._user_id)

    def choose_message(self, user_message):
        return self._state.choose_message(user_message)


class State(ABC):
    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def send_message(self, text_message, user_id) -> None:
        pass

    @abstractmethod
    def choose_message(self, user_message) -> str:
        pass


class HelloLogicState(State):

    ignore_counter = 0

    messages = {
        'hello': '{name}, добрый день!'
                 ' Вас беспокоит компания {company_name},'
                 ' мы проводим опрос удовлетворенности нашими услугами.'
                 '  Подскажите, вам удобно сейчас говорить?',
        'hello_repeat': 'Это компания {company_name}'
                        '  Подскажите, вам удобно сейчас говорить?',
        'hello_null': 'Извините, вас не слышно. Вы могли бы повторить'
    }

    def send_message(self, text_message, user_id) -> None:
        if text_message in self.messages:
            print(f"!SENDING \"{self.messages[text_message]}\" to {user_id}")
            self.context.set_state(self)
        elif text_message == 'recommend_main':
            self.context.set_state(MainLogicState())
            self.context.send_message(text_message)
        elif text_message in ['hangup_wrong_time', 'hangup_null']:
            self.context.set_state(HangupLogicState())
            self.context.send_message(text_message)
        else:
            raise Exception(f'No State for case {text_message}')

    def choose_message(self, user_message) -> str:
        chosen_message_id = None
        if user_message:
            if user_message in ['DEFAULT', 'Да']:
                chosen_message_id = 'recommend_main'
            elif user_message in ['Нет', 'Занят']:
                chosen_message_id = 'hangup_wrong_time'
            elif user_message == 'Еще раз':
                chosen_message_id = 'hello_repeat'
            else:
                chosen_message_id = 'hello_null'
        else:
            self.ignore_counter += 1
            if self.ignore_counter > 1:
                chosen_message_id = 'hangup_null'
            else:
                chosen_message_id = 'hello_null'

        return chosen_message_id


class MainLogicState(State):

    ignore_counter = 0

    messages = {
        'recommend_main': 'Скажите, а готовы ли вы рекомендовать нашу компанию своим друзьям?'
                          ' Оцените, пожалуйста, по шкале от «0» до «10», где «0» - не буду рекомендовать,'
                          ' «10» - обязательно порекомендую.',
        'recommend_repeat': 'Как бы вы оценили возможность порекомендовать нашу компанию своим знакомым'
                            ' по шкале от 0 до 10, где 0 - точно не порекомендую, 10 - обязательно порекомендую.',
        'recommend_repeat_2': 'Ну если бы вас попросили порекомендовать нашу компанию друзьям или знакомым,'
                              ' вы бы стали это делать? Если «да» - то оценка «10», если точно нет – «0».',
        'recommend_score_negative': 'Ну а от 0 до 10 как бы вы оценили бы: 0, 5 или может 7 ?',
        'recommend_score_neutral': 'Ну а от 0 до 10 как бы вы оценили ?',
        'recommend_score_positive': 'Хорошо,  а по 10-ти бальной шкале как бы вы оценили 8-9 или может 10  ?',
        'recommend_null': 'Извините вас свосем не слышно,  повторите пожалуйста ?',
        'recommend_default': 'повторите пожалуйста ',
    }

    def send_message(self, text_message, user_id) -> None:
        if text_message in self.messages:
            print(f"!SENDING \"{self.messages[text_message]}\" to {user_id}")
            self.context.set_state(self)
        elif text_message in ['hangup_wrong_time', 'hangup_positive', 'hangup_negative', 'hangup_null']:
            self.context.set_state(HangupLogicState())
            self.context.send_message(text_message)
        elif text_message == 'forward':
            self.context.set_state(ForwardLogicState())
            self.context.send_message(text_message)
        else:
            raise Exception(f'No State for case {text_message}')

    def choose_message(self, user_message) -> str:
        chosen_message_id = None
        if user_message:
            if user_message == 'DEFAULT':
                chosen_message_id = 'recommend_default'
            elif user_message in ['1', '2', '3', '4', '5', '6', '7', '8']:
                chosen_message_id = 'hangup_negative'
            elif user_message in ['9', '10']:
                chosen_message_id = 'hangup_positive'
            elif user_message == 'Нет':
                chosen_message_id = 'recommend_score_negative'
            elif user_message == 'Возможно':
                chosen_message_id = 'recommend_score_neutral'
            elif user_message == 'Да':
                chosen_message_id = 'recommend_score_positive'
            elif user_message == 'Еще раз':
                chosen_message_id = 'recommend_repeat'
            elif user_message == 'Не знаю':
                chosen_message_id = 'recommend_repeat_2'
            elif user_message == 'Занят':
                chosen_message_id = 'hangup_wrong_time'
            else:
                chosen_message_id = 'forward'
        else:
            self.ignore_counter += 1
            if self.ignore_counter > 1:
                chosen_message_id = 'hangup_null'
            else:
                chosen_message_id = 'recommend_null'
        return chosen_message_id


class HangupLogicState(State):
    messages = {
        'hangup_positive': 'Отлично!  Большое спасибо за уделенное время! Всего вам доброго!',
        'hangup_negative': 'Я вас понял. В любом случае большое спасибо за уделенное время!  Всего вам доброго. ',
        'hangup_wrong_time': 'Извините пожалуйста за беспокойство. Всего вам доброго',
        'hangup_null': 'Вас все равно не слышно, будет лучше если я перезвоню. Всего вам доброго'
    }

    def send_message(self, text_message, user_id) -> None:
        if text_message in self.messages:
            print(f"!SENDING \"{self.messages[text_message]}\" to {user_id}")
            self.context.set_state(ForwardLogicState())

    def choose_message(self, user_message) -> str:
        pass


class ForwardLogicState(State):
    messages = {
        'forward': 'Чтобы разобраться в вашем вопросе, я переключу звонок на моих коллег.'
                   ' Пожалуйста оставайтесь на линии.'
    }

    def send_message(self, text_message, user_id) -> None:
        if text_message in self.messages:
            print(f"!SENDING \"{self.messages[text_message]}\" to {user_id}")
        self.context.set_state(FinalState())

    def choose_message(self, user_message) -> str:
        if '?' in user_message:
            return 'forward'


class FinalState(State):

    def send_message(self, text_message, user_id) -> None:
        pass

    def choose_message(self, user_message) -> str:
        pass


if __name__ == '__main__':
    app = Context(HelloLogicState())
    app.set_user_id('123')
    app.send_message('hello')
    while type(app.get_state()).__name__ != 'FinalState':
        client_message = input('Сообщение пользователя: ')
        message = app.choose_message(client_message)
        app.send_message(message)
