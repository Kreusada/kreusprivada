import abc
import discord
import random

from typing import Literal
from redbot.core import commands, Config, i18n
from redbot.core.utils.chat_formatting import box, bold

from .timestables import TimesTables

T_ = i18n.Translator("Numeracy", __file__)


class CompositeMetaClass(type(commands.Cog), type(abc.ABC)):
    """Thanks Trusty!"""

    pass


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
        self.session_expire_quotes = [
            "Great work",
            "Amazing",
            "Awesome work",
            "Nice stuff",
        ]
        self.how_to_exit_early = "Remember, you can type `exit()` or `stop()` at any time to quit the session."
        self.config = Config.get_conf(self, 2345987543534, force_registration=True)
        self.config.register_guild(
            tt_inactive=3,
            tt_timeout=10,
            tt_sleep=2,
        )

    async def tt_build_stats(
        self, ctx, correct, incorrect, inactive, exited_early: bool
    ):
        msg = (
            (f"{random.choice(self.session_expire_quotes)} {ctx.author.name}!")
            if not exited_early
            else f"You exited early, {ctx.author.name}."
        )
        return await ctx.send(
            box(
                text=(
                    f"{msg}\n\nCorrect: {str(correct[-1])}\n"
                    f"Incorrect: {str(incorrect[-1])}\n"
                    f"Unanswered: {str(inactive[-1])}"
                ),
                lang="yml",
            )
        )
