from multiprocessing.connection import answer_challenge

from IPython.core.debugger import prompt
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

# тут будемо писати наш код :)

TOKEN="8237942912:AAEjm-JJwHmKggGrfTKx1xYMfMaB2-Ad1G0"

async def start(update, context):
    msg=load_message("main")
    dialog.mode=None
    await send_photo(update, context, "main")
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
        "start": "Головне меню",
        "profile": "Генерація Tinder-профіля \uD83D\uDE0E",
        "opener": "Повідомлення для знайомства \uD83E\uDD70",
        "message": "Переписка від вашого імені \uD83D\uDE08",
        "date": "Спілкування з зірками \uD83D\uDD25",
        "gpt": "Задати питання ChatGPT \uD83E\uDDE0",
    })

async def gpt(update, context):
    dialog.mode="gpt"
    await send_photo(update, context, "gpt")
    msg=load_message("gpt")
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    text = update.message.text
    l_prompt = load_prompt("gpt")
    my_message = await send_text(update, context, "Набирає повідомлення...")
    answer = await chatgpt.send_question(l_prompt, text)
    await my_message.edit_text(answer)


async def date(update, context):
    dialog.mode= "date"
    msg = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, msg, {
        "date_grande": "Аріана Гранде",
        "date_robbie": "Марго Роббі",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослінг",
        "date_hardy": "Том Харді",
    })

async def date_button(update, context):
    query=update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Гарний вибір! \uD83D\uDE05 Ваша задача запросити дівчину/хлопця на побачення за 5 повідомлень! \u2764\uFE0F")
    d_prompt=load_prompt(query)
    chatgpt.set_prompt(d_prompt)

async def date_dialog(update, context):
    text=update.message.text
    my_message= await send_text(update, context, "Набирає повідомлення...")
    answer=await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def message(update, context):
    dialog.mode="message"
    msg= load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, msg, {
        "message_next": "Написати повідомлення",
        "message_date": "Запросити на побачення",
    })
    dialog.list.clear()

async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    query=update.callback_query.data
    await update.callback_query.answer()

    m_prompt=load_prompt(query)
    user_chat_history="\n\n".join(dialog.list)

    my_message= await send_text(update, context, "Думаю над варіантами...")
    answer = await chatgpt.send_question(m_prompt, user_chat_history)
    await my_message.edit_text(answer)


async def profile(update, context):
    dialog.mode = "profile"
    msg = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter=0
    await send_text(update, context, "Як Вас звати?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.counter+=1

    if dialog.counter ==1:
        dialog.user["name"]=text
        await send_text(update, context, "Скільки Вам років?")
    if dialog.counter ==2:
        dialog.user["age"]=text
        await send_text(update, context, "Ким Ви працюєте?")
    if dialog.counter ==3:
        dialog.user["occupation"]=text
        await send_text(update, context, "У Вас є хобі? Якщо так, то яке?")
    if dialog.counter ==4:
        dialog.user["hobby"]=text
        await send_text(update, context, "Що Вам НЕ подобається в людях?")
    if dialog.counter ==5:
        dialog.user["annoys"]=text
        await send_text(update, context, "Мета знайомства?")
    if dialog.counter ==6:
        dialog.user["goals"]=text
        p_prompt=load_prompt("profile")
        user_info=dialog_user_info_to_str(dialog.user)

        my_message= await send_text(update, context, "ChatGPT 🧠 генерує Ваш профіль. Зачекайте кілька секунд...")
        answer= await chatgpt.send_question(p_prompt, user_info)
        await my_message.edit_text(answer)

async def opener(update, context):
    dialog.mode = "opener"
    msg = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Ім'я партнера(ки)?")

async def opener_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Скільки років партнеру(ці)?")
    if dialog.counter == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцініть зовнішність: 1-10 балів?")
    if dialog.counter == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Ким він/вона працює?")
    if dialog.counter == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Мета знайомства?")
    if dialog.counter == 5:
        dialog.user["goals"] = text
        o_prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "ChatGPT 🧠 генерує Ваше повідомлення...")
        answer = await chatgpt.send_question(o_prompt, user_info)
        await my_message.edit_text(answer)

async def hi(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)

dialog = Dialog()
dialog.mode=None
dialog.list= []
dialog.user={}
dialog.counter=0

chatgpt=ChatGptService(token="javcgk/s3WVH1V/3/eY+dOWWa+jvSy1lakmEGDVwq1h8XG3bvDbbBufJJRs/pGrIDgVhny5Qag1p3K8y+oGQU63QPq/fboIxvJ4mWTNtgIoURRvFdbWYXH1labl8JDmWT3NzSRnQIdxjFkbVj3g8fT19j15aM3UaKZYyeEcjXr01VSj3XHOhnumhEb+6+T71NKnk7rSZF/y42jb6LiZcPWoa5CqlyR0o6kXRXqzr7DWNDuQEQ=")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))

app.add_handler(MessageHandler(filters.TEXT & ~ filters.COMMAND, hi))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.run_polling()
