# pylint: disable=line-too-long

START_MESSAGE = "START_MESSAGE"
START_OVER_MESSAGE = "START_OVER_MESSAGE"
HELP_MESSAGE = "HELP_MESSAGE"
ABOUT_MESSAGE = "ABOUT_MESSAGE"
DEFAULT_MESSAGE = "DEFAULT_MESSAGE"
ASK_WHICH_MODULE = "ASK_WHICH_MODULE"
ASK_WHICH_TAG = "ASK_WHICH_TAG"
ASK_FOR_ALBUM = "ASK_FOR_ALBUM"
ASK_FOR_ALBUM_ART = "ASK_FOR_ALBUM_ART"
ALBUM_ART_CHANGED = "ALBUM_ART_CHANGED"
EXPECTED_NUMBER_MESSAGE = "EXPECTED_NUMBER_MESSAGE"
CLICK_PREVIEW_MESSAGE = "CLICK_PREVIEW_MESSAGE"
CLICK_DONE_MESSAGE = "CLICK_DONE_MESSAGE"
LANGUAGE_CHANGED = "LANGUAGE_CHANGED"
MUSIC_LENGTH = "MUSIC_LENGTH"
REPORT_BUG_MESSAGE = "REPORT_BUG_MESSAGE"
ERR_CREATING_USER_FOLDER = "ERR_CREATING_USER_FOLDER"
ERR_ON_DOWNLOAD_AUDIO_MESSAGE = "ERR_ON_DOWNLOAD_AUDIO_MESSAGE"
ERR_ON_DOWNLOAD_PHOTO_MESSAGE = "ERR_ON_DOWNLOAD_PHOTO_MESSAGE"
ERR_TOO_LARGE_FILE = "ERR_TOO_LARGE_FILE"
ERR_ON_READING_TAGS = "ERR_ON_READING_TAGS"
ERR_ON_UPDATING_TAGS = "ERR_ON_UPDATING_TAGS"
ERR_ON_UPLOADING = "ERR_ON_UPLOADING"
ERR_NOT_IMPLEMENTED = "ERR_NOT_IMPLEMENTED"
ERR_OUT_OF_RANGE = "ERR_OUT_OF_RANGE"
ERR_MALFORMED_RANGE = "ERR_MALFORMED_RANGE"
BTN_TAG_EDITOR = "BTN_TAG_EDITOR"
BTN_MUSIC_TO_VOICE_CONVERTER = "BTN_MUSIC_TO_VOICE_CONVERTER"
BTN_ALBUM = "BTN_ALBUM"
BTN_ALBUM_ART = "BTN_ALBUM_ART"
BTN_BACK = "BTN_BACK"
BTN_NEW_FILE = "BTN_NEW_FILE"
DONE = "DONE"
OR = "OR"

REPORT_BUG_MESSAGE_EN = "That's my fault! Please send a bug report here: @jojo"
REPORT_BUG_MESSAGE_FA = "این اشتباه منه! لطفا این باگ رو از اینجا گزارش کنید: @jojo"
EG_EN = "e.g."
EG_FA = "مثل"

keys = {
    START_MESSAGE: {
        "en": "Hello there! 👋\n"
              "Let's get started. Just send me a music and see how awesome I am!",
        "fa": "سلام! 👋\n"
              "خب شروع کنیم. یه موزیک برام بفرست تا ببینی چقدر خفنم!",
    },
    START_OVER_MESSAGE: {
        "en": "Send me a music and see how awesome I am!",
        "fa": "یه موزیک برام بفرست تا ببینی چقدر خفنم!",
    },
    HELP_MESSAGE: {
        "en": "It's simple! Just send or forward me an audio track, an MP3 file or a music. I'm waiting... 😁",
        "fa": "ساده س! یه فایل صوتی، یه MP3 یا یه موزیک برام بفرست. منتظرم... 😁",
    },
    ABOUT_MESSAGE: {
        "en": "This bot is created by jojo team.",
        "fa": "این ربات توسط تیم جوجو ساخته شده است.",
    },
    DEFAULT_MESSAGE: {
        "en": "Send or forward me an audio track, an MP3 file or a music. I'm waiting... 😁",
        "fa": "یه فایل صوتی، یه MP3 یا یه موزیک برام بفرست... منتظرم... 😁",
    },
    ASK_WHICH_MODULE: {
        "en": "What do you want to do with this file?",
        "fa": "میخوای با این فایل چیکار کنی؟",
    },
    ASK_WHICH_TAG: {
        "en": "Which tag do you want to edit?",
        "fa": "چه تگی رو میخوای ویرایش کنی؟",
    },
    ASK_FOR_ALBUM_ART: {
        "en": "Send me a photo:",
        "fa": "یک عکس برام بفرست:",
    },
    CLICK_PREVIEW_MESSAGE: {
        "en": "If you want to preview your changes click /preview.",
        "fa": "اگر میخوای تغییرات رو تا الان ببینی از دستور /preview استفاده کن.",
    },
    CLICK_DONE_MESSAGE: {
        "en": "Click /done to save your changes.",
        "fa": "روی /done کلیک کن تا تغییراتت ذخیره بشن.",
    },
    LANGUAGE_CHANGED: {
        "en": "Language has been changed. If you want to change the language later, use /language command.",
        "fa": "زبان تغییر یافت. اگر میخواهید زبان را مجددا تغییر دهید، از دستور /language استفاده کنید.",
    },
    MUSIC_LENGTH: {
        "en": "The file length is {}.",
        "fa": "طول کل فایل {} است.",
    },
    REPORT_BUG_MESSAGE: {
        "en": "That's my fault! Please send a bug report here: @jojo",
        "fa": "این اشتباه منه! لطفا این باگ رو از اینجا گزارش کنید: @jojo",
    },
    ERR_CREATING_USER_FOLDER: {
        "en": f"Error on starting... {REPORT_BUG_MESSAGE_EN}",
        "fa": f"به مشکل خوردم... {REPORT_BUG_MESSAGE_FA}",
    },
    ERR_ON_DOWNLOAD_AUDIO_MESSAGE: {
        "en": f"Sorry, I couldn't download your file... {REPORT_BUG_MESSAGE_EN}",
        "fa": f"متاسفم، نتونستم فایلت رو دانلود کنم... {REPORT_BUG_MESSAGE_FA}",
    },
    ERR_ON_DOWNLOAD_PHOTO_MESSAGE: {
        "en": f"Sorry, I couldn't download your file... {REPORT_BUG_MESSAGE_EN}",
        "fa": f"متاسفم، نتونستم فایلت رو دانلود کنم... {REPORT_BUG_MESSAGE_FA}",
    },
    ERR_TOO_LARGE_FILE: {
        "en": "This file is too big that I can process, sorry!",
        "fa": "این فایل بزرگتر از چیزی هست که من بتونم پردازش کنم، شرمنده!",
    },
    ERR_ON_READING_TAGS: {
        "en": f"Sorry, I couldn't read the tags of the file... {REPORT_BUG_MESSAGE_EN}",
        "fa": f"متاسفم، نتونستم تگ های فایل رو بخونم... {REPORT_BUG_MESSAGE_FA}",
    },
    ERR_ON_UPDATING_TAGS: {
        "en": f"Sorry, I couldn't update tags the tags of the file... {REPORT_BUG_MESSAGE_EN}",
        "fa": f"متاسفم، نتونستم تگ های فایل رو آپدیت کنم... {REPORT_BUG_MESSAGE_FA}",
    },
    ERR_ON_UPLOADING: {
        "en": "Sorry, due to network issues, I couldn't upload your file. Please try again.",
        "fa": "متاسفم. به دلیل اشکالات شبکه نتونستم فایل رو آپلود کنم. لطفا دوباره امتحان کن.",
    },
    ERR_NOT_IMPLEMENTED: {
        "en": "This feature has not been implemented yet. Sorry!",
        "fa": "این قابلیت هنوز پیاده سازی نشده. شرمنده!",
    },
    BTN_TAG_EDITOR: {
        "en": "🎵 Tag Editor",
        "fa": "🎵 تغییر تگ ها",
    },
    BTN_ALBUM: {
        "en": "🎼 Album",
        "fa": "🎼 آلبوم",
    },
    BTN_ALBUM_ART: {
        "en": "🖼 Album Art",
        "fa": "🖼 عکس آلبوم",
    },
    BTN_BACK: {
        "en": "🔙 Back",
        "fa": "🔙 بازگشت",
    },
    BTN_NEW_FILE: {
        "en": "🆕 New File",
        "fa": "🆕 فایل جدید",
    },
    DONE: {
        "en": "Done!",
        "fa": "انجام شد!",
    },
    OR: {
        "en": "or",
        "fa": "یا",
    },
}
