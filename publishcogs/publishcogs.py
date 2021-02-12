import discord
import asyncio
from redbot.core import commands, checks, Config
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("PublishCogs", __file__)

CHECK = "\N{WHITE HEAVY CHECK MARK}"
CROSS = "\N{CROSS MARK}"

default_guild = {
    "channel": None,
    "footer_date": True,
    "cog_creator": None,
    "description": True,
    "pre_requirements": True,
    "install_guide": True
}

@cog_i18n(_)
class PublishCogs(commands.Cog):
    """Publish your newly made cogs to a channel."""
  
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=3924082348, force_registration=True)
        self.config.register_guild(**default_guild)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return
      
    @commands.command()
    @commands.guild_only()
    async def publishcog(self, ctx: commands.Context):
        """Publish your cog!"""
        descr = await self.config.guild(ctx.guild).description()
        reqs = await self.config.guild(ctx.guild).pre_requirements()
        inst = await self.config.guild(ctx.guild).install_guide()
        footerdate = await self.config.guild(ctx.guild).footer_date()
        cog = discord.utils.get(ctx.guild.roles, id=await self.config.guild(ctx.guild).cog_creator())
        chan = discord.utils.get(ctx.guild.channels, id=await self.config.guild(ctx.guild).channel())
        if cog not in ctx.author.roles:
            return await ctx.send("It doesn't look like you have the cog creator role.")
        if not chan:
            return await ctx.send("The channel has not yet been configured by the admins.")
        try:
            pred = await self.session_establishment(ctx, "publish a cog")
            if pred is True:
                await ctx.send(f"Okay {ctx.author.mention}, I sent you a DM!")
                await ctx.author.send(f"Hey {ctx.author.name}, let's get started.")
                await asyncio.sleep(1)
                await ctx.author.send("What is the cog that you are wanting to publish today? Please use CamelCase.")
            else:
                return await ctx.send(f"Okay {ctx.author.name}, I've canceled the publishing")
        except discord.Forbidden:
            return await ctx.send("I am not able to DM you.")
        
        def check(m): 
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        def repo_check(m): 
            return m.author.id == ctx.author.id and m.channel == ctx.author.dm_channel and m.content.startswith("https://github.")
        
        try: 
            cogname = await self.bot.wait_for("message", timeout=200, check=check)
        except asyncio.TimeoutError:
            return await ctx.author.send("You took too long to answer.")
        if descr:
            await ctx.author.send("Please give a brief description of this cog.")
            try: 
                description = await self.bot.wait_for("message", timeout=200, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send("You took too long to answer.")
        if reqs:
            await ctx.author.send("Are there any pre-requirements needed for this cog? If not, type `None`.")
            try: 
                prereqs = await self.bot.wait_for("message", timeout=200, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send("You took too long to answer.")
        if inst:
            await ctx.author.send(
              "Could you send me a link to your repository?\n"
              f"{CHECK} `https://github.com/username/reponame`\n"
              f"{CROSS} `https://github.com/username/reponame/cogname`"
            )
            try: 
                repolink = await self.bot.wait_for("message", timeout=200, check=repo_check)
            except asyncio.TimeoutError:
                return await ctx.author.send("You took too long to provide a valid repository URL.")
        await ctx.author.send("Perfect! We're all done. Check your guild's channel to see the results!")
        if inst:
            instrepo = f"`[p]repo add {repolink.content.split('/')[3]} {repolink.content}`"
            instcog = f"`[p]cog install {repolink.content.split('/')[3]} {cogname.content}`"
        description = description.content if descr else None
        e = discord.Embed(
            title=f"New Cog from {ctx.author.name}!",
            description=description,
            color=await ctx.embed_colour(),
            timestamp=ctx.message.created_at if footerdate else None
        )
        e.add_field(name="Cog Name", value=cogname.content, inline=True)
        e.add_field(name="Author", value=ctx.author.name, inline=True)
        if not prereqs.content.lower() == 'none':
            e.add_field(name="Pre-Requirements:", value=prereqs.content, inline=True)
        if inst:
            e.add_field(name="Command to add repo", value=instrepo, inline=False)
            e.add_field(name="Command to add cog", value=instcog.lower(), inline=False)
        try:
            await chan.send(embed=e)
        except discord.Forbidden:
            await ctx.author.send(f"Doesn't look like I have permission to post in {chan.mention}. I'm sorry!")

    @commands.command()
    @commands.guild_only()
    async def updatecog(self, ctx: commands.Context):
      """Post updates to your cogs."""
      cog = await self.config.guild(ctx.guild).cog_creator()
      chan = await self.config.guild(ctx.guild).channel()
      descr = await self.config.guild(ctx.guild).description()
      reqs = await self.config.guild(ctx.guild).pre_requirements()
      inst = await self.config.guild(ctx.guild).install_guide()
      footerdate = await self.config.guild(ctx.guild).footer_date()
      cog = discord.utils.get(ctx.guild.roles, id=cog)
      chan = discord.utils.get(ctx.guild.channels, id=chan)
      if cog not in ctx.author.roles:
          return await ctx.send("It doesn't look like you have the cog creator role.")
      if not chan:
          return await ctx.send("The channel has not yet been configured by the admins.")
      try:
          pred = await self.session_establishment(ctx, "post a cog update")
          if pred:
              await ctx.send(f"Okay {ctx.author.mention}, I sent you a DM!")
              await ctx.author.send(f"Hey {ctx.author.name}, let's get started.")
              await asyncio.sleep(1)
              await ctx.author.send("What is the cog that you are wanting to update today? Please use CamelCase.")
      except discord.Forbidden:
          return await ctx.send("I am not able to DM you.")
      
      def check(m): 
          return m.author == ctx.author and m.channel == ctx.author.dm_channel
      
      try: 
          cogname = await self.bot.wait_for("message", timeout=200, check=check)
      except asyncio.TimeoutError:
          return await ctx.author.send("You took too long to answer.")
      await ctx.author.send("Please give a brief description of the changes you made. Markdown is supported.")
      try: 
          description = await self.bot.wait_for("message", timeout=200, check=check)
      except asyncio.TimeoutError:
          return await ctx.author.send("You took too long to answer.")
      if reqs:
          await ctx.author.send("Let's remind users about prerequirements. If there isn't any, type `None`.")
          try: 
              prereqs = await self.bot.wait_for("message", timeout=200, check=check)
          except asyncio.TimeoutError:
              return await ctx.author.send("You took too long to answer.")
      await ctx.author.send("Perfect! We're all done. Check your guild's channel to see the results!")
      if inst:
          cogupdate = f"`[p]cog update {cogname.content.lower()}`"
      e = discord.Embed(
          title=f"Cog Update: {cogname.content}! :gear:", 
          description=description.content, 
          color=await ctx.embed_colour(),
          timestamp=ctx.message.created_at if footerdate else None
      )
      e.add_field(name="Cog Name", value=cogname.content, inline=True)
      e.add_field(name="Author", value=ctx.author.name, inline=True)
      if not prereqs.content.lower() == 'none':
          e.add_field(name="Pre-Requirements:", value=prereqs.content, inline=True)
      if inst:
          e.add_field(name="Command to update cog", value=cogupdate, inline=False)
      try:
          await chan.send(embed=e)
      except discord.Forbidden:
          await ctx.author.send(f"Doesn't look like I have permission to post in {chan.mention}. I'm sorry!")

    @commands.group()
    @commands.guild_only()
    async def cogset(self, ctx):
        """Configure settings for publishing and updating cogs."""

    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        """Configure the channel where new cogs/cog updates will be posted."""
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await ctx.tick()
        await ctx.send(f"{channel.mention} will now be where new cogs are sent.")
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def footerdate(self, ctx):
      """Enable date and time display in new cog messages."""
      pred = await self.predicate_toggle(ctx, "the footer time")
      if pred:
          await self.config.guild(ctx.guild).footer_date.set(True)
      else:
          await self.config.guild(ctx.guild).footer_date.set(False)
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def cogcreator(self, ctx, role: discord.Role):
      """Configure your cog creator role."""
      await self.config.guild(ctx.guild).cog_creator.set(role.id)
      await ctx.tick()
      await ctx.send(f"{role.mention} will now be considered as the Cog Creator role.")
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def description(self, ctx):
      """Enable cogs to have descriptions."""
      pred = await self.predicate_toggle(ctx, "the description")
      if pred:
          await self.config.guild(ctx.guild).description.set(True)
      else:
          await self.config.guild(ctx.guild).description.set(False)
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def prerequirements(self, ctx):
      """Enable specifications for pre-requirements."""
      pred = await self.predicate_toggle(ctx, "the pre-requirements")
      if pred:
          await self.config.guild(ctx.guild).pre_requirements.set(True)
      else:
          await self.config.guild(ctx.guild).pre_requirements.set(False)
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def installguide(self, ctx):
      """Enable whether the cog creator can add an install guide."""
      pred = await self.predicate_toggle(ctx, "the install guide")
      if pred:
          await self.config.guild(ctx.guild).install_guide.set(True)
      else:
          await self.config.guild(ctx.guild).install_guide.set(False)
    
    @cogset.command()
    @commands.guild_only()
    async def showsettings(self, ctx):
      """Show the current settings for PublishCogs."""
      description = await self.config.guild(ctx.guild).description()
      requirements = await self.config.guild(ctx.guild).pre_requirements()
      install_guide = await self.config.guild(ctx.guild).install_guide()
      footer_date = await self.config.guild(ctx.guild).footer_date()
      chan = discord.utils.get(ctx.guild.channels, id=await self.config.guild(ctx.guild).channel())
      cog = discord.utils.get(ctx.guild.roles, id=await self.config.guild(ctx.guild).cog_creator())    
      No = "Not setup yet."
      if not chan:
        chan = No
      if not cog:
        cog = No
      title = f"Settings for **{ctx.guild.name}**:"
      embed = discord.Embed(title=title, color=await ctx.embed_colour())
      embed.add_field(name="Channel", value=chan, inline=False)
      embed.add_field(name="Cog Creator Role", value=cog, inline=False)
      embed.add_field(name="Description", value=description, inline=False)
      embed.add_field(name="Pre-requirements", value=requirements, inline=False)
      embed.add_field(name="Install Guide", value=install_guide, inline=False)
      embed.add_field(name="Footer Timestamp", value=footer_date, inline=False)
      await ctx.send(embed=embed)
    
    @cogset.command()
    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    async def setall(self, ctx):
      """Toggle all toggleable settings."""
      pred = await self.predicate_toggle_all(ctx, "all the settings")
      if pred:
          await self.config.guild(ctx.guild).description.set(True)
          await self.config.guild(ctx.guild).footer_date.set(True)
          await self.config.guild(ctx.guild).pre_requirements.set(True)
          await self.config.guild(ctx.guild).install_guide.set(True)
      else:
          await self.config.guild(ctx.guild).description.set(False)
          await self.config.guild(ctx.guild).footer_date.set(False)
          await self.config.guild(ctx.guild).pre_requirements.set(False)
          await self.config.guild(ctx.guild).install_guide.set(False)
      
    async def predicate_toggle(self, ctx: commands.Context, toggle: str) -> bool:
        """Used for enabling settings."""
        msg = await ctx.send(f"Would you like to enable {toggle}?")
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"{CROSS} You took too long to respond.")
            return False
        if not pred.result:
            await msg.delete()
            await ctx.send(f"{CROSS} Okay. {toggle.capitalize()} is now disabled.")
            return False
        else:
            await msg.delete()
            await ctx.send(f"{CHECK} Okay. {toggle.capitalize()} is now enabled.")
            return True

    async def predicate_toggle_all(self, ctx: commands.Context, toggle: str) -> bool:
        """Used for enabling ALL settings."""
        msg = await ctx.send(f"Would you like to enable {toggle}?")
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"{CROSS} You took too long to respond.")
            return False
        if not pred.result:
            await msg.delete()
            await ctx.send(f"{CROSS} Okay. {toggle.capitalize()} are now disabled.")
            return False
        else:
            await msg.delete()
            await ctx.send(f"{CHECK} Okay. {toggle.capitalize()} are now enabled.")
            return True

    async def session_establishment(self, ctx: commands.Context, type: str):
        """Predicate used to confirm DMs."""
        msg = await ctx.send(f"Are you sure you would like to {type}? I will send you some DMs.")
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"{CROSS} You took too long to respond.")
            return False
        if not pred.result:
            await msg.delete()
            return False
        else:
            await msg.delete()
            return True

def setup(bot):
    bot.add_cog(PublishCogs(bot))
