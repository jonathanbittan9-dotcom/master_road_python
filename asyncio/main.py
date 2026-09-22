import asyncio


async def gta6(install, delay):
    print(f"installing GTA 6... {delay} seconds to finish")
    await asyncio.sleep(delay)          # await an actual awaitable, not a str
    return f"{install}: GTA 6 installed"


async def zelda(install, delay):
    print(f"installing Zelda... {delay} seconds to finish")
    await asyncio.sleep(delay)
    return f"{install}: zelda ocarine of time installed"


async def main():
    result_gta6 = await gta6("epic", 2)
    result_zelda = await zelda("epic", 2)
    return result_gta6, result_zelda


if __name__ == "__main__":
    print(gta6)
    print(zelda)
    print(asyncio.run(main()))
