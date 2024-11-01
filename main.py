import asyncio

from src import app


async def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    asyncio.run(main())
