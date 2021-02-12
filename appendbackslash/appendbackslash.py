from redbot.core import commands

class AppendBackslash(commands.Cog):
    def __init__(self, bot): self.bot = bot
    
    @commands.command()
    async def abs(self, ctx, str: str): await ctx.send(f'\{str}')
