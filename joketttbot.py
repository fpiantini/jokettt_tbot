#!/usr/bin/env python3
#
from argparse import ArgumentParser

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, BaseFilter
import logging

from jokettt.board import Board
from jokettt.consoleplayer import ConsolePlayer
from jokettt.minimaxplayer import MinimaxPlayer
from jokettt.learnerplayer import LearnerPlayer

AI_PIECE = 'x'
HUMAN_PIECE = 'o'
ALPHA_VALUE = 0.1

# -----------------------------------------------------------------------
class MoveFilter(BaseFilter):
    def filter(self, message):
        b = Board('x', 'o')
        return b.is_valid_move(message.text)

# -----------------------------------------------------------------------
def newgame(update, context):
    chat_id = update.message.chat_id
    print("newgame() called. chat_id = ", chat_id, ", effective_chat_id = ", update.effective_chat.id)
    context.bot.send_message(chat_id, 'hello world!')

# -----------------------------------------------------------------------
def getmove(update, context):
    chat_id = update.message.chat_id
    print("getmove() called. chat_id = ", chat_id, ", effective_chat_id = ", update.effective_chat.id)
    context.bot.send_message(chat_id, 'I got the move: ' + update.message.text)

# -----------------------------------------------------------------------
def illegaltext(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, 'I cannot understand the text: ' + update.message.text)

# -----------------------------------------------------------------------
def main():

    # --------------------------------------------------
    # 1. PARSE COMMAND LINE ARGUMENTS
    parser = ArgumentParser()
    parser.add_argument("telegram_api_key", help="telegram HTTP API token")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(args.telegram_api_key, use_context=True)
    move_filter = MoveFilter()
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('g', newgame))
    dispatcher.add_handler(MessageHandler(move_filter, getmove))
    dispatcher.add_handler(MessageHandler(Filters.text, illegaltext))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

