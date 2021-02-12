import discord
import asyncio

from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import error, box
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions


class Codefest(commands.Cog):
    """Host coding challenges in your guild!"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 3242384, force_registration=True)
        self.config.register_guild(
            leaders=[],
            ongoing=None,
            announce_channel=None,
            submit_channel=None,
            inbox_channel=None,
        )
        self.config.register_member(submitted=False)
        self.no_events = "There are no codefest events running."
        self.is_event = "Current codefest event:\n - {event}"
        self.already_event = "There is already a codefest event running:\n - {event}"
        self.lang = "yaml"

    @commands.group(aliases=["cf"])
    async def codefest(self, ctx):
        """Commands with CodeFest."""

    @codefest.group(name="set")
    async def _set(self, ctx):
        """Settings for codefest."""

    @_set.group()
    async def leaders(self, ctx):
        """Current settings for codefest leaders."""

    @leaders.command()
    @commands.admin_or_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member):
        """Add a user as a codefest leader."""
        leaders = await self.config.guild(ctx.guild).leaders()
        leaders.append(member.id)
        await self.config.guild(ctx.guild).leaders.set(leaders)
        await ctx.send(f"{member.name} was added as a codefest leader.")

    @leaders.command(name="list")
    async def _list(self, ctx):
        """Shows all the current codefest leaders."""
        leaders = await self.config.guild(ctx.guild).leaders()
        if not len(leaders):
            description = "There are no codefest leaders."
        else:
            description = ", ".join(self.bot.get_user(u).name for u in leaders)
        embed = discord.Embed(description=description, colour=await ctx.embed_colour())
        await ctx.send(embed=embed)

    @leaders.command()
    async def clear(self, ctx):
        """Clear the leaders list."""
        await self.config.guild(ctx.guild).leaders.clear()
        await ctx.tick()

    @_set.group()
    async def channel(self, ctx):
        """Setting for codefest channels."""

    @channel.command()
    async def announce(self, ctx, channel: discord.TextChannel):
        """Set the channel where codefest announcements are posted."""
        await self.config.guild(ctx.guild).announce_channel.set(channel.id)
        await ctx.tick()

    @channel.command()
    async def submit(self, ctx, channel: discord.TextChannel):
        """Set the channel where codefest submissions can be posted."""
        await self.config.guild(ctx.guild).submit_channel.set(channel.id)
        await ctx.tick()

    @channel.command()
    async def inbox(self, ctx, channel: discord.TextChannel):
        """Set the channel where codefest leaders will receive submissions."""
        await self.config.guild(ctx.guild).inbox_channel.set(channel.id)
        await ctx.tick()

    @channel.command()
    async def show(self, ctx):
        """Show the current channels used for codefest."""
        announce_channel = self.bot.get_channel(
            await self.config.guild(ctx.guild).announce_channel()
        )
        submit_channel = self.bot.get_channel(
            await self.config.guild(ctx.guild).submit_channel()
        )
        inbox_channel = self.bot.get_channel(
            await self.config.guild(ctx.guild).inbox_channel()
        )
        embed = discord.Embed(color=await ctx.embed_colour())
        embed.add_field(
            name="Announce channel",
            value=announce_channel.mention if announce_channel else "None",
            inline=False,
        )
        embed.add_field(
            name="Submission channel",
            value=submit_channel.mention if submit_channel else "None",
            inline=False,
        )
        embed.add_field(
            name="Inbox channel",
            value=inbox_channel.mention if inbox_channel else "None",
            inline=False,
        )
        await ctx.send(embed=embed)

    @codefest.command()
    async def current(self, ctx):
        """View the current codefest event."""
        ongoing = await self.config.guild(ctx.guild).ongoing()
        if ongoing:
            await ctx.send(
                box(text=self.is_event.format(event=ongoing), lang=self.lang)
            )
        else:
            await ctx.send(self.no_events)

    @codefest.command()
    async def start(self, ctx):
        """Start a code event."""
        leaders = await self.config.guild(ctx.guild).leaders()
        ongoing = await self.config.guild(ctx.guild).ongoing()
        if ctx.author.id not in leaders:
            return await ctx.send(
                error("You aren't authorized to run codefest events yet. Sorry!")
            )
        if not await self.config.guild(ctx.guild).announce_channel():
            return await ctx.send(
                error(
                    f"Required setup missing: `announce_channel`. Use `{ctx.clean_prefix}codefest channel announce`."
                )
            )
        if not await self.config.guild(ctx.guild).submit_channel():
            return await ctx.send(
                error(
                    f"Required setup missing: `submit_channel`. Use `{ctx.clean_prefix}codefest channel submit`."
                )
            )
        if not await self.config.guild(ctx.guild).inbox_channel():
            return await ctx.send(
                error(
                    f"Required setup missing: `receive_inbox`. Use `{ctx.clean_prefix}codefest channel inbox`."
                )
            )
        if ongoing:
            return await ctx.send(
                box(
                    text=error(self.already_event.format(event=ongoing)), lang=self.lang
                )
            )
        await ctx.send(f"Please answer these few questions {ctx.author.display_name}.")

        def check(x):
            return x.author == ctx.author and x.channel == ctx.channel

        await ctx.send("Could you give a title for your codefest event?")
        try:
            title = await self.bot.wait_for("message", timeout=50, check=check)
            if len(title.content) > 30:
                await ctx.send("Your title must be under 30 characters.")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to answer, please start over.")
        await ctx.send(
            "Give a detailed description for this event so your participants understand. Be sure to include any examples."
        )
        try:
            description = await self.bot.wait_for("message", timeout=200, check=check)
            if len(description.content) > 30:
                await ctx.send("Your description must be under 30 characters.")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to answer, please start over.")
        await ctx.send("Explain how users will upload their efforts at this event.")
        try:
            upload_type = await self.bot.wait_for("message", timeout=200, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to answer, please start over.")
        await ctx.send("All done!")
        embed = discord.Embed(
            title=title.content,
            description=f"A new codefest event was started by {ctx.author.display_name}!",
            colour=await ctx.embed_colour(),
        )
        embed.add_field(name="Description", value=description.content, inline=False)
        embed.add_field(
            name="How to participate", value=upload_type.content, inline=False
        )
        announce_channel = self.bot.get_channel(
            await self.config.guild(ctx.guild).announce_channel()
        )
        await self.config.guild(ctx.guild).ongoing.set(title.content)
        for x in ctx.guild.members:
            await self.config.member(x).clear()
        await announce_channel.send(embed=embed)

    @codefest.command()
    async def end(self, ctx):
        """End the current codefest event, select a winner."""
        ongoing = await self.config.guild(ctx.guild).ongoing()
        if not ongoing:
            return await ctx.send(self.no_events)
        await self.end_codefest_event(ctx, ongoing)

    async def end_codefest_event(self, ctx, event: str):
        msg = await ctx.send(
            f"Are you sure you want to end the following event: {event}?"
        )
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)

        def digit(x):
            return (
                x.author == ctx.author
                and x.channel == ctx.channel
                and x.content.isdigit()
            )

        def check(x):
            return x.author == ctx.author and x.channel == ctx.channel

        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond.")
        if not pred.result:
            return await ctx.send("Okay, the event shall continue.")
        else:
            await ctx.send(
                "Please specify the user's ID that you selected as the winner."
            )
            try:
                win = await self.bot.wait_for("message", check=digit, timeout=30)
                winner = ctx.guild.get_member(int(win.content))
                if winner:
                    await ctx.send(
                        f"{winner.display_name} has been selected as the winner."
                    )
                else:
                    return await ctx.send(
                        f"Could not find a member with the ID `{win.content}`. Please start over."
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "You took too long to specify a winner. Please restart the session."
                )
            await ctx.send(
                "Could you provide some additional notes/details, runner ups, or special mentions? Go ahead."
            )
            try:
                detail = await self.bot.wait_for("message", check=check, timeout=300)
                if len(detail.content) > 1500:
                    return await ctx.send(
                        f"The maximum character limit is 1500, you typed {len(detail.content)}. Please start over."
                    )
            except asyncio.TimeoutError:
                await ctx.send(
                    "I assume there were no additional details, lets announce our winner!"
                )
            announce_channel = self.bot.get_channel(
                await self.config.guild(ctx.guild).announce_channel()
            )
            await ctx.send(
                f"All done! This has been posted to {announce_channel.mention}."
            )
            embed = discord.Embed(
                title=f"The {event} event has ended!", color=await ctx.embed_colour()
            )
            embed.add_field(name="Winner", value=winner.name, inline=False)
            embed.add_field(
                name="Additional information", value=detail.content, inline=False
            )
            embed.set_footer(text="Thanks for participating!")
            await announce_channel.send(embed=embed)
            await self.config.guild(ctx.guild).ongoing.set(False)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        ctx = await self.bot.get_context(message)
        inbox_channel = self.bot.get_channel(
            await self.config.guild(message.guild).inbox_channel()
        )
        submit_channel = await self.config.guild(message.guild).submit_channel()
        ongoing = await self.config.guild(message.guild).ongoing()
        submitted = await self.config.member(message.author).submitted()
        if submitted:
            return
        if message.author.bot:
            return
        if not message.guild:
            return
        if not ongoing:
            return
        if message.channel != submit_channel:
            return
        embed = discord.Embed(
            title=f"{message.author.name} has submitted for a codefest event!",
            colour=await ctx.embed_colour(),
        )
        embed.add_field(name="Event Name", value=ongoing, inline=False)
        embed.add_field(name="Submission Content", value=message.content, inline=False)
        await inbox_channel.send(embed=embed)
        await message.delete()
        await message.channel.send(
            f"Thanks for submitting {message.author.mention}!", delete_after=3
        )
        await self.config.member(message.author).submitted.set(True)
