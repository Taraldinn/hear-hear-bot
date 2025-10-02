"""
Production-ready Web Server for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com

Clean, secure, and well-documented web server implementation.
"""

# pylint: disable=broad-exception-caught

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from aiohttp import web
from aiohttp.web import Response, Request

try:
    import aiohttp_jinja2
    import jinja2

    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    aiohttp_jinja2 = None
    jinja2 = None

from config.settings import Config

logger = logging.getLogger(__name__)


class WebServer:
    """Production-ready web server for bot homepage and API endpoints"""

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.setup_middleware()
        self.setup_routes()
        self.setup_templates()

    def setup_middleware(self) -> None:
        """Setup middleware for error handling and logging"""

        @web.middleware
        async def error_middleware(request: Request, handler):
            try:
                response = await handler(request)
                return response
            except web.HTTPException as ex:
                logger.warning("HTTP %s: %s", ex.status, request.path)
                return ex
            except Exception as ex:  # pragma: no cover - generic safety net
                logger.error("Unhandled error in %s: %s", request.path, ex)
                logger.error(traceback.format_exc())
                return web.Response(
                    text="Internal Server Error",
                    status=500,
                    content_type="text/plain",
                )

        @web.middleware
        async def logging_middleware(request: Request, handler):
            start_time = datetime.utcnow()
            response = await handler(request)
            process_time = (datetime.utcnow() - start_time).total_seconds()

            logger.info(
                "%s %s - %s - %.3fs",
                request.method,
                request.path,
                response.status,
                process_time,
            )
            return response

        # register middlewares
        self.app.middlewares.append(error_middleware)
        self.app.middlewares.append(logging_middleware)

    def setup_templates(self) -> None:
        """Setup Jinja2 templates with error handling"""
        if HAS_JINJA and aiohttp_jinja2 and jinja2:
            try:
                template_path = Path(__file__).parent / "templates"
                if not template_path.exists():
                    logger.warning("Template directory not found: %s", template_path)
                    return

                aiohttp_jinja2.setup(
                    self.app, loader=jinja2.FileSystemLoader(str(template_path))
                )
                logger.info("Jinja2 templates configured successfully")
            except Exception as e:  # pragma: no cover - init fallback
                logger.error("Failed to setup templates: %s", e)
        else:
            logger.warning(
                "Jinja2 templates not available - using fallback HTML responses"
            )

    def setup_routes(self) -> None:
        """Setup web routes with error handling"""
        try:
            # Static files
            static_path = Path(__file__).parent / "static"
            if static_path.exists():
                self.app.router.add_static("/static/", static_path, name="static")
            else:
                logger.warning("Static directory not found: %s", static_path)

            # API endpoints
            self.app.router.add_get("/", self.home)
            self.app.router.add_get("/docs", self.documentation)
            self.app.router.add_get("/documentation", self.documentation)
            self.app.router.add_get("/stats", self.stats)
            self.app.router.add_get("/commands", self.commands)
            self.app.router.add_get("/api/stats", self.api_stats)
            self.app.router.add_get("/health", self.health)
            self.app.router.add_get("/invite", self.invite)

            logger.info("Web routes configured successfully")
        except Exception as e:  # pragma: no cover - init fallback
            logger.error("Failed to setup routes: %s", e)

    def _render_template(
        self,
        template_name: str,
        request: Request,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Response]:
        """Safe template rendering with fallback"""
        if HAS_JINJA and aiohttp_jinja2:
            try:
                return aiohttp_jinja2.render_template(
                    template_name, request, context or {}
                )
            except Exception as e:  # pragma: no cover - template fallback
                logger.error("Template rendering failed for %s: %s", template_name, e)
                return None
        return None

    def get_bot_stats(self) -> Dict[str, Any]:
        """Get current bot statistics safely"""
        try:
            if not self.bot:
                return {
                    "guilds": 0,
                    "users": 0,
                    "latency": 0,
                    "version": getattr(Config, "BOT_VERSION", "1.0.0"),
                    "uptime": "Unknown",
                    "status": "Offline",
                }

            return {
                "guilds": (
                    len(self.bot.guilds)
                    if hasattr(self.bot, "guilds") and self.bot.guilds
                    else 0
                ),
                "users": (
                    sum(
                        getattr(guild, "member_count", 0) or 0
                        for guild in self.bot.guilds
                    )
                    if hasattr(self.bot, "guilds") and self.bot.guilds
                    else 0
                ),
                "latency": (
                    round(self.bot.latency * 1000)
                    if hasattr(self.bot, "latency")
                    and self.bot.latency is not None
                    and not (
                        isinstance(self.bot.latency, float)
                        and (self.bot.latency != self.bot.latency)
                    )  # Check for NaN
                    else 0
                ),
                "version": getattr(Config, "BOT_VERSION", "1.0.0"),
                "uptime": self.get_bot_uptime(),
                "status": (
                    "Online"
                    if hasattr(self.bot, "is_ready") and self.bot.is_ready()
                    else "Starting"
                ),
            }
        except Exception as e:  # pragma: no cover - metrics fallback
            logger.error("Error getting bot stats: %s", e)
            return {
                "guilds": 0,
                "users": 0,
                "latency": 0,
                "version": "Unknown",
                "uptime": "Unknown",
                "status": "Error",
            }

    def get_bot_uptime(self) -> str:
        """Get bot uptime safely"""
        try:
            if hasattr(self.bot, "start_time") and self.bot.start_time:
                if hasattr(self.bot, "get_uptime"):
                    return str(self.bot.get_uptime())
                else:
                    uptime = datetime.utcnow() - self.bot.start_time
                    days = uptime.days
                    hours, remainder = divmod(uptime.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)

                    if days:
                        return f"{days}d {hours}h {minutes}m"
                    elif hours:
                        return f"{hours}h {minutes}m"
                    else:
                        return f"{minutes}m"
            return "Unknown"
        except Exception as e:  # pragma: no cover - uptime fallback
            logger.error("Error calculating uptime: %s", e)
            return "Unknown"

    async def home(self, request: Request) -> Response:
        """Homepage with comprehensive error handling"""
        try:
            bot_stats = self.get_bot_stats()

            # Try template rendering first
            template_response = self._render_template(
                "index.html",
                request,
                {
                    "bot_name": getattr(Config, "BOT_NAME", "AldinnBot"),
                    "bot_author": getattr(Config, "BOT_AUTHOR", "aldinn"),
                    "bot_stats": bot_stats,
                    "features": self._get_features_list(),
                },
            )

            if template_response:
                return template_response

            # Fallback HTML response
            return self._get_fallback_homepage(bot_stats)

        except Exception as e:
            logger.error("Error in home endpoint: %s", e)
            return web.Response(
                text=(
                    "<h1>Service Temporarily Unavailable</h1>"
                    "<p>Please try again later.</p>"
                ),
                content_type="text/html",
                status=503,
            )

    def _get_features_list(self) -> List[Dict[str, str]]:
        """Get list of bot features"""
        return [
            {
                "icon": "⏱️",
                "title": "Debate Timer",
                "description": (
                    "Advanced timer system with visual progress bars "
                    "and multiple timers"
                ),
            },
            {
                "icon": "🎯",
                "title": "Tournament Management",
                "description": (
                    "Complete tournament setup with role assignment "
                    "and venue management"
                ),
            },
            {
                "icon": "📊",
                "title": "Tabbycat Integration",
                "description": (
                    "Full tournament software integration for professional "
                    "competitions"
                ),
            },
            {
                "icon": "🛡️",
                "title": "Moderation System",
                "description": (
                    "Professional moderation with timed actions and audit trails"
                ),
            },
            {
                "icon": "🎲",
                "title": "Debate Tools",
                "description": (
                    "Motion system, feedback collection, and venue management"
                ),
            },
            {
                "icon": "⚙️",
                "title": "Server Config",
                "description": (
                    "Extensive customization with auto-roles and welcome systems"
                ),
            },
            {
                "icon": "🌐",
                "title": "Multi-language",
                "description": (
                    "English and Bangla support with expandable architecture"
                ),
            },
            {
                "icon": "⚡",
                "title": "Modern UI",
                "description": ("Discord's latest UI components with slash commands"),
            },
        ]

    def _get_fallback_homepage(self, bot_stats: Dict[str, Any]) -> Response:
        """Generate fallback HTML for homepage with Shadcn UI theme"""
        bot_name = getattr(Config, "BOT_NAME", "AldinnBot")

        html = f"""
        <!DOCTYPE html>
        <html lang="en" class="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{bot_name} - Discord Debate Bot</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                tailwind.config = {{
                    darkMode: 'class',
                    theme: {{
                        extend: {{
                            colors: {{
                                border: 'hsl(240 3.7% 15.9%)',
                                background: 'hsl(240 10% 3.9%)',
                                foreground: 'hsl(0 0% 98%)',
                                primary: {{
                                    DEFAULT: 'hsl(0 0% 98%)',
                                    foreground: 'hsl(240 5.9% 10%)',
                                }},
                                card: {{
                                    DEFAULT: 'hsl(240 10% 3.9%)',
                                    foreground: 'hsl(0 0% 98%)',
                                }},
                                muted: {{
                                    DEFAULT: 'hsl(240 3.7% 15.9%)',
                                    foreground: 'hsl(240 5% 64.9%)',
                                }},
                            }},
                        }},
                    }},
                }}
            </script>
            <meta name="description" content="Professional Discord bot for debate tournaments with Tabbycat integration">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                * {{ font-family: 'Inter', sans-serif; }}
                
                .grid-pattern {{
                    background-image: 
                        linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
                    background-size: 4rem 4rem;
                }}
                
                .gradient-text {{
                    background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .glow {{
                    box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
                }}
            </style>
        </head>
        <body class="bg-background text-foreground antialiased">
            <div class="fixed inset-0 grid-pattern -z-10"></div>
            
            <nav class="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
                <div class="container mx-auto flex h-16 items-center px-6">
                    <div class="flex items-center gap-3">
                        <img src="/static/Logo.png" alt="AldinnBot Logo" class="h-10 w-10">
                        <span class="text-xl font-bold">{bot_name}</span>
                        {('<span class="ml-2 flex h-2 w-2 rounded-full bg-green-500"><span class="absolute inline-flex h-2 w-2 animate-ping rounded-full bg-green-400 opacity-75"></span></span>' if bot_stats['status'] == 'Online' else '')}
                    </div>
                    
                    <div class="ml-auto flex items-center gap-4">
                        <a href="/docs" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Documentation
                        </a>
                        <a href="/commands" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Commands
                        </a>
                        <a href="/invite" class="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">
                            Add to Discord
                        </a>
                    </div>
                </div>
            </nav>
            
            <section class="container mx-auto px-4 py-20 md:py-32">
                <div class="mx-auto max-w-5xl text-center space-y-8">
                    <div class="inline-flex items-center rounded-full border border-border px-3 py-1 text-sm">
                        <span class="mr-2">✨</span>
                        <span class="text-muted-foreground">Professional Debate Tournament Management</span>
                    </div>
                    
                    <h1 class="text-5xl font-extrabold tracking-tight sm:text-6xl md:text-7xl">
                        The Ultimate
                        <span class="gradient-text block">Discord Debate Bot</span>
                    </h1>
                    
                    <p class="mx-auto max-w-2xl text-lg text-muted-foreground sm:text-xl">
                        Professional timing, comprehensive motion database, and seamless Tabbycat integration 
                        for debate tournaments.
                    </p>
                    
                    <div class="flex flex-wrap justify-center gap-8 pt-4">
                        <div class="text-center">
                            <div class="text-4xl font-bold">{bot_stats['guilds']}</div>
                            <div class="text-sm text-muted-foreground">Servers</div>
                        </div>
                        <div class="text-center">
                            <div class="text-4xl font-bold">{bot_stats['users']}</div>
                            <div class="text-sm text-muted-foreground">Users</div>
                        </div>
                        <div class="text-center">
                            <div class="text-4xl font-bold">{bot_stats['latency']}ms</div>
                            <div class="text-sm text-muted-foreground">Latency</div>
                        </div>
                        <div class="text-center">
                            <div class="text-4xl font-bold">{bot_stats['uptime']}</div>
                            <div class="text-sm text-muted-foreground">Uptime</div>
                        </div>
                    </div>
                    
                    <div class="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                        <a href="/invite" class="inline-flex h-12 items-center justify-center rounded-md bg-primary px-8 text-base font-semibold text-primary-foreground hover:bg-primary/90 transition-all glow">
                            <span class="mr-2">🚀</span>
                            Add to Discord
                        </a>
                        <a href="/docs" class="inline-flex h-12 items-center justify-center rounded-md border border-border bg-background px-8 text-base font-semibold hover:bg-accent transition-colors">
                            <span class="mr-2">📚</span>
                            View Documentation
                        </a>
                    </div>
                </div>
            </section>
            
            <footer class="border-t border-border mt-20">
                <div class="container mx-auto px-4 py-8">
                    <div class="flex flex-col items-center justify-between gap-4 md:flex-row">
                        <div class="flex items-center gap-3">
                            <img src="/static/Logo.png" alt="AldinnBot Logo" class="h-8 w-8">
                            <span class="font-semibold">{bot_name}</span>
                        </div>
                        <div class="flex gap-6 text-sm text-muted-foreground">
                            <a href="/" class="hover:text-foreground transition-colors">Home</a>
                            <a href="/docs" class="hover:text-foreground transition-colors">Documentation</a>
                            <a href="/health" class="hover:text-foreground transition-colors">Status</a>
                        </div>
                        <div class="text-sm text-muted-foreground">
                            <p>© 2025 aldinn. Version {bot_stats['version']}</p>
                        </div>
                    </div>
                </div>
            </footer>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    async def stats(self, request: Request) -> Response:
        """Stats page - redirect to home for now"""
        return await self.home(request)

    async def documentation(self, request: Request) -> Response:
        """Comprehensive documentation page"""
        try:
            template_response = self._render_template("documentation.html", request, {})
            if template_response:
                return template_response

            # Fallback documentation
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hear! Hear! Bot - Documentation</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen py-8">
                    <div class="max-w-4xl mx-auto px-4">
                        <h1 class="text-4xl font-bold text-center mb-8">🎤 Hear! Hear! Bot Documentation</h1>
                        <div class="bg-white rounded-lg shadow p-6">
                            <h2 class="text-2xl font-bold mb-4">📚 Complete Bot Documentation</h2>
                <p class="text-gray-600 mb-4">
                    Comprehensive documentation for Hear! Hear! Bot is
                    available with full template support. Please ensure
                    Jinja2 templates are properly configured to view the
                    complete documentation.
                </p>
                            <div class="bg-blue-50 border border-blue-200 rounded p-4">
                                <h3 class="font-bold text-blue-800">Quick Start:</h3>
                                <ul class="list-disc list-inside text-blue-700 mt-2">
                                    <li>Use <code class="bg-blue-100 px-1 rounded">.setup-tournament</code> to initialize tournament</li>
                                    <li>Use <code class="bg-blue-100 px-1 rounded">.tabsync</code> to connect with Tabbycat</li>
                                    <li>Use <code class="bg-blue-100 px-1 rounded">.assign-roles</code> for modern role assignment</li>
                                    <li>Use <code class="bg-blue-100 px-1 rounded">.timer</code> for debate timing</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type="text/html")

        except Exception as e:
            logger.error("Error in documentation endpoint: %s", e)
            return web.Response(
                text="Documentation temporarily unavailable",
                content_type="text/plain",
                status=503,
            )

    async def commands(self, request: Request) -> Response:
        """Commands page"""
        try:
            template_response = self._render_template(
                "commands.html",
                request,
                {
                    "slash_commands": self._get_commands_list(),
                    "prefix_commands": self._get_prefix_commands_list(),
                },
            )

            if template_response:
                return template_response

            # Fallback commands page
            commands_html = self._generate_commands_fallback()
            return web.Response(text=commands_html, content_type="text/html")

        except Exception as e:
            logger.error("Error in commands endpoint: %s", e)
            return web.Response(
                text="Commands page temporarily unavailable",
                content_type="text/plain",
                status=503,
            )

    def _get_commands_list(self) -> List[Dict[str, str]]:
        """Get list of slash commands"""
        return [
            {"name": "/timer start", "description": "Start a debate timer"},
            {"name": "/timer stop", "description": "Stop your active timer"},
            {"name": "/timer check", "description": "Check timer status"},
            {"name": "/setup-tournament", "description": "Initialize tournament setup"},
            {"name": "/tabsync", "description": "Sync with Tabbycat tournament"},
            {"name": "/register", "description": "Register for tournament"},
            {"name": "/checkin", "description": "Check in for tournament"},
            {"name": "/status", "description": "View tournament status"},
            {"name": "/motion", "description": "Display round motion"},
            {"name": "/feedback", "description": "Submit adjudicator feedback"},
        ]

    def _get_prefix_commands_list(self) -> List[Dict[str, str]]:
        """Get list of prefix commands"""
        return [
            {
                "name": ".setup-tournament",
                "description": "Complete tournament initialization",
            },
            {"name": ".create-venues", "description": "Create debate venues"},
            {"name": ".assign-roles", "description": "Modern role assignment"},
            {"name": ".tabsync", "description": "Sync with Tabbycat"},
            {"name": ".register", "description": "Register with key"},
            {"name": ".checkin/.checkout", "description": "Check availability"},
            {"name": ".timer", "description": "Start debate timer"},
            {"name": ".announce", "description": "Send announcements"},
            {"name": ".begin-debate", "description": "Move to debate rooms"},
            {"name": ".call-to-venue", "description": "Call participants to venue"},
        ]

    def _generate_commands_fallback(self) -> str:
        """Generate fallback HTML for commands page"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Commands - Hear! Hear! Bot</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="min-h-screen py-8">
                <div class="max-w-6xl mx-auto px-4">
                    <h1 class="text-4xl font-bold text-center mb-8">🤖 Bot Commands</h1>
                    
                    <div class="grid md:grid-cols-2 gap-8">
                        <div class="bg-white rounded-lg shadow p-6">
                            <h2 class="text-2xl font-bold mb-4">🏆 Tournament Commands</h2>
                            <ul class="space-y-2">
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.setup-tournament</code> - Initialize tournament</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.tabsync</code> - Connect with Tabbycat</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.register</code> - Register for tournament</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.status</code> - View tournament status</li>
                            </ul>
                        </div>
                        
                        <div class="bg-white rounded-lg shadow p-6">
                            <h2 class="text-2xl font-bold mb-4">⏰ Timer Commands</h2>
                            <ul class="space-y-2">
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.timer 8 speech</code> - Start speech timer</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.timer-stop</code> - Stop timer</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.timer-pause</code> - Pause/resume</li>
                                <li><code class="bg-gray-100 px-2 py-1 rounded">.timer-status</code> - Check status</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="text-center mt-8">
                        <a href="/docs" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                            View Complete Documentation
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    async def health(self, _request: Request) -> Response:
        """Health check endpoint for monitoring"""
        try:
            bot_stats = self.get_bot_stats()

            health_data = {
                "status": "healthy" if bot_stats["status"] == "Online" else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "version": bot_stats["version"],
                "uptime": bot_stats["uptime"],
                "bot": {
                    "connected": bot_stats["status"] == "Online",
                    "guilds": bot_stats["guilds"],
                    "latency_ms": bot_stats["latency"],
                },
                "services": {
                    "web_server": "healthy",
                    "database": "unknown",  # Could check database connection here
                    "templates": "healthy" if HAS_JINJA else "fallback",
                },
            }

            status_code = 200 if health_data["status"] == "healthy" else 503
            return web.json_response(health_data, status=status_code)

        except Exception as e:
            logger.error("Health check failed: %s", e)
            return web.json_response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                status=503,
            )

    async def api_stats(self, _request: Request) -> Response:
        """JSON API for bot statistics"""
        try:
            stats = self.get_bot_stats()
            return web.json_response(stats)
        except Exception as e:
            logger.error("Error in API stats: %s", e)
            return web.json_response(
                {"error": "Failed to retrieve statistics"}, status=500
            )

    async def invite(self, _request: Request) -> Response:
        """Bot invitation page with proper invite URL"""
        try:
            # Get invite URL from config (auto-generated or custom)
            invite_url = Config.BOT_INVITE_URL

            if not invite_url:
                # Fallback: generate from BOT_ID if available
                bot_id = Config.BOT_ID
                if bot_id:
                    invite_url = (
                        f"https://discord.com/api/oauth2/authorize?"
                        f"client_id={bot_id}"
                        f"&permissions=8"
                        f"&scope=bot%20applications.commands"
                    )
                else:
                    invite_url = "#"  # Fallback if not configured

            html = f"""
            <!DOCTYPE html>
            <html lang="en" class="dark">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invite {Config.BOT_NAME} - Discord Debate Bot</title>
                <meta name="description" content="{Config.BOT_DESCRIPTION}">
                <meta name="keywords" content="discord bot, debate bot, tournament management, discord invite">
                <script src="https://cdn.tailwindcss.com"></script>
                <script>
                    tailwind.config = {{
                        darkMode: 'class',
                        theme: {{
                            extend: {{
                                colors: {{
                                    border: 'hsl(240 3.7% 15.9%)',
                                    background: 'hsl(240 10% 3.9%)',
                                    foreground: 'hsl(0 0% 98%)',
                                    primary: {{
                                        DEFAULT: 'hsl(0 0% 98%)',
                                        foreground: 'hsl(240 5.9% 10%)',
                                    }},
                                    card: {{
                                        DEFAULT: 'hsl(240 10% 3.9%)',
                                        foreground: 'hsl(0 0% 98%)',
                                    }},
                                    muted: {{
                                        DEFAULT: 'hsl(240 3.7% 15.9%)',
                                        foreground: 'hsl(240 5% 64.9%)',
                                    }},
                                }},
                            }},
                        }},
                    }}
                </script>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
                    * {{ font-family: 'Inter', sans-serif; }}
                    
                    .grid-pattern {{
                        background-image: 
                            linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
                        background-size: 4rem 4rem;
                    }}
                    
                    .glow {{
                        box-shadow: 0 0 30px rgba(59, 130, 246, 0.6), 0 0 60px rgba(59, 130, 246, 0.4);
                    }}
                    
                    .glow:hover {{
                        box-shadow: 0 0 40px rgba(59, 130, 246, 0.8), 0 0 80px rgba(59, 130, 246, 0.5);
                        transform: translateY(-2px);
                    }}
                    
                    .gradient-text {{
                        background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    }}
                    
                    @keyframes float {{
                        0%, 100% {{ transform: translateY(0px); }}
                        50% {{ transform: translateY(-20px); }}
                    }}
                    
                    .float {{ animation: float 3s ease-in-out infinite; }}
                </style>
            </head>
            <body class="bg-background text-foreground antialiased min-h-screen flex items-center justify-center p-4">
                <!-- Grid Background -->
                <div class="fixed inset-0 grid-pattern -z-10"></div>
                
                <!-- Floating Orbs -->
                <div class="fixed top-20 left-20 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl -z-10 float"></div>
                <div class="fixed bottom-20 right-20 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl -z-10 float" style="animation-delay: -1.5s;"></div>
                
                <div class="max-w-4xl w-full">
                    <div class="rounded-xl border border-border bg-card p-8 md:p-16 text-center space-y-8">
                        <!-- Bot Icon -->
                        <div class="flex justify-center">
                            <div class="relative">
                                <div class="text-8xl float">🎤</div>
                                <div class="absolute -top-2 -right-2 w-4 h-4 bg-green-500 rounded-full">
                                    <div class="absolute w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Title -->
                        <div>
                            <h1 class="text-4xl md:text-6xl font-black mb-4">
                                Add <span class="gradient-text">{Config.BOT_NAME}</span>
                            </h1>
                            <p class="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
                                Professional debate tournament management for Discord. 
                                Advanced timing, motion database, and Tabbycat integration.
                            </p>
                        </div>
                        
                        <!-- Features Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                            <div class="rounded-lg border border-border bg-muted/50 p-6 hover:bg-muted transition-colors">
                                <div class="text-4xl mb-3">⏱️</div>
                                <div class="font-semibold text-lg mb-1">Debate Timer</div>
                                <div class="text-sm text-muted-foreground">Professional timing with protected time tracking</div>
                            </div>
                            <div class="rounded-lg border border-border bg-muted/50 p-6 hover:bg-muted transition-colors">
                                <div class="text-4xl mb-3">📋</div>
                                <div class="font-semibold text-lg mb-1">Motion Database</div>
                                <div class="text-sm text-muted-foreground">1000+ curated debate motions</div>
                            </div>
                            <div class="rounded-lg border border-border bg-muted/50 p-6 hover:bg-muted transition-colors">
                                <div class="text-4xl mb-3">🏆</div>
                                <div class="font-semibold text-lg mb-1">Tournament Tools</div>
                                <div class="text-sm text-muted-foreground">Full Tabbycat integration</div>
                            </div>
                        </div>
                        
                        <!-- Stats -->
                        <div class="flex flex-wrap justify-center gap-8 pt-4 pb-4">
                            <div>
                                <div class="text-3xl font-bold text-blue-400">1000+</div>
                                <div class="text-sm text-muted-foreground">Motions</div>
                            </div>
                            <div>
                                <div class="text-3xl font-bold text-purple-400">50ms</div>
                                <div class="text-sm text-muted-foreground">Latency</div>
                            </div>
                            <div>
                                <div class="text-3xl font-bold text-pink-400">24/7</div>
                                <div class="text-sm text-muted-foreground">Uptime</div>
                            </div>
                        </div>
                        
                        <!-- Invite Button -->
                        <div>
                            <a href="{invite_url}" 
                               target="_blank"
                               rel="noopener noreferrer"
                               class="inline-flex items-center justify-center h-14 px-10 text-lg font-bold rounded-lg bg-primary text-primary-foreground glow transition-all duration-300">
                                <span class="mr-2">🚀</span>
                                Add to Discord Now
                            </a>
                        </div>
                        
                        <!-- Features List -->
                        <div class="rounded-lg border border-border bg-muted/30 p-6 text-left">
                            <div class="text-sm font-medium mb-3">What's Included:</div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                                <div>✅ Unlimited debate timers</div>
                                <div>✅ Multi-language motion support</div>
                                <div>✅ Tabbycat tournament sync</div>
                                <div>✅ Role & channel management</div>
                                <div>✅ Real-time pairings</div>
                                <div>✅ Automated announcements</div>
                                <div>✅ Comprehensive analytics</div>
                                <div>✅ Free forever</div>
                            </div>
                        </div>
                        
                        <!-- Navigation -->
                        <div class="pt-4 border-t border-border">
                            <div class="flex flex-wrap justify-center gap-4 text-sm">
                                <a href="/" class="text-muted-foreground hover:text-foreground transition-colors">
                                    ← Home
                                </a>
                                <span class="text-muted-foreground">•</span>
                                <a href="/docs" class="text-muted-foreground hover:text-foreground transition-colors">
                                    📚 Documentation
                                </a>
                                <span class="text-muted-foreground">•</span>
                                <a href="/commands" class="text-muted-foreground hover:text-foreground transition-colors">
                                    🤖 Commands
                                </a>
                                <span class="text-muted-foreground">•</span>
                                <a href="https://github.com/Taraldinn/hear-hear-bot" 
                                   target="_blank" 
                                   class="text-muted-foreground hover:text-foreground transition-colors">
                                    💻 GitHub
                                </a>
                            </div>
                        </div>
                        
                        <!-- Footer -->
                        <div class="text-xs text-muted-foreground">
                            Version {Config.BOT_VERSION} • Made with ❤️ by {Config.BOT_AUTHOR}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type="text/html")
        except Exception as e:
            logger.error("Error in invite endpoint: %s", e)
            return web.Response(
                text="Invite page temporarily unavailable",
                content_type="text/plain",
                status=503,
            )

    async def start_server(self, port: int = 8080, host: str = "0.0.0.0"):
        """Start the web server"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()

            site = web.TCPSite(runner, host, port)
            await site.start()

            logger.info("Web server started on http://%s:%s", host, str(port))
            return runner
        except Exception as e:
            logger.error("Failed to start web server: %s", e)
            raise

    async def stop_server(self) -> None:
        """Stop the web server gracefully"""
        try:
            await self.app.cleanup()
            logger.info("Web server stopped gracefully")
        except Exception as e:
            logger.error("Error stopping web server: %s", e)
