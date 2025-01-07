from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from typing import List, Tuple

# Function to send a simple text message
async def send_text_message(update: Update, message: str):
    """
    Sends a simple text message without any buttons.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send.
    
    Example Usage:
        await send_text_message(update, "Hello! This is a simple message.")
    """
    await update.message.reply_text(message)

# Function to send a text message with a custom keyboard (not inline buttons)
async def send_text_with_custom_keyboard(update, message: str, button_data: List[str]):
    """
    Sends a text message with a custom keyboard (not inline). Custom keyboards are displayed 
    below the message for easy user interaction.
    
    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send.
    :param button_data: A list of button labels that will appear on the custom keyboard.
    """
    # Split the button_data into rows (you can customize the number of buttons per row)
    buttons_per_row = 3
    keyboard = [button_data[i:i + buttons_per_row] for i in range(0, len(button_data), buttons_per_row)]
    
    # Create the reply markup for the custom keyboard
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Send the message with the custom keyboard
    await update.message.reply_text(message, reply_markup=reply_markup)

# Function to send a message with inline buttons
async def send_dynamic_message(update: Update, message: str, button_data: List[Tuple[str, str]]):
    """
    Sends a message with inline buttons dynamically created based on button_data.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send.
    :param button_data: A list of tuples with button text and callback_data (e.g., [("Button 1", "button_1"), ...]).
    
    Example Usage:
        button_data = [("Button 1", "button_1"), ("Button 2", "button_2")]
        await send_dynamic_message(update, "Here are your buttons:", button_data)
    """
    buttons = [InlineKeyboardButton(text, callback_data=callback_data) for text, callback_data in button_data]
    keyboard = InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)])
    
    await update.message.reply_text(message, reply_markup=keyboard)

# Function to send a photo with a caption
async def send_photo_with_message(update: Update, message: str, photo_url: str):
    """
    Sends a photo along with a text message.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send.
    :param photo_url: URL or path to the photo to send.
    
    Example Usage:
        await send_photo_with_message(update, "Check out this photo!", "http://example.com/photo.jpg")
    """
    await update.message.reply_photo(photo_url, caption=message)

# Function to send a document with a caption
async def send_document_with_message(update: Update, message: str, document_url: str):
    """
    Sends a document along with a text message.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send.
    :param document_url: URL or path to the document to send.
    
    Example Usage:
        await send_document_with_message(update, "Here is your document.", "http://example.com/document.pdf")
    """
    await update.message.reply_document(document_url, caption=message)

# Function to send a message with Markdown formatting
async def send_markdown_message(update: Update, message: str):
    """
    Sends a message with Markdown formatting.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send, formatted using Markdown.
    
    Example Usage:
        message = "*Bold Text*\n_Italic Text_"
        await send_markdown_message(update, message)
    """
    await update.message.reply_text(message, parse_mode="Markdown")

# Function to send a message with HTML formatting
async def send_html_message(update: Update, message: str):
    """
    Sends a message with HTML formatting.

    :param update: The update object that contains information about the message and the user.
    :param message: The text message to send, formatted using HTML.
    
    Example Usage:
        message = "<b>Bold Text</b><i>Italic Text</i>"
        await send_html_message(update, message)
    """
    await update.message.reply_text(message, parse_mode="HTML")
