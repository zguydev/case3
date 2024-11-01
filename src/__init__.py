import threading
import asyncio

from src import site
from src.bot import bot


class app:
    @staticmethod
    def _run_site(debug: bool) -> None:
        site.app.run(debug=debug, use_reloader=False)

    @staticmethod
    def run(debug: bool) -> None:
        threading.Thread(target=app._run_site, args=(debug,), daemon=True).start()
        try:
            asyncio.run(bot.run())
        except KeyboardInterrupt:
            return
        except: pass
        while 1: pass
