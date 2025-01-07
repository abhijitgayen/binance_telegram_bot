import asyncio
import time

async def async_function():
    print("Starting async function...")
    await asyncio.sleep(2)
    print("Async function finished!")

async def main():
    # Calling the async function without await, no waiting for it to complete
    asyncio.create_task(async_function())
    
    print("Other code is running concurrently.")

    await time.sleep(10)

# Run the main function
asyncio.run(main())
