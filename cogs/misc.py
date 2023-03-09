import discord
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


async def setup(bot):
    await bot.add_cog(Misc(bot))
