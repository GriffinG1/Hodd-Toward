import discord
import functools
from discord.ext import commands


class Roles(commands.Cog):
    """Commands for managing roles."""

    def __init__(self, bot):
        self.bot = bot
        self.roles = {
            # Pronouns
            "they": 1078180553704091668,
            "she": 1078180522624307310,
            "he": 1078180484640669777,
            "any": 1078180610939568218,

            # Location
            "uptown": 1078182681554194513,
            "caphill": 1078182733743919114,
            "cheesman": 1078182767373856778,
            "other": 1078210712884748338
        }
        print(f"Loaded {self.__class__.__name__} cog.")

    def channel_is_bot_commands(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if ctx.author == self.bot.creator:
                pass
            elif ctx.channel != self.bot.bot_channel:
                await ctx.message.delete()
                return await ctx.send(f"❌ {ctx.author.mention} Please use this command in {self.bot.bot_channel.mention}.", delete_after=10)
            await func(self, ctx, *args, **kwargs)
        return wrapper

    async def handle_roles(self, member, role, is_location=False):
        """Handles role assignment."""
        if role not in member.roles:
            await member.add_roles(role)
            if is_location:
                return "✅ Added location role for {}.\n"
            return "✅ Added pronoun role for `{}`.\n"
        await member.remove_roles(role)
        if is_location:
            return "✅ Removed location role for {}.\n"
        return "✅ Removed pronoun role for `{}`.\n"

    @commands.command(aliases=["pronouns"])
    @channel_is_bot_commands
    async def set_pronouns(self, ctx, *, pronouns: str):
        """Sets your pronouns. Use again to remove. Currently supported pronouns: they, she, he, any. Please ask a mod if yours aren't available.
        Please note that combined pronouns (ex she/they) are not supported, please separate them. (ex she | they)
        Example: .set_pronouns they | she > adds the pronoun roles for they/them and she/her"""
        pronouns = pronouns.lower().replace(" ", "").split("|")
        message = ""
        invalid_pronouns = []
        for pronoun in pronouns:
            if pronoun == "they" or pronoun == "them" or pronoun == "they/them":
                message += (await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["they"]))).format("they/them")
            elif pronoun == "she" or pronoun == "her" or pronoun == "she/her":
                message += (await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["she"]))).format("she/her")
            elif pronoun == "he" or pronoun == "him" or pronoun == "he/him":
                message += (await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["he"]))).format("he/him")
            elif pronoun == "any":
                message += (await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["any"]))).format("any")
            else:
                invalid_pronouns.append(pronoun)
        if invalid_pronouns:
            message += f"❌ Some pronouns were not recognized. Please ask a mod if yours aren't available.\nUnrecognized pronouns: `{'`, `'.join(invalid_pronouns)}`"
        await ctx.send(message)

    @commands.command(aliases=["location"])
    @channel_is_bot_commands
    async def set_location(self, ctx, *, location: str):
        """Set your location in Cap Hill. Use again to remove. Currently supported locations: Uptown, Capitol Hill, Cheesman Park, Other. See #resources for more info."""
        if location.lower() == "uptown":
            message = await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["uptown"]), True)
            return await ctx.send(message.format("Uptown"))
        elif location.lower() == "caphill" or location.lower() == "capitol hill" or location.lower() == "cap hill":
            message = await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["caphill"]), True)
            return await ctx.send(message.format("Capitol Hill"))
        elif location.lower() == "cheesman" or location == "cheesman park":
            message = await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["cheesman"]), True)
            return await ctx.send(message.format("Cheesman Park"))
        message = await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["other"]), True)
        return await ctx.send(message.format("Other"))


async def setup(bot):
    await bot.add_cog(Roles(bot))
