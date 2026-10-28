import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- BAN COMMAND ---
    @commands.command(name="ban", help="Bans a specified user from the server.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot ban yourself!")
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban a member with an equal or higher role!")
            return

        await member.ban(reason=reason)
        await ctx.send(f"🔨 **{member}** has been banned. Reason: {reason or 'No reason provided'}")

    # --- UNBAN COMMAND ---
    @commands.command(name="unban", help="Unbans a user by their ID.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = None):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"🔓 **{user}** has been unbanned. Reason: {reason or 'No reason provided'}")
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned.")
        except discord.HTTPException:
            await ctx.send("❌ An error occurred while trying to unban this user.")

    # --- KICK COMMAND ---
    @commands.command(name="kick", help="Kicks a specified user from the server.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot kick yourself!")
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick a member with an equal or higher role!")
            return

        await member.kick(reason=reason)
        await ctx.send(f"👢 **{member}** has been kicked. Reason: {reason or 'No reason provided'}")

    # --- TIMEOUT (MUTE) COMMAND ---
    @commands.command(name="timeout", aliases=["mute"], help="Times out a user (restricts messaging and voice). Default is 15m. Usage: w!timeout @user 15m reason")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration_str: str = "15m", *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot timeout yourself!")
            return

        unit = duration_str[-1].lower()
        try:
            value = int(duration_str[:-1])
        except ValueError:
            await ctx.send("❌ Invalid duration format! Example: `w!timeout @user 15m` or `w!timeout @user 2h`")
            return

        if unit == 's':
            seconds = value
        elif unit == 'm':
            seconds = value * 60
        elif unit == 'h':
            seconds = value * 3600
        elif unit == 'd':
            seconds = value * 86400
        else:
            await ctx.send("❌ Invalid time unit! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days).")
            return

        duration = timedelta(seconds=seconds)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"🔇 **{member}** has been timed out for {duration_str}. Reason: {reason or 'No reason provided'}")

    # --- UNTIMEOUT (UNMUTE) COMMAND ---
    @commands.command(name="untimeout", aliases=["unmute"], help="Removes timeout from a user.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 **{member}**'s timeout has been removed.")

    # --- CLEAR (SIL) COMMAND ---
    @commands.command(name="clear", aliases=["sil"], help="Deletes a specified number of messages. Usage: w!clear 100")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("❌ Please enter a number greater than 0.")
            return

        # Komutun kendi mesajını da dahil etmek için +1 ekleyebiliriz veya direkt silebiliriz
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Successfully deleted **{len(deleted) - 1}** messages.", delete_after=5)

    # --- ERROR HANDLERS ---
    @ban.error
    @unban.error
    @kick.error
    @timeout.error
    @untimeout.error
    @clear.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Please check the command usage.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Specified member was not found in this server.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))