import discord
import os
import re
import wavelink
from discord.ext import commands
from wavelink.ext import spotify

SPOTIFY_ID = os.environ["SPOTIFY_ID"]
SPOTIFY_SECRET = os.environ["SPOTIFY_SECRET"]

class CustomPlayer(wavelink.Player):
  def __init__(self):
    super().__init__()
    self.queue = wavelink.Queue()
    self.loop = False

class Music(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.song_queue = {}
    self.cid = SPOTIFY_ID
    self.csecret = SPOTIFY_SECRET
    self.player = None
    client.loop.create_task(self.connect_nodes())

  async def connect_nodes(self):
    await self.client.wait_until_ready()
    sc = spotify.SpotifyClient(client_id = self.cid, client_secret = self.csecret)
    node: wavelink.Node = wavelink.Node(uri = "http://127.0.0.1:2333/", password = "")
    await wavelink.NodePool.connect(client = self.client, nodes = [node], spotify = sc)

  @commands.Cog.listener()
  async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
    player = payload.player
    if not player.queue.is_empty:
      next_track = player.queue.get()
      await player.play(next_track)

  @commands.Cog.listener()
  async def on_wavelink_node_ready(self, node: wavelink.Node):
    print(f"Node: <{node}> đã sẵn sàng!")

  @commands.Cog.listener()
  async def on_ready(self):
    print("music.py Loaded")

  @commands.hybrid_command(name = "join", aliases = ["j", "connect", "c"], with_app_command = True, description = "Kết nối vào kênh thoại.")
  async def join(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not author:
        embed = discord.Embed(
          description = "Bạn cần phải ở trong một kênh thoại để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if not vc:
          await author.channel.connect(cls = CustomPlayer())
          embed = discord.Embed(
            description = "Đã kết nối vào kênh thoại.",
            colour = discord.Colour(0x00ff00))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        elif vc and vc.channel != author.channel:
          members = vc.channel.members
          if (len(members) <= 1 or not vc.is_playing()) and not vc.is_paused():
            await vc.stop()
            await vc.resume()
            await vc.move_to(author.channel)
            embed = discord.Embed(
              description = "Đã kết nối vào kênh thoại.",
              colour = discord.Colour(0x00ff00))
            embed.set_author(
              name = ctx.author.name,
              icon_url = ctx.author.avatar.url)
            await ctx.send(embed = embed)
          else:
            embed = discord.Embed(
              description = "Ifrit hiện đang kết nối tại kênh thoại khác.",
              colour = discord.Colour(0xff0000))
            embed.set_author(
              name = ctx.author.name,
              icon_url = ctx.author.avatar.url)
            await ctx.send(embed = embed)
        elif vc and vc.channel == author.channel:
          embed = discord.Embed(
            description = "Ifrit hiện đã kết nối vào kênh thoại.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)

  @commands.hybrid_command(name = "leave", aliases = ["l", "disconnect", "d"], with_app_command = True, description = "Ngắt kết nối khỏi kênh thoại.")
  async def leave(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        embed = discord.Embed(
            description = "Ifrit hiện không kết nối vào kênh thoại.",
            colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        await vc.disconnect()
        embed = discord.Embed(
          description = "Đã ngắt kết nối khỏi kênh thoại.",
          colour = discord.Colour(0x00ff00))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)
      
  @commands.hybrid_command(name = "play", aliases = ["p"], with_app_command = True, description = "Phát một bài hát.")
  async def play(self, ctx: commands.Context, *, search: str = commands.parameter):
    url_type = self.check_string(search)
    action = self.url_type_mapping.get(url_type, None)
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls = custom_player)
        if action:
          await action(self, ctx, search, vc)
        else:
          embed = discord.Embed(
            description = "Ifrit không thể phát nhạc từ đường link này, vui lòng bạn sử dụng đường link khác.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if action:
          await action(self, ctx, search, vc)
        else:
          embed = discord.Embed(
            description = "Ifrit không thể phát nhạc từ đường link này, vui lòng bạn sử dụng đường link khác.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)

  @commands.hybrid_command(name = "loop", aliases = ["lo"], with_app_command = True, description = " Lặp lại bài hát hiện tại.")
  async def loop(self, ctx):

  @commands.hybrid_command(name = "pause", aliases = ["pa"], with_app_command = True, description = "Tạm dừng phát bài hát.")
  async def pause(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        embed = discord.Embed(
            description = "Ifrit hiện không kết nối vào kênh thoại.",
            colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if vc.is_playing() and not vc.is_paused():
          await vc.pause()
          embed = discord.Embed(
            description = "Đã tạm dừng bài hát.",
            colour = discord.Colour(0x00ff00))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        elif vc.is_paused():
          embed = discord.Embed(
            description = "Bài hát hiện đã tạm dừng.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        else:
          embed = discord.Embed(
            description = "Không có bài hát nào đang được phát.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)

  @commands.hybrid_command(name = "resume", aliases = ["re"], with_app_command = True, description = "Tiếp tục phát bài hát.")
  async def resume(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        embed = discord.Embed(
          description = "Ifrit hiện không kết nối vào kênh thoại.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if vc.is_paused():
          await vc.resume()
          embed = discord.Embed(
            description = "Đã tiếp tục bài hát.",
            colour = discord.Colour(0x00ff00))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        elif vc.is_playing() and not vc.is_paused():
          embed = discord.Embed(
            description = "Bài hát hiện chưa được tạm dừng.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        else:
          embed = discord.Embed(
            description = "Không có bài hát nào đang được phát.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)
      
  @commands.command(name="nowplaying", aliases=["np"], description="Hiển thị bài hát đang phát.")
  async def nowplaying(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        embed = discord.Embed(
          description = "Ifrit hiện không kết nối vào kênh thoại.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if vc.is_playing():
          track = vc.current
          embed = discord.Embed(
              title="Đang phát:",
              description=f"**{track.title}** \n \n**Link Gốc:** {track.uri}",
              colour = discord.Colour(0x00ebff))
          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(
            description = "Không có bài hát nào đang được phát.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)

  @commands.hybrid_command(name = "skip", aliases = ["s"], with_app_command = True, description = "Bỏ qua bài hát hiện tại.")
  async def skip(self, ctx):
    vc = ctx.voice_client
    author = ctx.author.voice
    if ctx.channel.id == 987421806333943828 or ctx.channel.id == 982951847398617098 or ctx.channel.id == 934816502522208256:
      if not vc:
        embed = discord.Embed(
            description = "Ifrit hiện không kết nối vào kênh thoại.",
            colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      elif not author or vc.channel != author.channel:
        embed = discord.Embed(
          description = "Bạn cần phải kết nối vào cùng kênh thoại với Ifrit để có thể sử dụng lệnh này.",
          colour = discord.Colour(0xff0000))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        if vc.queue.is_empty and not vc.is_playing():
          await vc.stop()
          embed = discord.Embed(
            description = "Không có bài hát nào đang được phát.",
            colour = discord.Colour(0xff0000))
          embed.set_author(
            name = ctx.author.name,
           icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
        else:
          await vc.seek(vc.current.length * 1000)
          await vc.resume()
          embed = discord.Embed(
            description = "Đã bỏ qua bài hát.",
            colour = discord.Colour(0x00ff00))
          embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar.url)
          await ctx.send(embed = embed)
    else:
      embed = discord.Embed(
        description = "Câu lệnh này chỉ được phép sử dụng tại <#987421806333943828> hoặc <#934816502522208256>",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      embed.set_footer(
        text = "tin nhắn sẽ tự động xóa sau 5s")
      await ctx.message.delete()
      await ctx.send(embed = embed, delete_after = 5)

  async def play_spotify_track(self, ctx: discord.ext.commands.Context, track: str, vc: CustomPlayer):
    track = await spotify.SpotifyTrack.search(track, return_first = True)
    if vc.is_playing() or not vc.queue.is_empty:
      vc.queue.put(item = track)
      embed = discord.Embed(
        title = "Link Gốc",
        url = track.uri,
        description = f"Đã thêm **{track.title}** vào hàng chờ.",
        colour = discord.Colour(0xe3f708))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      await ctx.send(embed = embed)
    else:
      await vc.play(track)
      embed = discord.Embed(
        title = "Link Gốc",
        url = track.uri,
        description = f"Đã thêm **{track.title}** vào hàng chờ.",
        colour = discord.Colour(0xe3f708))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      await ctx.send(embed = embed)

  async def play_spotify_playlist(self, ctx: discord.ext.commands.Context, playlist: str, vc: CustomPlayer):
    embed = discord.Embed(
      description = "Đang tải danh sách phát...",
      colour = discord.Colour(0xe3f708))
    embed.set_author(
        name = ctx.author.name,
       icon_url = ctx.author.avatar.url)
    await ctx.send(embed = embed)
    async for partial in spotify.SpotifyTrack.iterator(query = playlist):
      if vc.is_playing() or not vc.queue.is_empty:
        vc.queue.put(item = partial)
      else:
        await vc.play(partial)
        embed = discord.Embed(
          title = "Link Gốc",
          url = vc.current.uri,
          description = f"Đang phát **{vc.current.title}**.",
          colour = discord.Colour(0x00ff00))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)

  async def play_youtube_song(self, ctx: discord.ext.commands.Context, query: str, vc: CustomPlayer):
    try:
      query = re.sub(r"&t=\d+", "", query)
      print(query)
      track = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, query)
      track = track[0]
      if vc.is_playing() or not vc.queue.is_empty:
        vc.queue.put(item = track)
        embed = discord.Embed(
          title = "Link Gốc",
          url = track.uri,
          description = f"Đã thêm **{track.title}** vào hàng chờ.",
          colour = discord.Colour(0xe3f708))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
      else:
        await vc.play(track)
        embed = discord.Embed(
          title = "Link Gốc",
          url = vc.current.uri,
          description = f"Đang phát **{vc.current.title}**.",
          colour = discord.Colour(0x00ff00))
        embed.set_author(
          name = ctx.author.name,
          icon_url = ctx.author.avatar.url)
        await ctx.send(embed = embed)
    except Exception as e:
      embed = discord.Embed(
        description = "Xin lỗi, Ifrit không thể phát nhạc từ đường link này.",
        colour = discord.Colour(0xff0000))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      await ctx.send(embed = embed)

  async def play_youtube_playlist(ctx: discord.ext.commands.Context, playlist: str):
    pass

  async def play_query(self, ctx: discord.ext.commands.Context, search: str, vc: CustomPlayer):
    track = await wavelink.YouTubeTrack.search(search, return_first = True)
    if vc.is_playing() or not vc.queue.is_empty:
      vc.queue.put(item = track)
      embed = discord.Embed(
        title = "Link Gốc",
        url = track.uri,
        description = f"Đã thêm **{track.title}** vào hàng chờ.",
        colour = discord.Colour(0xe3f708))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      await ctx.send(embed = embed)
    else:
      await vc.play(track)
      embed = discord.Embed(
        title = "Link Gốc",
        url = vc.current.uri,
        description = f"Đang phát **{vc.current.title}**.",
        colour = discord.Colour(0x00ff00))
      embed.set_author(
        name = ctx.author.name,
        icon_url = ctx.author.avatar.url)
      await ctx.send(embed = embed)

  url_type_mapping = {
    "Spotify Track": play_spotify_track,
    "Spotify Playlist": play_spotify_playlist,
    "Spotify Album": play_spotify_playlist,
    "YouTube Song": play_youtube_song,
    "YouTube Playlist": play_youtube_playlist,
    "Text": play_query,}

  def check_string(self, input_string):
    youtube_pattern = re.compile(
      (r"https?://(www\.)?(youtube|youtu)(\.com|\.be)/"
       "(playlist\?list=|watch\?v=|embed/|)([a-zA-Z0-9-_]+)(\&t=\d+s)?"
       "|https://youtu.be/([a-zA-Z0-9-_]+)(\?t=\d+s)?"))
    spotify_pattern = re.compile(
      (r"https?://open\.spotify\.com/(album|playlist|track)"
        "/([a-zA-Z0-9-]+)(/[a-zA-Z0-9-]+)?(\?.*)?"))

    youtube_match = youtube_pattern.match(input_string)
    spotify_match = spotify_pattern.match(input_string)

    if youtube_match:
      return self.get_youtube_pattern(youtube_match)
    elif spotify_match:
      return self.get_spotify_pattern(spotify_match)
    return "Text"

  def get_spotify_pattern(self, spotify_match):
    if spotify_match:
      if "track" in spotify_match.group():
        return "Spotify Track"
      elif "playlist" in spotify_match.group():
        return "Spotify Playlist"
      elif "album" in spotify_match.group():
        return "Spotify Album"
      else:
        return "Spotify URL"

  def get_youtube_pattern(self, youtube_match):
    if youtube_match:
      if "watch?v=" in youtube_match.group() or "youtu.be" in youtube_match.group():
        return "YouTube Song"
      elif "playlist?list=" in youtube_match.group():
        return "YouTube Playlist"
      else:
        return "YouTube URL"

async def setup(client):
  await client.add_cog(Music(client))
