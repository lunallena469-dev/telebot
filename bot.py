import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, ChatMemberHandler, MessageHandler, Filters, CallbackQueryHandler
import threading

# Token del bot
TOKEN = "8075777545:AAFaoOeTcf-z6SuB69TTjMwZOjrgLoGV1tg"

# Diccionario para rastrear usuarios pendientes
pending_users = {}

# Mensaje de bienvenida
WELCOME_MESSAGE = (
    "🚨 NUEVO MIEMBRO DETECTADO\n\n"
    "🎯 Para entrar al grupo y evitar que se te banee permanentemente:\n\n"
    "📸 Envía una foto o video de alguien de Salamanca con captura de su perfil (SOLO SALAMANCA!) .\n\n"
    "📵 *No memes, no stickers, no imágenes de internet. Si no lo haces, serás expulsado automáticamente.*\n\n"
    "⏳ Tiempo restante: 60 segundos\n"
    "🕐 El reloj corre...\n\n"
    "🔘 Presiona el botón abajo para verificar que no eres un bot."
)

# Función para expulsar al usuario
def kick_user(context, chat_id, user_id):
    try:
        context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        pending_users.pop(user_id, None)  # Elimina al usuario de la lista
    except Exception as e:
        print(f"Error al expulsar al usuario {user_id}: {e}")

# Manejar nuevos miembros
def handle_new_member(update, context):
    chat_member = update.chat_member
    if chat_member.new_chat_member.status == "member":
        user_id = chat_member.new_chat_member.user.id
        chat_id = chat_member.chat.id

        # Crea el botón inline
        keyboard = [[InlineKeyboardButton("Verificar", callback_data=f"verify_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Envía el mensaje
        context.bot.send_message(chat_id=chat_id, text=WELCOME_MESSAGE, reply_markup=reply_markup)

        # Programa la expulsión en 60 segundos
        job = context.job_queue.run_once(kick_user, 60, context=(chat_id, user_id))
        pending_users[user_id] = job  # Almacena la tarea

# Manejar mensajes con foto o video
def handle_media(update, context):
    user_id = update.message.from_user.id
    if user_id in pending_users:
        if update.message.photo or update.message.video:
            # Cancela la expulsión si envía foto o video
            job = pending_users.pop(user_id)
            job.schedule_removal()
            context.bot.send_message(chat_id=update.message.chat_id, text="¡Gracias! Has pasado la verificación.")

# Manejar el botón
def handle_button(update, context):
    query = update.callback_query
    user_id = int(query.data.split("_")[1])
    if user_id in pending_users:
        query.answer("Gracias por verificar, pero aún necesitas enviar una imagen.")
    else:
        query.answer("Ya estás verificado.")

# Configuración del bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    dp.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))
    dp.add_handler(CallbackQueryHandler(handle_button))

    # Inicia el bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()