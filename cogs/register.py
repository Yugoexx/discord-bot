import discord
from discord.ext import commands
from discord import app_commands
import json
import os

def get_settings():
    if not os.path.exists("settings.json"):
        return {}
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_staff_stat(staff_id: int):
    stats_file = "stats.json"
    data = {}
    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    
    staff_key = str(staff_id)
    data[staff_key] = data.get(staff_key, 0) + 1
    
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    return data[staff_key]


# --- REGISTRATION MODAL (NAME & AGE) ---
class RegisterModal(discord.ui.Modal, title="Member Registration"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Enter member's name...",
        min_length=2,
        max_length=20,
        required=True
    )
    age = discord.ui.TextInput(
        label="Age",
        placeholder="Enter member's age...",
        min_length=1,
        max_length=3,
        required=True
    )

    def __init__(self, target_member: discord.Member, gender: str):
        super().__init__()
        self.target_member = target_member
        self.gender = gender

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        settings = get_settings()
        reg_cfg = settings.get("registration", {})
        
        staff_role_id = reg_cfg.get("register_staff_role_id")
        unreg_role_id = reg_cfg.get("unregistered_role_id")
        man_role_id = reg_cfg.get("man_role_id")
        woman_role_id = reg_cfg.get("woman_role_id")
        chat_channel_id = reg_cfg.get("chat_channel_id")
        tag = reg_cfg.get("tag", "")

        # Staff Permission Check
        staff_role = interaction.guild.get_role(staff_role_id) if staff_role_id else None
        is_staff = (staff_role in interaction.user.roles) if staff_role else False
        
        if not is_staff and not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Only **Registration Staff** can perform this action!", ephemeral=True)
            return

        target_role_id = man_role_id if self.gender == "man" else woman_role_id
        target_role = interaction.guild.get_role(target_role_id)
        unreg_role = interaction.guild.get_role(unreg_role_id)

        if not target_role:
            await interaction.response.send_message("❌ Configured gender role not found in the server!", ephemeral=True)
            return

        # Update Nickname
        new_nick = f"{tag} {self.name.value.capitalize()} | {self.age.value}".strip()
        try:
            await self.target_member.edit(nick=new_nick)
        except discord.Forbidden:
            pass

        # Update Roles
        try:
            if unreg_role and unreg_role in self.target_member.roles:
                await self.target_member.remove_roles(unreg_role)
            await self.target_member.add_roles(target_role)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions to manage roles for this user! (Check role hierarchy)", ephemeral=True)
            return

        # Update Stats
        total_registers = add_staff_stat(interaction.user.id)
        gender_text = "👨 Male" if self.gender == "man" else "👩 Female"
        
        # 1. Staff Log Embed (Sent to Registration Channel)
        embed = discord.Embed(
            title="✅ Successful Registration",
            description=f"{self.target_member.mention} has been successfully registered!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=self.target_member.display_avatar.url)
        embed.add_field(name="Registered User", value=f"{self.target_member} (`{self.target_member.id}`)", inline=False)
        embed.add_field(name="Name | Age", value=f"`{self.name.value.capitalize()} | {self.age.value}`", inline=True)
        embed.add_field(name="Gender", value=gender_text, inline=True)
        embed.add_field(name="Registered By", value=f"{interaction.user.mention} (Total Registers: **{total_registers}**)", inline=False)
        embed.set_footer(text=f"Timestamp: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M')}")

        await interaction.followup.send(embed=embed)

        # 2. Welcome Embed (Sent to General Chat Channel)
        if chat_channel_id:
            chat_channel = interaction.guild.get_channel(chat_channel_id)
            if chat_channel:
                welcome_embed = discord.Embed(
                    title="🎉 A New Member Has Arrived!",
                    description=(
                        f"Welcome to the server, {self.target_member.mention}! 🎉\n\n"
                        f"We are now **{interaction.guild.member_count}** members strong. "
                        f"Enjoy your stay!"
                    ),
                    color=discord.Color.gold()
                )
                welcome_embed.set_thumbnail(url=self.target_member.display_avatar.url)
                welcome_embed.set_footer(text=f"{interaction.guild.name} Family")
                
                await chat_channel.send(content=f"Welcome to the server, {self.target_member.mention}! 👋", embed=welcome_embed)


# --- REGISTRATION ACTION VIEW (BUTTONS) ---
class RegisterActionView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=None)
        self.target_member = target_member

    @discord.ui.button(label="Male", style=discord.ButtonStyle.primary, custom_id="reg_btn_man", emoji="👨")
    async def register_man(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = get_settings()
        staff_role_id = settings.get("registration", {}).get("register_staff_role_id")
        staff_role = interaction.guild.get_role(staff_role_id) if staff_role_id else None
        
        if staff_role and staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only **Registration Staff** can use this button!", ephemeral=True)
            return

        await interaction.response.send_modal(RegisterModal(target_member=self.target_member, gender="man"))

    @discord.ui.button(label="Female", style=discord.ButtonStyle.danger, custom_id="reg_btn_woman", emoji="👩")
    async def register_woman(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = get_settings()
        staff_role_id = settings.get("registration", {}).get("register_staff_role_id")
        staff_role = interaction.guild.get_role(staff_role_id) if staff_role_id else None
        
        if staff_role and staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only **Registration Staff** can use this button!", ephemeral=True)
            return

        await interaction.response.send_modal(RegisterModal(target_member=self.target_member, gender="woman"))


# --- COG & SLASH COMMANDS ---
class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = get_settings()
        reg_cfg = settings.get("registration", {})
        channel_id = reg_cfg.get("register_channel_id")
        unreg_role_id = reg_cfg.get("unregistered_role_id")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        if unreg_role_id:
            unreg_role = member.guild.get_role(unreg_role_id)
            if unreg_role:
                try:
                    await member.add_roles(unreg_role)
                except Exception:
                    pass

        embed = discord.Embed(
            title="👋 A New Member Joined!",
            description=f"Welcome {member.mention}!\n\nRegistration staff will assist you shortly.",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=f"`{member.created_at.strftime('%Y-%m-%d')}`", inline=False)
        embed.set_footer(text=f"User ID: {member.id}")

        view = RegisterActionView(target_member=member)
        await channel.send(content=f"Registration panel for {member.mention}:", embed=embed, view=view)

    @app_commands.command(name="setup-register", description="Configures the server registration system.")
    @app_commands.describe(
        channel="The channel where registration messages will be sent",
        staff_role="The registration staff role",
        unreg_role="The unregistered role assigned to newcomers",
        man_role="The male member role",
        woman_role="The female member role",
        chat_channel="The general chat channel for welcome announcements",
        tag="Tag to prefix names with (e.g., ✦)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_register(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel, 
        staff_role: discord.Role, 
        unreg_role: discord.Role, 
        man_role: discord.Role, 
        woman_role: discord.Role, 
        chat_channel: discord.TextChannel = None,
        tag: str = "✦"
    ):
        settings = get_settings()
        if "registration" not in settings:
            settings["registration"] = {}

        settings["registration"]["register_channel_id"] = channel.id
        settings["registration"]["register_staff_role_id"] = staff_role.id
        settings["registration"]["unregistered_role_id"] = unreg_role.id
        settings["registration"]["man_role_id"] = man_role.id
        settings["registration"]["woman_role_id"] = woman_role.id
        settings["registration"]["chat_channel_id"] = chat_channel.id if chat_channel else None
        settings["registration"]["tag"] = tag

        save_settings(settings)

        embed = discord.Embed(
            title="✅ Registration System Successfully Configured",
            description="The server registration system is now active and ready.",
            color=discord.Color.green()
        )
        embed.add_field(name="Registration Channel", value=channel.mention, inline=False)
        embed.add_field(name="Staff Role", value=staff_role.mention, inline=True)
        embed.add_field(name="Unregistered Role", value=unreg_role.mention, inline=True)
        embed.add_field(name="Male / Female Roles", value=f"{man_role.mention} / {woman_role.mention}", inline=False)
        if chat_channel:
            embed.add_field(name="Welcome Chat Channel", value=chat_channel.mention, inline=False)
        embed.add_field(name="Registration Tag", value=f"`{tag}`", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Register(bot))