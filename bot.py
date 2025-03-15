import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import pytz

TOKEN = "TOKEN"

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

FIND_PHONE_NUMBERS = 1

async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(f'Привет {user.full_name}!')

async def helpCommand(update: Update, context):
    await update.message.reply_text('Help!')

async def findPhoneNumbersCommand(update: Update, context):
    await update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return FIND_PHONE_NUMBERS

async def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        await update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phoneNumbers = ''
    for i, number in enumerate(phoneNumberList, start=1):
        phoneNumbers += f'{i}. {number}\n'

    await update.message.reply_text(phoneNumbers)
    return ConversationHandler.END

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

def main():
    application = Application.builder().token(TOKEN).build()

    application.job_queue.scheduler.configure(timezone=pytz.UTC)

    conv_handler_find_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            FIND_PHONE_NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helpCommand))
    application.add_handler(conv_handler_find_phone_numbers)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == '__main__':
    main()