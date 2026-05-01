"""
SAI-OS Background Daemon.

Systemd user service that runs continuously, managing system monitoring,
intelligent notifications, scheduled maintenance, and Ollama health checks.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from datetime import datetime

import click

from sai_core.config import SAI_CACHE_DIR, get_config

logger = logging.getLogger("sai-daemon")


class SAIDaemon:
    """Main background daemon for SAI-OS intelligence."""

    def __init__(self):
        self.config = get_config()
        self._running = False
        self._monitor = None
        self._notifier = None
        self._scheduler = None

    async def start(self) -> None:
        """Start all daemon services."""
        self._running = True
        logger.info("SAI Daemon starting...")

        # Initialize subsystems
        from sai_core.daemon.monitor import SystemMonitor
        from sai_core.daemon.notifier import SmartNotifier
        from sai_core.daemon.scheduler import TaskScheduler

        self._monitor = SystemMonitor(self.config.daemon)
        self._notifier = SmartNotifier()
        self._scheduler = TaskScheduler()

        # Run all services concurrently
        tasks = [
            asyncio.create_task(self._monitor_loop()),
            asyncio.create_task(self._scheduler_loop()),
            asyncio.create_task(self._ollama_watchdog()),
        ]

        logger.info("SAI Daemon running.")

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("SAI Daemon shutting down...")

    async def _monitor_loop(self) -> None:
        """Continuous system health monitoring."""
        interval = self.config.daemon.monitor_interval
        while self._running:
            try:
                alerts = self._monitor.check()
                for alert in alerts:
                    await self._notifier.send(
                        title=alert["title"],
                        message=alert["message"],
                        urgency=alert.get("urgency", "normal"),
                    )
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            await asyncio.sleep(interval)

    async def _scheduler_loop(self) -> None:
        """Check for scheduled tasks every minute."""
        while self._running:
            try:
                self._scheduler.check_and_run()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60)

    async def _ollama_watchdog(self) -> None:
        """Ensure Ollama is running and responsive."""
        while self._running:
            try:
                import ollama
                ollama.list()
            except Exception:
                logger.warning("Ollama is not responding")
                await self._notifier.send(
                    title="AI Engine Offline",
                    message="Ollama is not running. Some AI features are unavailable.",
                    urgency="normal",
                )
            await asyncio.sleep(300)  # Check every 5 minutes

    def stop(self) -> None:
        self._running = False


def _setup_logging() -> None:
    log_file = SAI_CACHE_DIR / "sai-daemon.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(),
        ],
    )


@click.command()
def main() -> None:
    """SAI-OS Background Daemon."""
    _setup_logging()
    daemon = SAIDaemon()

    def handle_signal(sig, frame):
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    asyncio.run(daemon.start())


if __name__ == "__main__":
    main()
