import discordtest as discord
import itertools

import pickle
import asyncio

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await self.spam()

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

    async def spam(self):
      await asyncio.sleep(1)

      home = 'Google DSC UBCO'
      target_guilds = []

      for target_guild in self.guilds:
        if(target_guild.name == home): continue
        print("Targeting guild {} ({})".format(target_guild.id, target_guild.name))
        await target_guild.subscribe()
        target_guilds.append(target_guild)

      print("Loading home guild members...")
      dsc_guild = next((x for x in self.guilds if x.name == home), None)
      await dsc_guild.subscribe()

      raw_members = itertools.chain.from_iterable([await self.get_unmessaged_members(guild) for guild in target_guilds])
      members = list(set(raw_members)) # remove duplicates

      for member in members:
        dm_channel = await member.create_dm()
        if len(await dm_channel.history(limit=1).flatten()) == 1:
          continue

        message_sent = False
        while not message_sent:
          try:
            await dm_channel.send(
              'Did you know that a **Google Student Developer Club** has arrived at UBCO coming **this fall?!?!**\n' +
              '\n' +
              '**Google Developer Student Clubs** are community groups for **college and university students** interested in Google developer technologies.\n' +
              'Students from all **undergraduate or graduate** programs and skill levels with an interest in growing as a developer are welcome. By joining a GDSC, students grow their knowledge in a peer-to-peer learning environment and build solutions for local businesses and their community.'
            )
            await dm_channel.send(
              file = discord.File('./promo.mp4')
            )
            await dm_channel.send(
              'Check us out on Instagram   https://www.instagram.com/dsc.ubco/\n' +
              'Join our Discord server   https://discord.gg/3qfsHQ96T7'
            )
            print("Messaged {}#{}".format(member.name, member.discriminator))
            message_sent = True
          except discord.errors.Forbidden as ex:
            print(ex)
            print("ERROR: Messaging {}#{} failed".format(member.name, member.discriminator))
            if str(ex) == '403 Forbidden (error code: 40003): You are opening direct messages too fast.':
              print("Message throttling for 10 minutes")
              await asyncio.sleep(600)
            else:
              message_sent = True
        
        self.dump_messaged_members()
        await asyncio.sleep(3)
      
      print("DONE!")

    async def get_unmessaged_members(self, guild):
      return [
        guild_member
        for guild_member in guild.members if
        not any(guild_member == messaged_member for messaged_member in self.get_messaged_members())
        and not any(guild_member == recruited_member for recruited_member in await self.get_recruited_members())
        and guild_member != self.user
        and guild_member.name != 'raghav'
        and not any(role for role in guild_member.roles if role.name == "Admin")
        and not any(role for role in guild_member.roles if role.name == "Executive")
        and guild_member.bot == False
      ]

    def get_messaged_members(self):
      return [
        channel.recipient
        for channel in self.private_channels if 
        isinstance(channel, discord.DMChannel)
      ]

    def dump_messaged_members(self):
      with open('messaged_dump', 'wb') as fp:
        pickle.dump([member.id for member in self.get_messaged_members()], fp)

    def load_messaged_members(self):
      with open('messaged_dump', 'rb') as fp:
        return pickle.load(fp)

    async def get_recruited_members(self):
      dsc_guild = next((x for x in self.guilds if x.name == 'Google DSC UBCO'), None)
      return dsc_guild.members

client = MyClient(guild_subscription_options = discord.GuildSubscriptionOptions.disabled())
client.run('NzA4MTc1Mjg1NjczMTMyMTEz.YS5hSw.IhtGkokKqQZ7Du6clrHa8MS__l4')