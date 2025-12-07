import aiohttp
import asyncio
import requests
import pandas as pd
from tqdm.asyncio import tqdm_asyncio
import nest_asyncio
import os
from datetime import datetime
from config import Config

nest_asyncio.apply()

SEM_PLAYERS = asyncio.Semaphore(Config.MAX_CONCURRENT_PLAYER_REQUESTS)
SEM_STORE = asyncio.Semaphore(Config.MAX_CONCURRENT_STORE_REQUESTS)

#fetch all apps
def fetch_all_apps():
    url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
    all_apps = []
    last_appid = 0
    
    print("Fetching Steam apps...")
    
    while True:
        params = {
            "key": Config.STEAM_API_KEY,
            "include_games": "true",
            "include_dlc": "false",
            "include_software": "false",
            "last_appid": last_appid,
            "max_results": 50000
        }
        
        try:
            resp = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
            if resp.status_code != 200:
                break
            
            data = resp.json().get("response", {})
            batch = data.get("apps", [])
            if not batch:
                break
            
            all_apps.extend(batch)
            last_appid = batch[-1]["appid"]
            
            if len(batch) < 1000:
                break
        except:
            break
    
    return [{"id": str(a["appid"]), "name": a["name"]} for a in all_apps]

#get current player count
async def get_player_count(session, app):
    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app['id']}&key={Config.STEAM_API_KEY}"
    
    async with SEM_PLAYERS:
        try:
            async with session.get(url, timeout=Config.REQUEST_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    count = data.get("response", {}).get("player_count", 0)
                    if count > 0:
                        return {**app, "players": count}
        except:
            pass
    return None

#get metadata from store
async def get_store_details(session, app):
    url = f"https://store.steampowered.com/api/appdetails?appids={app['id']}&cc=US&l=en"
    
    async with SEM_STORE:
        try:
            await asyncio.sleep(Config.STORE_API_DELAY)
            async with session.get(url, timeout=Config.REQUEST_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entry = data.get(str(app["id"]))
                    
                    if entry and entry.get("success"):
                        meta = entry["data"]
                        app["price_usd"] = meta.get("price_overview", {}).get("final", 0) / 100 if meta.get("price_overview") else 0
                        app["is_free"] = meta.get("is_free", False)
                        app["genres"] = ", ".join(g["description"] for g in meta.get("genres", []))
                        app["release_date"] = meta.get("release_date", {}).get("date", "")
                        return app
                elif resp.status == 429:
                    await asyncio.sleep(Config.RETRY_DELAY)
        except:
            pass
    
    app["price_usd"] = -1
    app["is_free"] = False
    app["genres"] = ""
    app["release_date"] = ""
    return app


async def main():
    print("="*50)
    print("Steam Crawler Started")
    print("="*50)
    
    os.makedirs(Config.DATA_RAW_DIR, exist_ok=True)
    
    apps = fetch_all_apps()
    if not apps:
        print("Failed to fetch apps")
        return
    
    print(f"Found {len(apps)} apps")
    
    async with aiohttp.ClientSession() as session:
        print("Checking player counts...")
        player_tasks = [get_player_count(session, a) for a in apps]
        player_results = await tqdm_asyncio.gather(*player_tasks)
        active_games = [r for r in player_results if r]
        
        print(f"Active games: {len(active_games)}")
        print("Fetching metadata...")
        
        meta_tasks = [get_store_details(session, a) for a in active_games]
        final_data = []
        for task in tqdm_asyncio.as_completed(meta_tasks):
            final_data.append(await task)
    
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in final_data:
        item["crawl_date"] = crawl_time
    
    df = pd.DataFrame(final_data)
    df = df[['id', 'name', 'players', 'price_usd', 'is_free', 'genres', 'release_date', 'crawl_date']]
    
    output_path = os.path.join(Config.DATA_RAW_DIR, Config.get_crawl_filename())
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"Saved to: {output_path}")
    print(f"Total games: {len(df)}")
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())