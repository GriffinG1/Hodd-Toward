import discord
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(f"Loaded {self.__class__.__name__} cog.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Gives new members the join role."""
        try:
            role = discord.utils.get(member.guild.roles, id=self.bot.roles["server_stuff"]["join_role"])
            await member.add_roles(role)
        except KeyError:
            await self.bot.err_logs_channel.send(f"❌ Failed to give {member.mention} the join role. The role is not set. Use `set_join_role` to set it.")


async def setup(bot):
    await bot.add_cog(Events(bot))
