import asyncio
from src.app import create_app_manager

quart_manager = asyncio.run(create_app_manager())
app = quart_manager.app

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
