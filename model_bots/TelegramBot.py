import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackContext, ApplicationBuilder, ContextTypes
import logging
from model_bots.Qradar import *


class TelegramBot:
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    async def start(self, update: Update, context: CallbackContext) -> None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    async def send_logsources_status_message(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = self.generate_logsource_status_message()
        await context.bot.send_message(chat_id=self.chat_id, text=message,parse_mode=ParseMode.MARKDOWN)
        
    def get_chatid(self):
        url = f'https://api.telegram.org/bot{self.token}/getUpdates'
        try:
            data = requests.get(url).json()
            if data['ok']:
                try:
                    chat_id = data['result'][0]['message']['chat']['id']
                    return chat_id
                except Exception as e:
                    logging.log(logging.ERROR,e)
        except Exception as e:
            logging.log(logging.ERROR,e)
            
    def run(self):
        # Start the bot
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(CommandHandler('start', self.start))
        
        #job = app.job_queue.run_repeating(self.send_logsources_status_message,interval=15*60,first=1)
        #app.run_polling()


