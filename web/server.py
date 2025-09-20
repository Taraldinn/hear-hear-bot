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
                    'description': 'Advanced timer system with visual progress bars and multiple timers'
                },
                {
                    'icon': '🎯',
                    'title': 'Motion System',
                    'description': 'Load from Google Sheets/CSV with info slides and statistics tracking'
                },
                {
                    'icon': '🎭',
                    'title': 'Reaction Roles',
                    'description': 'Carl-bot level reaction roles with 6 modes, self-destruct, and role limits'
                },
                {
                    'icon': '�',
                    'title': 'Advanced Logging',
                    'description': 'Comprehensive logging system tracking all server activity with smart filtering'
                },
                {
                    'icon': '🛡️',
                    'title': 'Moderation System',
                    'description': 'Professional moderation with timed actions, sticky roles, and audit trails'
                },
                {
                    'icon': '🎲',
                    'title': 'Debate Tools',
                    'description': 'AP/BP toss, position guides, formats, and tournament management'
                },
                {
                    'icon': '⚙️',
                    'title': 'Server Config',
                    'description': 'Extensive customization with auto-roles, prefixes, and welcome systems'
                },
                {
                    'icon': '�',
                    'title': 'Tabbycat Integration',
                    'description': 'Full tournament software integration for professional competitions'
                },
                {
                    'icon': '🌐',
                    'title': 'Multi-language',
                    'description': 'English and Bangla support with expandable architecture'
                },
                {
                    'icon': '⚡',
                    'title': 'Slash Commands',
                    'description': 'Modern Discord interface with instant guild sync for testing'
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
                            <h2 class="text-5xl font-bold mb-6">Complete Discord Server Management</h2>
                            <p class="text-xl mb-8 opacity-90">Advanced debate tools + Carl-bot level features: reaction roles, logging, moderation, and more</p>
                            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                                <a href="/invite" class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                                    🚀 Add to Discord
                                </a>
                                <a href="/commands" class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                                    📖 View Commands
                                </a>
                            </div>
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
                            <h2 class="text-3xl font-bold text-center mb-12">🚀 Advanced Features</h2>
                            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
                                    <div class="text-4xl mb-4">⏱️</div>
                                    <h3 class="text-xl font-semibold mb-2">Advanced Timer</h3>
                                    <p class="text-gray-600">Visual progress bars, multiple timers, pause/resume</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
                                    <div class="text-4xl mb-4">�</div>
                                    <h3 class="text-xl font-semibold mb-2">Reaction Roles</h3>
                                    <p class="text-gray-600">6 modes, self-destruct, role limits, any emoji</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
                                    <div class="text-4xl mb-4">�</div>
                                    <h3 class="text-xl font-semibold mb-2">Advanced Logging</h3>
                                    <p class="text-gray-600">Message/member/server logs with smart filtering</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-500">
                                    <div class="text-4xl mb-4">🛡️</div>
                                    <h3 class="text-xl font-semibold mb-2">Pro Moderation</h3>
                                    <p class="text-gray-600">Timed actions, sticky roles, audit trails</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-yellow-500">
                                    <div class="text-4xl mb-4">🎯</div>
                                    <h3 class="text-xl font-semibold mb-2">Debate Tools</h3>
                                    <p class="text-gray-600">AP/BP toss, motions from Google Sheets</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-indigo-500">
                                    <div class="text-4xl mb-4">⚙️</div>
                                    <h3 class="text-xl font-semibold mb-2">Server Config</h3>
                                    <p class="text-gray-600">Auto-roles, prefixes, welcome systems</p>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- Carl-bot Features Section -->
                    <section class="py-16 bg-white">
                        <div class="max-w-6xl mx-auto px-4">
                            <div class="text-center mb-12">
                                <h2 class="text-3xl font-bold mb-4">🤖 Carl-bot Level Features</h2>
                                <p class="text-gray-600 text-lg">Professional server management tools that rival the best Discord bots</p>
                            </div>
                            <div class="grid md:grid-cols-2 gap-8">
                                <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
                                    <h3 class="text-xl font-bold mb-4 text-purple-800">🎭 Advanced Reaction Roles</h3>
                                    <ul class="space-y-2 text-gray-700">
                                        <li>✅ <strong>6 Modes:</strong> Unique, verify, reversed, binding, temporary</li>
                                        <li>✅ <strong>High Limits:</strong> 250+ roles per message</li>
                                        <li>✅ <strong>Any Emoji:</strong> Custom emojis from any server</li>
                                        <li>✅ <strong>Self-Destruct:</strong> Auto-delete messages</li>
                                        <li>✅ <strong>Role Control:</strong> Whitelist/blacklist & max uses</li>
                                    </ul>
                                </div>
                                <div class="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                                    <h3 class="text-xl font-bold mb-4 text-blue-800">📊 Comprehensive Logging</h3>
                                    <ul class="space-y-2 text-gray-700">
                                        <li>✅ <strong>Message Logs:</strong> Edits, deletes, purges</li>
                                        <li>✅ <strong>Member Tracking:</strong> Roles, nicknames, avatars</li>
                                        <li>✅ <strong>Server Changes:</strong> Channels, roles, emojis</li>
                                        <li>✅ <strong>Invite Tracking:</strong> See which invite was used</li>
                                        <li>✅ <strong>Smart Filtering:</strong> Ignore channels/users/prefixes</li>
                                    </ul>
                                </div>
                                <div class="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-lg">
                                    <h3 class="text-xl font-bold mb-4 text-red-800">🛡️ Professional Moderation</h3>
                                    <ul class="space-y-2 text-gray-700">
                                        <li>✅ <strong>Timed Actions:</strong> Auto-expiring mutes & bans</li>
                                        <li>✅ <strong>Sticky Roles:</strong> Persist when users rejoin</li>
                                        <li>✅ <strong>Audit Trails:</strong> Full mod action history</li>
                                        <li>✅ <strong>Case IDs:</strong> Track every moderation action</li>
                                        <li>✅ <strong>Drama Channel:</strong> Alert mods to violations</li>
                                    </ul>
                                </div>
                                <div class="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                                    <h3 class="text-xl font-bold mb-4 text-green-800">⚙️ Server Configuration</h3>
                                    <ul class="space-y-2 text-gray-700">
                                        <li>✅ <strong>Auto Roles:</strong> Automatic role assignment</li>
                                        <li>✅ <strong>Custom Prefixes:</strong> Multiple command prefixes</li>
                                        <li>✅ <strong>Welcome System:</strong> Member join/leave messages</li>
                                        <li>✅ <strong>Multi-language:</strong> English & Bangla support</li>
                                        <li>✅ <strong>Easy Setup:</strong> Intuitive configuration commands</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- Quick Start Section -->
                    <section class="py-16 bg-gradient-to-r from-gray-50 to-blue-50">
                        <div class="max-w-4xl mx-auto px-4 text-center">
                            <h2 class="text-3xl font-bold mb-8">🚀 Quick Start Guide</h2>
                            <div class="grid md:grid-cols-3 gap-6">
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-3xl mb-4">1️⃣</div>
                                    <h3 class="text-lg font-semibold mb-2">Add Bot</h3>
                                    <p class="text-gray-600">Invite the bot with full permissions</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-3xl mb-4">2️⃣</div>
                                    <h3 class="text-lg font-semibold mb-2">Use /guild_sync</h3>
                                    <p class="text-gray-600">Get instant access to slash commands</p>
                                </div>
                                <div class="bg-white p-6 rounded-lg shadow-sm">
                                    <div class="text-3xl mb-4">3️⃣</div>
                                    <h3 class="text-lg font-semibold mb-2">Configure</h3>
                                    <p class="text-gray-600">Use /setup commands to customize</p>
                                </div>
                            </div>
                            <div class="mt-8">
                                <a href="/commands" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                                    📖 View All Commands
                                </a>
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
                # Debate Commands
                {'name': '/timer start', 'description': 'Start a debate timer'},
                {'name': '/timer stop', 'description': 'Stop your active timer'},
                {'name': '/timer check', 'description': 'Check timer status'},
                {'name': '/randommotion', 'description': 'Get a random debate motion'},
                {'name': '/coinflip', 'description': 'Flip a coin for decisions'},
                {'name': '/diceroll', 'description': 'Roll a dice'},
                {'name': '/toss ap', 'description': 'AP debate toss with member mentions'},
                {'name': '/toss bp', 'description': 'BP debate toss with member mentions'},
                {'name': '/positions', 'description': 'Show debate positions guide'},
                {'name': '/formats', 'description': 'Show debate formats'},
                {'name': '/motionstats', 'description': 'Show motion statistics'},
                
                # Carl-bot Level Features
                {'name': '/reaction_role add', 'description': 'Add reaction roles with advanced modes'},
                {'name': '/reaction_role remove', 'description': 'Remove reaction roles'},
                {'name': '/reaction_role edit', 'description': 'Edit existing reaction roles'},
                {'name': '/reaction_role list', 'description': 'List all reaction roles'},
                
                {'name': '/log setup', 'description': 'Configure logging channels'},
                {'name': '/log disable', 'description': 'Disable specific logging'},
                {'name': '/log ignore', 'description': 'Ignore channels/users from logs'},
                
                {'name': '/moderation mute', 'description': 'Mute a user with optional duration'},
                {'name': '/moderation unmute', 'description': 'Unmute a user'},
                {'name': '/moderation ban', 'description': 'Ban a user with optional duration'},
                {'name': '/moderation unban', 'description': 'Unban a user'},
                {'name': '/moderation kick', 'description': 'Kick a user from server'},
                {'name': '/moderation sticky_role add', 'description': 'Add sticky roles that persist'},
                {'name': '/moderation modlogs', 'description': 'View moderation logs'},
                
                {'name': '/setup autorole', 'description': 'Configure automatic role assignment'},
                {'name': '/setup prefix', 'description': 'Set custom command prefixes'},
                {'name': '/setup welcome', 'description': 'Configure welcome messages'},
                {'name': '/setup language', 'description': 'Set server language'},
                
                # Utility Commands
                {'name': '/help', 'description': 'Show comprehensive help system'},
                {'name': '/ping', 'description': 'Check bot latency'},
                {'name': '/guild_sync', 'description': 'Instantly sync slash commands for testing'},
            ]
            
            prefix_commands = [
                {'name': '.tabsync', 'description': 'Connect to Tabbycat tournament (Admin)'},
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
                                            <code class="text-yellow-600">.tabsync &lt;url&gt; &lt;token&gt;</code>
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
