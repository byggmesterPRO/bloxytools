import discord
import json


async def process_command(ctx):
    with open('lib/json/stats.json', 'r') as f:
        stats = json.load(f)
        COUNT_TOTAL = stats['commands_total']
        COUNT_TODAY = stats['commands_today']
        stats['commands_total'] = COUNT_TOTAL + 1
        stats['commands_today'] = COUNT_TODAY + 1
    with open('lib/json/stats.json', 'w') as f:
        stats = json.dump(stats, f)

async def register_user(ctx):
    with open('lib/json/stats.json', 'r') as f:
        stats = json.load(f)
        COUNT_TODAY = stats['verified_users_today']
        stats['verified_users_today'] = COUNT_TODAY + 1
    with open('lib/json/stats.json', 'w') as f:
        stats = json.dump(stats, f)    