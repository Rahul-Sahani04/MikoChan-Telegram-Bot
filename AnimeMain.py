from keep_alive import keep_alive

import os
from dotenv import load_dotenv

load_dotenv()

my_secret = os.environ.get("TOKEN")

import logging
import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TOKEN = my_secret

# Constants
RESULTS_PER_PAGE = 5  # Number of search results to display per page

results = None
page = 0
num_pages = 0

import random


def send_random_cute_message(update, context):
  cute_emojis = ['😊', '🥰', '😍', '🐻', '🐼', '🌸', '🌈', '🍩']
  messages = [
    "Enjoy!", "Here you go!", "I hope you enjoy!", "Oo", "let's watch!",
    "Now you can watch."
  ]

  random_emoji = random.choice(cute_emojis)
  random_message = random.choice(messages)

  text = f"{random_emoji} {random_message}"

  context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def update_bot_chat_id(context, sent_msg):
  # Get the message ID and chat ID of the sent message
  message_id = sent_msg.message_id
  chat_id = sent_msg.chat_id

  # Store the message ID and chat ID in user_data for later use
  context.user_data['prev_bot_chat_id'] = chat_id
  context.user_data['prev_bot_message_id'] = message_id


def update_user_chat_id(update, context):
  user_message_id = update.message.message_id
  user_chat_id = update.effective_chat.id

  context.user_data['prev_user_chat_id'] = user_chat_id
  context.user_data['prev_user_message_id'] = user_message_id


def start(update, context):
  context.user_data['page'] = 1
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text="Welcome to the Anime Bot!")


def go_back(update, context):
  context.user_data.pop('episode_id', None)  # Remove episode_id from user_data
  context.user_data.pop('anime_id', None)  # Remove anime_id from user_data
  context.user_data.pop('search_results',
                        None)  # Remove search_results from user_data
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text="You have gone back one step.")


def search(update, context):
  context.user_data['page'] = 1
  reply_markup = ReplyKeyboardMarkup([['/cancel']])
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text="Enter anime name to search:")
  return "SEARCH"


def process_search(update, context):
  query = update.message.text
  page = 1
  search_results = search_anime(query)
  context.user_data['search_results'] = search_results

  if search_results:
    total_results = len(search_results)
    num_pages = (total_results - 1) // RESULTS_PER_PAGE + 1
    context.user_data['num_pages'] = num_pages

    reply_markup = create_pagination_keyboard(context, page, num_pages)
    message = create_search_results_message(search_results, page, num_pages)
    sent_message = context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=message,
                                            reply_markup=reply_markup)

    update_bot_chat_id(context, sent_message)

  return "SELECT_ANIME"


def create_pagination_keyboard(context, current_page, num_pages):
  buttons = []
  # for page_num in range(1, num_pages + 1):
  #     buttons.append(f"/p {page_num}")
  page_number = context.user_data['page']
  num_pages = context.user_data['num_pages']
  if page_number <= num_pages:
    buttons.append("next")
  if page_number <= num_pages and page_number > 1:
    buttons.append("back")
  keyboard = []
  keyboard.append(buttons)
  keyboard.append(['/cancel', '/goback'])

  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_search_results_message(results, page, num_pages):
  start_index = (page - 1) * RESULTS_PER_PAGE
  end_index = start_index + RESULTS_PER_PAGE

  message = "Search results:\n"
  for i, result in enumerate(results[start_index:end_index],
                             start=start_index):
    message += f"{i+1}. {result['title']}\n"

  message += f"\nPage {page} of {num_pages}"  # Add page information to the message

  return message


def select_anime(update, context):

  if update.message.text == "next" or update.message.text == "back":
    page = context.user_data['page']
    update_user_chat_id(update, context)
    return select_page(update, context, page)
  elif update.message.text == "/cancel":
    cancel(update, context)
    return ConversationHandler.END
  elif update.message.text == "/search":
    return "SEARCH"
  elif update.message.text == "/start":
    return "START"

  selected_index = int(update.message.text) - 1
  search_results = context.user_data['search_results']
  selected_anime = search_results[selected_index]
  context.user_data['anime_id'] = selected_anime['id']

  anime_info = get_anime_info(selected_anime['id'])
  message, image, total_ep = get_anime_details(anime_info)
  reply_markup = ReplyKeyboardMarkup([['/goback']])
  context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text=message,
                           reply_markup=reply_markup)
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text=f"Select an episode (Total: {total_ep}): ")

  return "SELECT_EPISODE"


def select_page(update, context, page):
  # page_number = int(update.message.text[2:])
  # print(page_number)
  page_number = context.user_data['page']
  num_pages = context.user_data['num_pages']
  search_results = context.user_data['search_results']

  if update.message.text == "/cancel":
    cancel(update, context)
  if update.message.text == "next" and page_number < num_pages:
    page_number = page + 1
  if update.message.text == "back" and page_number <= num_pages and page_number > 1:
    page_number = page - 1

  if 1 <= page_number <= num_pages:
    page = page_number
    context.user_data['page'] = page
    reply_markup = create_pagination_keyboard(context, page, num_pages)
    message = create_search_results_message(search_results, page, num_pages)

    chat_id = context.user_data['prev_bot_chat_id']
    msg_id = context.user_data['prev_bot_message_id']

    user_chat_id = context.user_data['prev_user_chat_id']
    user_msg_id = context.user_data['prev_user_message_id']
    context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    context.bot.delete_message(chat_id=user_chat_id, message_id=user_msg_id)
    send_msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=message,
                                        reply_markup=reply_markup)
    update_bot_chat_id(context, send_msg)

  return "SELECT_ANIME"


def get_anime_info(anime_id):
  url = f"https://api.consumet.org/anime/gogoanime/info/{anime_id}"
  response = requests.get(url)
  return response.json()


def get_anime_details(anime_info):
  title = anime_info['title']
  total_episodes = anime_info['totalEpisodes']
  release_date = anime_info['releaseDate']
  description = anime_info['description']

  message = f"Title: {title}\n"
  message += f"Total Episodes: {total_episodes}\n"
  message += f"Release Date: {release_date}\n"
  message += f"Description: {description}"
  image_url = anime_info['image']
  return message, image_url, total_episodes


def select_episode(update, context):
  selected_episode_number = int(update.message.text)
  anime_id = context.user_data['anime_id']
  print("ID: ", anime_id)
  anime_info = get_anime_info(anime_id)
  episodes = anime_info["episodes"]
  print("Episode 1: ", episodes[0])
  selected_episode_id = None
  for episode in episodes:
    if episode['number'] == selected_episode_number:
      selected_episode_id = episode['id']
      break
  if selected_episode_id:
    context.user_data['episode_id'] = selected_episode_id
    episode_sources = get_episode_sources(selected_episode_id)
    if "headers" in episode_sources:
      first_source = episode_sources["sources"][0]
      head = episode_sources["headers"]
      streamlink = head["Referer"]
      context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Stream Link for episode {selected_episode_number}: {streamlink}"
      )
      send_random_cute_message(update, context)
    else:
      context.bot.send_message(chat_id=update.effective_chat.id,
                               text="Episode sources not found.")
  else:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Selected episode not found.")
  return ConversationHandler.END


def get_episode_sources(episode_id):
  url = f"https://api.consumet.org/anime/gogoanime/watch/{episode_id}"
  response = requests.get(url)
  data = response.json()
  if data:
    return data
  else:
    return None


def cancel(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text="Search canceled.")
  return ConversationHandler.END


# def search_anime(query):
#     url = f"https://api.consumet.org/anime/gogoanime/{query}?page={page}"
#     response = requests.get(url)
#     return response.json()


def search_anime(query):
  results = []
  page = 1
  has_next_page = True

  while has_next_page:
    # print(page)
    url = f"https://api.consumet.org/anime/gogoanime/{query}?page={page}"
    response = requests.get(url)
    data = response.json()
    # print(data.get("hasNextPage"))
    # Append the current page results to the overall results
    results.extend(data.get("results", []))

    # Check if there is a next page
    has_next_page = data.get("hasNextPage", False)

    # Increment the page number for the next iteration
    page += 1
  # file = open('data.json', 'w')
  # file.write(str(results))
  return results


def main():
  updater = Updater(TOKEN, use_context=True)

  dp = updater.dispatcher

  conv_handler = ConversationHandler(
    entry_points=[CommandHandler('search', search)],
    states={
      "SEARCH":
      [MessageHandler(Filters.text & ~Filters.command, process_search)],
      "SELECT_ANIME": [MessageHandler(Filters.text, select_anime)],
      "SELECT_EPISODE":
      [MessageHandler(Filters.text & ~Filters.command, select_episode)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
  )

  dp.add_handler(CommandHandler('start', start))
  dp.add_handler(CommandHandler('goback', go_back))
  dp.add_handler(conv_handler)

  updater.start_polling()
  updater.idle()


if __name__ == '__main__':
  keep_alive()
  main()
