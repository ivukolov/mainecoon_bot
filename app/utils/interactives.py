from aiogram.types import Poll, PollOption

class PollMaker:
    def __init__(self, poll_option_text):
        self.poll_option_text = poll_option_text

    def make_poll_options_list(self):
        return self.poll_option_text.split(",")

    def make_poll_options(self) ->list[list[PollOption]]:
        poll_options_list = self.make_poll_options_list()
        options = [
            [
                PollOption(text=option, voter_count=0),
            ]
                for option in poll_options_list
        ]
        return options

    def create_poll(self) -> Poll:
        options = self.make_poll_options()
        return Poll(
            id="1",  # Уникальный ID голосования
            question="Какой вариант вам нравится больше?",
            options=options,
            is_closed=False,
            is_anonymous=True,  # Анонимное голосование
            type="regular",  # Тип голосования
            allows_multiple_answers=False,  # Разрешить выбор нескольких вариантов
            correct_option_id=None,  # ID правильного ответа (для викторин)
            explanation=None,  # Объяснение для викторин
            open_period=None,  # Время в секундах, после которого голосование закроется
            close_date=None,  # Дата закрытия голосования
        )