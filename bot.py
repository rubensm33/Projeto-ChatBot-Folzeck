
import logging
from venv import logger

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

NAME, LASTNAME, AGE, GENRE, RETRIEVE = range(5)



import httpx
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:

    #creates the conversation and asks the user about their name.    

    await update.message.reply_text(
        "Hi! My name is FolzeckGroup Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "What is your name?",
        
    )
    return NAME



async def name(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    #Stores the name
    
    context.user_data["name"] = update.message.text    
    logger.info("Your name is: %s", update.message.text)
    
    #Asks the user about their lastname.
    await update.message.reply_text(
        
        "And about your lastname?",
        
    )
    return LASTNAME



async def lastname(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    
    context.user_data["lastname"] = update.message.text    
    logger.info("Your lastname is: %s", update.message.text)
    
    #Asks the user about their age.
    await update.message.reply_text(
        
        "In order for us to proceed with your service, please enter your age.",
        
    )
    return AGE



async def age(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:


    context.user_data["age"] = update.message.text    
    user = update.message.from_user
    logger.info("Your age is: %s",  update.message.text)


    reply_keyboard = [["Male", "Female"]]

    #Asks the user about their gender.

    await update.message.reply_text(
        
        "Are you a Male or Female?",

        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Male or Female?"
        
    ))
    return GENRE



async def genre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #Stores genre

    context.user_data["genre"] = update.message.text    
    logger.info("Your genre is: %s", update.message.text)

    
    await update.message.reply_text("Thank you! I hope we can talk again some day.")
    print(context.user_data)
    r = httpx.post("http://127.0.0.1:8000/add-user", json=context.user_data)
    r
    print(r.text)
    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""

    
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Welcome to Folzeck Bot, please type /help to know the commands')



async def help(update: Update,context: ContextTypes.DEFAULT_TYPE)-> None:

    reply_help=[["/start", "/help", "/create", "/retrieve", "/retrieve_by_index"]]

    await update.message.reply_text("""
    The following commands are available:
    
    /start -> Welcome to the channel
    /help -> This message
    /create -> Create New User
    /retrieve -> List All
    /retrieve_by_index -> List User By Index

    """,
    reply_markup=ReplyKeyboardMarkup(
            reply_help, one_time_keyboard=True, input_field_placeholder="Choose one")
     
     )



async def retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:

    retrieve = httpx.get('http://127.0.0.1:8000/list-users')
    dict_format = 'Name: {name}\nLastname: {lastname}\nAge: {age}\nGenre: {genre}'

    users = "".join([dict_format.format_map(user) + "\n" for user in retrieve.json()])

    await update.message.reply_text(f'These are all users\n\n{users}')      
    
    
    return ConversationHandler.END



async def retrieve_by_index(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:

    await update.message.reply_text(f'Select an user by Index')
    
    return RETRIEVE



async def return_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    reply_user = update.message.text

    retrieve = httpx.get(f'http://127.0.0.1:8000/list-user-by-index/{reply_user}')

    await update.message.reply_text(f'These are the user selected\n\n{retrieve.text}')

    return ConversationHandler.END 



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    app = ApplicationBuilder().token("5890227974:AAFI_vdRD7GXSE3Iy4aiE6GF6vFAhMt_J3w").build()

    # Add conversation handler with the states NAME, LASTNAME, AGE, GENRE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={

            NAME: [MessageHandler(filters.TEXT ,name)],
            LASTNAME: [MessageHandler(filters.TEXT, lastname)],
            AGE: [MessageHandler(filters.TEXT, age)],
            GENRE: [MessageHandler(filters.Regex("^(Male|Female$)"), genre)],
           
            
            
            
            
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    conv_retrieve = ConversationHandler(
        entry_points=[CommandHandler("retrieve_by_index", retrieve_by_index)],
        states={
            RETRIEVE: [MessageHandler(filters.TEXT, return_retrieve)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    
    
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("retrieve", retrieve))
    app.add_handler(conv_retrieve)
    
    app.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    app.run_polling()



if __name__ == "__main__":
    main()




