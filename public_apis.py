import requests
from telegram import Update
from telegram.ext import ContextTypes

traffic_api = "https://api.data.gov.sg/v1/transport/traffic-images"


async def get_traffic_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(traffic_api)
    data = response.json()
    if data["api_info"]["status"] != "healthy":
        return False  # False implies failure to get data
    images = {}
    item = data["items"][0]
    for camera in item["cameras"]:
        images[camera["camera_id"]] = camera["image"]
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=camera["image"],
            caption=camera["camera_id"],
        )
