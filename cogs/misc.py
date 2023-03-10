import discord
import json
from discord.ext import commands


class Misc(commands.Cog):
    """Commands for miscellaneous things."""

    def __init__(self, bot):
        self.bot = bot
        print(f"Loaded {self.__class__.__name__} cog.")

    @commands.command(name="steal")
    async def steal_emote(self, ctx, emotes: commands.Greedy[discord.PartialEmoji]):
        """Steals emotes from other servers."""
        new_emotes = []
        for emote in emotes:
            new_emotes.append(await ctx.guild.create_custom_emoji(name=emote.name, image=(await emote.read())))
        await ctx.send(f"✅ Successfully stole {len(new_emotes)} emote(s).\n{', '.join([str(emote) for emote in new_emotes])}")

    @commands.has_permissions(manage_guild=True)
    @commands.command(hidden=True)
    async def set_join_role(self, ctx, role: discord.Role):
        """Sets the role to be given to new members."""
        self.bot.roles["server_stuff"]["join_role"] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Set join role to `{str(role)}`.")


async def setup(bot):
    await bot.add_cog(Misc(bot))
