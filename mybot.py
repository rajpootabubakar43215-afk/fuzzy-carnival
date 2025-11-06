import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import re
import random
from PIL import Image, ImageDraw, ImageFont  # pip install pillow
import io

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Own Server Config
SERVER_IP = '5.39.63.207'
SERVER_PORT = 3938

# API
COD_PM_API = 'https://api.cod.pm/masterlist/cod/1.1'

# CoD Colors for Preview Image
COD_COLORS = {
    '^0': (0, 0, 0),      # Black
    '^1': (255, 0, 0),    # Red
    '^2': (0, 255, 0),    # Green
    '^3': (255, 255, 0),  # Yellow
    '^4': (0, 0, 255),    # Blue
    '^5': (255, 0, 255),  # Magenta
    '^6': (0, 255, 255),  # Cyan
    '^7': (255, 255, 255),# White
    '^8': (128, 0, 0),    # Dark Red
    '^9': (0, 128, 0),    # Dark Green
}

# Country flags mapping
COUNTRY_FLAGS = {
    'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'IN': '🇮🇳', 'BR': '🇧🇷', 'RU': '🇷🇺', 'JP': '🇯🇵', 'CN': '🇨🇳', 'KR': '🇰🇷',
    'NL': '🇳🇱', 'SE': '🇸🇪', 'IT': '🇮🇹', 'ES': '🇪🇸', 'PL': '🇵🇱', 'TR': '🇹🇷'
}

# CoD Quotes
COD_QUOTES = [
    '"Stay frosty." - Captain Price',
    '"All we are is dust in the wind." - Soap',
    '"Ghost, this is it. Were done." - Price',
    '"Boom, headshot!" - Random camper',
    '"No Russian... but you know, in game." - Makarov'
]

def clean_text(text):
    """Clean CoD color codes and non-printable chars."""
    text = re.sub(r'\^[0-9a-f]', '', text, flags=re.IGNORECASE)
    text = ''.join(c for c in text if c.isprintable() or c == ' ')
    return text.strip()[:50]

def get_flag(country_code):
    """Get flag emoji for country code."""
    return COUNTRY_FLAGS.get(country_code.upper(), '🌍')

async def get_servers_from_api():
    """Fetch server list from cod.pm API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(COD_PM_API) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('servers', [])
    except Exception as e:
        print(f"API Error: {e}")
    return []

@bot.event
async def on_ready():
    print(f'{bot.user} online hai, bhai! Ready for CoD queries.')

# Custom Help Command
@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(title="🛡️ Eclipse Bot - CoD 1.1 Commands", description="All commands with emojis! 🎮", color=0x00ff00)
    embed.add_field(name="🖥️ Server Status", value="!status - Your server info\n!status all - Top 20 servers\n!serverinfo <index> - Detailed server info", inline=False)
    embed.add_field(name="👥 Players", value="!players - Your server players\n!playersall - Top servers players summary\n!topplayers - Global top scorers", inline=False)
    embed.add_field(name="🔍 Search & Filter", value="!search <name> - Find servers\n!filter <gametype> - Filter by mode (dm, tdm, etc.)\n!random - Random server\n!join <index> - Connect to server", inline=False)
    embed.add_field(name="📊 Stats", value="!servercount - Total online\n!topmaps - Popular maps\n!gametypes - Game modes\n!lowpop - Low player count servers", inline=False)
    embed.add_field(name="🎨 Fun", value="!previewtag <text> - Preview CoD colored tag\n!codjoke - Random CoD joke\n!randommap - Suggest a map\n!quote - Random CoD quote\n!kill <user> - Fun kill message", inline=False)
    embed.add_field(name="⚙️ Bot", value="!ping - Bot latency\n!info - Bot details\n!rules - Server rules\n!invite - Bot invite link\n!support - Support info", inline=False)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="Type !help for this menu")
    await ctx.send(embed=embed)

# Status Commands
@bot.command(name='status')
async def status(ctx, *, arg=None):
    """Own server or all servers status."""
    servers = await get_servers_from_api()
    if not servers:
        embed = discord.Embed(title="❌ No servers found!", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    if arg and arg.lower() == 'all':
        # All servers - Top 20
        embed = discord.Embed(title="🌐 All CoD 1.1 Servers (Top 20 by Players)", color=0xff9900)
        sorted_servers = sorted(servers, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)), reverse=True)[:20]
        summary = []
        for i, server in enumerate(sorted_servers, 1):
            hostname = clean_text(server.get('sv_hostname', 'Unknown'))
            map_name = server.get('mapname', 'Unknown')
            players = server.get('clients', 0) + server.get('bots', 0)
            max_players = server.get('sv_maxclients', 0)
            country = get_flag(server.get('country', ''))
            ip_port = f"{server['ip']}:{server['port']}"
            summary.append(f"{i}. 🏷️ **{hostname}** {country} | 🗺️ {map_name} | 👥 {players}/{max_players}\n   🔗 `\\connect {ip_port}`")
        
        embed.description = '\n'.join(summary) if summary else "No active servers."
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        # Own server
        embed = discord.Embed(title="🖥️ Eclipse | Clan Server Status", color=0x00ff00)
        my_server = next((s for s in servers if s['ip'] == SERVER_IP and s['port'] == SERVER_PORT), None)
        if my_server:
            hostname = clean_text(my_server['sv_hostname'])
            map_name = my_server.get('mapname', 'Unknown')
            gametype = my_server.get('g_gametype', 'Unknown')
            players = my_server.get('clients', 0) + my_server.get('bots', 0)
            max_players = my_server.get('sv_maxclients', 0)
            country = get_flag(my_server.get('country', ''))
            ip_port = f"{my_server['ip']}:{my_server['port']}"
            embed.add_field(name="🏷️ Name", value=hostname, inline=True)
            embed.add_field(name="🌍 Location", value=country, inline=True)
            embed.add_field(name="🗺️ Map", value=map_name, inline=True)
            embed.add_field(name="⚔️ Gametype", value=gametype, inline=True)
            embed.add_field(name="👥 Players", value=f"{players}/{max_players}", inline=True)
            embed.add_field(name="🔗 Connect", value=f"`\\connect {ip_port}`", inline=False)
            
            # Players list if few
            if my_server.get('playerinfo'):
                playerinfo = my_server['playerinfo'][:5]  # Top 5
                player_text = '\n'.join([f"👤 {clean_text(p.get('name', 'Unknown'))} ({p.get('score', 0)} pts)" for p in playerinfo])
                if player_text:
                    embed.add_field(name="⭐ Top Players", value=player_text, inline=False)
                else:
                    embed.add_field(name="👥 Online Players", value="None right now! Join in.", inline=False)
            embed.timestamp = discord.utils.utcnow()
        else:
            embed.description = "❌ Server not found on cod.pm! IP/port check kar."
        await ctx.send(embed=embed)

# Server Info Command
@bot.command(name='serverinfo')
async def server_info(ctx, index: int = None):
    if not index:
        await ctx.send("ℹ️ !serverinfo <number> - Use after !status all, e.g., !serverinfo 1")
        return
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    sorted_servers = sorted(servers, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)), reverse=True)
    if 1 <= index <= len(sorted_servers):
        server = sorted_servers[index - 1]
        hostname = clean_text(server['sv_hostname'])
        map_name = server.get('mapname', 'Unknown')
        gametype = server.get('g_gametype', 'Unknown')
        players = server.get('clients', 0) + server.get('bots', 0)
        max_players = server.get('sv_maxclients', 0)
        country = get_flag(server.get('country', ''))
        ip_port = f"{server['ip']}:{server['port']}"
        protocol = server.get('protocol', 'Unknown')
        embed = discord.Embed(title=f"ℹ️ Detailed Info: Server #{index}", color=0x0099ff)
        embed.add_field(name="🏷️ Name", value=f"{hostname} {country}", inline=True)
        embed.add_field(name="🗺️ Map", value=map_name, inline=True)
        embed.add_field(name="⚔️ Gametype", value=gametype, inline=True)
        embed.add_field(name="👥 Players", value=f"{players}/{max_players}", inline=True)
        embed.add_field(name="🔗 Connect", value=f"`\\connect {ip_port}`", inline=False)
        embed.add_field(name="📡 Protocol", value=protocol, inline=True)
        if server.get('playerinfo'):
            top_player = clean_text(server['playerinfo'][0].get('name', 'Unknown')) if server['playerinfo'] else 'N/A'
            embed.add_field(name="👑 Top Player", value=top_player, inline=True)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Invalid index! Check !status all for numbers.")

# Players Commands
@bot.command(name='players')
async def players(ctx):
    """Own server players list."""
    embed = discord.Embed(title="👥 Eclipse Players", color=0x0099ff)
    servers = await get_servers_from_api()
    my_server = next((s for s in servers if s['ip'] == SERVER_IP and s['port'] == SERVER_PORT), None)
    if my_server and my_server.get('playerinfo'):
        playerinfo = my_server['playerinfo']
        total = len(playerinfo)
        if total > 0:
            player_text = '\n'.join([f"👤 {clean_text(p.get('name', 'Unknown'))} | 📡 {p.get('ping', 0)} | 🏆 {p.get('score', 0)}" for p in playerinfo])[:1024]
            embed.add_field(name=f"Total: {total} Players", value=player_text or "No players.", inline=False)
        else:
            embed.add_field(name="Total: 0 Players", value="No players online. Invite friends! 🎉", inline=False)
    else:
        embed.description = "❌ No players or server unreachable!"
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='playersall')
async def players_all(ctx):
    """All servers players summary."""
    embed = discord.Embed(title="👥 All CoD 1.1 Servers Players Summary (Top Active)", color=0x9900ff)
    servers = await get_servers_from_api()
    if not servers:
        embed.description = "❌ No servers found!"
        await ctx.send(embed=embed)
        return
    
    sorted_servers = sorted(servers, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)), reverse=True)
    total_players = sum((s.get('clients', 0) + s.get('bots', 0)) for s in sorted_servers[:15])
    active_servers = [s for s in sorted_servers[:15] if (s.get('clients', 0) + s.get('bots', 0)) > 0]
    
    summary = []
    for server in active_servers:
        hostname = clean_text(server['sv_hostname'])
        players = server.get('clients', 0) + server.get('bots', 0)
        max_players = server.get('sv_maxclients', 0)
        playerinfo = server.get('playerinfo', [])
        sample = ', '.join([clean_text(p.get('name', 'Unknown')) for p in playerinfo[:3]]) if playerinfo else 'Empty'
        country = get_flag(server.get('country', ''))
        summary.append(f"🏷️ **{hostname}** {country} 👥 {players}/{max_players}\n👨‍👩‍👧‍👦 {sample}...")
    
    embed.add_field(name="Total Players Across Top Servers", value=str(total_players), inline=True)
    embed.description = '\n\n'.join(summary) if summary else "No active players."
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Search Command
@bot.command(name='search')
async def search(ctx, *, query: str = None):
    if not query:
        await ctx.send("🔍 !search <server name> - e.g., !search EgC")
        return
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    
    matches = [s for s in servers if query.lower() in clean_text(s.get('sv_hostname', '')).lower()]
    embed = discord.Embed(title=f"🔍 Search Results for '{query}'", color=0x0099ff)
    if matches:
        summary = []
        for server in matches[:5]:
            hostname = clean_text(server['sv_hostname'])
            map_name = server.get('mapname', 'Unknown')
            players = server.get('clients', 0) + server.get('bots', 0)
            country = get_flag(server.get('country', ''))
            ip_port = f"{server['ip']}:{server['port']}"
            summary.append(f"🏷️ **{hostname}** {country} | 🗺️ {map_name} | 👥 {players}\n   🔗 `\\connect {ip_port}`")
        embed.description = '\n'.join(summary)
    else:
        embed.description = "No servers found matching your query. Try broader terms!"
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Filter by Gametype
@bot.command(name='filter')
async def filter_servers(ctx, gametype: str = None):
    if not gametype:
        await ctx.send("🔧 !filter <gametype> - e.g., !filter tdm (dm, tdm, ctf, sd, htf)")
        return
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    filtered = [s for s in servers if gametype.lower() in s.get('g_gametype', '').lower()]
    if not filtered:
        await ctx.send(f"❌ No servers with gametype '{gametype}' found!")
        return
    embed = discord.Embed(title=f"🎯 Servers with {gametype.upper()} Mode (Top 10)", color=0x00ff00)
    sorted_filtered = sorted(filtered, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)), reverse=True)[:10]
    summary = []
    for server in sorted_filtered:
        hostname = clean_text(server['sv_hostname'])
        map_name = server.get('mapname', 'Unknown')
        players = server.get('clients', 0) + server.get('bots', 0)
        max_players = server.get('sv_maxclients', 0)
        country = get_flag(server.get('country', ''))
        ip_port = f"{server['ip']}:{server['port']}"
        summary.append(f"🏷️ **{hostname}** {country} | 🗺️ {map_name} | 👥 {players}/{max_players}\n   🔗 `\\connect {ip_port}`")
    embed.description = '\n'.join(summary)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Random Server
@bot.command(name='random')
async def random_server(ctx):
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    server = random.choice(servers)
    hostname = clean_text(server['sv_hostname'])
    map_name = server.get('mapname', 'Unknown')
    players = server.get('clients', 0) + server.get('bots', 0)
    max_players = server.get('sv_maxclients', 0)
    country = get_flag(server.get('country', ''))
    ip_port = f"{server['ip']}:{server['port']}"
    embed = discord.Embed(title="🎲 Random CoD Server", color=0x00ff00)
    embed.add_field(name="🏷️ Name", value=f"{hostname} {country}", inline=True)
    embed.add_field(name="🗺️ Map", value=map_name, inline=True)
    embed.add_field(name="👥 Players", value=f"{players}/{max_players}", inline=True)
    embed.add_field(name="🔗 Connect", value=f"`\\connect {ip_port}`", inline=False)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Join Command
@bot.command(name='join')
async def join(ctx, index: int = None):
    if not index:
        await ctx.send("🌐 !join <number> - Use after !status all, e.g., !join 1")
        return
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    sorted_servers = sorted(servers, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)), reverse=True)
    if 1 <= index <= len(sorted_servers):
        server = sorted_servers[index - 1]
        ip_port = f"{server['ip']}:{server['port']}"
        hostname = clean_text(server['sv_hostname'])
        embed = discord.Embed(title=f"🚀 Join Server #{index}", description=f"Copy: `\\connect {ip_port}`\n\n🏷️ **{hostname}**", color=0x00ff00)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Invalid index! Check !status all for numbers.")

# Server Count
@bot.command(name='servercount')
async def server_count(ctx):
    servers = await get_servers_from_api()
    total = len(servers)
    active = len([s for s in servers if s.get('clients', 0) + s.get('bots', 0) > 0])
    embed = discord.Embed(title="📊 CoD 1.1 Server Stats", color=0x0099ff)
    embed.add_field(name="Total Servers", value=str(total), inline=True)
    embed.add_field(name="Active Servers", value=str(active), inline=True)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Top Maps
@bot.command(name='topmaps')
async def top_maps(ctx):
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    map_counts = {}
    for s in servers:
        map_name = s.get('mapname', 'Unknown')
        map_counts[map_name] = map_counts.get(map_name, 0) + 1
    top_maps = sorted(map_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(title="🗺️ Top 5 Popular Maps", color=0xff9900)
    summary = '\n'.join([f"{i+1}. {m[0]} ({m[1]} servers)" for i, m in enumerate(top_maps)])
    embed.description = summary or "No data."
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Gametypes
@bot.command(name='gametypes')
async def gametypes(ctx):
    types = {
        'dm': '💀 Deathmatch - Free-for-all kills!',
        'tdm': '⚔️ Team Deathmatch - Team kills!',
        'ctf': '🏴 Capture the Flag - Steal the flag!',
        'sd': '🔫 Search & Destroy - Plant/defuse bomb!',
        'htf': '👑 Hold the Flag - Hold the flag longest!'
    }
    embed = discord.Embed(title="⚔️ CoD Gametypes Guide", color=0x9900ff)
    for gt, desc in types.items():
        embed.add_field(name=gt.upper(), value=desc, inline=False)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Top Players (Global from API, top scorers across servers)
@bot.command(name='topplayers')
async def top_players(ctx):
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    all_players = []
    for s in servers:
        if s.get('playerinfo'):
            for p in s['playerinfo'][:3]:  # Top 3 per server
                all_players.append((p.get('score', 0), clean_text(p.get('name', 'Unknown')), clean_text(s.get('sv_hostname', ''))))
    all_players.sort(reverse=True, key=lambda x: x[0])[:10]
    embed = discord.Embed(title="🏆 Top 10 Global Players (by Score)", color=0x00ff00)
    summary = '\n'.join([f"{i+1}. {name} ({score} pts) on {server}" for i, (score, name, server) in enumerate(all_players)])
    embed.description = summary or "No player data."
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Low Pop Servers
@bot.command(name='lowpop')
async def low_pop(ctx):
    servers = await get_servers_from_api()
    if not servers:
        await ctx.send("❌ No servers found!")
        return
    low_servers = [s for s in servers if (s.get('clients', 0) + s.get('bots', 0)) < 10]
    if not low_servers:
        await ctx.send("❌ No low-pop servers found!")
        return
    embed = discord.Embed(title="👥 Low Population Servers (Under 10 Players)", color=0x0099ff)
    sorted_low = sorted(low_servers, key=lambda s: (s.get('clients', 0) + s.get('bots', 0)))[:10]
    summary = []
    for server in sorted_low:
        hostname = clean_text(server['sv_hostname'])
        map_name = server.get('mapname', 'Unknown')
        players = server.get('clients', 0) + server.get('bots', 0)
        max_players = server.get('sv_maxclients', 0)
        country = get_flag(server.get('country', ''))
        ip_port = f"{server['ip']}:{server['port']}"
        summary.append(f"🏷️ **{hostname}** {country} | 🗺️ {map_name} | 👥 {players}/{max_players}\n   🔗 `\\connect {ip_port}`")
    embed.description = '\n'.join(summary)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# Preview Tag with Image
@bot.command(name='previewtag')
async def preview_tag(ctx, *, text: str = None):
    if not text:
        await ctx.send("🎨 !previewtag <text> - e.g., !previewtag ^1Eclipse ^2Gaming ^3Community")
        return
    
    # Parse text into segments
    segments = []
    i = 0
    current_color = (255, 255, 255)  # Default white
    while i < len(text):
        if text[i:i+2] in COD_COLORS:
            current_color = COD_COLORS[text[i:i+2]]
            i += 2
        else:
            start = i
            while i < len(text) and text[i:i+2] not in COD_COLORS:
                i += 1
            segments.append((text[start:i], current_color))
    
    # Generate image
    img = Image.new('RGB', (600, 50), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)  # Assume system font
    except:
        font = ImageFont.load_default()
    
    x = 10
    for seg_text, color in segments:
        draw.text((x, 10), seg_text, fill=color, font=font)
        bbox = draw.textbbox((x, 10), seg_text, font=font)
        x += bbox[2] - bbox[0]
    
    # Save to bytes
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    
    clean = clean_text(text)
    embed = discord.Embed(title="🎨 CoD Tag Preview", description=f"**Clean Text:** {clean}", color=0x00ff00)
    embed.set_image(url="attachment://tag_preview.png")
    embed.add_field(name="Color Guide", value="^1=Red, ^2=Green, ^3=Yellow, ^4=Blue, ^5=Magenta, ^6=Cyan, ^7=White", inline=False)
    file = discord.File(bio, 'tag_preview.png')
    await ctx.send(embed=embed, file=file)

# CoD Joke
@bot.command(name='codjoke')
async def cod_joke(ctx):
    jokes = [
        "Why did the camper bring a tent to CoD? Because he wanted to 'camp' out! 🏕️",
        "What's a sniper's favorite music? Heavy metal... with a scope! 🎸",
        "Why don't CoD players trust stairs? They're always up to something! ⬆️",
        "How does a noob apologize? 'Sorry, I was just warming up my potato aim!' 🥔"
    ]
    joke = random.choice(jokes)
    embed = discord.Embed(title="😂 Random CoD Joke", description=joke, color=0xff9900)
    await ctx.send(embed=embed)

# Random Map
@bot.command(name='randommap')
async def random_map(ctx):
    maps = ['mp_harbor', 'mp_toujane', 'mp_brecourt', 'mp_carentan', 'mp_chateau', 'mp_dawnville']
    map_name = random.choice(maps)
    embed = discord.Embed(title="🗺️ Random Map Suggestion", description=f"Try: **{map_name}** - Perfect for some action! 🚀", color=0x0099ff)
    await ctx.send(embed=embed)

# CoD Quote
@bot.command(name='quote')
async def cod_quote(ctx):
    quote = random.choice(COD_QUOTES)
    embed = discord.Embed(title="💬 Random CoD Quote", description=quote, color=0x9900ff)
    await ctx.send(embed=embed)

# Fun Kill Command
@bot.command(name='kill')
async def fun_kill(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    kills = [
        f"{member.mention} was headshot by a camper! 💥",
        f"{member.mention} tripped on a grenade! 🧨",
        f"{member.mention} got knifed from behind! 🔪",
        f"{member.mention} fell off the map! 😵"
    ]
    kill_msg = random.choice(kills)
    embed = discord.Embed(title="💀 You Died", description=kill_msg, color=0xff0000)
    await ctx.send(embed=embed)

# Rules
@bot.command(name='rules')
async def rules(ctx):
    rules = [
        "1. No cheating or hacks! 🚫",
        "2. Respect all players - no toxicity! 😡",
        "3. Listen to admins. 👮",
        "4. Have fun! 🎉"
    ]
    embed = discord.Embed(title="📜 Eclipse Gaming Community Rules", description='\n'.join(rules), color=0x00ff00)
    await ctx.send(embed=embed)

# Invite
@bot.command(name='invite')
async def invite(ctx):
    invite_link = "https://discord.com/oauth2/authorize?client_id=1427722782308962405&permissions=277025463296&integration_type=0&scope=bot"  # Replace with your bot ID
    embed = discord.Embed(title="🔗 InviteEclipse Bot", description=f"Click to invite: {invite_link}", color=0x00ff00)
    await ctx.send(embed=embed)

# Support
@bot.command(name='support')
async def support(ctx):
    support_server = "https://discord.gg/your-support-server"  # Add your support server link
    embed = discord.Embed(title="🆘 Support", description=f"Join support: {support_server}\nFor bugs or features!", color=0x0099ff)
    await ctx.send(embed=embed)

# Ping
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: {latency}ms", color=0x00ff00)
    await ctx.send(embed=embed)

# Info
@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(title="ℹ️ Eclipse | Bot Info", color=0x0099ff)
    embed.add_field(name="Version", value="2.0 -  CoD Edition", inline=True)
    embed.add_field(name="Servers Monitored", value="CoD 1.1 via cod.pm", inline=True)
    embed.add_field(name="Prefix", value="!", inline=True)
    embed.add_field(name="Developer", value="Zytrix", inline=True)
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=" Pro Level! 🎮")
    await ctx.send(embed=embed)

# Run Bot
if __name__ == '__main__':
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or 'MTQyNzcyMjc4MjMwODk2MjQwNQ.GHSoec.jN33QPedQkNS7TfrA9__QocHcNtRtyTQLxyZUE'
    bot.run(DISCORD_TOKEN)
