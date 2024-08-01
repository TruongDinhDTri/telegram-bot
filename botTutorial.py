from typing import Final

from setuptools import Command
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, ConversationHandler, PicklePersistence

TOKEN: Final = '7309592513:AAEpzQRvSkQhB9taxFPoWhXYKgWAmxyTLzI'
BOT_USERNAME: Final = '@wizSIZ_bot'
ADD_LINKS = 1


#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
# update: represents the incoming update from telegram API 
    await update.message.reply_text("Hello! Thanks for chatting with me! I am Wiganz Bot!")
    
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Here are the available commands: \n"
                                    "/start - start the bot \n"
                                    "/addlinks - Add new links \n"
                                    "/help - Show this helo message")
    
    
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command")
    
async def addlinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please paste your links here one at a time");
    return ADD_LINKS


async def store_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id: int = update.message.from_user.id
    link: str = update.message.text
    
    # store the linkk in the user's context 
    if user_id not in context.user_data:
        context.user_data[user_id] = []
    context.user_data[user_id].append(link)
    
    await update.message.reply_text('Linked add, You can add another one or type /done when you are finish')
    return ADD_LINKS

async def done(update: Update, context: CallbackContext):
    user_id: int = update.message.from_user.id
    
    formatted_items = [f'Link {i + 1}: {item}' for i, item in enumerate(context.user_data[user_id])]
    response  = '\n'.join(formatted_items);
    await update.message.reply_text("Thanks for your works 🐥 All links has been saved\n 😽"
                                    f'Here are your link 👇🏻 \n{response}\n'
                                    f'id: {user_id}')
    
    print("User data: ", context.user_data[user_id]);
    
    return ConversationHandler.END;
    
        


# Respones

def handle_response(text: str) -> str:
    processed: str = text.lower();
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed: 
        return "I am good"
    return "I do not understand what you wrote..."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text    
    
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}" ')
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()
            response: str = handle_response(new_text)
            
        else: 
            return 
    else: 
        response: str = handle_response(text)
    print('Bot:' , response)
    
    await update.message.reply_text(response)
    
    
async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error {context.error}')
    

if __name__ == '__main__':
    print('Starting Bot...')
    
    # Create persistence object
    persistence = PicklePersistence(filepath='bot_data')
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    # Add conversation handler for /addlinks command
    addlinks_handler = ConversationHandler(
        entry_points=[CommandHandler('addlinks', addlinks_command)],
        states={
            ADD_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_links)],
        },
        fallbacks=[CommandHandler('done', done)],
    )
    
    
    #Message 
    app.add_handler(addlinks_handler)
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors 
    app.add_error_handler(error)
    
    # Poll the bot 
    print('Polling...')
    app.run_polling(poll_interval=3)
    