import signal
from bot import Bot
import os
import sys


def main():
    bot = Bot(os.environ.get('TELEGRAM_TOKEN'))
    bot.define_reactions()


if __name__ == '__main__':
    main()
