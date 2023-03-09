import discord
import os
import json
from discord.ext import commands


class Roles(commands.Cog):
    """Commands for managing roles."""

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists("data/roles.json"):
            with open("data/roles.json", "w") as file:
                json.dump({}, file, indent=4)
        with open("data/roles.json", "r") as file:
            self.roles = json.load(file)
        print(f"Loaded {self.__class__.__name__} cog.")

    async def handle_roles(self, member, role_name):
        """Handles role assignment."""
        if role_name not in self.roles["pronouns"].keys():
            return False
        role = discord.utils.get(member.guild.roles, id=self.roles["pronouns"][role_name])
        if role not in member.roles:
            await member.add_roles(role)
            return "✅ Added pronoun role for `{}`.\n"
        await member.remove_roles(role)
        return "✅ Removed pronoun role for `{}`.\n"

    @commands.command(aliases=["pronouns"])
    async def set_pronouns(self, ctx, *, pronouns: str):
        """Sets your pronouns. Use again to remove.
        Please note that combined pronouns (ex she/they) are not supported, please separate them. (ex she | they).
        You can use ?lp for a list of pronouns.
        Please ask for help if your pronouns aren't available.

        Example: ?set_pronouns they | she > adds the pronoun roles for they/them and she/her"""
        pronouns = pronouns.lower().replace(" ", "").split("|")
        message = ""
        invalid_pronouns = []
        for pronoun in pronouns:
            resp = await self.handle_roles(ctx.author, pronoun)
            if not resp:
                invalid_pronouns.append(pronoun)
                continue
            else:
                message += resp.format(pronoun)
        if invalid_pronouns:
            message += f"❌ Some pronouns were not recognized. Please ask a mod if yours aren't available.\nUnrecognized pronouns: `{'`, `'.join(invalid_pronouns)}`"
        await ctx.send(message)

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["addpronouns"])
    async def add_pronoun(self, ctx, pronoun: str, role: discord.Role):
        """Adds a pronoun role to the list of available roles.
        Example: ?add_pronoun they @they/them"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun in self.roles["pronouns"].keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is already in the list. Please use `.edit_pronoun` to edit it.")
        self.roles["pronouns"][pronoun] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Added pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["editpronouns"])
    async def edit_pronoun(self, ctx, pronoun: str, new_role: discord.Role):
        """Edits a pronoun role in the list of available roles.
        Example: ?edit_pronoun they @they/them"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.roles.keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list. Please use `.add_pronoun` to add it.")
        self.roles["pronouns"][pronoun] = new_role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Edited pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["removepronouns"])
    async def remove_pronoun(self, ctx, pronoun: str):
        """Removes a pronoun role from the list of available roles.
        Example: ?remove_pronoun they"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.roles["pronouns"].keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list.")
        self.roles["pronouns"].pop(pronoun)
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Removed pronoun role for `{pronoun}`.")

    @commands.command(aliases=["listpronouns", "lp"])
    async def list_pronouns(self, ctx):
        """Lists all available pronoun roles."""
        pronouns = sorted([f"`{pronoun.title()}`" for pronoun in self.roles["pronouns"].keys()])
        await ctx.send(f"Available pronouns: {', '.join(pronouns)}")


async def setup(bot):
    await bot.add_cog(Roles(bot))
