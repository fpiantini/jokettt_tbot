#!/usr/bin/env python3
#
from argparse import ArgumentParser
import gettext
import os

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

from jokettt.board import Board
from jokettt.consoleplayer import ConsolePlayer
from jokettt.minimaxplayer import MinimaxPlayer
from jokettt.learnerplayer import LearnerPlayer

AI_PIECE = 'x'
HUMAN_PIECE = 'o'
ALPHA_VALUE = 0.1
DEFAULT_LANG = 'it_IT'

###ldir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
###lang_it = gettext.translation('messages', ldir, languages=['it_IT'], fallback=True)
###_T = lang_it.gettext

# ********************************************************************************
# COMMAND HANDLERS
# ********************************************************************************
# -----------------------------------------------------------------------
def print_bot_info(update, context):
    check_userdata(context)
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id,
         "<b>" + context.user_data['lang'].gettext("jokettt telegram bot") + "</b>\n" +
         context.user_data['lang'].gettext("A telegram bot that plays Tic-tac-toe"), parse_mode='HTML')

# -----------------------------------------------------------------------
def print_bot_help(update, context):
    check_userdata(context)
    chat_id = update.message.chat_id
    print_bot_info(update, context)
    context.bot.send_message(chat_id,
         "<b>" + context.user_data['lang'].gettext("Commands") + "</b>\n" +
         context.user_data['lang'].gettext("/help - Print help informations") + "\n" +
         context.user_data['lang'].gettext("/info - Print program informations") + "\n" +
         context.user_data['lang'].gettext("/n - Start a new game") + "\n" +
         "<b>" + context.user_data['lang'].gettext("How to play") + "</b>\n" +
         context.user_data['lang'].gettext("When its your turn, enter the move with the format:") + "\n" +
         "<b>" + context.user_data['lang'].gettext("[R][C]") + "</b>\n" +
         context.user_data['lang'].gettext("where [R] is the row where to place the pawn, and [C] is the column") + "\n" +
         context.user_data['lang'].gettext("Rows are A, B and C starting from top, and columns are 1, 2 and 3 starting from left.") + "\n" +
         context.user_data['lang'].gettext("For example, enter 'A1' to place a pawn on upper left corner.") + "\n" +
         context.user_data['lang'].gettext("After your move, I will do my move, and the board status will be printed.") + "\n" +
         context.user_data['lang'].gettext("If the game is ended the result is printed"),
         parse_mode='HTML')

# -----------------------------------------------------------------------
def newgame(update, context):
    check_userdata(context)
    c_id = update.message.chat_id
    logging.info(f'newgame() called. chat_id = {c_id}')
    context.user_data['board'].reset()
    context.bot.send_message(c_id, context.user_data['lang'].gettext("--- New game. Awaiting you move ---"))
    print_user_board(context, c_id)

# -----------------------------------------------------------------------
def firstmove_to_ai(update, context):
    check_userdata(context)
    c_id = update.message.chat_id
    if context.user_data['board'].is_empty():
        context.bot.send_message(c_id, context.user_data['lang'].gettext("Ok, I move"))
        _ = do_ai_move(context, c_id, AI_PIECE)
        print_user_board(context, c_id)
        context.bot.send_message(c_id, context.user_data['lang'].gettext("Your move..."))
    else:
        context.bot.send_message(c_id,
            context.user_data['lang'].gettext("Game already started, cannot change order of players"))

# -----------------------------------------------------------------------
def print_status(update, context):
    check_userdata(context)
    print_user_board(context, update.message.chat_id)

# -----------------------------------------------------------------------
def lang_setitalian(update, context):
    set_lang_for_user(context, 'it_IT')

# -----------------------------------------------------------------------
def lang_setenglish(update, context):
    set_lang_for_user(context, 'en_US')


# ********************************************************************************
# MESSAGE HANDLERS
# ********************************************************************************

# -----------------------------------------------------------------------
def parse_message(update, context):
    check_userdata(context)
    if context.user_data['board'].is_valid_move(update.message.text):
        parse_move_message(update, context)
    else:
        parse_nomove_message(update, context)

# -----------------------------------------------------------------------
def parse_move_message(update, context):
    c_id = update.message.chat_id
    logging.info(f'parse_move_message() called. chat_id {c_id}')
    context.bot.send_message(c_id, context.user_data['lang'].gettext("Your move: ") + update.message.text.upper())
    _x, _y = context.user_data['board'].convert_movestring_to_indexes(update.message.text)
    _, _res = context.user_data['board'].place_pawn(_x, _y, HUMAN_PIECE)
    end_of_game = check_end_of_game(_res, context.user_data['board'])

    if not end_of_game:
        # if game is not terminated, do an AI move
        _res = do_ai_move(context, c_id, AI_PIECE)
        print_user_board(context, c_id)
        end_of_game = check_end_of_game(_res, context.user_data['board'])
    else:
        print_user_board(context, c_id)

    if end_of_game:
        # if game terminated print result and start a new one
        print_result(context, c_id, _res)
        newgame(update, context)
    else:
        context.bot.send_message(c_id, context.user_data['lang'].gettext("Your move..."))

# -----------------------------------------------------------------------
def parse_nomove_message(update, context):
    c_id = update.message.chat_id
    context.bot.send_message(c_id,
            context.user_data['lang'].gettext("Invalid move: ") +
            update.message.text)

# ********************************************************************************
# UTILITIES
# ********************************************************************************

# -----------------------------------------------------------------------
def do_ai_move(ctx, c_id, ai_piece):
    _x, _y = ctx.user_data['ai'].move(ctx.user_data['board'])
    _, _res = ctx.user_data['board'].place_pawn(_x, _y, ai_piece)
    ctx.bot.send_message(c_id, ctx.user_data['lang'].gettext("My move: ") +
                         ctx.user_data['board'].convert_move_to_movestring([_x, _y]))
    return -_res;

# -----------------------------------------------------------------------
def print_result(ctx, c_id, res):
    if res < 0:
        msg = ctx.user_data['lang'].gettext("You lose! :-D")
    elif res > 0:
        msg = ctx.user_data['lang'].gettext("You win!! :-(")
    else:
        msg = ctx.user_data['lang'].gettext("Draw! ;-)")
    ctx.bot.send_message(c_id, msg)

# -----------------------------------------------------------------------
def print_user_board(ctx, c_id):
    ctx.bot.send_message(c_id, "```\n" +
                         str(ctx.user_data['board']) + "```",
                         parse_mode='Markdown')

# -----------------------------------------------------------------------
def check_end_of_game(res, brd):
    if res != 0 or brd.is_full():
        return True
    return False

# -----------------------------------------------------------------------
def check_userdata(ctx):
    if 'board' not in ctx.user_data:
        # no board... this means that this
        # is the first time we see this user
        logging.info(f'initializing new user. chat_id = {c_id}')
        create_board_for_user(ctx)
        create_ai_for_user(ctx)
        set_lang_for_user(ctx, DEFAULT_LANG)


# -----------------------------------------------------------------------
def create_board_for_user(ctx):
    ctx.user_data['board'] = Board('x', 'o')

# -----------------------------------------------------------------------
def create_ai_for_user(ctx):
    ctx.user_data['ai'] = MinimaxPlayer(AI_PIECE, False)

# -----------------------------------------------------------------------
def set_lang_for_user(ctx, lng_str):
    ldir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    lng = gettext.translation('messages', ldir, languages=[lng_str], fallback=True)
    ctx.user_data['lang'] = lng

# ********************************************************************************
# MAIN
# ********************************************************************************

def main():

    # --------------------------------------------------
    # 1. PARSE COMMAND LINE ARGUMENTS
    parser = ArgumentParser()
    parser.add_argument("telegram_api_key", help="telegram HTTP API token")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(args.telegram_api_key, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('info', print_bot_info))
    dispatcher.add_handler(CommandHandler('start', print_bot_help))
    dispatcher.add_handler(CommandHandler('help', print_bot_help))
    dispatcher.add_handler(CommandHandler('n', newgame))
    dispatcher.add_handler(CommandHandler('move', firstmove_to_ai))
    dispatcher.add_handler(CommandHandler('p', print_status))
    dispatcher.add_handler(CommandHandler('en', lang_setenglish))
    dispatcher.add_handler(CommandHandler('it', lang_setitalian))

    dispatcher.add_handler(MessageHandler(Filters.text, parse_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

