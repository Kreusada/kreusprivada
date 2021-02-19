from redbot.core import commands



@commands.command(name="abs")
async def append_backslash(ctx, text: str):
    """Add a backslash to the start of a string."""
    await ctx.send(f"\\{text}")


def setup(bot):
    bot.add_command(append_backslash)
