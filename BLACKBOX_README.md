 # Anime Search Bot

This is a Telegram bot that allows users to search for anime and watch episodes. The bot uses the Gogoanime API to search for anime and get episode sources.

## Prerequisites

- Python 3.6 or later
- The Python Telegram Bot API library
- The requests library
- The csv library
- The dotenv library

## Setup

1. Clone the repository.
2. Create a `.env` file in the project directory and add your Telegram bot token to it.
3. Install the required Python libraries.
4. Run the bot.

## Usage

To use the bot, send a message to the bot with the command `/start`. The bot will then send you a message with instructions on how to use it.

To search for an anime, send a message to the bot with the command `/search` followed by the name of the anime. The bot will then send you a list of search results.

To select an anime, send a message to the bot with the number of the anime in the search results. The bot will then send you a message with information about the anime and a list of episodes.

To select an episode, send a message to the bot with the number of the episode. The bot will then send you a message with a link to the episode.

## Code Explanation

The code for the bot is divided into two files: `AnimeMain.py` and `keep_alive.py`.

`AnimeMain.py` contains the main code for the bot. It includes the following functions:

- `start()`: This function is called when the bot is started. It sends a message to the user with instructions on how to use the bot.
- `search()`: This function is called when the user sends the `/search` command. It sends a message to the user with a list of search results.
- `process_search()`: This function is called when the user selects an anime from the search results. It sends a message to the user with information about the anime and a list of episodes.
- `select_anime()`: This function is called when the user selects an episode from the list of episodes. It sends a message to the user with a link to the episode.
- `cancel()`: This function is called when the user sends the `/cancel` command. It sends a message to the user that the search has been canceled.

`keep_alive.py`: This file ensures the bot remains active by utilizing a Flask web server. It prevents the bot from going offline due to inactivity.

## Protecting Your Data
To ensure security, store sensitive data like your Telegram bot token as environment variables in the .env file. This prevents your credentials from being exposed in the codebase.
## Contributing
Contributions are welcome! If you find any issues or improvements, feel free to open a pull request.

## License
This project is licensed under the [MIT License](https://mit-license.org/).

Feel free to reach out if you have any questions or need assistance with the Anime Search Bot!

---

Happy coding!