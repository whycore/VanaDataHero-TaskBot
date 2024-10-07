import aiohttp
import asyncio
import json
import random
import time
from datetime import datetime
from aiohttp import ClientSession
from fake_useragent import UserAgent
from colorama import Fore, Style, init

init(autoreset=True)

# Watermark besar di awal
def print_watermark():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}")
    print("██╗   ██╗ █████╗ ███╗   ██╗ █████╗ ")
    print("██║   ██║██╔══██╗████╗  ██║██╔══██╗")
    print("██║   ██║███████║██╔██╗ ██║███████║")
    print("╚██╗ ██╔╝██╔══██║██║╚██╗██║██╔══██║")
    print(" ╚████╔╝ ██║  ██║██║ ╚████║██║  ██║")
    print("  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝")
    print("                                   ")
    print("    auto complete task by WHYCORE")
    print(f"{Style.RESET_ALL}")

# Read query IDs from queries.txt
async def read_query_ids():
    with open('queries.txt', 'r') as file:
        queries = [line.strip() for line in file.readlines()]
    return queries

class Vana:
    def __init__(self, query_id: str):
        self.query_id = query_id
        self.base_url = "https://www.vanadatahero.com/api/"
        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(120))

    # Get player information
    async def get_player_info(self):
        async with self.session.get(f'{self.base_url}player', headers={"X-Telegram-Web-App-Init-Data": self.query_id}) as response:
            player_info = await response.json()
            return player_info

    # Get tasks from the API
    async def get_tasks(self):
        async with self.session.get(f'{self.base_url}tasks', headers={"X-Telegram-Web-App-Init-Data": self.query_id}) as response:
            tasks = await response.json()
            return tasks.get('tasks', [])

    # Complete a specific task by task ID
    async def complete_task(self, task_id: int, reward: [int, float]):
        json_data = {"status": "completed", "points": reward}
        async with self.session.post(f'{self.base_url}tasks/{task_id}', headers={"X-Telegram-Web-App-Init-Data": self.query_id}, json=json_data) as response:
            return await response.text() == ''

    # Logout and close the session
    async def logout(self):
        await self.session.close()

# Process each query ID to fetch tasks, complete tasks, and get player info
async def process_query_id(query_id: str):
    vana = Vana(query_id)
    
    try:
        # Fetch player information
        player_info = await vana.get_player_info()
        tg_username = player_info.get('tgUsername', 'N/A')
        tg_wallet = player_info.get('tgWalletAddress', 'N/A')
        vana_wallet = player_info.get('vanaWalletAddress', 'N/A')
        
        # Print player info with colors
        print(f"{Fore.YELLOW}Player Info for {Fore.CYAN}{tg_username}{Style.RESET_ALL}:")
        print(f"{Fore.GREEN}  tgUsername       : {tg_username}")
        print(f"{Fore.GREEN}  tgWalletAddress  : {tg_wallet}")
        print(f"{Fore.GREEN}  vanaWalletAddress: {vana_wallet}\n")

        # Fetch tasks
        tasks = await vana.get_tasks()
        print(f"{Fore.YELLOW}Found {Fore.CYAN}{len(tasks)}{Fore.YELLOW} tasks for {Fore.CYAN}{tg_username}{Style.RESET_ALL}\n")

        # Complete tasks
        for task in tasks:
            if not task['completed']:
                success = await vana.complete_task(task['id'], task['points'])
                if success:
                    print(f"{Fore.GREEN}Task '{task['name']}' completed, earned {task['points']} points!")
                else:
                    print(f"{Fore.RED}Failed to complete task '{task['name']}'")
            
            # Delay between task completions
            await asyncio.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"{Fore.RED}Error processing query ID {query_id}: {e}")
    finally:
        await vana.logout()

# Main function to process multiple query IDs
async def main():
    print_watermark()
    query_ids = await read_query_ids()
    
    # Process each query ID asynchronously
    tasks = [asyncio.create_task(process_query_id(query_id)) for query_id in query_ids]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
