import discord
import io
from datetime import timedelta
from discord.ext import commands


class Moderation(commands.Cog):
    """Moderation related commands."""

    def __init__(self, bot):
        self.bot = bot
        print(f"Loaded {self.__class__.__name__} cog.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided."):
        """Kicks a member from the server."""
        has_attch = bool(ctx.message.attachments)
        if member == ctx.message.author:
            return await ctx.send("You can't kick yourself, obviously")
        elif ctx.author.top_role.position < member.top_role.position + 1:
            return await ctx.send("That person has a role higher than or equal to yours, you can't kick them.")
        else:
            embed = discord.Embed(title=f"{member} kicked")
            embed.description = f"{member} was kicked by {ctx.message.author} for:\n\n{reason}"
            try:
                if has_attch:
                    img_bytes = await ctx.message.attachments[0].read()
                    kick_img = discord.File(io.BytesIO(img_bytes), 'image.png')
                    log_img = discord.File(io.BytesIO(img_bytes), 'kick_image.png')
                    await member.send(f"You were kicked from {ctx.guild.name} for reason: `{reason}`.", file=kick_img)
                else:
                    await member.send(f"You were kicked from {ctx.guild.name} for reason: `{reason}`.")
            except discord.Forbidden:
                pass  # bot blocked or not accepting DMs
            if has_attch:
                embed.set_thumbnail(url="attachment://kick_image.png")
                await self.bot.mod_logs_channel.send(embed=embed, file=log_img)
            else:
                await self.bot.mod_logs_channel.send(embed=embed)
            if len(reason) > 512:
                await member.kick(reason=f"Failed to log reason, as reason length was {len(reason)}. Please check bot logs.")
            else:
                await member.kick(reason=reason)
            await ctx.send(f"Successfully kicked user {member}!")

    async def generic_ban_things(self, ctx, user, reason):
        has_attch = bool(ctx.message.attachments)
        if user.id == ctx.message.author.id:
            return await ctx.send("You can't ban yourself, obviously")
        try:
            member_guild = ctx.guild.get_member(user.id)
            if ctx.author.top_role.position < member_guild.top_role.position + 1:
                return await ctx.send("That person has a role higher than or equal to yours, you can't ban them.")
        except AttributeError:
            pass  # Happens when banning via id, as they have no roles if not on guild
        try:
            if has_attch:
                img_bytes = await ctx.message.attachments[0].read()
                ban_img = discord.File(io.BytesIO(img_bytes), 'ban_image.png')
                await user.send(f"You were banned from {ctx.guild.name} for: `{reason}`", file=ban_img)
            else:
                await user.send(f"You were banned from {ctx.guild.name} for `{reason}`")
        except discord.Forbidden:
            pass  # bot blocked or not accepting DMs
        embed = discord.Embed(title=f"{user} banned")
        embed.description = f"{user} was banned by {ctx.author} for:\n\n`{reason}`"
        if has_attch:
            ban_img = discord.File(io.BytesIO(img_bytes), 'ban_image.png')
            embed.set_thumbnail(url="attachment://ban_image.png")
            await self.bot.mod_logs_channel.send(embed=embed, file=ban_img)
        else:
            await self.bot.mod_logs_channel.send(embed=embed)
        if len(reason) > 512:
            await ctx.guild.ban(user, delete_message_days=0, reason=f"Failed to log reason as length was {len(reason)}. Please check bot logs.")
        else:
            await ctx.guild.ban(user, delete_message_days=0, reason=reason)
        await ctx.send(f"Successfully banned user {user}!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, *, reason="No reason provided."):
        """Bans a user."""
        if not member:  # Edge case in which UserConverter may fail to get a User
            return await ctx.send("Could not find user. They may no longer be in the global User cache. If you are sure this is a valid user, try `.banid` instead.")
        await self.generic_ban_things(ctx, member, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def banid(self, ctx, user: int, *, reason="No reason provided."):
        """Ban a user with their user ID, for use when a user is not in the global User cache."""
        user = await self.bot.fetch_user(user)
        if not user:
            return await ctx.send("This is not a valid discord user.")
        await self.generic_ban_things(ctx, user, reason)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration, *, reason="No reason provided."):
        """Mute a user using discord's timeout function. Units are m, h, d with an upper cap of 28 days (discord limit)"""
        cap_msg = ""
        if member == ctx.message.author:
            return await ctx.send("You can't mute yourself, obviously")
        if ctx.author.top_role.position < member.top_role.position + 1:
            return await ctx.send("That person has a role higher than or equal to yours, you can't time them out.")
        elif member.is_timed_out():
            return await ctx.send("That member is already timed out.")
        curr_time = discord.utils.utcnow()
        try:
            if int(duration[:-1]) == 0:
                return await ctx.send("You can't mute for a time length of 0.")
            elif duration.lower().endswith("m"):
                diff = timedelta(minutes=int(duration[:-1]))
            elif duration.lower().endswith("h"):
                diff = timedelta(hours=int(duration[:-1]))
            elif duration.lower().endswith("d"):
                diff = timedelta(days=int(duration[:-1]))
            else:
                await ctx.send("That's not an appropriate duration value.")
                return await ctx.send_help(ctx.command)
        except ValueError:
            await ctx.send("You managed to throw a ValueError! Congrats! I guess. Use one of the correct values, and don't mix and match. Bitch.")
            return await ctx.send_help(ctx.command)
        if diff.days > 28:
            diff = timedelta(hours=672)
            cap_msg = "\n\nTimeouts are limited to 28 days on Discord's side. The length of this timeout has been lowered to 28 days."
        end = curr_time + diff
        end_str = discord.utils.format_dt(end)
        try:
            await member.send(f"You have been timed out on {ctx.guild} for: `{reason}`\n\nYour timeout will expire on {end_str}.")
        except discord.Forbidden:
            pass  # blocked DMs
        embed = discord.Embed(title=f"{member} timed out")
        embed.add_field(name="Member", value=f"{member.mention} ({member.id})")
        embed.add_field(name="Timed out by", value=ctx.author)
        embed.add_field(name="Timed out until", value=end_str, inline=False)
        embed.add_field(name="Reason", value=reason)
        await self.bot.mod_logs_channel.send(embed=embed)
        await member.timeout(diff - timedelta(seconds=1), reason=reason)  # Reduce diff by 1 second due to communication_disabled_until when it's *exactly* 28 days
        await ctx.send(f"Successfully timed out {member} until {end_str}!{cap_msg}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
