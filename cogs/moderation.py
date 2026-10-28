import logging
from datetime import timedelta

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

BIRIMLER = {"s": 1, "m": 60, "h": 3600, "d": 86400}
MAX_TIMEOUT_SANIYE = 28 * 86400  # Discord sınırı: 28 gün


def yetki_hatasi(ctx, member):
    # İşlem yapılabilir mi? Yapılamazsa kullanıcıya gösterilecek mesajı döndürür
    if member == ctx.author:
        return "❌ You cannot do this to yourself!"
    if member == ctx.guild.owner:
        return "❌ You cannot do this to the server owner!"
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return "❌ You cannot do this to a member with an equal or higher role!"
    if member.top_role >= ctx.guild.me.top_role:
        return "❌ My role is not high enough to manage this member."
    return None


def sebep_metni(ctx, reason):
    # Denetim kaydında komutu kullanan yetkili görünsün (Discord'da en fazla 512 karakter)
    return f"{ctx.author}: {reason or 'No reason provided'}"[:500]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- BAN COMMAND ---
    @commands.command(name="ban", help="Bans a specified user from the server.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        hata = yetki_hatasi(ctx, member)
        if hata:
            await ctx.send(hata)
            return

        await member.ban(reason=sebep_metni(ctx, reason))
        await ctx.send(f"🔨 **{member}** has been banned. Reason: {reason or 'No reason provided'}")

    # --- UNBAN COMMAND ---
    @commands.command(name="unban", help="Unbans a user by their ID.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = None):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=sebep_metni(ctx, reason))
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
        hata = yetki_hatasi(ctx, member)
        if hata:
            await ctx.send(hata)
            return

        await member.kick(reason=sebep_metni(ctx, reason))
        await ctx.send(f"👢 **{member}** has been kicked. Reason: {reason or 'No reason provided'}")

    # --- TIMEOUT (MUTE) COMMAND ---
    @commands.command(name="timeout", aliases=["mute"], help="Times out a user (restricts messaging and voice). Default is 15m. Usage: w!timeout @user 15m reason")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration_str: str = "15m", *, reason: str = None):
        hata = yetki_hatasi(ctx, member)
        if hata:
            await ctx.send(hata)
            return

        birim = duration_str[-1].lower()
        try:
            deger = int(duration_str[:-1])
        except ValueError:
            await ctx.send("❌ Invalid duration format! Example: `w!timeout @user 15m` or `w!timeout @user 2h`")
            return

        carpan = BIRIMLER.get(birim)
        if carpan is None:
            await ctx.send("❌ Invalid time unit! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days).")
            return

        seconds = deger * carpan
        if seconds <= 0 or seconds > MAX_TIMEOUT_SANIYE:
            await ctx.send("❌ Duration must be between 1 second and 28 days.")
            return

        await member.timeout(timedelta(seconds=seconds), reason=sebep_metni(ctx, reason))
        await ctx.send(f"🔇 **{member}** has been timed out for {duration_str}. Reason: {reason or 'No reason provided'}")

    # --- UNTIMEOUT (UNMUTE) COMMAND ---
    @commands.command(name="untimeout", aliases=["unmute"], help="Removes timeout from a user.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        hata = yetki_hatasi(ctx, member)
        if hata:
            await ctx.send(hata)
            return

        await member.timeout(None, reason=sebep_metni(ctx, None))
        await ctx.send(f"🔊 **{member}**'s timeout has been removed.")

    # --- CLEAR (SIL) COMMAND ---
    @commands.command(name="clear", aliases=["sil"], help="Deletes a specified number of messages (1-100). Usage: w!clear 50")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if not 1 <= amount <= 100:
            await ctx.send("❌ Please enter a number between 1 and 100.")
            return

        # +1: komutu yazan mesajı da siler
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Successfully deleted **{len(deleted) - 1}** messages.", delete_after=5)

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
        elif isinstance(error, commands.BotMissingPermissions):
            eksik = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ I am missing the required permission(s): `{eksik}`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Please check the command usage.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Specified member was not found in this server.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            await ctx.send("❌ Discord refused this action. Check my role position and permissions.")
        else:
            log.error("Unexpected error in moderation command", exc_info=error)
            await ctx.send("❌ An unexpected error occurred.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))