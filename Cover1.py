import logging
import os

import music_tag
from orator import Model
from telegram.error import TelegramError
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, \
     Defaults, PicklePersistence
from telegram import Update, ReplyKeyboardMarkup, ChatAction, ParseMode, ReplyKeyboardRemove
from telegram import (
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
)

import moviepy
import moviepy.editor 

import localization as lp
from utils.init1 import translate_key_to, reset_user_data_context, generate_start_over_keyboard, \
create_user_directory, download_file, increment_usage_counter_for_user, delete_file, \
generate_module_selector_keyboard, generate_module_selector_video_keyboard, generate_tag_editor_keyboard, \
generate_music_info, generate_tag_editor_video_keyboard, save_tags_to_file, convert_video

from models.admin import Admin
from models.user import User
from dbConfig import db

Model.set_connection_resolver(db)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

logger = logging.getLogger()

def command_start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username

    reset_user_data_context(context)

    user = User.where('user_id', '=', user_id).first()

    update.message.reply_text(
        translate_key_to(lp.START_MESSAGE, context.user_data['language']),
        reply_markup=ReplyKeyboardRemove()
    )

    show_language_keyboard(update, context)

    if not user:
        new_user = User()
        new_user.user_id = user_id
        new_user.username = username
        new_user.number_of_files_sent = 0

        new_user.save()

        logger.info("A user with id %s has been started to use the bot.", user_id)

def start_over(update: Update, context: CallbackContext) -> None:
    reset_user_data_context(context)

    update.message.reply_text(
        translate_key_to(lp.START_OVER_MESSAGE, context.user_data['language']),
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=ReplyKeyboardRemove()
    )

def command_help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(translate_key_to(lp.HELP_MESSAGE, context.user_data['language']))

def command_about(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(translate_key_to(lp.ABOUT_MESSAGE, context.user_data['language']))

def show_language_keyboard(update: Update, _context: CallbackContext) -> None:
    language_button_keyboard = ReplyKeyboardMarkup(
        [
            ['???????? English', '???????? ??????????'],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    update.message.reply_text(
        "Please choose a language:\n\n"
        "???????? ???????? ???? ???????????? ????????:",
        reply_markup=language_button_keyboard,
    )

def set_language(update: Update, context: CallbackContext) -> None:
    lang = update.message.text.lower()
    user_data = context.user_data
    user_id = update.effective_user.id

    if "english" in lang:
        user_data['language'] = 'en'
    elif "??????????" in lang:
        user_data['language'] = 'fa'

    update.message.reply_text(translate_key_to(lp.LANGUAGE_CHANGED, user_data['language']))
    update.message.reply_text(
        translate_key_to(lp.START_OVER_MESSAGE, user_data['language']),
        reply_markup=ReplyKeyboardRemove()
    )

    user = User.where('user_id', '=', user_id).first()
    user.language = user_data['language']
    user.push()

def handle_music_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_id = update.effective_user.id
    user_data = context.user_data
    music_duration = message.audio.duration
    music_file_size = message.audio.file_size
    old_music_path = user_data['music_path']
    old_art_path = user_data['art_path']
    old_new_art_path = user_data['new_art_path']
    language = user_data['language']

    if music_duration >= 3600 and music_file_size > 48000000:
        message.reply_text(
            translate_key_to(lp.ERR_TOO_LARGE_FILE, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        return

    context.bot.send_chat_action(
        chat_id=message.chat_id,
        action=ChatAction.TYPING
    )

    try:
        create_user_directory(user_id)
    except OSError:
        message.reply_text(translate_key_to(lp.ERR_CREATING_USER_FOLDER, language))
        logger.error("Couldn't create directory for user %s", user_id, exc_info=True)
        return

    try:
        file_download_path = download_file(
            user_id=user_id,
            file_to_download=message.audio,
            file_type='audio',
            context=context
        )
    except ValueError:
        message.reply_text(
            translate_key_to(lp.ERR_ON_DOWNLOAD_AUDIO_MESSAGE, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        logger.error("Error on downloading %s's file. File type: Audio", user_id, exc_info=True)
        return

    try:
        music = music_tag.load_file(file_download_path)
    except (OSError, NotImplementedError):
        message.reply_text(
            translate_key_to(lp.ERR_ON_READING_TAGS, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        logger.error(
            "Error on reading the tags %s's file. File path: %s",
            user_id,
            file_download_path,
            exc_info=True
        )
        return

    reset_user_data_context(context)

    user_data['music_path'] = file_download_path
    user_data['art_path'] = ''
    user_data['music_message_id'] = message.message_id
    user_data['music_duration'] = message.audio.duration

    tag_editor_context = user_data['tag_editor']

    artist = music['artist']
    title = music['title']
    album = music['album']
    genre = music['genre']
    art = music['artwork']
    year = music.raw['year']
    disknumber = music.raw['disknumber']
    tracknumber = music.raw['tracknumber']

    if art:
        art_path = user_data['art_path'] = f"{file_download_path}.jpg"
        with open(art_path, 'wb') as art_file:
            art_file.write(art.first.data)

    tag_editor_context['artist'] = str(artist)
    tag_editor_context['title'] = str(title)
    tag_editor_context['album'] = str(album)
    tag_editor_context['genre'] = str(genre)
    tag_editor_context['year'] = str(year)
    tag_editor_context['disknumber'] = str(disknumber)
    tag_editor_context['tracknumber'] = str(tracknumber)

    show_module_selector(update, context)

    increment_usage_counter_for_user(user_id=user_id)

    user = User.where('user_id', '=', user_id).first()
    user.username = update.effective_user.username
    user.push()

    delete_file(old_music_path)
    delete_file(old_art_path)
    delete_file(old_new_art_path)

def handle_photo_message(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    message = update.message
    user_id = update.effective_user.id
    music_path = user_data['music_path']
    current_active_module = user_data['current_active_module']
    current_tag = user_data['tag_editor']['current_tag']
    lang = user_data['language']

    tag_editor_keyboard = generate_tag_editor_keyboard(lang)

    if music_path:
        if current_active_module == 'tag_editor':
            if not current_tag or current_tag != 'album_art':
                reply_message = translate_key_to(lp.ASK_WHICH_TAG, lang)
                message.reply_text(reply_message, reply_markup=tag_editor_keyboard)
            else:
                try:
                    file_download_path = download_file(
                        user_id=user_id,
                        file_to_download=message.photo[len(message.photo) - 1],
                        file_type='photo',
                        context=context
                    )
                    reply_message = f"{translate_key_to(lp.ALBUM_ART_CHANGED, lang)} " \
                                    f"{translate_key_to(lp.CLICK_PREVIEW_MESSAGE, lang)} " \
                                    f"{translate_key_to(lp.OR, lang).upper()} " \
                                    f"{translate_key_to(lp.CLICK_DONE_MESSAGE, lang).lower()}"
                    user_data['new_art_path'] = file_download_path
                    message.reply_text(reply_message, reply_markup=tag_editor_keyboard)
                except (ValueError, BaseException):
                    message.reply_text(translate_key_to(lp.ERR_ON_DOWNLOAD_AUDIO_MESSAGE, lang))
                    logger.error(
                        "Error on downloading %s's file. File type: Photo",
                        user_id,
                        exc_info=True
                    )
                    return
    else:
        reply_message = translate_key_to(lp.DEFAULT_MESSAGE, lang)
        message.reply_text(reply_message, reply_markup=ReplyKeyboardRemove())

def handle_video_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_id = update.effective_user.id
    user_data = context.user_data
    video_duration = message.video.duration
    video_file_size = message.video.file_size
    video_mime_type = message.video.mime_type
    old_music_path = user_data['music_path']
    old_art_path = user_data['art_path']
    old_new_art_path = user_data['new_art_path']
    language = user_data['language']

    if video_duration >= 3600 and video_file_size > 48000000:
        message.reply_text(
            translate_key_to(lp.ERR_TOO_LARGE_FILE, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        return

    context.bot.send_chat_action(
        chat_id=message.chat_id,
        action=ChatAction.TYPING
    )

    try:
        create_user_directory(user_id)
    except OSError:
        message.reply_text(translate_key_to(lp.ERR_CREATING_USER_FOLDER, language))
        logger.error("Couldn't create directory for user %s", user_id, exc_info=True)
        return

    try:
        file_download_path = download_file(
            user_id=user_id,
            file_to_download=message.video,
            file_type='video',
            context=context
        )
    except ValueError:
        message.reply_text(
            translate_key_to(lp.ERR_ON_DOWNLOAD_VIDEO_MESSAGE, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        logger.error("Error on downloading %s's file. File type: Video", user_id, exc_info=True)
        return

    try:
        video = file_download_path
    except (OSError, NotImplementedError):
        message.reply_text(
            translate_key_to(lp.ERR_ON_READING_TAGS, language),
            reply_markup=generate_start_over_keyboard(language)
        )
        logger.error(
            "Error on reading the tags %s's file. File path: %s",
            user_id,
            file_download_path,
            exc_info=True
        )
        return

    reset_user_data_context(context)

    user_data['video_path'] = file_download_path
    user_data['video_message_id'] = message.message_id
    user_data['video_duration'] = message.video.duration
    user_data['video_mimeType'] = message.video.mime_type

    # tag_editor_context = user_data['tag_editor']

    # artist = music['artist']
    # title = music['title']
    # album = music['album']
    # genre = music['genre']
    # art = music['artwork']
    # year = music.raw['year']
    # disknumber = music.raw['disknumber']
    # tracknumber = music.raw['tracknumber']

    # if art:
    #     art_path = user_data['art_path'] = f"{file_download_path}.jpg"
    #     with open(art_path, 'wb') as art_file:
    #         art_file.write(art.first.data)

    # tag_editor_context['artist'] = str(artist)
    # tag_editor_context['title'] = str(title)
    # tag_editor_context['album'] = str(album)
    # tag_editor_context['genre'] = str(genre)
    # tag_editor_context['year'] = str(year)
    # tag_editor_context['disknumber'] = str(disknumber)
    # tag_editor_context['tracknumber'] = str(tracknumber)
    # logger.info("A user with id %s has been started to use the bot.", user_data)
    # show_module_selector(update, context)
    show_module_selector_video(update, context)

    increment_usage_counter_for_user(user_id=user_id)

    user = User.where('user_id', '=', user_id).first()
    user.username = update.effective_user.username
    user.push()

    # delete_file(old_music_path)
    # delete_file(old_art_path)
    # delete_file(old_new_art_path)

def show_module_selector_video(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    context.user_data['current_active_module'] = ''
    lang = user_data['language']

    module_selector_keyboard = generate_module_selector_video_keyboard(lang)

    update.message.reply_text(
        translate_key_to(lp.ASK_WHICH_MODULE, lang),
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=module_selector_keyboard
    )

def convert_mp4_to_webm(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_data = context.user_data
    video_path = user_data['video_path']
    lang = user_data['language']

    user_data['current_active_module'] = 'tag_editor'

    tag_editor_context = user_data['tag_editor']
    tag_editor_context['current_tag'] = ''

    tag_editor_keyboard = generate_tag_editor_video_keyboard(lang)
    chat_id = update.message.chat_id

    if video_path:
        # with open(video_path.format(chat_id, "webm"), 'rb') as video_file:
        with open(video_path, 'rb') as video_file:
            # video_file = file_name.split(".")[0]
            # logger.error(video_file)
            #   video_file = str(video_file) +'.webm'

            # context.bot.send_document(
            #     chat_id=chat_id, 
            #     document=open('./output_media/{}.{}'.format(chat_id, 'webm'), 'rb'), 
            #     caption="Here is your file!"
            # )
            # logger.info(video_file)
            # convert_video(chat_id, video_path, "webp")
            # v = moviepy.VideoFileClip(video_path)
            # v.write_videofile()

            # video = moviepy.editor.VideoFileClip(video_path)
            # audio = video.audio
            # video.write_videofile(filename + ".wav")

            # video_file = moviepy.editor.VideoFileClip(video_path)
            # wav_file_name = video_path.replace('.mp4', '.webm')  # Replace .mkv with .wav
            # video_file.write_videofile(wav_file_name)

            # context.bot.send_document(
            #     chat_id=chat_id, 
            #     document=open(video_path.format(chat_id, "webp"), 'rb'), 
            #     caption="Here is your file!"
            # )
            # context.bot.send_video(
            #     chat_id=update.message.chat_id, 
            #     video=open('output.mp4', 'rb'), 
            #     supports_streaming=True
            # )

            message.reply_video_note(
                video_note=video_file,
                reply_to_message_id=update.effective_message.message_id,
                reply_markup=tag_editor_keyboard,
            )
            # message.reply_video(
            #     video=video_file,
            #     reply_to_message_id=update.effective_message.message_id,
            #     reply_markup=tag_editor_keyboard,
            #     parse_mode='Markdown'
            # )   
    else:
        message.reply_text(
            generate_music_info(tag_editor_context).format(f"\n???? {BOT_USERNAME}"),
            reply_to_message_id=update.effective_message.message_id,
            reply_markup=tag_editor_keyboard
        )

def show_module_selector(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    context.user_data['current_active_module'] = ''
    lang = user_data['language']

    module_selector_keyboard = generate_module_selector_keyboard(lang)

    update.message.reply_text(
        translate_key_to(lp.ASK_WHICH_MODULE, lang),
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=module_selector_keyboard
    )

def handle_music_tag_editor(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_data = context.user_data
    art_path = user_data['art_path']
    lang = user_data['language']

    user_data['current_active_module'] = 'tag_editor'

    tag_editor_context = user_data['tag_editor']
    tag_editor_context['current_tag'] = ''

    tag_editor_keyboard = generate_tag_editor_keyboard(lang)

    if art_path:
        with open(art_path, 'rb') as art_file:
            message.reply_photo(
                photo=art_file,
                caption=generate_music_info(tag_editor_context).format(f"\n???? {BOT_USERNAME}"),
                reply_to_message_id=update.effective_message.message_id,
                reply_markup=tag_editor_keyboard,
                parse_mode='Markdown'
            )
    else:
        message.reply_text(
            generate_music_info(tag_editor_context).format(f"\n???? {BOT_USERNAME}"),
            reply_to_message_id=update.effective_message.message_id,
            reply_markup=tag_editor_keyboard
        )

def prepare_for_album_art(update: Update, context: CallbackContext) -> None:
    if len(context.user_data) == 0:
        message_text = translate_key_to(lp.DEFAULT_MESSAGE, context.user_data['language'])
    else:
        context.user_data['tag_editor']['current_tag'] = 'album_art'
        message_text = translate_key_to(lp.ASK_FOR_ALBUM_ART, context.user_data['language'])

    update.message.reply_text(message_text)

def finish_editing_tags(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_data = context.user_data

    context.bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.UPLOAD_AUDIO
    )

    music_path = user_data['music_path']
    new_art_path = user_data['new_art_path']
    music_tags = user_data['tag_editor']
    lang = user_data['language']
    thumb = open(new_art_path, 'rb').read()

    start_over_button_keyboard = generate_start_over_keyboard(lang)

    try:
        save_tags_to_file(
            file=music_path,
            tags=music_tags,
            new_art_path=new_art_path
        )
    except (OSError, BaseException):
        message.reply_text(
            translate_key_to(lp.ERR_ON_UPDATING_TAGS, lang),
            reply_markup=start_over_button_keyboard
        )
        logger.error("Error on updating tags for file %s's file.", music_path, exc_info=True)
        return

    try:
        with open(music_path, 'rb') as music_file:
            context.bot.send_audio(
                audio=music_file,
                duration=user_data['music_duration'],
                chat_id=update.message.chat_id,
                caption=f"???? {BOT_USERNAME}",
                thumb=thumb,
                reply_markup=start_over_button_keyboard,
                reply_to_message_id=user_data['music_message_id']
            )
    except (TelegramError, BaseException) as error:
        message.reply_text(
            translate_key_to(lp.ERR_ON_UPLOADING, lang),
            reply_markup=start_over_button_keyboard
        )
        logger.exception("Telegram error: %s", error)

    reset_user_data_context(context)

def display_preview(update: Update, context: CallbackContext) -> None:
    message = update.message
    user_data = context.user_data
    tag_editor_context = user_data['tag_editor']
    art_path = user_data['art_path']
    new_art_path = user_data['new_art_path']
    lang = user_data['language']

    if art_path or new_art_path:
        with open(new_art_path if new_art_path else art_path, "rb") as art_file:
            message.reply_photo(
                photo=art_file,
                caption=f"{generate_music_info(tag_editor_context).format('')}"
                        f"{translate_key_to(lp.CLICK_DONE_MESSAGE, lang)}\n\n"
                        f"???? {BOT_USERNAME}",
                reply_to_message_id=update.effective_message.message_id,
            )
    else:
        message.reply_text(
            f"{generate_music_info(tag_editor_context).format('')}"
            f"{translate_key_to(lp.CLICK_DONE_MESSAGE, lang)}\n\n"
            f"???? {BOT_USERNAME}",
            reply_to_message_id=update.effective_message.message_id,
        )

def main():
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN, timeout=120)
    persistence = PicklePersistence('persistence_storage')
    ##########
    updater = Updater(BOT_TOKEN, persistence=persistence, defaults=defaults)
    add_handler = updater.dispatcher.add_handler
    ##########
    add_handler(CommandHandler('start', command_start))
    add_handler(CommandHandler('new', start_over))
    add_handler(CommandHandler('language', show_language_keyboard))
    add_handler(CommandHandler('help', command_help))
    add_handler(CommandHandler('about', command_about))
    ##########
    add_handler(CommandHandler('done', finish_editing_tags))
    add_handler(CommandHandler('preview', display_preview))
    ##########
    add_handler(MessageHandler(
        (Filters.regex('^(???? New File)$') | Filters.regex('^(???? ???????? ????????)$')),
        start_over)
    )
    add_handler(MessageHandler(
        (Filters.regex('^(???? Tag Editor)$') | Filters.regex('^(???? ?????????? ???? ????)$')),
        handle_music_tag_editor)
    )
    ##########
    add_handler(MessageHandler(
        (Filters.regex('^(???? convert to circular video)$') | Filters.regex('^(???? ?????????? ???? ?????????? ?????????????????)$')),
        convert_mp4_to_webm)
    )
    ##########
    add_handler(CommandHandler('done', finish_editing_tags))
    add_handler(CommandHandler('preview', display_preview))
    ##########
    add_handler(MessageHandler(
        (Filters.regex('^(???? Album Art)$') | Filters.regex('^(???? ?????? ??????????)$')),
        prepare_for_album_art)
    )
    ##########
    add_handler(MessageHandler(Filters.audio, handle_music_message))
    add_handler(MessageHandler(Filters.photo, handle_photo_message))
    add_handler(MessageHandler(Filters.video, handle_video_message))
    ##########
    add_handler(MessageHandler(Filters.regex('^(???????? English)$'), set_language))
    add_handler(MessageHandler(Filters.regex('^(???????? ??????????)$'), set_language))
    ##########
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()