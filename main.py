import time, asyncio
from bs4 import BeautifulSoup
from discord.ext import commands
import discord, os, json, requests

from datetime import datetime
from dotenv import load_dotenv


# All globals and loading env
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PRICE_PER_ROBUX = eval(os.environ.get("PRICE_PER_ROBUX"))
BOLD_API_KEY = os.environ.get("BOLD_API_KEY")
RBXCRATE_API_KEY = os.environ.get("RBXCRATE_API_KEY")

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
    
def set_review_channel(review_id: int):
    with open("./storage/server.json" , "r") as file:
        everything = json.load(file)
        everything["review_id"] = review_id
        
    with open("./storage/server.json" , "w") as file:
        json.dump(everything , file , indent=4)

def get_review_channel():
    with open("./storage/server.json" , "r") as file:
        return json.load(file)["review_id"]
    
def get_order_no():
    current_count = 0
    with open("./storage/server.json" , "r") as file:
        everything = json.load(file)
        current_count = everything["order_count"]
        everything["order_count"] += 1
        
    with open("./storage/server.json" , "w") as file:
        json.dump(everything , file , indent=4)
        
    return current_count

def generate_payment_details(user_id: int , gamepass_url: str):
    all_details = {}

    response = requests.get(url=gamepass_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    robux_amount = eval(soup.find(name="div" , attrs={"id": "item-container"})["data-expected-price"])
    username = soup.find(name="div" , attrs={"id": "item-container"})["data-seller-name"].replace("@" , "")
    placeid = int(soup.find(name="a" , class_="text-name text-overflow font-caption-body")["href"].split("PlaceId=")[-1].split("&")[0])
    
    url = "https://integrations.api.bold.co/online/link/v1"
    json_body = {
        "amount_type": "CLOSE",
        "amount": {
            "currency": "COP",
            "total_amount": f"{((robux_amount * PRICE_PER_ROBUX) // 100) * 100}",
            "tip_amount": 0
        }
    }
    headers = {
        "Authorization": f"x-api-key {BOLD_API_KEY}"
    }
    
    response = requests.post(url=url , json=json_body , headers=headers)
    all_details["payment_link"] = response.json()["payload"]["payment_link"]
    all_details["url"] = response.json()["payload"]["url"]
    all_details["robux_amount"] = int(robux_amount)
    all_details["total_price"] = ((robux_amount * PRICE_PER_ROBUX) // 100) * 100
    all_details["user_id"] = user_id
    all_details["username"] = username
    all_details["placeid"] = int(placeid)

    return all_details

def is_paid(payment_link: str):
    url = f"https://integrations.api.bold.co/online/link/v1/{payment_link}"
    headers = {
        "Authorization": f"x-api-key {BOLD_API_KEY}"
    }
    response = requests.get(url=url , headers=headers)
    if response.json()["status"] == "PAID":
        return True
    else:
        return False

def save_order_data(order_id, order_user_id, order_user_name, order_robux_amount, order_price):
    order_details = f"\n{order_id}, {order_user_id}, {order_user_name.replace(',', '')}, {order_robux_amount}, {order_price}"
    with open(f"./storage/orders.csv" , "a") as file:
        file.write(order_details)

def create_robux_order(all_details: dict):
    url = f"https://rbxcrate.com/api/orders/gamepass"
    headers = {
        "api-key": RBXCRATE_API_KEY
    }
    json_body = {
        "robloxUsername": all_details["username"],
        "orderId": f'{all_details["order_id"]}',
        "robuxAmount": all_details["robux_amount"],
        "placeId": all_details["placeid"],
        "isPreOrder": True,
        "checkOwnership": False
    }

    response = requests.post(url=url , headers=headers , json=json_body)
    print(response.json())
    return response.status_code


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
    if interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="Setting Category" , color=discord.Color.green())
        embed.add_field(name="Category Set To:" , value=f"{category}")
        embed.set_thumbnail(url=bot.user.avatar.url)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed.set_footer(text=f"{interaction.user} • {current_time}", icon_url=interaction.user.avatar.url)
        set_category(category_id=category.id)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Forbidden")

@bot.tree.command(name="set-review" , description="Command to set category of purchase channels")
async def set_review_command(interaction: discord.Interaction , channel: discord.TextChannel):
    if interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="Setting Review Channel" , color=discord.Color.green())
        embed.add_field(name="Review Channel Set To:" , value=f"{channel.mention}")
        embed.set_thumbnail(url=bot.user.avatar.url)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed.set_footer(text=f"{interaction.user} • {current_time}", icon_url=interaction.user.avatar.url)
        set_review_channel(review_id=channel.id)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Forbidden")


@bot.tree.command(name="buy" , description="Command to buy robux.")
async def buy_command(interaction: discord.Interaction , gamepass_url: str):
    await interaction.response.send_message(content="Please wait..." )
    payment_details = generate_payment_details(user_id=interaction.user.id , gamepass_url=gamepass_url)
    
    if payment_details["robux_amount"] < 358:
        return await interaction.edit_original_response(content="🔴Gamepass price less than 358 Robux🔴")

    category = interaction.guild.get_channel(get_category())
    if not category or not isinstance(category, discord.CategoryChannel):
        await interaction.response.send_message(f"🔴Category with ID '{get_category()}' not found!🔴")
        return
    
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True , send_messages=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True , send_messages=True),
    }
    order_id = get_order_no()
    payment_details["order_id"] = order_id
    channel = await category.create_text_channel(
        name=f"Order-{order_id}",
        overwrites=overwrites
    )

    embed = discord.Embed(
        title="Payment Details",
        description=f"Here are your payment details for purchasing Robux.",
        color=discord.Color.blue()
    )

    embed.add_field(name="Username", value=payment_details["username"], inline=False)
    embed.add_field(name="User ID", value=payment_details["user_id"], inline=False)
    embed.add_field(name="Place ID", value=payment_details["placeid"], inline=True)
    embed.add_field(name="Robux Amount", value=f"{payment_details['robux_amount']} R$", inline=True)
    embed.add_field(name="Total Price", value=f"${payment_details['total_price']}", inline=True)
    embed.add_field(name="Payment Link", value=f"{payment_details['payment_link']}", inline=False)
    embed.add_field(name="URL", value=f"[Visit Here]({payment_details['url']})", inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Thank you for using our service!")

    message = await channel.send(embed=embed)
    view = OrderView(payment_details=payment_details, channel=channel, message=message)
    await message.edit(embed=embed, view=view)
    
    return await interaction.edit_original_response(content=f"Order has been created successfully in {channel.mention}")


class OrderView(discord.ui.View):
    def __init__(self, payment_details: dict, channel: discord.TextChannel , message: discord.Message):
        super().__init__(timeout=None)
        self.payment_details = payment_details
        self.channel = channel
        self.message = message

    @discord.ui.button(label="Money Paid", style=discord.ButtonStyle.green)
    async def money_paid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if is_paid(payment_link=self.payment_details["payment_link"]):
            button.disabled = True
            embed = discord.Embed(title="Payment Status" , description="Money has been marked as paid!\nSending robux, please wait." , color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
            await self.message.edit(view=self)

            response_code = create_robux_order(all_details=self.payment_details)

            if response_code == 201:
                embed = discord.Embed(title="Order Status" , description="Order has been created successfully.\nYou will recieve your robux in some time.\nDeleting channel in 60s." , color=discord.Color.green())

                review_channel = interaction.guild.get_channel(get_review_channel())
                if not review_channel or not isinstance(review_channel, discord.TextChannel):
                    ...
                else:
                    embed.add_field(name="Review Drop" , value=f"Please leave a review at {review_channel.mention}")

                await interaction.followup.send(embed=embed)
                save_order_data(order_id=self.payment_details["order_id"] , order_user_id=self.payment_details["user_id"] , order_user_name=self.payment_details["username"] , order_robux_amount=self.payment_details["robux_amount"] , order_price=self.payment_details["total_price"])

                await asyncio.sleep(60)
                await self.channel.delete()

            elif response_code == 403:
                button.disabled = False
                await self.message.edit(view=self)
                embed = discord.Embed(title="Order Status" , description="Don't have enough funds right now.\n Please wait for some time and try again." , color=discord.Color.red())
                await interaction.followup.send(embed=embed)
            elif response_code == 404:
                button.disabled = False
                await self.message.edit(view=self)
                embed = discord.Embed(title="Order Status" , description="Gamepass not found or your user roblox client not found" , color=discord.Color.red())
                await interaction.followup.send(embed=embed)
            else:
                button.disabled = False
                await self.message.edit(view=self)
                embed = discord.Embed(title="Order Status" , description=f"Some other error occured: {response_code}" , color=discord.Color.red())
                await interaction.followup.send(embed=embed)

        else:
            embed = discord.Embed(title="Payment Status" , description="Money has not been marked as paid!" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

    # @discord.ui.button(label="Close Order", style=discord.ButtonStyle.red)
    # async def close_order_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     if not interaction.user.guild_permissions.administrator:
    #         await interaction.response.send_message(
    #             "You do not have the required permissions to close this order.", 
    #             ephemeral=True
    #         )
    #         return

    #     try:
    #         await self.channel.delete(reason=f"Order closed by {interaction.user}")
    #     except discord.Forbidden:
    #         await interaction.response.send_message(
    #             "I do not have the permissions to delete this channel.", 
    #             ephemeral=True
    #         )
    #     except discord.HTTPException as e:
    #         await interaction.response.send_message(
    #             f"An error occurred while trying to delete the channel: {str(e)}", 
    #             ephemeral=True
    #         )



# Running the bot:
bot.run(BOT_TOKEN)