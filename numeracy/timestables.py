import random
import asyncio

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
    async def start(self, ctx, number_of_questions: int):
        """Start a timestables session."""

        inactive = await self.config.guild(ctx.guild).tt_inactive()
        timeout = await self.config.guild(ctx.guild).tt_timeout()
        sleep = await self.config.guild(ctx.guild).tt_sleep()

        if number_of_questions > 20:
            return await ctx.send("Sorry, you cannot have more than 20 questions.")
        await ctx.send(
            f"Starting timestable session with {number_of_questions} questions...\n{self.how_to_exit_early}"
        )

        def check(x):
            return x.author == ctx.author and x.channel == ctx.channel

        inactive_counter = [0]
        correct_answers = [0]
        incorrect_answers = [0]

        for i in range(number_of_questions):
            F = random.randint(1, 12)
            S = random.randint(1, 12)
            await ctx.send(f"{bold(f'{F} x {S}')}?")

            try:
                time_start = self.time()
                answer = await self.bot.wait_for(
                    "message", timeout=timeout, check=check
                )
                inactive_counter.clear()
                if answer.content == str(F * S):
                    await answer.add_reaction("✅")
                    await ctx.send(f"This question took you {round(self.time() - time_start)} seconds.")
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