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
    async def set_pronouns(self, ctx, *, pronouns: str):
        """Sets your pronouns. Use again to remove.
        Please note that combined pronouns (ex she/they) are not supported, please separate them. (ex she | they)
        Please ask for help if your pronouns aren't available.

        Example: .set_pronouns they | she > adds the pronoun roles for they/them and she/her"""
        pronouns = pronouns.lower().replace(" ", "").split("|")
        message = ""
        invalid_pronouns = []
        for pronoun in pronouns:
            resp = await self.handle_roles(ctx.author, ctx.guild.get_role(self.roles["they"]))
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
        Example: .add_pronoun they @they/them"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun in self.roles.keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is already in the list. Please use `.edit_pronoun` to edit it.")
        self.roles[pronoun] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Added pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliaes=["editpronouns"])
    async def edit_pronoun(self, ctx, pronoun: str, new_role: discord.Role):
        """Edits a pronoun role in the list of available roles.
        Example: .edit_pronoun they @they/them"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.roles.keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list. Please use `.add_pronoun` to add it.")
        self.roles[pronoun] = new_role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Edited pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliaes=["removepronouns"])
    async def remove_pronoun(self, ctx, pronoun: str):
        """Removes a pronoun role from the list of available roles.
        Example: .remove_pronoun they"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.roles.keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list.")
        self.roles.pop(pronoun)
        with open("data/roles.json", "w") as file:
            json.dump(self.roles, file, indent=4)
        await ctx.send(f"✅ Removed pronoun role for `{pronoun}`.")


async def setup(bot):
    await bot.add_cog(Roles(bot))
