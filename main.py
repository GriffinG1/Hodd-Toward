import discord
import os
import json
import shutil
import psutil
import traceback
import asyncio
from discord.ext import commands


description = "It just works"

if not os.path.exists("config.json"):
    shutil.copy("config.json.sample", "config.json")
    print("Please edit the config.json file and restart the bot.")

with open("config.json") as f:
    config = json.load(f)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

token = config["token"]
prefix = config["prefix"]

if token == "" or len(prefix) == 0:
    print("Please edit the config.json file and restart the bot.")

intents = discord.Intents.all()
intents.members = True
intents.presences = True
intents.message_content = True
help_cmd = commands.DefaultHelpCommand(show_parameter_descriptions=False)
bot = commands.Bot(command_prefix=prefix, description=description, intents=intents, help_command=help_cmd)

bot.ready = False
bot.is_beta = config["is_beta"]


@bot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        raise commands.NoPrivateMessage("This command cannot be used in DMs.")
        return False
    return True


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("You are missing required arguments.")
        await ctx.send_help(ctx.command)
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("You cannot use this command in DMs! Please go to <#1078220948622295120> to use this command.")
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send("A bad argument was provided, please try again.")
    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention} This command is on a cooldown.")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is currently disabled.")
    else:
        if ctx.command:
            await ctx.send(f"An error occurred while processing the `{ctx.command.name}` command.")
        print(f'Ignoring exception in command {ctx.command} in {ctx.message.channel}')
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        error_trace = "".join(tb)
        print(error_trace)
        embed = discord.Embed(description=error_trace.replace("__", "_\\_").replace("**", "*\\*"))
        await bot.err_logs_channel.send(f"An error occurred while processing the `{ctx.command.name}` command in channel `{ctx.message.channel}`.", embed=embed)


@bot.event
async def on_error(event_method, *args, **kwargs):
    print(args[0])
    if isinstance(args[0], commands.errors.CommandNotFound):
        return
    print(f"Ignoring exception in {event_method}")
    tb = traceback.format_exc()
    error_trace = "".join(tb)
    print(error_trace)
    embed = discord.Embed(description=error_trace.replace("__", "_\\_").replace("**", "*\\*"))
    await bot.err_logs_channel.send(f"An error occurred while processing `{event_method}`.", embed=embed)


@bot.event
async def on_ready():
    bot.guild = bot.get_guild(config["guild_id"])

    bot.err_logs_channel = discord.utils.get(bot.guild.channels, id=1078386362828472491)
    bot.bot_channel = discord.utils.get(bot.guild.channels, id=1078220948622295120)
    bot.mods_role = discord.utils.get(bot.guild.roles, id=1078179931705577543)
    bot.creator = await bot.fetch_user(177939404243992578)

    print(f"Started up on {bot.guild.name}!")
    bot.ready = True

cogs = [
    "cogs.events",
    "cogs.mod",
    "cogs.roles"
]


async def setup_cogs(bot):
    return  # TODO: Add cogs
    failed_cogs = []
    for cog in cogs:
        try:
            await bot.load_extension(cog)
        except Exception as exception:
            print(f"{cog} failed to load.\n{type(exception).__name__}: {exception}")
            failed_cogs.append(cog)
    if not failed_cogs:
        print("All cogs loaded successfully!")
    else:
        print(f"{len(failed_cogs)} cogs failed to load.")


@bot.command(hidden=True)
async def load(ctx, cog):
    """Loads a cog."""
    if ctx.author != bot.creator:
        raise commands.CheckFailure()
    if not cog.startswith("cogs."):
        cog = f"cogs.{cog}"
    try:
        await bot.load_extension(cog)
    except Exception as exception:
        return await ctx.send(f"❌ Failed!\n```{type(exception).__name__}: {exception}```")
    await ctx.send(f"✅ Loaded `{cog}`.")


@bot.command(hidden=True)
async def unload(ctx, cog):
    """Unloads a cog."""
    if ctx.author != bot.creator:
        raise commands.CheckFailure()
    if not cog.startswith("cogs."):
        cog = f"cogs.{cog}"
    try:
        await bot.unload_extension(cog)
    except Exception as exception:
        return await ctx.send(f"❌ Failed!\n```{type(exception).__name__}: {exception}```")
    await ctx.send(f"✅ Unloaded `{cog}`.")


@bot.command(hidden=True)
async def reload(ctx, cog=None):
    """Reloads all cogs or a specific cog."""
    if ctx.author != bot.creator:
        raise commands.CheckFailure()
    if not cog:
        errors = []
        cog_dict = {
            "Events": "events",
            "Moderation": "mod",
            "Roles": "roles"
        }
        loaded_cogs = bot.cogs.copy()
        for loaded_cog in loaded_cogs:
            try:
                await bot.reload_extension(f"cogs.{cog_dict[loaded_cog]}")
            except Exception as exception:
                if loaded_cog not in cog_dict:
                    pass  # ignore cogs that aren't in the cog_dict
                errors.append(f"❌ Failed to reload `{loaded_cog}.py`.\n```{type(exception).__name__}: {exception}```")
        if not errors:
            return await ctx.send("✅ Reloaded all cogs.")
        else:
            return await ctx.send("\n".join(errors))
    if not cog.startswith("cogs."):
        cog = f"cogs.{cog}"
    try:
        await bot.reload_extension(cog)
    except Exception as exception:
        return await ctx.send(f"❌ Failed!\n```{type(exception).__name__}: {exception}```")
    await ctx.send(f"✅ Reloaded `{cog}`.")


@bot.command(hidden=True)
async def ping(ctx):
    """Get time between HEARTBEAT and HEARTBEAT_ACK in ms."""
    ping = bot.latency * 1000
    ping = round(ping, 3)
    await ctx.send(f"🏓 Pong! `{ping}ms`")


@bot.command(hidden=True)
async def restart(ctx):
    """Restarts the bot."""
    if ctx.author != bot.creator:
        raise commands.CheckFailure()
    await ctx.send("Restarting...")
    await bot.close()


@bot.command()
async def about(ctx):
    """Information about the bot."""
    embed = discord.Embed()
    embed.description = ("Python bot utilizing [discord.py](https://github.com/Rapptz/discord.py) for use in the Denver Capitol Hill Gays Discord server. It just works.\n"
                         "You can view the source code [here](https://github.com/GriffinG1/Hodd-Toward).\n"
                         f"Written and maintained by {bot.creator.mention}.")
    embed.set_author(name="GriffinG1", url='https://github.com/GriffinG1', icon_url='https://avatars0.githubusercontent.com/u/28538707')
    total_mem = psutil.virtual_memory().total / float(1 << 30)
    used_mem = psutil.Process().memory_info().rss / float(1 << 20)
    embed.set_footer(text=f"{round(used_mem, 2)} MB used out of {round(total_mem, 2)} GB")
    await ctx.send(embed=embed)


async def main():
    print("Bot directory: ", dir_path)
    async with bot:
        await setup_cogs(bot)
        await bot.start(token)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
