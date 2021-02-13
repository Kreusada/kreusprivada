import abc
import time
import random
import discord

from typing import Literal
from redbot.core import commands, Config, i18n
from redbot.core.utils.chat_formatting import box, bold

from .timestables import TimesTables

T_ = i18n.Translator("Numeracy", __file__)


class CompositeMetaClass(type(commands.Cog), type(abc.ABC)):
    """Thanks Trusty!"""


@i18n.cog_i18n(T_)
class Numeracy(
    TimesTables,
    commands.Cog,
    metaclass=CompositeMetaClass,
):
    """Games and tools with numbers."""

    __version__ = "1.1.1"
    __author__ = ["Kreusada"]

    def __init__(self, bot):
        self.bot = bot
        self.correct = "\N{WHITE HEAVY CHECK MARK}"
        self.incorrect = "\N{CROSS MARK}"
        self.session_quotes = [
            "Great work",
            "Amazing",
            "Awesome work",
            "Nice stuff",
        ]
        self.how_to_exit_early = "Remember, you can type `exit()` or `stop()` at any time to quit the session."
        self.config = Config.get_conf(self, 2345987543534, force_registration=True)
        self.config.register_guild(
            tt_inactive=3, tt_timeout=10, tt_sleep=2, tt_time_taken=False
        )

    def time(self):
        return time.perf_counter()

    def average(self, times):
        try:
            return round(sum(times) / len(times), 2)
        except ZeroDivisionError:
            return 0

    def total(self, times):
        try:
            return round(sum(times), 2)
        except ZeroDivisionError:
            return 0

    async def tt_build_stats(
        self, ctx, correct, incorrect, inactive, average_time, exited_early: bool
    ):
        msg = (
            (
                f"{random.choice(self.session_quotes)} {ctx.author.name}! The session has ended."
            )
            if not exited_early
            else f"You exited early, {ctx.author.name}."
        )
        if average_time:
            timing = (
                f"\n\nAverage time per question: {self.average(average_time)}s\n"
                f"Total time spent answering: {self.total(average_time)}s"
            )
        else:
            timing = ''
        return await ctx.send(
            box(
                text=(
                    f"{msg}\n\nCorrect: {str(correct[-1])}\n"
                    f"Incorrect: {str(incorrect[-1])}\n"
                    f"Unanswered: {str(inactive[-1])}"
                    f"{timing}"
                ),
                lang="yml",
            )
        )
