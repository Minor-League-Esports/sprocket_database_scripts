import csv
import discord
from discord.ext import tasks

intents = discord.Intents.all()

client = discord.Client(intents=intents)

cats = []
channels = []

@tasks.loop(seconds=5)
async def background_task():
	await client.wait_until_ready()
	print('Doing the thing')
	channel = client.get_channel(1256670839806361702)
	await channel.send('Hello!')

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')

	if message.content.startswith('$makeChannels'):
		await message.channel.send('Making channels')
		await make_them_channels()


async def make_them_channels():
	roles = {}
	with open('input_data/tm_lo_ids.csv') as csvfile:
		reader = csv.reader(csvfile)
		for i, row in enumerate(reader):
			if i == 0:
				continue
			roleName = row[0]
			roleId = row[1]
			roles[roleName] = roleId
		
	matches = {}
	with open('input_data/tm_s1_schedule.csv') as csvfile:
		reader = csv.reader(csvfile)
		for i, row in enumerate(reader):
			if i == 0:
				continue
			home = row[0]
			away = row[1]
			week = row[2]
			matches.setdefault(week, []).append((home, away))

	print(roles)
	print(matches)

	guild = client.get_guild(1249187170355380264)

	try:
		for week in matches:
			cat = await guild.create_category(f'Match {week}')
			cats.append(cat)
			pairs = matches[week]
			for pair in pairs:
				home = pair[0]
				away = pair[1]
				homeId = roles[home]
				awayId = roles[away]
				channel = await guild.create_text_channel(f'{home} vs {away}', category=cat)
				channels.append(channel)
				home_role = guild.get_role(int(homeId))
				away_role = guild.get_role(int(awayId))
				print(f'Guilds roles: {guild.roles}')
				print(f'Creating channel for {home}:{homeId}:{home_role} vs {away}:{awayId}:{away_role}')
				print('Setting home perms')
				print(f'Perms: {channel.overwrites}')
				overwrite1 = discord.PermissionOverwrite()
				overwrite1.send_messages = False
				overwrite1.read_messages = False
				overwrite2 = discord.PermissionOverwrite()
				overwrite2.send_messages = True
				overwrite2.read_messages = True

				await channel.set_permissions(home_role, overwrite=overwrite2)
				print('Setting away perms')
				await channel.set_permissions(away_role, overwrite=overwrite2)
				print('Setting default perms')
				await channel.set_permissions(guild.default_role, overwrite=overwrite1)
	except Exception as e:
		print(e)
		print('Failed to create channels')
		for c in channels:
			await c.delete()
		for cat in cats:
			await cat.delete()

client.run('bot_token_here')