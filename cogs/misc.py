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

    @commands.has_permissions(manage_guild=True)
    @commands.command(hidden=True)
    async def set_colorado_role(self, ctx, role: discord.Role):
        """Sets the role to be given to colorado peeps."""
        self.bot.roles["server_stuff"]["colorado_role"] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Set Colorado role to `{str(role)}`.")

    @commands.command(aliases=['ui', 'user'])
    async def userinfo(self, ctx, user: discord.Member = None, depth=False):
        """Pulls a user's info. Passing no member returns your own. depth is a bool that will specify account creation and join date, and account age"""
        if not user:
            user = ctx.author
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"User info for {user} ({user.id})", icon_url=str(user.display_avatar))
        if user.nick:
            embed.add_field(name="Nickname", value=user.nick)
        embed.add_field(name="Avatar Link", value=f"[Here]({str(user.display_avatar)})")
        status = str(user.status).capitalize()
        if user.is_on_mobile():
            status += " (Mobile)"
        embed.add_field(name="Status", value=status)
        if user.activity and not depth:
            embed.add_field(name="Top Activity", value=f"`{user.activity}`")
        if len(user.roles) > 1 and not depth:
            embed.add_field(name="Highest Role", value=user.top_role)
        embed.add_field(name="Created At", value=f"{discord.utils.format_dt(user.created_at)}")
        embed.add_field(name="Joined At", value=f"{discord.utils.format_dt(user.joined_at)}")
        acc_age_days = (discord.utils.utcnow() - user.created_at).days
        acc_age_years = acc_age_days // 365
        acc_age_months = (acc_age_days % 365) // 30
        embed.add_field(name="Account Age", value=f"About {acc_age_years} Years, {acc_age_months} Months, {(acc_age_days % 365) % 30} Days")
        if depth:
            embed.add_field(name=u"\u200B", value=u"\u200B", inline=False)
            if len(user.roles) > 1:
                embed.add_field(name="Roles", value=f"`{'`, `'.join(role.name for role in user.roles[1:])}`")
            if len(user.activities) > 0:
                embed.add_field(name="Activities" if len(user.activities) > 1 else "Activity", value=f"`{'`, `'.join(str(activity.name) for activity in user.activities)}`", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['fui'])
    async def fetch_userinfo(self, ctx, user: discord.User):
        """Pulls a discord.User instead of discord.Member. More limited than userinfo"""
        embed = discord.Embed(colour=user.colour)
        embed.set_author(name=f"User info for {user} ({user.id})", icon_url=str(user.display_avatar))
        embed.add_field(name="Avatar Link", value=f"[Here]({str(user.display_avatar)})")
        embed.add_field(name="Created At", value=f"{discord.utils.format_dt(user.created_at)}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['si', 'guild', 'gi', 'server', 'serverinfo'])
    async def guildinfo(self, ctx, depth=False):
        embed = discord.Embed()
        embed.set_author(name=f"Guild info for {ctx.guild.name} ({ctx.guild.id})", icon_url=str(ctx.guild.icon))
        embed.add_field(name="Guild Owner", value=f"{ctx.guild.owner} ({ctx.guild.owner.mention})")
        embed.add_field(name="Highest Role", value=f"{ctx.guild.roles[-1].name} ({ctx.guild.roles[-1].id})")
        embed.add_field(name="Member Count", value=f"{len([member for member in ctx.guild.members if not member.bot])} members, {len([member for member in ctx.guild.members if member.bot])} bots\n({ctx.guild.member_count} total)")
        embed.add_field(name="Channel Count", value=f"{len([channel for channel in ctx.guild.channels if not isinstance(channel, discord.CategoryChannel)])} channels in {len(ctx.guild.categories)} categories\n({len(ctx.guild.text_channels)} text, {len(ctx.guild.voice_channels)} voice)")
        embed.add_field(name="Emoji Slots", value=f"{len(ctx.guild.emojis)}/{ctx.guild.emoji_limit} slots used")
        embed.add_field(name="Role Count", value=str(len(ctx.guild.roles)))
        if depth:
            since_creation = (discord.utils.utcnow() - ctx.guild.created_at).days
            embed.add_field(name="Created At", value=f"{discord.utils.format_dt(ctx.guild.created_at)}")
            embed.add_field(name="Server Age", value=f"{discord.utils.format_dt(ctx.guild.created_at, 'R')} ({since_creation} days ago)")
            embed.add_field(name="Total Boosts", value=f"{ctx.guild.premium_subscription_count} boosters (Current level: {ctx.guild.premium_tier})")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Misc(bot))
