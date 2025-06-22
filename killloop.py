import asyncio

async def my_async_function():
    print("Running async function")

# Stop the current event loop
loop = asyncio.get_event_loop()
loop.stop()