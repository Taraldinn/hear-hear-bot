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
                    if hasattr(self.bot, "latency") and self.bot.latency
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
                    "bot_name": getattr(Config, "BOT_NAME", "Hear! Hear! Bot"),
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
        """Generate fallback HTML for homepage"""
        bot_name = getattr(Config, "BOT_NAME", "Hear! Hear! Bot")

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{bot_name} - Discord Debate Bot</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <meta name="description" content="Professional Discord bot for debate tournaments "
                  "with Tabbycat integration">
        </head>
        <body class="bg-gray-50 font-sans">
            <div class="min-h-screen">
                <header class="bg-white shadow-sm">
                    <div class="max-w-6xl mx-auto px-4 py-6">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="text-3xl">🎤</div>
                                <div>
                                    <h1 class="text-2xl font-bold text-gray-900">{bot_name}</h1>
                                    <p class="text-gray-600">Professional Discord Bot for Debate Tournaments</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm text-gray-500">
                                    Status: {bot_stats['status']}
                                </div>
                                <div class="text-lg font-semibold text-blue-600">
                                    {bot_stats['guilds']} Servers
                                </div>
                            </div>
                        </div>
                    </div>
                </header>
                
                <main class="max-w-6xl mx-auto px-4 py-12">
                    <div class="text-center mb-12">
                        <h2 class="text-4xl font-bold text-gray-900 mb-4">Complete Tournament Management</h2>
                        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                            Advanced Discord bot for debate tournaments with Tabbycat integration,
                            modern UI components, and comprehensive tournament management tools.
                        </p>
                    </div>
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center mb-12">
                        <div class="bg-white p-6 rounded-lg shadow">
                            <div class="text-3xl font-bold text-blue-600">
                                {bot_stats['guilds']}
                            </div>
                            <div class="text-gray-600">Discord Servers</div>
                        </div>
                        <div class="bg-white p-6 rounded-lg shadow">
                            <div class="text-3xl font-bold text-purple-600">
                                {bot_stats['users']}
                            </div>
                            <div class="text-gray-600">Users Served</div>
                        </div>
                        <div class="bg-white p-6 rounded-lg shadow">
                            <div class="text-3xl font-bold text-green-600">
                                {bot_stats['latency']}ms
                            </div>
                            <div class="text-gray-600">Response Time</div>
                        </div>
                        <div class="bg-white p-6 rounded-lg shadow">
                            <div class="text-3xl font-bold text-orange-600">
                                {bot_stats['uptime']}
                            </div>
                            <div class="text-gray-600">Uptime</div>
                        </div>
                    </div>
                    
                    <div class="text-center space-y-4">
                        <a href="/docs" 
                           class="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                            View Documentation
                        </a>
                        <div class="text-gray-600">
                            <a href="/health" class="hover:text-blue-600">Health Check</a> |
                            <a href="/api/stats" class="hover:text-blue-600">API Stats</a> |
                            <a href="/commands" class="hover:text-blue-600">Commands</a>
                        </div>
                    </div>
                </main>
                
                <footer class="bg-gray-800 text-white py-8 mt-12">
                    <div class="max-w-6xl mx-auto px-4 text-center">
                        <p>&copy; 2025 {bot_name} by aldinn. Built for the debate community.</p>
                        <p class="text-gray-400 text-sm mt-2">
                            Version {bot_stats['version']} | 
                            <a href="/health" class="hover:text-blue-400">Health Check</a>
                        </p>
                    </div>
                </footer>
            </div>
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
        """Bot invitation page"""
        try:
            invite_url = getattr(Config, "BOT_INVITE_URL", "#")

            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invite Hear! Hear! Bot</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen flex items-center justify-center">
                    <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
                        <div class="text-6xl mb-4">🎤</div>
                        <h1 class="text-2xl font-bold mb-4">Add Hear! Hear! Bot</h1>
                        <p class="text-gray-600 mb-6">
                            Add the most advanced Discord bot for debate tournaments to your server.
                        </p>
                        <a href="{invite_url}"
                           class="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                            Add to Discord
                        </a>
                        <div class="mt-4 text-sm text-gray-500">
                            <a href="/" class="hover:text-blue-600">← Back to Homepage</a>
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
