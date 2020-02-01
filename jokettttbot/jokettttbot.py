#!/usr/bin/env python3
#
from argparse import ArgumentParser
import gettext
import os

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
board = Board('x', 'o')
ai_player = MinimaxPlayer(AI_PIECE, False)

ldir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
lang_it = gettext.translation('messages', ldir, languages=['it_IT'], fallback=True)
_T = lang_it.gettext

# -----------------------------------------------------------------------
class MoveFilter(BaseFilter):
    def filter(self, message):
        return board.is_valid_move(message.text)

# -----------------------------------------------------------------------
def print_bot_info(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, "<b>" + _T("jokettt telegram bot") + "</b>\n" +
                             _T("A telegram bot that plays Tic-tac-toe"), parse_mode='HTML')

# -----------------------------------------------------------------------
def print_bot_help(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id,
                             "<b>" + _T("Commands") + "</b>\n" +
                             _T("/? - Print help informations") + "\n" +
                             _T("/info - Print program informations") + "\n" +
                             _T("/n - Start a new game") + "\n" +
                             "<b>" + _T("How to play") + "</b>\n" +
                             _T("When its your turn, enter the move with the format:") + "\n" +
                             "<b>" + _T("[R][C]") + "</b>\n" +
                             _T("where [R] is the row where to place the pawn, and [C] is the column") + "\n" +
                             _T("Rows are A, B and C starting from top, and columns are 1, 2 and 3 starting from left.") + "\n" +
                             _T("For example, enter 'A1' to place a pawn on upper left corner.") + "\n" +
                             _T("After your move, I will do my move, and the board status will be printed.") + "\n" +
                             _T("If the game is ended the result is printed"),
                             parse_mode='HTML')

# -----------------------------------------------------------------------
def newgame(update, context):
    chat_id = update.message.chat_id
    print("newgame() called. chat_id = ", chat_id, ", effective_chat_id = ", update.effective_chat.id)
    board.reset()
    context.bot.send_message(chat_id, _T("--- New game. Awaiting you move ---"))
    print_board(board, chat_id, context.bot)

# -----------------------------------------------------------------------
def getmove(update, context):
    chat_id = update.message.chat_id
    print("getmove() called. chat_id = ", chat_id, ", effective_chat_id = ", update.effective_chat.id)
    context.bot.send_message(chat_id, _T("your move: ") + update.message.text.upper())
    _x, _y = board.convert_movestring_to_indexes(update.message.text)
    _, _res = board.place_pawn(_x, _y, HUMAN_PIECE)
    end_of_game = check_end_of_game(_res, board)
    if end_of_game:
        # if game terminated print board and result
        print_board(board, chat_id, context.bot)
        print_result(_res, chat_id, context.bot)
    else:
        # if game is not terminated, do an AI move
        _res = do_ai_move(board, AI_PIECE, chat_id, context.bot)
        print_board(board, chat_id, context.bot)
        end_of_game = check_end_of_game(_res, board)
        if end_of_game:
            # if game terminated print result
            print_result(_res, chat_id, context.bot)

# -----------------------------------------------------------------------
def illegaltext(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, _T("I cannot understand the text: ") + update.message.text)


# -----------------------------------------------------------------------
def do_ai_move(brd, ai_piece, c_id, bot):
    _x, _y = ai_player.move(brd)
    _, _res = brd.place_pawn(_x, _y, ai_piece)
    bot.send_message(c_id, _T("my move: ") + brd.convert_move_to_movestring([_x, _y]))
    return -_res;

# -----------------------------------------------------------------------
def check_end_of_game(res, board):
    if res != 0 or board.is_full():
        return True
    return False

# -----------------------------------------------------------------------
def print_result(res, c_id, bot):
    if res < 0:
        msg = _T("You lose! :-D")
    elif res > 0:
        msg = _T("You win!! :-(")
    else:
        msg = _T("Draw! ;-)")
    bot.send_message(c_id, msg)

# -----------------------------------------------------------------------
def print_board(brd, c_id, bot):
    bot.send_message(c_id, "```\n" + str(brd) + "```", parse_mode='Markdown')

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
    dispatcher.add_handler(CommandHandler('info', print_bot_info))
    dispatcher.add_handler(CommandHandler('help', print_bot_help))
    dispatcher.add_handler(CommandHandler('aiuto', print_bot_help))
    dispatcher.add_handler(CommandHandler('n', newgame))
    dispatcher.add_handler(MessageHandler(move_filter, getmove))
    dispatcher.add_handler(MessageHandler(Filters.text, illegaltext))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

