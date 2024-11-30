from discord.ext import commands
import discord, os, json, requests

from datetime import datetime
from dotenv import load_dotenv


# All globals and loading env
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PRICE_PER_ROBUX = int(os.environ.get("PRICE_PER_ROBUX"))
BOLD_API_KEY = os.environ.get("BOLD_API_KEY")

# All related methods:
def set_category(category_id: int):
    with open("./storage/server.json" , "r") as file:
        everything = json.load(file)
        everything["category_id"] = category_id
        
    with open("./storage/server.json" , "w") as file:
        json.dump(everything , file , indent=4)
    
    
def get_category():
    with open("./storage/server.json" , "r") as file:
        return json.load(file)["category_id"]
    
def get_order_no():
    current_count = 0
    with open("./storage/server.json" , "r") as file:
        everything = json.load(file)
        current_count = everything["order_count"]
        everything["order_count"] += 1
        
    with open("./storage/server.json" , "w") as file:
        json.dump(everything , file , indent=4)
        
    return current_count

def generate_payment_details(robux_amount: int , user_id: int):
    all_details = {}
    
    url = "https://integrations.api.bold.co/online/link/v1"
    json_body = {
        "amount_type": "CLOSE",
        "amount": {
            "currency": "COP",
            "total_amount": f"{robux_amount * PRICE_PER_ROBUX}",
            "tip_amount": 0
        }
    }
    headers = {
        "Authorization": f"x-api-key {BOLD_API_KEY}"
    }
    
    response = requests.post(url=url , json=json_body , headers=headers)
    all_details["payment_link"] = response.json()["payload"]["payment_link"]
    all_details["url"] = response.json()["payload"]["url"]
    all_details["robux_amount"] = robux_amount
    all_details["total_price"] = robux_amount * PRICE_PER_ROBUX
    all_details["user_id"] = user_id

    return all_details

def save_order_data(order_id, order_user_id, order_user_name, order_robux_amount, order_price):
    order_details = f"{order_id}, {order_user_id}, {order_user_name.replace(',', '')}, {order_robux_amount}, {order_price}\n"
    with open(f"./storage/orders.csv" , "a") as file:
        file.write(order_details)

# Main bot commands:
bot = commands.Bot(command_prefix="!" , intents=discord.Intents().all())

@bot.event
async def on_ready():
    print(f"🟢 | Bot loaded")
    print(f"🟢 | Username: {bot.user.name}")
    print(f"🟢 | User Id: {bot.user.id}")
    
    await bot.tree.sync()
    
@bot.tree.command(name="set-category" , description="Command to set category of purchase channels")
async def set_category_command(interaction: discord.Interaction , category: discord.CategoryChannel):
    embed = discord.Embed(title="Setting Category" , color=discord.Color.green())
    embed.add_field(name="Category Set To:" , value=f"{category}")
    embed.set_thumbnail(url=bot.user.avatar.url)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"{interaction.user} • {current_time}", icon_url=interaction.user.avatar.url)
    set_category(category_id=category.id)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy")
async def buy_command(interaction: discord.Interaction , robux_amount: int , roblox_username: str , place_id: int):
    if robux_amount < 35:
        return await interaction.response.send_message(f"🔴Minimum amount to purchase is 35 Robux!🔴")
    
    payment_details = generate_payment_details(robux_amount=robux_amount , user_id=interaction.user.id)
    payment_details["roblox_username"] = roblox_username
    payment_details["place_id"] = place_id
    
    category = interaction.guild.get_channel(get_category())
    if not category or not isinstance(category, discord.CategoryChannel):
        await interaction.response.send_message(f"🔴Category with ID '{get_category()}' not found!🔴", ephemeral=True)
        return
    
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True , send_messages=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True , send_messages=True),
    }
    
    channel = await category.create_text_channel(
        name=f"Order-{get_order_no()}",
        overwrites=overwrites
    )
    
    await interaction.response.send_message("Done")

# Running the bot:
bot.run(BOT_TOKEN)