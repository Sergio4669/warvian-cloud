import asyncio
import time
import random
from playwright.async_api import async_playwright

BASE = "https://s1.warvian.it/"

COOKIES = [
    {"name": "COOKEMAIL", "value": "Sergiooliveira4669%2540hotmail.com", "domain": "s1.warvian.it", "path": "/"},
    {"name": "COOKUSR", "value": "Brinca", "domain": "s1.warvian.it", "path": "/"},
    {"name": "PHPSESSID", "value": "issfmgdgpjtuvl2sq394kp5lmg", "domain": "s1.warvian.it", "path": "/"},
]

TARGETS = {"wood": 5, "clay": 5, "iron": 4, "crop": 4}

class BotState:
    running = False
    paused = False
    last_action = "Bot parado"
    log = []

    @staticmethod
    def add_log(msg):
        BotState.log.append(msg)
        if len(BotState.log) > 50:
            BotState.log.pop(0)

state = BotState()

async def upgrade_best_field(page):
    state.last_action = "Verificando campos externos"
    state.add_log(state.last_action)

    await page.goto(BASE + "dorf1.php")
    areas = await page.locator("area[href*='build.php?id=']").all()

    ranked = []

    for area in areas:
        href = await area.get_attribute("href")
        title = await area.get_attribute("title")

        if not title:
            continue

        title_low = title.lower()

        if "woodcutter" in title_low:
            ftype = "wood"
        elif "clay" in title_low:
            ftype = "clay"
        elif "iron" in title_low:
            ftype = "iron"
        elif "crop" in title_low:
            ftype = "crop"
        else:
            continue

        lvl = 0
        if "level" in title_low:
            try:
                lvl = int(title.split("Level")[1].strip())
            except:
                lvl = 0

        gap = TARGETS[ftype] - lvl
        ranked.append((gap, href))

    ranked.sort(reverse=True, key=lambda x: x[0])

    for gap, href in ranked:
        if gap <= 0:
            continue

        await page.goto(BASE + href)

        upgrade_btn = page.locator("a.build:has-text('Upgrade')")
        if await upgrade_btn.count() > 0:
            up_href = await upgrade_btn.first.get_attribute("href")
            state.last_action = f"Upgrade externo: {up_href}"
            state.add_log(state.last_action)
            await page.goto(BASE + up_href)
            return True

    return False

async def build_internal(page):
    state.last_action = "Verificando edifícios internos"
    state.add_log(state.last_action)

    await page.goto(BASE + "dorf2.php")

    PRIORITY = [
        ("Warehouse", 20),
        ("Granary", 20),
        ("Main Building", 15),
        ("Barracks", 10),
        ("Marketplace", 10),
        ("Academy", 10),
        ("Smithy", 10),
        ("Stable", 10),
    ]

    for building, target in PRIORITY:
        slot = page.locator(f"area[title*='{building}']")
        if await slot.count() > 0:
            href = await slot.first.get_attribute("href")
            await page.goto(BASE + href)

            title = await page.locator("h1").inner_text()
            lvl = 0
            if "Level" in title:
                try:
                    lvl = int(title.split("Level")[1].strip())
                except:
                    lvl = 0

            if lvl >= target:
                continue

            upgrade_btn = page.locator("a.build:has-text('Upgrade')")
            if await upgrade_btn.count() > 0:
                up_href = await upgrade_btn.first.get_attribute("href")
                state.last_action = f"Upgrade interno: {building}"
                state.add_log(state.last_action)
                await page.goto(BASE + up_href)
                return True

        construct_btn = page.locator(f"a.build:has-text('{building}')")
        if await construct_btn.count() > 0:
            href = await construct_btn.first.get_attribute("href")
            state.last_action = f"Construindo: {building}"
            state.add_log(state.last_action)
            await page.goto(BASE + href)
            return True

    return False

async def bot_loop():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(COOKIES)
        page = await context.new_page()

        while True:
            if not state.running:
                await asyncio.sleep(1)
                continue

            if state.paused:
                state.last_action = "Bot pausado"
                await asyncio.sleep(1)
                continue

            upgraded = await upgrade_best_field(page)
            if not upgraded:
                await build_internal(page)

            await asyncio.sleep(random.randint(5, 10))
