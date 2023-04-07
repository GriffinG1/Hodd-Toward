import discord
import json
from discord.ext import commands

# TODO: Rewrite into group commands with shared functions


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

    @commands.group(aliases=["role"])
    async def set_role(self, ctx):
        """Sets a role for the user."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid role type. Please see <#1083198618837721129> for command usage.")

    @set_role.command()
    async def colorado(self, ctx):
        """Sets your colorado role. Use the command again to remove it.
        Example: ?role colorado > adds the colorado role."""
        result = await self.handle_roles(ctx.author, "colorado_role", self.bot.roles["server_stuff"])
        if not result:
            return await ctx.send("❌ Colorado role not found. Please ask a mod if this is a mistake.")
        await ctx.send(result.format("colorado"))

    @set_role.command()
    async def pronoun(self, ctx, *, pronouns: str):
        """Sets your pronoun(s). Pass pronouns you already have to remove them. Input as a pipe (|) separated list.
        Please note that combined pronouns (ex she/they) are not supported, please separate them. (ex she | they).
        See <#1083198618837721129> for a list of available pronouns. Please ask if yours are not listed.
        Example: ?role pronoun she | they > adds the pronoun roles for she/her and they/them."""
        pronouns = pronouns.lower().replace(" ", "").split("|")
        message = ""
        invalid_pronouns = []
        for pronoun in pronouns:
            result = await self.handle_roles(ctx.author, pronoun, self.bot.roles["pronouns"])
            if not result:
                invalid_pronouns.append(pronoun)
                continue
            message += result.format(pronoun)
        if invalid_pronouns:
            message += f"❌ Some pronouns were not recognized. Please ask a mod if yours aren't available.\nUnrecognized pronouns: `{'`, `'.join(invalid_pronouns)}`"
        await ctx.send(message)

    @set_role.command()
    async def animal(self, ctx, animal: str):
        """Sets your animal role. Use the command again to remove it.
        See <#1083198618837721129> for a list of available animals. Please ask if yours is not listed.
        Example: ?role animal kitty > adds the kitty role."""
        result = await self.handle_roles(ctx.author, animal.lower(), self.bot.roles["animals"])
        if not result:
            return await ctx.send(f"❌ Animal role for `{animal}` not found. Please ask a mod to add it.")
        await ctx.send(result.format(animal))

    @set_role.command()
    async def misc(self, ctx, role: str):
        """Sets a misc role. Use the command again to remove it.
        See <#1083198618837721129> for a list of available misc roles.
        Example: ?role misc silly > adds the silly role."""
        result = await self.handle_roles(ctx.author, role.lower(), self.bot.roles["misc"])
        if not result:
            return await ctx.send(f"❌ Misc role named `{role}` not found.")
        await ctx.send(result.format(role))

    @set_role.command(aliases=["color"])
    async def colour(self, ctx, colour: str):
        """Sets your colour role. Use the command again to remove it.
        See <#1083198618837721129> for a list of available colours.
        Example: ?role colour red > adds the red role."""
        result = await self.handle_roles(ctx.author, colour.lower(), self.bot.roles["colours"])
        if not result:
            return await ctx.send(f"❌ Colour role for `{colour}` not found. Please ask a mod to add it.")
        await ctx.send(result.format(colour))

    @set_role.command(name="list")
    async def list_roles(self, ctx, category: str = None):
        """Lists all roles in a category."""
        if category is None:
            embed = discord.Embed(title="All Toggleable Roles", colour=discord.Colour.purple())
            embed.description = "The following roles are available to add to yourself."
            pronouns = sorted([f"`{pronoun.title()}`" for pronoun in self.bot.roles["pronouns"].keys()])
            animals = sorted([f"`{animal.title()}`" for animal in self.bot.roles["animals"].keys()])
            misc = sorted([f"`{role.title()}`" for role in self.bot.roles["misc"].keys()])
            colours = sorted([f"`{colour.title()}`" for colour in self.bot.roles["colours"].keys()])
            embed.add_field(name="Pronouns", value=', '.join(pronouns))
            embed.add_field(name="Animals", value=', '.join(animals))
            embed.add_field(name="Misc", value=', '.join(misc))
            embed.add_field(name="Colours", value=', '.join(colours))
            return await ctx.send(embed=embed)
        elif category.lower() in ["pronoun", "pronouns"]:
            dict_scope = self.bot.roles["pronouns"]
        elif category.lower() in ["animal", "animals"]:
            dict_scope = self.bot.roles["animals"]
        elif category.lower() in ["misc"]:
            dict_scope = self.bot.roles["misc"]
        elif category.lower() in ["colour", "colours"]:
            dict_scope = self.bot.roles["colours"]
        roles = [f"`{name.title()}`: {ctx.guild.get_role(role_id).mention}" for name, role_id in dict_scope.items()]
        await ctx.send(embed=discord.Embed(title=f"Roles for {category.title()}", description='\n'.join(roles)))

    @set_role.command(aliases=["help"])
    async def role_help(self, ctx):
        """Sends info on how to use the role commands."""
        embed = discord.Embed(title="Role Usage", colour=discord.Colour.purple())
        embed.description = "You can use the below commands to add roles from yourself. Using the same command will remove them.\nPlease only use them in <#1066262751376326696> or <#1084259970318618654>.\nIf you would like a role to be added, please ask in <#1084220504384229537>."
        embed.add_field(name="Pronouns", value=f"`{ctx.prefix}role pronoun pronoun1 | pronoun2 | ...` > adds pronoun1, pronoun2, etc. to your roles.\n"
                        f"Example: `{ctx.prefix}role pronoun they | she | he`.\nPaired pronouns (ex `she/they`) are not supported.", inline=False)
        embed.add_field(name="Animals", value=f"`{ctx.prefix}role animal animal` > adds animal to your roles.\n"
                        f"Example: `{ctx.prefix}role animal kitty`.", inline=False)
        embed.add_field(name="Misc", value=f"`{ctx.prefix}role misc misc` > adds misc to your roles.\n"
                        f"Example: `{ctx.prefix}role misc silly`.", inline=False)
        embed.add_field(name="colours", value=f"`{ctx.prefix}role colour colour` > adds colour to your roles.\n"
                        f"Example: `{ctx.prefix}role colour blue`.", inline=False)
        embed.add_field(name="Colorado", value=f"`{ctx.prefix}role colorado` > adds the colorado role to your roles.", inline=False)
        await ctx.send(embed=embed)

    @commands.group()
    @commands.has_permissions(manage_roles=True)
    async def rolesedit(self, ctx):
        """Commands for editing roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rolesedit.command(aliases=["edit"])
    async def add(self, ctx, category: str, name: str, role: discord.Role):
        """Adds to, or edits, a role."""
        if category.lower() in ["pronoun", "pronouns"]:
            dict_scope = self.bot.roles["pronouns"]
        elif category.lower() in ["animal", "animals"]:
            dict_scope = self.bot.roles["animals"]
        elif category.lower() in ["misc"]:
            dict_scope = self.bot.roles["misc"]
        elif category.lower() in ["colour", "colours"]:
            dict_scope = self.bot.roles["colours"]
        else:
            return await ctx.send(f"❌ Category `{category}` not found.")
        name = name.lower()
        exists = (name in dict_scope.keys())
        self.bot.roles[category][name] = role.id
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ {'Added' if not exists else 'Edited'} role for `{name}`.")

    @rolesedit.command()
    async def remove(self, ctx, category: str, name: str):
        """Removes a role."""
        if category.lower() in ["pronoun", "pronouns"]:
            dict_scope = self.bot.roles["pronouns"]
        elif category.lower() in ["animal", "animals"]:
            dict_scope = self.bot.roles["animals"]
        elif category.lower() in ["misc"]:
            dict_scope = self.bot.roles["misc"]
        elif category.lower() in ["colour", "colours"]:
            dict_scope = self.bot.roles["colours"]
        else:
            return await ctx.send(f"❌ Category `{category}` not found.")
        name = name.lower()
        if name not in dict_scope.keys():
            return await ctx.send(f"❌ Role for `{name}` not found.")
        del self.bot.roles[category][name]
        with open("data/roles.json", "w") as file:
            json.dump(self.bot.roles, file, indent=4)
        await ctx.send(f"✅ Removed role for `{name}`.")

    @rolesedit.command(aliases=["sri"])
    async def send_roles_info(self, ctx):
        """Sends the roles info to the roles channel."""
        await ctx.message.delete()
        await ctx.channel.purge(limit=2, check=lambda message: message.author == self.bot.user)
        await ctx.invoke(self.role_help)
        await ctx.invoke(self.list_roles)



async def setup(bot):
    await bot.add_cog(Roles(bot))
