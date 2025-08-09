"""
Web Server for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com

A beautiful landing page for the Discord bot
"""

from aiohttp import web
import json
import logging
from pathlib import Path
from config.settings import Config

# Try to import optional dependencies
try:
    import aiohttp_jinja2
    import jinja2
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

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
        if HAS_JINJA:
            template_path = Path(__file__).parent / 'templates'
            aiohttp_jinja2.setup(
                self.app,
                loader=jinja2.FileSystemLoader(str(template_path))
            )
        else:
            logger.warning("Jinja2 templates not available - using fallback HTML responses")
    
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
    
    async def home(self, request):
        """Homepage - with fallback HTML if templates not available"""
        bot_stats = {
            'guilds': len(self.bot.guilds) if self.bot.guilds else 0,
            'users': sum(guild.member_count or 0 for guild in self.bot.guilds) if self.bot.guilds else 0,
            'latency': round(self.bot.latency * 1000) if self.bot.latency else 0,
            'version': Config.BOT_VERSION,
            'uptime': self.get_uptime()
        }
        
        if HAS_JINJA:
            # Use template rendering
            features = [
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
            
            return aiohttp_jinja2.render_template('index.html', request, {
                'bot_name': Config.BOT_NAME,
                'bot_author': Config.BOT_AUTHOR,
                'bot_stats': bot_stats,
                'features': features
            })
        else:
            # Fallback HTML response
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{Config.BOT_NAME} - Discord Debate Bot</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    body {{ font-family: Inter, system-ui, sans-serif; }}
                </style>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen">
                    <!-- Header -->
                    <header class="bg-white shadow-sm">
                        <div class="max-w-6xl mx-auto px-4 py-6">
                            <div class="flex items-center space-x-3">
                                <div class="text-3xl">🎯</div>
                                <div>
                                    <h1 class="text-2xl font-bold text-gray-900">{Config.BOT_NAME}</h1>
                                    <p class="text-gray-600">by {Config.BOT_AUTHOR}</p>
                                </div>
                            </div>
                        </div>
                    </header>
                    
                    <!-- Hero Section -->
                    <section class="bg-gradient-to-br from-blue-500 to-purple-600 text-white py-20">
                        <div class="max-w-6xl mx-auto px-4 text-center">
                            <h2 class="text-5xl font-bold mb-6">Professional Discord Debate Bot</h2>
                            <p class="text-xl mb-8 opacity-90">Complete tournament management with timing, motions, and Tabbycat integration</p>
                            <a href="/invite" class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                                🚀 Add to Discord
                            </a>
                        </div>
                    </section>
                    
                    <!-- Stats -->
                    <section class="py-16 bg-white">
                        <div class="max-w-6xl mx-auto px-4">
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                                <div>
                                    <div class="text-3xl font-bold text-blue-600">{bot_stats['guilds']}</div>
                                    <div class="text-gray-600">Discord Servers</div>
                                </div>
                                <div>
                                    <div class="text-3xl font-bold text-purple-600">{bot_stats['users']}</div>
                                    <div class="text-gray-600">Users Served</div>
                                </div>
                                <div>
                                    <div class="text-3xl font-bold text-green-600">{bot_stats['latency']}ms</div>
                                    <div class="text-gray-600">Response Time</div>
                                </div>
                                <div>
                                    <div class="text-3xl font-bold text-orange-600">{bot_stats['uptime']}</div>
                                    <div class="text-gray-600">Uptime</div>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- Features -->
                    <section class="py-16 bg-gray-50">
                        <div class="max-w-6xl mx-auto px-4">
                            <h2 class="text-3xl font-bold text-center mb-12">Key Features</h2>
                            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">⏱️</div>
                                    <h3 class="text-xl font-semibold mb-2">Debate Timer</h3>
                                    <p class="text-gray-600">Built-in timer system with slash commands</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">🎯</div>
                                    <h3 class="text-xl font-semibold mb-2">Motion Database</h3>
                                    <p class="text-gray-600">Thousands of debate motions in multiple languages</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">🔗</div>
                                    <h3 class="text-xl font-semibold mb-2">Tabbycat Integration</h3>
                                    <p class="text-gray-600">Full tournament software integration</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">🌐</div>
                                    <h3 class="text-xl font-semibold mb-2">Multi-language</h3>
                                    <p class="text-gray-600">English and Bangla support</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">⚡</div>
                                    <h3 class="text-xl font-semibold mb-2">Slash Commands</h3>
                                    <p class="text-gray-600">Modern Discord command interface</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-4xl mb-4">👑</div>
                                    <h3 class="text-xl font-semibold mb-2">Admin Tools</h3>
                                    <p class="text-gray-600">Comprehensive server management</p>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- Footer -->
                    <footer class="bg-gray-800 text-white py-8">
                        <div class="max-w-6xl mx-auto px-4 text-center">
                            <p>&copy; 2025 {Config.BOT_NAME}. Made for the debate community.</p>
                            <div class="mt-4 space-x-6">
                                <a href="/commands" class="text-blue-400 hover:text-blue-300">Commands</a>
                                <a href="/api/stats" class="text-blue-400 hover:text-blue-300">API</a>
                                <a href="/invite" class="text-blue-400 hover:text-blue-300">Add to Discord</a>
                            </div>
                        </div>
                    </footer>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
    
    async def stats(self, request):
        """Stats page"""
        return await self.home(request)
    
    async def commands(self, request):
        """Commands page"""
        if HAS_JINJA:
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
            
            return aiohttp_jinja2.render_template('commands.html', request, {
                'bot_name': Config.BOT_NAME,
                'slash_commands': slash_commands,
                'prefix_commands': prefix_commands
            })
        else:
            # Fallback HTML for commands
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Commands - {Config.BOT_NAME}</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen">
                    <header class="bg-white shadow-sm">
                        <div class="max-w-6xl mx-auto px-4 py-6">
                            <div class="flex justify-between items-center">
                                <a href="/" class="flex items-center space-x-3">
                                    <div class="text-3xl">🎯</div>
                                    <div class="text-xl font-bold">{Config.BOT_NAME}</div>
                                </a>
                                <a href="/invite" class="bg-blue-600 text-white px-4 py-2 rounded-lg">Add to Discord</a>
                            </div>
                        </div>
                    </header>
                    
                    <section class="py-16">
                        <div class="max-w-6xl mx-auto px-4">
                            <h1 class="text-4xl font-bold text-center mb-8">Bot Commands</h1>
                            
                            <div class="grid md:grid-cols-2 gap-8">
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <h2 class="text-2xl font-bold mb-4">⚡ Slash Commands</h2>
                                    <div class="space-y-3">
                                        <div class="border-l-4 border-blue-500 pl-4">
                                            <code class="text-blue-600">/timer start/stop/check</code>
                                            <p class="text-gray-600">Manage debate timer</p>
                                        </div>
                                        <div class="border-l-4 border-blue-500 pl-4">
                                            <code class="text-blue-600">/randommotion</code>
                                            <p class="text-gray-600">Get random debate motion</p>
                                        </div>
                                        <div class="border-l-4 border-blue-500 pl-4">
                                            <code class="text-blue-600">/coinflip</code>
                                            <p class="text-gray-600">Flip a coin</p>
                                        </div>
                                        <div class="border-l-4 border-blue-500 pl-4">
                                            <code class="text-blue-600">/ping</code>
                                            <p class="text-gray-600">Check bot latency</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <h2 class="text-2xl font-bold mb-4">📝 Prefix Commands</h2>
                                    <div class="space-y-3">
                                        <div class="border-l-4 border-yellow-500 pl-4">
                                            <code class="text-yellow-600">.sync &lt;url&gt; &lt;token&gt;</code>
                                            <p class="text-gray-600">Connect to Tabbycat</p>
                                        </div>
                                        <div class="border-l-4 border-yellow-500 pl-4">
                                            <code class="text-yellow-600">.register &lt;key&gt;</code>
                                            <p class="text-gray-600">Register for tournament</p>
                                        </div>
                                        <div class="border-l-4 border-yellow-500 pl-4">
                                            <code class="text-yellow-600">.motion &lt;round&gt;</code>
                                            <p class="text-gray-600">Get round motion</p>
                                        </div>
                                        <div class="border-l-4 border-yellow-500 pl-4">
                                            <code class="text-yellow-600">.setlanguage &lt;lang&gt;</code>
                                            <p class="text-gray-600">Set server language</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
    
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
