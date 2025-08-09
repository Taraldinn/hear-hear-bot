"""
Web Server for Hear! Hear! Bot
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com

A beautiful landing page for the Discord bot
"""

from aiohttp import web, web_response
from aiohttp.web_static import static_file_response
import aiohttp_jinja2
import jinja2
import json
import logging
from pathlib import Path
from config.settings import Config

logger = logging.getLogger(__name__)

class WebServer:
    """Web server for bot homepage and API endpoints"""
    
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.setup_routes()
        self.setup_templates()
    
    def setup_templates(self):
        """Setup Jinja2 templates"""
        template_path = Path(__file__).parent / 'templates'
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(template_path))
        )
    
    def setup_routes(self):
        """Setup web routes"""
        # Static files
        static_path = Path(__file__).parent / 'static'
        self.app.router.add_static('/static/', static_path, name='static')
        
        # Pages
        self.app.router.add_get('/', self.home)
        self.app.router.add_get('/stats', self.stats)
        self.app.router.add_get('/commands', self.commands)
        self.app.router.add_get('/api/stats', self.api_stats)
        self.app.router.add_get('/invite', self.invite)
    
    @aiohttp_jinja2.template('index.html')
    async def home(self, request):
        """Homepage"""
        bot_stats = {
            'guilds': len(self.bot.guilds) if self.bot.guilds else 0,
            'users': sum(guild.member_count for guild in self.bot.guilds) if self.bot.guilds else 0,
            'latency': round(self.bot.latency * 1000) if self.bot.latency else 0,
            'version': Config.BOT_VERSION,
            'uptime': self.get_uptime()
        }
        
        return {
            'bot_name': Config.BOT_NAME,
            'bot_author': Config.BOT_AUTHOR,
            'bot_stats': bot_stats,
            'features': [
                {
                    'icon': '⏱️',
                    'title': 'Debate Timer',
                    'description': 'Built-in timer system with slash commands for debate timing'
                },
                {
                    'icon': '🎯',
                    'title': 'Motion Database',
                    'description': 'Access thousands of debate motions in multiple languages'
                },
                {
                    'icon': '🔗',
                    'title': 'Tabbycat Integration',
                    'description': 'Full integration with Tabbycat tournament software'
                },
                {
                    'icon': '🌐',
                    'title': 'Multi-language',
                    'description': 'Support for English and Bangla with expandable architecture'
                },
                {
                    'icon': '⚡',
                    'title': 'Slash Commands',
                    'description': 'Modern Discord slash commands for better user experience'
                },
                {
                    'icon': '👑',
                    'title': 'Admin Tools',
                    'description': 'Comprehensive moderation and server management features'
                }
            ]
        }
    
    @aiohttp_jinja2.template('stats.html')
    async def stats(self, request):
        """Stats page"""
        return await self.home(request)
    
    @aiohttp_jinja2.template('commands.html')
    async def commands(self, request):
        """Commands page"""
        slash_commands = [
            {'name': '/timer start', 'description': 'Start a debate timer'},
            {'name': '/timer stop', 'description': 'Stop your active timer'},
            {'name': '/timer check', 'description': 'Check timer status'},
            {'name': '/randommotion', 'description': 'Get a random debate motion'},
            {'name': '/coinflip', 'description': 'Flip a coin for decisions'},
            {'name': '/diceroll', 'description': 'Roll a dice'},
            {'name': '/ping', 'description': 'Check bot latency'},
            {'name': '/help', 'description': 'Show all commands'},
        ]
        
        prefix_commands = [
            {'name': '.sync', 'description': 'Connect to Tabbycat tournament (Admin)'},
            {'name': '.register', 'description': 'Register for tournament'},
            {'name': '.checkin', 'description': 'Check in to tournament'},
            {'name': '.motion', 'description': 'Get round motion'},
            {'name': '.setlanguage', 'description': 'Set server language (Admin)'},
        ]
        
        return {
            'bot_name': Config.BOT_NAME,
            'slash_commands': slash_commands,
            'prefix_commands': prefix_commands
        }
    
    async def api_stats(self, request):
        """API endpoint for bot stats"""
        stats = {
            'guilds': len(self.bot.guilds) if self.bot.guilds else 0,
            'users': sum(guild.member_count for guild in self.bot.guilds) if self.bot.guilds else 0,
            'latency': round(self.bot.latency * 1000) if self.bot.latency else 0,
            'version': Config.BOT_VERSION,
            'status': 'online' if self.bot.is_ready() else 'offline'
        }
        
        return web.json_response(stats)
    
    async def invite(self, request):
        """Redirect to bot invite"""
        bot_id = self.bot.user.id if self.bot.user else Config.BOT_TOKEN.split('.')[0] if Config.BOT_TOKEN else '1401966904578408539'
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot%20applications.commands"
        
        return web.Response(
            status=302,
            headers={'Location': invite_url}
        )
    
    def get_uptime(self):
        """Get bot uptime"""
        try:
            if hasattr(self.bot, 'start_time'):
                import time
                uptime_seconds = time.time() - self.bot.start_time
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
            return "Just started"
        except:
            return "Unknown"
    
    async def start_server(self, port=8080):
        """Start the web server"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"Web server started on port {port}")
            return runner
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            raise
