import logging
import re
import paramiko
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import pytz
import os

load_dotenv('data.env')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

FIND_PHONE_NUMBERS = 1
FIND_EMAILS = 2
VERIFY_PASSWORD = 3

async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(f'Доброе время суток, {user.full_name}!\nДля просмотра доступных команд используйте /help.')

async def helpCommand(update: Update, context):
    await update.message.reply_text(
        "Доступные для использования команды:\n1. /start - приветствие;\n2. /find_email - выделение из текста email-адресов;\n"
        "3. /find_phone_number - выделение из текста номеров телефонов;\n"
        "4. /verify_password - проверка сложности пароля;\n"
        "5. /get_release - информация о релизе системы;\n"
        "6. /get_uname - информация об архитектуре процессора, имени хоста системы и версии ядра;\n"
        "7. /get_uptime - информация о времени работы системы;\n"
        "8. /get_df - информация о состоянии файловой системы;\n"
        "9. /get_free - информация о состоянии оперативной памяти;\n"
        "10. /get_mpstat - информация о производительности системы;\n"
        "11. /get_w - информация о работающих в данной системе пользователях;\n"
        "12. /get_auths - информация о последних 10 входах в систему;\n"
        "13. /get_critical - информация о последних 5 критических событиях;\n"
        "14. /get_ps - информация о запущенных процессах;\n"
        "15. /get_ss - информация об используемых портах;\n"
        "16. /get_apt_list - информация об установленных пакетах (при использовании можно ввести название пакета для поиска, /get_apt_list <имя_пакета>);\n"
        "17. /get_services - информация о запущенных сервисах.\n")


async def findPhoneNumbersCommand(update: Update, context):
    await update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return FIND_PHONE_NUMBERS

async def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(?<!\d)(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\d)')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        await update.message.reply_text('Телефонные номера не найдены.')
        return ConversationHandler.END

    phoneNumbers = ''
    for i, number in enumerate(phoneNumberList, start=1):
        phoneNumbers += f'{i}. {number}\n'

    await update.message.reply_text(phoneNumbers)
    return ConversationHandler.END

async def findEmailsCommand(update: Update, context):
    await update.message.reply_text('Введите текст для поиска email-адресов: ')
    return FIND_EMAILS

async def findEmails(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z-]+\.[a-zA-Z-.]+'
    )

    emailList = emailRegex.findall(user_input)

    if not emailList:
        await update.message.reply_text('Email-адреса не найдены.')
        return ConversationHandler.END

    emails = ''
    for i, email in enumerate(emailList, start=1):
        emails += f'{i}. {email}\n'

    await update.message.reply_text(emails)
    return ConversationHandler.END

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

async def verifyPasswordCommand(update: Update, context):
    await update.message.reply_text("При проверке учитываются следующие требования:\n"
                                    "1. должен содержать не менее восьми символов;\n"
                                    "2. должен включать как минимум одну заглавную букву (A–Z);\n"
                                    "3. должен включать хотя бы одну строчную букву (a–z);\n"
                                    "4. должен включать хотя бы одну цифру (0–9);\n"
                                    "5. должен включать хотя бы один специальный символ, такой как !?@#$%^&\\*().\n\n"
                                    "Введите пароль для проверки сложности:")
    return VERIFY_PASSWORD

async def verifyPassword(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!?@#$%^&*()]).{8,}$'
    )

    if passwordRegex.match(user_input):
        await update.message.reply_text('Пароль сложный.')
        return ConversationHandler.END
    else:
        await update.message.reply_text('Пароль простой.')
        return ConversationHandler.END

def execute_ssh_command(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(os.getenv('RM_HOST'), port=int(os.getenv('RM_PORT')), username=os.getenv('RM_USER'), password=os.getenv('RM_PASSWORD'))

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        ssh.close()

        if error:
            return f"Ошибка: {error}"
        return output
    except Exception as e:
        return f"Ошибка при выполнении команды: {str(e)}"

async def get_release(update: Update, context):
    result = execute_ssh_command("lsb_release -a")
    await update.message.reply_text(result)

async def get_uname(update: Update, context):
    result = execute_ssh_command("uname -a")
    await update.message.reply_text(result)

async def get_uptime(update: Update, context):
    result = execute_ssh_command("uptime")
    await update.message.reply_text(result)

async def get_df(update: Update, context):
    result = execute_ssh_command("df -h")
    await update.message.reply_text(result)

async def get_free(update: Update, context):
    result = execute_ssh_command("free -h")
    await update.message.reply_text(result)

async def get_mpstat(update: Update, context):
    result = execute_ssh_command("mpstat")
    await update.message.reply_text(result)

async def get_w(update: Update, context):
    result = execute_ssh_command("w")
    await update.message.reply_text(result)

async def get_auths(update: Update, context):
    result = execute_ssh_command("last -n 10")
    await update.message.reply_text(result)

async def get_critical(update: Update, context):
    result = execute_ssh_command("sudo journalctl -p crit -n 5 --no-pager")
    await update.message.reply_text(result)

async def get_ps(update: Update, context):
    await update.message.reply_text(
        "Создаю файл со списком всех запущенных процессов...\nЭто может занять некоторое время."
    )

    result = execute_ssh_command("sudo ps aux > ps.txt")

    if "Ошибка" in result:
        await update.message.reply_text("Ошибка при создании списка процессов")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        os.getenv('RM_HOST'),
        port=int(os.getenv('RM_PORT')),
        username=os.getenv('RM_USER'),
        password=os.getenv('RM_PASSWORD')
    )

    sftp = ssh.open_sftp()
    remote_file = sftp.file('ps.txt', 'r')
    local_file = 'ps.txt'
    sftp.get('ps.txt', local_file)
    sftp.close()
    ssh.close()

    await update.message.reply_document(
        document=open(local_file, 'rb'),
        caption="Список всех запущенных процессов."
    )

    os.remove(local_file)
    execute_ssh_command("rm ps.txt")

async def get_ss(update: Update, context):
    result = execute_ssh_command("ss -tuln")
    await update.message.reply_text(result)


async def get_apt_list(update: Update, context):
    try:
        if context.args:
            package_name = ' '.join(context.args)
            result = execute_ssh_command(f"apt-cache show {package_name} || dpkg-query -s {package_name}")

            if not result or "не установлен" in result.lower() or "не найден" or "ошибка" in result.lower():
                await update.message.reply_text(f"Пакет '{package_name}' не найден.")
                return

            await update.message.reply_text(f"Информация о пакете {package_name}:\n\n{result}")
        else:
            await update.message.reply_text(
                "Создаю файл со списком всех пакетов...\nЭто может занять некоторое время."
            )

            result = execute_ssh_command("dpkg-query -f '${Package}\t${Version}\n' -W > all_packages.txt")

            if "Ошибка" in result:
                await update.message.reply_text("Ошибка при создании списка пакетов")
                return

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                os.getenv('RM_HOST'),
                port=int(os.getenv('RM_PORT')),
                username=os.getenv('RM_USER'),
                password=os.getenv('RM_PASSWORD')
            )

            sftp = ssh.open_sftp()
            remote_file = sftp.file('all_packages.txt', 'r')
            local_file = 'all_packages.txt'
            sftp.get('all_packages.txt', local_file)
            sftp.close()
            ssh.close()

            await update.message.reply_document(
                document=open(local_file, 'rb'),
                caption="Список всех установленных пакетов. Для поиска конкретного пакета используйте: /get_apt_list <имя_пакета>"
            )

            os.remove(local_file)
            execute_ssh_command("rm all_packages.txt")

    except Exception as e:
        logger.error(f"Error in get_apt_list: {str(e)}")
        await update.message.reply_text("Произошла ошибка при обработке запроса")

async def get_services(update: Update, context):
    await update.message.reply_text(
        "Создаю файл с информацией о запущенных сервисах...\nЭто может занять некоторое время."
    )

    result = execute_ssh_command("systemctl list-units --type=service --state=running > services.txt")

    if "Ошибка" in result:
        await update.message.reply_text("Ошибка при создании файла")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        os.getenv('RM_HOST'),
        port=int(os.getenv('RM_PORT')),
        username=os.getenv('RM_USER'),
        password=os.getenv('RM_PASSWORD')
    )

    sftp = ssh.open_sftp()
    remote_file = sftp.file('services.txt', 'r')
    local_file = 'services.txt'
    sftp.get('services.txt', local_file)
    sftp.close()
    ssh.close()

    await update.message.reply_document(
        document=open(local_file, 'rb'),
        caption="Вся полученная информация о запущенных сервисах."
    )

    os.remove(local_file)
    execute_ssh_command("rm services.txt")

def main():
    application = Application.builder().token(os.getenv('TOKEN')).build()
    application.job_queue.scheduler.configure(timezone=pytz.UTC)

    conv_handler_find_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", findPhoneNumbersCommand)],
        states={
            FIND_PHONE_NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    conv_handler_find_emails = ConversationHandler(
        entry_points=[CommandHandler("find_email", findEmailsCommand)],
        states={
            FIND_EMAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, findEmails)],
        },
        fallbacks=[]
    )

    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            VERIFY_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, verifyPassword)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helpCommand))
    application.add_handler(conv_handler_find_phone_numbers)
    application.add_handler(conv_handler_find_emails)
    application.add_handler(conv_handler_verify_password)
    application.add_handler(CommandHandler("get_release", get_release))
    application.add_handler(CommandHandler("get_uname", get_uname))
    application.add_handler(CommandHandler("get_uptime", get_uptime))
    application.add_handler(CommandHandler("get_df", get_df))
    application.add_handler(CommandHandler("get_free", get_free))
    application.add_handler(CommandHandler("get_mpstat", get_mpstat))
    application.add_handler(CommandHandler("get_w", get_w))
    application.add_handler(CommandHandler("get_auths", get_auths))
    application.add_handler(CommandHandler("get_critical", get_critical))
    application.add_handler(CommandHandler("get_ps", get_ps))
    application.add_handler(CommandHandler("get_ss", get_ss))
    application.add_handler(CommandHandler("get_apt_list", get_apt_list))
    application.add_handler(CommandHandler('get_services', get_services))

    try:
        application.run_polling()
    except AttributeError as e:
        if "_pending_futures" in str(e):
            logger.warning("Ignoring JobQueue shutdown error")
        else:
            raise

if __name__ == '__main__':
    main()