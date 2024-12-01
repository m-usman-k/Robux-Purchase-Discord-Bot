# Robux Purchase Bot

This is a Discord bot designed to facilitate the purchase of Robux through game passes. It allows users to order Robux, make payments, and track their orders directly within Discord.

## Features

- **Set Category Channel:** Set the category where purchase-related channels will be created.
- **Set Review Channel:** Set the channel where users can leave reviews after purchasing Robux.
- **Create Order:** Users can place an order to buy Robux by providing a game pass URL.
- **Payment System:** The bot integrates with the Bold API to generate payment links for the purchase of Robux.
- **Order Management:** Automatically creates an order channel, sends payment details, and tracks the payment status.
- **Robux Delivery:** If the payment is successful, Robux is delivered to the user through the RBX Crate API.

## Prerequisites

- Python 3.8+
- Libraries: `discord.py`, `requests`, `beautifulsoup4`, `dotenv`
- A Discord bot token
- API keys for Bold API and RBX Crate API

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/m-usman-k/Robux-Purchase-Discord-Bot.git
   cd Robux-Purchase-Discord-Bot
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following content:

   ```env
   BOT_TOKEN=your_discord_bot_token
   PRICE_PER_ROBUX=your_price_per_robux_value
   BOLD_API_KEY=your_bold_api_key
   RBXCRATE_API_KEY=your_rbxcrate_api_key
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

### `!set-category <category_channel>`

Sets the category for the purchase channels. Only accessible by users with administrator permissions.

### `!set-review <review_channel>`

Sets the channel for users to leave reviews. Only accessible by users with administrator permissions.

### `!buy <gamepass_url>`

Initiates the Robux purchase process. Requires a valid game pass URL. The bot will generate payment details, including a link to process the payment.

## File Structure

- `bot.py`: Main bot file that contains all the commands and logic.
- `storage/`: Directory where the bot stores server-related data (e.g., `server.json`, `orders.csv`).
- `.env`: File containing the bot token and API keys (ensure this is not public).
- `requirements.txt`: List of Python dependencies for the project.

## Configuration

### `server.json`

This file contains important data related to the bot's setup:

- `category_id`: The ID of the category channel where orders will be created.
- `review_id`: The ID of the channel where users can leave reviews.
- `order_count`: A counter for the number of orders placed.

### `orders.csv`

This file stores the details of all orders placed, including user ID, username, order ID, Robux amount, and total price.

## Contributing

Feel free to fork this project, submit issues, or create pull requests with improvements or fixes. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
