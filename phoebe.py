"""

        Project : Phoebe
        Bot for downloading YouTube Music


"""

# Required Libraries
from os import path, makedirs, listdir
from telebot.types import InputFile
from telebot import TeleBot as tbot
from random import choice, randint
import logging as lgr
import validators
import shutil
import string
import yt_dlp
import eyed3
import json

# Setting up logger
lgr.basicConfig(format=" => %(message)s", level=lgr.INFO)

# Loading Configurations
with open("config.json", "r") as config_data:
    configs = json.loads(config_data.read())

# Setting up configurations
greets = configs["greetings"]
err_mesg = configs["err_msgs"]
cache_path = configs["cache"]
dl_configs = configs["download_config"]

# Randomizer
def randomizer():
    salt_len = randint(8, 16)
    syms = string.ascii_lowercase
    return "".join(choice(syms) for i in range(salt_len))

# Greeting Message
lgr.info("Project Phoebe : ThumbiBot")
lgr.info("Server : ACTIVE")

# The Poetry
pbot = tbot(configs["key"])

# For starting bot
@pbot.message_handler(commands=['start', 'hello'])
def welcome(message):
    pbot.reply_to(message, choice(greets))

# For help message
@pbot.message_handler(commands=['help'])
def help(message):
    pbot.reply_to(message, configs["help_mesg"])

# The Function
@pbot.message_handler(func=lambda msg: True)
def response(message):
    
    is_valid = validators.url(message.text)
    lgr.info("Getting Data...")
    
    if not is_valid:
        lgr.info("Not a good URL!")
        pbot.reply_to(message, err_mesg["invalidURL"])
        pbot.reply_to(message, "/help for instructions")   

    else:

        # Create Directories for session
        session_path = path.join(cache_path, randomizer())
        makedirs(session_path)
        
        # First step : Filename
        dl_configs["outtmpl"] = path.join(session_path, "%(title)s.%(ext)s")
        pbot.reply_to(message, "Download request processing...")
        
        # Downloading using yt-dlp
        with yt_dlp.YoutubeDL(dl_configs) as dlr:
            rsp_info = dlr.extract_info(message.text)
        
        # Logging it
        lgr.info("ExeCode : "+ ("Success" if rsp_info else "Fail" ))
        
        # Labelling files for tagging
        send_targets = {}
        for fname in listdir(session_path):
            sessFile = path.join(session_path, fname)
            if path.isfile(sessFile):
                sessFileType = "musicFile" if fname.endswith(".mp3") else "thumbnail"
                send_targets[sessFileType] = sessFile
        music_file = send_targets["musicFile"]
        img_file = send_targets["thumbnail"]
        
        # Thumbnail for tag
        with open(img_file, "rb") as imgb:
            img_bin = imgb.read()
        
        # The Tagging process
        try:
            audioObject = eyed3.load(music_file)
            if audioObject:
                lgr.info("Extracting Tags")
                audioObject.tag.title = rsp_info["title"]
                audioObject.tag.artist = rsp_info["uploader"]
                audioObject.tag.album_artist = rsp_info["channel"]
                audioObject.tag.album = "YouTube"
                audioObject.tag.images.set(3, img_bin, "image/webp", u'cover')
                audioObject.tag.save()
            else:
                pass
        except IOError:
            lgr.error("Cant open the file")
        finally:
            # The finale step : Sending it!
            pbot.send_document(message.chat.id, InputFile(music_file))
        
        # Clearing caches, because limited memory!
        shutil.rmtree(session_path)
        lgr.info("Request Complete!")

# The Run
pbot.infinity_polling()

