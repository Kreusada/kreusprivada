import discord
import asyncio

from redbot.core import checks, commands, Config
from redbot.core.utils.chat_formatting import bold, box, error
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

mod = "\N{OPEN MAILBOX WITH RAISED FLAG}\N{VARIATION SELECTOR-16}"

class ModMail(commands.Cog):
    """
    An interactive global modmail cog.
    """

    __author__ = "Kreusada"
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 3280947324, force_registration=True)
        self.config.register_global(server=None, chan=None, toggle=True, blacklist=[], mods=[])

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        return f"{super().format_help_for_context(ctx)}\n\nAuthor: {self.__author__}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete.
        """
        return

    async def clear_blacklist(self, ctx: commands.Context):
        msg = await ctx.send(f"Please confirm that you want to clear the *entire* blacklist.")
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"You took too long to respond.")
        if pred.result:
            await self.config.blacklist.clear()
            await ctx.tick()
            await ctx.send("Blacklist cleared.")

    async def pred(self, ctx: commands.Context, message: str):
        msg = await ctx.send(f"Please confirm that you want to send the following message: {box(message, lang='md')}")
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"You took too long to respond.")
        if pred.result:
            return True

    @commands.group()
    async def modmail(self, ctx):
        """Commands with ModMail."""
        pass

    @modmail.command()
    @commands.is_owner()
    async def channel(self, ctx, mail_channel: discord.TextChannel):
        """Set the ModMail channel."""
        await self.config.chan.set(mail_channel.id)
        await ctx.tick()
        await ctx.send(f"{mail_channel.mention} is now the modmail channel.")

    @modmail.command()
    @commands.is_owner()
    async def toggle(self, ctx, true_or_false: bool):
        """Toggles the ModMail on or off."""
        await self.config.toggle.set(true_or_false)
        await ctx.tick()
        await ctx.send("Enabled.") if true_or_false else await ctx.send("Disabled.")

    @modmail.command()
    async def showsettings(self, ctx):
        """Shows the current settings for ModMail."""
        chan = self.bot.get_channel(await self.config.chan())
        tog = await self.config.toggle()
        embed = discord.Embed(
            description=(
                f"**Channel:** {chan.mention}\n"
                f"**Enabled:** {tog}"
            ),
            colour=await ctx.embed_colour()
        )
        await ctx.send(embed=embed)

    @modmail.command()
    async def reply(self, ctx, user: discord.User, *, message: str):
        """Reply to a user."""
        if not str(ctx.author) in await self.config.mods():
            await ctx.send(error(text='You are not authorized to use this command.'))
        else:
            if await ctx.embed_requested():
                embed = discord.Embed(
                    title=f"{mod} Reply from {bold(ctx.author.name)}!",
                    description=message,
                    colour=await ctx.embed_colour(),
                    timestamp=ctx.message.created_at
                )
                embed.set_footer(text=f"You recently used ModMail with {ctx.me}.")
                try:
                    await user.send(embed=embed)
                    await ctx.send(f"{mod} mail has been flown back to {user.name} successfully.")
                except discord.Forbidden:
                    await ctx.send(f"{user.name} could not be DMed.")
            else:
                await ctx.send(f"Reply from {bold(ctx.author.name)}!\n\n{message}")

    @modmail.group()
    async def mods(self, ctx):
        """Review mods who can reply to modmails."""
        pass

    @mods.command(name="add")
    @commands.is_owner()
    async def mod_add(self, ctx, user: discord.User):
        """Add a user as a modmail correspondent."""
        mods = await self.config.mods()
        if user in mods:
            await ctx.send(f"{user} is already a modmail correspondent.")
        else:
            mods.append(str(user))
            await self.config.mods.set(mods)
            await ctx.send(f"{user} was added as a modmail correspondent.")

    @mods.command(name="del")
    @commands.is_owner()
    async def mod_del(self, ctx, user: discord.User):
        """Remove a user as a modmail correspondent."""
        mods = await self.config.mods()
        if str(user) in mods:
            mods.remove(str(user))
            await self.config.mods.set(mods)
            await ctx.send(f"{user} was removed as a modmail correspondent.")
        else:
            await ctx.send(f"{user} was not a modmail correspondent originally.")

    @mods.command(name="list")
    async def mod_list(self, ctx):
        """View the current modmail correspondents."""
        mods = await self.config.mods()
        if len(mods) == 0:
            await ctx.send(f"There are no modmail correspondents.")
        else:
            description = ", ".join(x for x in mods)
            if await ctx.embed_requested():
                embed = discord.Embed(
                    title=f"{mod} ModMail Correspondents",
                    description=description,
                    colour=await ctx.embed_colour()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(box(description, lang='md'))

    @modmail.group()
    async def blacklist(self, ctx):
        """Blacklist users."""

    @blacklist.command()
    @commands.is_owner()
    async def black_add(self, ctx, user: discord.User):
        """Add a user to the blacklist."""
        blacklist = await self.config.blacklist()
        if user in blacklist:
            await ctx.send(f"{user} has already been blacklisted.")
        else:
            blacklist.append(str(user))
            await self.config.blacklist.set(blacklist)
            await ctx.send(f"{user} was added to the blacklist.")

    @blacklist.command(name="del")
    @commands.is_owner()
    async def black_del(self, ctx, user: discord.User):
        """Remove a user from the blacklist."""
        blacklist = await self.config.blacklist()
        if str(user) in blacklist:
            blacklist.remove(str(user))
            await self.config.blacklist.set(blacklist)
            await ctx.send(f"{user} was removed from the blacklist.")
        else:
            await ctx.send(f"{user} was not in the blacklist.")

    @blacklist.command(name="list")
    async def black_list(self, ctx):
        """View the current blacklist."""
        blacklist = await self.config.blacklist()
        if len(blacklist) == 0:
            await ctx.send("The blacklist is empty!")
        else:
            description = ", ".join(x for x in blacklist)
            if await ctx.embed_requested():
                embed = discord.Embed(
                    title=f"{mod} ModMail Blacklist",
                    description=description,
                    colour=await ctx.embed_colour()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(box(description, lang='md'))

    @blacklist.command()
    @commands.is_owner()
    async def clear(self, ctx):
        """Clear the entire blacklist."""
        await self.clear_blacklist(ctx)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        ctx = await self.bot.get_context(message)
        if message.guild:
            return
        if message.author.bot:
            return
        if not await self.config.chan():
            return
        if not await self.config.toggle():
            return
        if str(message.author) in await self.config.blacklist():
            return await ctx.send(error(text='You have been blacklisted from using our ModMail.'))
        if len(message.content) > 1500:
            return await message.channel.send(f"Sorry {message.author}! Your message must be under 1500 characters.")
        channel = self.bot.get_channel(await self.config.chan())
        pred = await self.pred(ctx, message.content)
        if pred:
            await message.author.send("Done! Your message has been sent.")
            await ctx.tick()
            embed = discord.Embed(
                title=f"{mod} Message received from {bold(message.author.name)}!",
                description=(f"{bold('Message: ')}{message.content}"),
                colour=await ctx.embed_colour(),
                timestamp=ctx.message.created_at
            )
            embed.add_field(name="Author Details", value=f"{message.author} ({message.author.id})")
            await channel.send(embed=embed)