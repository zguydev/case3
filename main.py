import asyncio

from src import app


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
