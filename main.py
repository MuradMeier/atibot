import logging
from modules import bot
assert bot


logging.basicConfig(level=logging.INFO,
                    # filemode='w',
                    # filename='scrapper.log'
                    )


if __name__ == '__main__':
    bot.run()
