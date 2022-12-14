import os
import re
from pathlib import Path

import logging
import subprocess

import ffmpeg

import ffmpy, os, pyheif
from PIL import Image

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import music_tag
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from models.admin import Admin
from models.user import User
from localization import keys

logger = logging.getLogger()

def translate_key_to(key: str, destination_lang: str) -> str:
    """Find the specified key in the `keys` dictionary and returns the corresponding
    value for the given language

    **Keyword arguments:**
     - file_path (str) -- The file path of the file to delete

    **Returns:**
     - The value of the requested key in the dictionary
    """
    if key not in keys:
        raise KeyError("Specified key doesn't exist")

    return keys[key][destination_lang]


def delete_file(file_path: str) -> None:
    """Deletes a file from the filesystem. Simply ignores the files that don't exist.

    **Keyword arguments:**
     - file_path (str) -- The file path of the file to delete
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def generate_music_info(tag_editor_context: dict) -> str:
    """Generate the details of the music based on the values in `tag_editor_context`
    dictionary

    **Keyword arguments:**
     - tag_editor_context (dict) -- The context object of the user

    **Returns:**
     `str`
    """
    ctx = tag_editor_context

    return (
        f"*🗣 Artist:* {ctx['artist'] if ctx['artist'] else '-'}\n"
        f"*🎵 Title:* {ctx['title'] if ctx['title'] else '-'}\n"
        f"*🎼 Album:* {ctx['album'] if ctx['album'] else '-'}\n"
        f"*🎹 Genre:* {ctx['genre'] if ctx['genre'] else '-'}\n"
        f"*📅 Year:* {ctx['year'] if ctx['year'] else '-'}\n"
        f"*💿 Disk Number:* {ctx['disknumber'] if ctx['disknumber'] else '-'}\n"
        f"*▶️ Track Number:* {ctx['tracknumber'] if ctx['tracknumber'] else '-'}\n"
        "{}\n"
    )


def increment_usage_counter_for_user(user_id: int) -> int:
    """Increment the `number_of_files_sent` column of user with the specified `user_id`.

    **Keyword arguments:**
     - user_id (int) -- The user id of the user

    **Returns:**
     The new value for `user.number_of_files_sent`
    """
    user = User.where('user_id', '=', user_id).first()

    if user:
        user.number_of_files_sent = user.number_of_files_sent + 1
        user.push()

        return user.number_of_files_sent

    raise LookupError(f'User with id {user_id} not found.')

def reset_user_data_context(context: CallbackContext) -> None:
    user_data = context.user_data
    language = user_data['language'] if ('language' in user_data) else 'en'

    if 'music_path' in user_data:
        delete_file(user_data['music_path'])
    if 'art_path' in user_data:
        delete_file(user_data['art_path'])
    if 'new_art_path' in user_data:
        delete_file(user_data['new_art_path'])

    new_user_data = {
        'video_path': '',
        'video_message_id': '',
        'video_duration': '',
        'video_mimeType': '',
        'tag_editor': {},
        'music_path': '',
        'music_duration': 0,
        'art_path': '',
        'new_art_path': '',
        'current_active_module': '',
        'music_message_id': 0,
        'language': language,
    }
    context.user_data.update(new_user_data)

def create_user_directory(user_id: int) -> str:
    """Create a directory for a user with a given id.

    **Keyword arguments:**
     - user_id (int) -- The user id of the user

    **Returns:**
     The path of the created directory
    """
    user_download_dir = f"downloads/{user_id}"

    try:
        Path(user_download_dir).mkdir(parents=True, exist_ok=True)
    except (OSError, FileNotFoundError, BaseException) as error:
        raise Exception(f"Can't create directory for user_id: {user_id}") from error

    return user_download_dir

def download_file(user_id: int, file_to_download, file_type: str, context: CallbackContext) -> str:
    """Download a file using convenience methods of "python-telegram-bot"

    **Keyword arguments:**
     - user_id (int) -- The user's id
     - file_to_download (*) -- The file object to download
     - file_type (str) -- The type of the file, either 'photo' or 'audio'
     - context (CallbackContext) -- The context object of the user

    **Returns:**
     The path of the downloaded file
    """
    user_download_dir = f"downloads/{user_id}"
    file_id = ''
    file_extension = ''

    if file_type == 'audio':
        file_id = context.bot.get_file(file_to_download.file_id)
        file_name = file_to_download.file_name
        file_extension = file_name.split(".")[-1]
    elif file_type == 'photo':
        file_id = context.bot.get_file(file_to_download.file_id)
        file_extension = 'jpg'
    elif file_type == 'video':
        file_id = context.bot.get_file(file_to_download.file_id)
        file_name = file_to_download.file_name
        file_extension = file_name.split(".")[-1]
        # if file_extension == "mp4":
        #     file_name.format = "webm"
        #     file_extension = "webm"
        # logger.error(file_name)

    # convert_mp4_to_webm_subprocess()
    # convert_mp4_to_webm_module()
    file_download_path = f"{user_download_dir}/{file_id.file_id}.{file_extension}"
    # logger.error(file_download_path)

    try:
        file_id.download(f"{user_download_dir}/{file_id.file_id}.{file_extension}")
    except ValueError as error:
        raise Exception(f"Couldn't download the file with file_id: {file_id}") from error

    return file_download_path

def generate_start_over_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Create an return an instance of `start_over_keyboard`


    **Keyword arguments:**
     - language (str) -- The desired language to generate labels

    **Returns:**
     ReplyKeyboardMarkup instance
    """
    return (
        ReplyKeyboardMarkup(
            [
                [translate_key_to('BTN_NEW_FILE', language)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


def generate_module_selector_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Create an return an instance of `module_selector_keyboard`


    **Keyword arguments:**
     - language (str) -- The desired language to generate labels

    **Returns:**
     ReplyKeyboardMarkup instance
    """
    return (
        ReplyKeyboardMarkup(
            [
                [
                    translate_key_to('BTN_TAG_EDITOR', language),
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

def generate_module_selector_video_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Create an return an instance of `module_selector_video_keyboard`


    **Keyword arguments:**
     - language (str) -- The desired language to generate labels

    **Returns:**
     ReplyKeyboardMarkup instance
    """
    return (
        ReplyKeyboardMarkup(
            [
                [
                    translate_key_to('BTN_CONVERT_VIDEO_TO_CIRCLE', language),
                    translate_key_to('BTN_CONVERT_VIDEO_TO_GIF', language),
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

def generate_tag_editor_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Create an return an instance of `tag_editor_keyboard`


    **Keyword arguments:**
     - language (str) -- The desired language to generate labels

    **Returns:**
     ReplyKeyboardMarkup instance
    """
    return (
        ReplyKeyboardMarkup(
            [
                [
                    translate_key_to('BTN_ALBUM_ART', language)
                ],
            ],
            resize_keyboard=True,
        )
    )

def generate_tag_editor_video_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Create an return an instance of `tag_editor_keyboard`


    **Keyword arguments:**
     - language (str) -- The desired language to generate labels

    **Returns:**
     ReplyKeyboardMarkup instance
    """
    return (
        ReplyKeyboardMarkup(
            [
                [
                    translate_key_to('BTN_CONVERT_VIDEO_TO_CIRCLE', language),
                    translate_key_to('BTN_CONVERT_VIDEO_TO_GIF', language),
                ],
            ],
            resize_keyboard=True,
        )
    )

def save_tags_to_file(file: str, tags: dict, new_art_path: str) -> str:
    """Create an return an instance of `tag_editor_keyboard`


    **Keyword arguments:**
     - file (str) -- The path of the file
     - tags (str) -- The dictionary containing the tags and their values
     - new_art_path (str) -- The new album art to set

    **Returns:**
     The path of the file
    """
    music = music_tag.load_file(file)

    try:
        if new_art_path:
            with open(new_art_path, 'rb') as art:
                music['artwork'] = art.read()
    except OSError as error:
        raise Exception("Couldn't set hashtags") from error

    music['artist'] = tags['artist'] if tags['artist'] else ''
    music['title'] = tags['title'] if tags['title'] else ''
    music['album'] = tags['album'] if tags['album'] else ''
    music['genre'] = tags['genre'] if tags['genre'] else ''
    music['year'] = int(tags['year']) if tags['year'] else 0
    music['disknumber'] = int(tags['disknumber']) if tags['disknumber'] else 0
    music['tracknumber'] = int(tags['tracknumber']) if tags['tracknumber'] else 0

    music.save()

    return file

def convert_mp4_to_webm_subprocess(input_file, output_file):
    try:
        command = 'ffmpeg -i ' + input_file + ' ' + output_file
        subprocess.run(command)
    except:
        print("ok")

def convert_mp4_to_webm_module(input_file, output_file):
    try:
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(stream, output_file)
        ffmpeg.run(stream)
    except:
        print("ok")

def convert_video(chat_id, input_type, output_type):
	"""
	The function converts video of one type to another.
	Args:
		chat_id: unique identification for video
		input_type: video input type
		output_type: video output type
	"""
	inputs = {'./input_media/{}.{}'.format(chat_id, input_type): None}
	if output_type == "gif":
		outputs = {'./output_media/{}.{}'.format(chat_id, output_type): '-t 3 -vf "fps=30,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0'}
	else:
		outputs = {'./output_media/{}.{}'.format(chat_id, output_type): None}
	ff = ffmpy.FFmpeg(
	    inputs=inputs,
	    outputs=outputs
	)
	ff.run()
	return None

def convert_image(chat_id, input_type, output_type):
	"""
	The function converts image of one type to another.
	Args:
		chat_id: unique identification for image
		input_type: video input type
		output_type: video output type
	"""
	if (input_type == "heif"):
		heif_file = pyheif.read('./input_media/{}.{}'.format(chat_id, input_type))
		img = Image.frombytes(
		    heif_file.mode, 
		    heif_file.size, 
		    heif_file.data,
		    "raw",
		    heif_file.mode,
		    heif_file.stride)
	else:
		img = Image.open('./input_media/{}.{}'.format(chat_id, input_type))
	if output_type == "jpg" or ((input_type == "tiff" or input_type == "png") and output_type == "pdf"):
		img = img.convert('RGB')
	elif output_type == "ico":
		icon_size = [(32, 32)]
		img.save('./output_media/{}.{}'.format(chat_id, output_type), sizes=icon_size)
		return None
	img.save('./output_media/{}.{}'.format(chat_id, output_type), quality=95, optimize=True)
	return None

def build_menu(buttons, header_buttons=None, footer_buttons=None):
    """
    Function to build the menu buttons to show users.
    """
    menu = [buttons[i] for i in range(0, len(buttons))]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def show_options(n_rows, text, media_type, input_type):
    """
    Function that takes in button text and callback data to generate the view.
    Args:
        n_rows: rows for button
        text: list of texts to show
        media_type: currently supports videos and images
        input_type: format of video
    """
    button_list = []
    for i in range(0,n_rows):
        button_list.append([InlineKeyboardButton(text[i], callback_data=media_type + "_" + input_type + "_" + text[i])])
    reply_markup = InlineKeyboardMarkup(build_menu(button_list))
    return reply_markup

def check_exist_media(chat_id, input_type):
    """
    Function to check if media exist.
    Args:
        chat_id: id of user
        input_type: format of video
    """
    #checks if media exist by looking for file with user's username
    if not os.path.isfile("./input_media/{}.{}".format(str(chat_id), input_type)): 
        return False
    directory, filename = os.path.split("./input_media/{}.{}".format(str(chat_id), input_type))
    return filename in os.listdir(directory)