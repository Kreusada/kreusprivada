import random
import asyncio
import discord

from redbot.core import commands
from redbot.core.utils.chat_formatting import bold, box

from .meta import MixinMeta


class TimesTables(MixinMeta):
    pass

    @commands.group()
    async def tt(self, ctx):
        """Commands for times tables."""
        pass

    @tt.command()
    async def inactive(self, ctx, questions: int):
        """
        Set the number of questions unanswered before the session is closed.
        """
        if questions <= 2:
            return await ctx.send("Must be more than 2.")
        elif questions >= 10:
            return await ctx.send("Must be less than 10.")
        await self.config.guild(ctx.guild).tt_inactive.set(questions)
        await ctx.tick()

    @tt.command()
    async def timeout(self, ctx, seconds: int):
        """
        Set the number of seconds before a question times out.
        """
        if seconds <= 3:
            return await ctx.send("Must be more than 3.")
        elif seconds >= 50:
            return await ctx.send("Must be less than 50.")
        await self.config.guild(ctx.guild).tt_timeout.set(seconds)
        await ctx.tick()

    @tt.command()
    async def sleep(self, ctx, seconds: int):
        """
        Set the number of seconds between each question.
        """
        if seconds >= 8:
            return await ctx.send("Must be less than 8.")
        elif seconds <= 0:
            return await ctx.send("Must be a positive number.")
        await self.config.guild(ctx.guild).tt_timeout.set(seconds)
        await ctx.tick()

    @tt.command()
    async def settings(self, ctx):
        """
        Shows the current settings for times tables.
        """
        time = await self.config.guild(ctx.guild).tt_time_taken()
        inactive = await self.config.guild(ctx.guild).tt_inactive()
        timeout = await self.config.guild(ctx.guild).tt_timeout()
        sleep = await self.config.guild(ctx.guild).tt_sleep()
        embed = discord.Embed(
            title=f"Settings for {ctx.guild.name}",
            description=(
                f"Time toggled: {'Yes' if time else 'No'}\n"
                f"Inactive count: {inactive} questions\n"
                f"Timeout per question: {timeout}s\n"
                f"Time between questions: {sleep}s"
            ),
            color=await ctx.embed_colour(),
        )
        await ctx.send(embed=embed)

    @tt.command(name="time")
    async def _time(self, ctx):
        """
        Toggle whether the command displays the time taken.

        Defaults to False.
        """
        time = await self.config.guild(ctx.guild).tt_time_taken()
        await self.config.guild(ctx.guild).tt_time_taken.set(
            True if not time else False
        )
        verb = "enabled" if not time else "disabled"
        await ctx.send(f"Time has been {verb}.")

    @tt.command()
    async def start(self, ctx, number_of_questions: int):
        """Start a timestables session."""

        inactive = await self.config.guild(ctx.guild).tt_inactive()
        timeout = await self.config.guild(ctx.guild).tt_timeout()
        sleep = await self.config.guild(ctx.guild).tt_sleep()
        time_taken = await self.config.guild(ctx.guild).tt_time_taken()

        if number_of_questions > 20:
            return await ctx.send("Sorry, you cannot have more than 20 questions.")
        await ctx.send(
            f"Starting timestable session with {number_of_questions} questions...\n{self.how_to_exit_early}"
        )

        def check(x):
            return x.author == ctx.author and x.channel == ctx.channel

        correct_answers = [0]
        incorrect_answers = [0]
        inactive_counter = [0]

        for i in range(number_of_questions):
            F = random.randint(1, 12)
            S = random.randint(1, 12)
            await ctx.send(f"{bold(f'{F} x {S}')}?")

            try:
                if time_taken:
                    time_start = self.time()
                answer = await self.bot.wait_for(
                    "message", timeout=timeout, check=check
                )
                if answer.content == str(F * S):
                    await answer.add_reaction("✅")
                    if time_taken:
                        await ctx.send(
                            f"{random.choice(self.session_quotes)}! This question took you {round(self.time() - time_start,2)} seconds."
                        )
                    correct_answers.append(correct_answers[-1] + 1)
                elif answer.content.lower() in {"exit()", "stop()"}:
                    await ctx.send("Session ended.")
                    return await self.tt_build_stats(
                        ctx, correct_answers, incorrect_answers, inactive_counter, True
                    )
                    break
                else:
                    await answer.add_reaction("❌")
                    await ctx.send(f"Not quite! The answer was {bold(str(F*S))}.")
                    incorrect_answers.append(incorrect_answers[-1] + 1)
                async with ctx.typing():
                    await asyncio.sleep(sleep)
            except asyncio.TimeoutError:
                inactive_counter.append(inactive_counter[-1] + 1)
                if inactive_counter[-1] == inactive:
                    return await ctx.send("Session ended due to inactivity.")
                    break
                await ctx.send(
                    f"You took too long! Not to worry - the answer was {bold(str(F*S))}."
                )

        await self.tt_build_stats(
            ctx, correct_answers, incorrect_answers, inactive_counter, False
        )
