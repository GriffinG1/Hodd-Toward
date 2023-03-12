import discord
import json
from discord.ext import commands


class Roles(commands.Cog):
    """Commands for managing roles."""

    def __init__(self, bot):
        self.bot = bot
        print(f"Loaded {self.__class__.__name__} cog.")

    async def handle_roles(self, member, role_name, dict_scope):
        """Handles role assignment."""
        if role_name not in dict_scope.keys():
            return False
        role = discord.utils.get(member.guild.roles, id=dict_scope[role_name])
        if role not in member.roles:
            await member.add_roles(role)
            return "✅ Added role for `{}`.\n"
        await member.remove_roles(role)
        return "✅ Removed role for `{}`.\n"

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
            resp = await self.handle_roles(ctx.author, pronoun, self.bot.roles["pronouns"])
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
        if pronoun in self.bot.roles["pronouns"].keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is already in the list. Please use `.edit_pronoun` to edit it.")
        self.bot.roles["pronouns"][pronoun] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Added pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["editpronouns"])
    async def edit_pronoun(self, ctx, pronoun: str, new_role: discord.Role):
        """Edits a pronoun role in the list of available roles.
        Example: ?edit_pronoun they @they/them"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.bot.roles.keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list. Please use `.add_pronoun` to add it.")
        self.bot.roles["pronouns"][pronoun] = new_role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Edited pronoun role for `{pronoun}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["removepronouns"])
    async def remove_pronoun(self, ctx, pronoun: str):
        """Removes a pronoun role from the list of available roles.
        Example: ?remove_pronoun they"""
        pronoun = pronoun.lower().replace(" ", "")
        if pronoun not in self.bot.roles["pronouns"].keys():
            return await ctx.send(f"❌ Pronoun `{pronoun}` is not in the list.")
        self.bot.roles["pronouns"].pop(pronoun)
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Removed pronoun role for `{pronoun}`.")

    @commands.command(aliases=["listpronouns", "lp"])
    async def list_pronouns(self, ctx):
        """Lists all available pronoun roles."""
        pronouns = sorted([f"`{pronoun.title()}`" for pronoun in self.bot.roles["pronouns"].keys()])
        await ctx.send(f"Available pronouns: {', '.join(pronouns)}")

    @commands.command(aliases=["colorado"])
    async def set_colorado(self, ctx):
        """Sets your Colorado role. Use again to remove."""
        resp = await self.handle_roles(ctx.author, "colorado_role", self.bot.roles["server_stuff"])
        if not resp:
            return await ctx.send("❌ Colorado role not found. Please set it with `?set_colorado_role`.")
        await ctx.send(resp.format("colorado"))

    @commands.command(aliases=["animal"])
    async def animal_role(self, ctx, animal: str):
        """Sets your animal role. Use again to remove.
        Example: ?animal_role kitty"""
        resp = await self.handle_roles(ctx.author, animal.lower(), self.bot.roles["animals"])
        if not resp:
            return await ctx.send(f"❌ Animal role for `{animal}` not found. Please set it with `?add_animal_role`.")
        await ctx.send(resp.format(animal))

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["addanimal"])
    async def add_animal_role(self, ctx, animal: str, role: discord.Role):
        """Adds an animal role to the list of available roles.
        Example: ?add_animal_role kitty @kitty"""
        animal = animal.lower()
        if animal in self.bot.roles["animals"].keys():
            return await ctx.send(f"❌ Animal `{animal}` is already in the list. Please use `.edit_animal_role` to edit it.")
        self.bot.roles["animals"][animal] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Added animal role for `{animal}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["editanimal"])
    async def edit_animal_role(self, ctx, animal: str, new_role: discord.Role):
        """Edits an animal role in the list of available roles.
        Example: ?edit_animal_role kitty @kitty"""
        animal = animal.lower()
        if animal not in self.bot.roles["animals"].keys():
            return await ctx.send(f"❌ Animal `{animal}` is not in the list. Please use `.add_animal_role` to add it.")
        self.bot.roles["animals"][animal] = new_role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Edited animal role for `{animal}`.")

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=["removeanimal"])
    async def remove_animal_role(self, ctx, animal: str):
        """Removes an animal role from the list of available roles.
        Example: ?remove_animal_role kitty"""
        animal = animal.lower()
        if animal not in self.bot.roles["animals"].keys():
            return await ctx.send(f"❌ Animal `{animal}` is not in the list.")
        self.bot.roles["animals"].pop(animal)
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Removed animal role for `{animal}`.")

    @commands.command(aliases=["listanimals", "la"])
    async def list_animals(self, ctx):
        """Lists all available animal roles."""
        animals = sorted([f"`{animal.title()}`" for animal in self.bot.roles["animals"].keys()])
        await ctx.send(f"Available animals: {', '.join(animals)}")


async def setup(bot):
    await bot.add_cog(Roles(bot))
