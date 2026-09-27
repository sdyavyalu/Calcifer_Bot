import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Здесь бот будет хранить связь:
# сообщение у тебя -> пользователь, которому нужно ответить
message_users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Можешь написать мне сообщение, вопрос или что-нибудь ещё. "
        "Я прочитаю и отвечу тебе здесь."
    )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Отправляем сообщение тебе
    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "👤 Анонимное сообщение\n\n"
            + (update.message.text or "")
        ),
    )

    # Запоминаем, кому принадлежит это сообщение
    message_users[sent.message_id] = user.id

    await update.message.reply_text("✅ Сообщение отправлено!")


async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    original_message_id = update.message.reply_to_message.message_id
    user_id = message_users.get(original_message_id)

    if not user_id:
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=update.message.text,
    )

    await update.message.reply_text("✅ Ответ отправлен.")


ADMIN_ID = int(os.environ["ADMIN_ID"])


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Ответ администратора на сообщение
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.REPLY & ~filters.COMMAND,
            reply_to_user,
        )
    )

    # Сообщения пользователей
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_message,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
