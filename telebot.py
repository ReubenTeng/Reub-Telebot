from matplotlib import pyplot as plt
from telegram import ForceReply, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from audio_splitter import download_song, split_song_file
from public_apis import get_traffic_images
from stained_glass import stain_glass
import os
import shutil
import config

api = config.API_KEY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to my personal chatbot! Feel free to use any of the functions here.",
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="This bot is for personal use. I add functions that I find useful or funny!",
    )


async def linkedIn_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("www.linkedin.com/in/reuben-teng")


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sorry I cannot understand '%s'" % update.message.text
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


async def get_user_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


async def handle_stain_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["500", "1000", "2000"]]
    await update.message.reply_text(
        "Please send me the number of segments you want to use",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return 0


async def receive_stain_segments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # check if the input is a number
    if not update.message.text.isdigit():
        return -1
    # store the number of segments in the context
    context.user_data["num_segments"] = int(update.message.text)

    await update.message.reply_text(
        "Please send me the image you want to convert to stained glass"
    )
    return 1


async def receive_stain_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    # create unique file name based on user id
    file_name = str(update.effective_user.id) + ".jpg"
    await file.download_to_drive(file_name)
    image = plt.imread(file_name)
    print("converting...")
    # convert to stained glass
    stained_glass = stain_glass(image, context.user_data["num_segments"], 10)
    plt.imsave(file_name, stained_glass)
    # send the image
    await context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open(file_name, "rb")
    )
    # delete the photo
    os.remove(file_name)
    return ConversationHandler.END


async def handle_split_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["File", "Youtube link"]]
    await update.message.reply_text(
        "Do you want to split a file or a youtube link?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="File or Youtube link",
        ),
    )
    return 0


async def choose_split_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "File":
        await update.message.reply_text("Please send me the audio file")
        return 1
    elif update.message.text == "Youtube link":
        await update.message.reply_text("Please send me the youtube link")
        return 2
    else:
        return -1


async def send_split_audio_files(dir_name, vocals, accompaniment, context, update):
    # send the audio files
    await context.bot.send_audio(
        chat_id=update.effective_chat.id, audio=open(vocals, "rb")
    )
    await context.bot.send_audio(
        chat_id=update.effective_chat.id, audio=open(accompaniment, "rb")
    )
    # delete the audio files
    shutil.rmtree(dir_name)
    return ConversationHandler.END


async def receive_split_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await download_song(update.message.text, str(update.effective_user.id))
    # split the audio file
    file_name = str(update.effective_user.id) + ".mp3"
    dir_name = str(update.effective_user.id)
    vocals, accompaniment = await split_song_file(file_name, dir_name)
    return await send_split_audio_files(
        dir_name, vocals, accompaniment, context, update
    )


async def receive_split_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.audio.get_file()
    # create unique file name based on user id
    dir_name = str(update.effective_user.id)
    file_name = str(update.effective_user.id) + ".mp3"
    await file.download_to_drive(dir_name + os.sep + file_name)
    # split the audio file
    vocals, accompaniment = await split_song_file(file_name, dir_name)
    return await send_split_audio_files(
        dir_name, vocals, accompaniment, context, update
    )


def main():
    application = Application.builder().token(api).build()

    # Add handlers to the dispatcher

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("linkedin", linkedIn_url))
    application.add_handler(CommandHandler("traffic", get_traffic_images))
    # application.add_handler(
    #     ConversationHandler(
    #         [
    #             CommandHandler("split", handle_split_request),
    #         ],
    #         states={
    #             0: [MessageHandler(filters.TEXT, choose_split_request)],
    #             1: [MessageHandler(filters.AUDIO, receive_split_file)],
    #             2: [MessageHandler(filters.TEXT, receive_split_link)],
    #         },
    #         fallbacks=[unknown],
    #     )
    # )
    application.add_handler(
        ConversationHandler(
            [
                CommandHandler("stain", handle_stain_request),
            ],
            states={
                0: [MessageHandler(filters.TEXT, receive_stain_segments)],
                1: [MessageHandler(filters.PHOTO, receive_stain_image)],
            },
            fallbacks=[unknown],
        )
    )

    # on non command i.e message - echo the message on Telegram

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C

    application.run_polling()


if __name__ == "__main__":
    main()
