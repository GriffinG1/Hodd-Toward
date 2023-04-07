import discord
from discord.ext import commands
from datetime import datetime


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(f"Loaded {self.__class__.__name__} cog.")

    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Add role to new member
        try:
            role = discord.utils.get(member.guild.roles, id=self.bot.roles["server_stuff"]["join_role"])
            await member.add_roles(role)
        except KeyError:
            await self.bot.err_logs_channel.send(f"❌ Failed to give {member.mention} the join role. The role is not set. Use `set_join_role` to set it.")

        # Send welcome message
        message = f"Welcome to {self.bot.guild.name}, {member.mention}! Please read through <#1067004379904872448> and <#1083198618837721129>, and send a message here to introduce yourself!\n\nPlease note that you will not be able to access some channels until you have been an active member for a bit, as a safety measure."
        await self.bot.join_channel.send(message)

        # Log joins
        embed = discord.Embed(title="Member Joined", colour=discord.Colour.green())
        embed.add_field(name="Member", value=f"{member.mention} | {member}", inline=False)
        embed.add_field(name="Joined At", value=discord.utils.format_dt(member.joined_at, style="F"), inline=False)
        await self.bot.mod_logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member Left", colour=discord.Colour.red())
        embed.add_field(name="Member", value=f"{member.mention} | {member}", inline=False)
        embed.add_field(name="Joined At", value=discord.utils.format_dt(member.joined_at, style="F"), inline=False)
        embed.add_field(name="Left At", value=discord.utils.format_dt(datetime.now(), style="F"), inline=False)
        await self.bot.mod_logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        role = discord.utils.get(self.bot.guild.roles, id=self.bot.roles["server_stuff"]["join_role"])
        if role in before.roles and role not in after.roles:
            embed = discord.Embed(title="New Member Role Removed", colour=discord.Colour.blue())
            embed.add_field(name="Member", value=f"{after.mention} | {after}", inline=False)
            embed.add_field(name="Joined At", value=discord.utils.format_dt(after.joined_at, style="F"), inline=False)
            embed.add_field(name="Role Removed At", value=discord.utils.format_dt(datetime.now(), style="F"), inline=False)
            await self.bot.mod_logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
