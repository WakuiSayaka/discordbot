# 環境変数用 標準ライブラリなのでインストール不要
import os
import subprocess
# 乱数用
import random
# 正規表現
import re
# 時刻
import datetime
# load_opus用
import ctypes
# wait_forのTimeoutErrorに必要
import asyncio
# インストールした discord.py を読み込む
import discord

# Botのアクセストークン 環境変数から
TOKEN = os.environ['DISCORDBOT_TOKEN_ID']

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 反応するチャンネルのID
CHANNEL_ID_BOTROOM    = 872481513504124970
CHANNEL_ID_GENERAL    = 872192669965754451
CHANNEL_ID_VC_GENERAL = 872192669965754452



async def greet():
    channel = client.get_channel(CHANNEL_ID_BOTROOM)
    await channel.send('おはようございます！');

# 起動時に動作する処理
@client.event
async def on_ready():
    await greet() #挨拶をする非同期関数
    # 起動したらターミナルにログイン通知が表示される
    # print('ログインしました')


#@bot名を除いた内容を抽出
def extract_reply(message):
    target = '@Tsumugi Wenders '
    res = message[len(target):] # target以降を抽出
    return res

# 返信する非同期関数を定義
async def reply(message):
    # リプライの内容
    message_contents = extract_reply(message.clean_content)
    if message_contents == '':
        reply = f'{message.author.mention} 呼んだ？' # 返信メッセージの作成
    elif message_contents == '/clear':
        if message.author.guild_permissions.administrator:
            await message.channel.purge()
            reply = f'{message.author.mention} お掃除終わりました！'
        else:
            reply = f'{message.author.mention} 管理者専用コマンドだよ！'
    else :
        reply = f'{message.author.mention} {message_contents}\nってにゃに？' # 返信メッセージの作成
    await message.channel.send(reply) # 返信メッセージを送信

# 発言したチャンネルのカテゴリ内にチャンネルを作成する非同期関数
async def create_channel(message, channel_name):
    category_id = message.channel.category_id
    category = message.guild.get_channel(category_id)
    new_channel = await category.create_text_channel(name=channel_name)
    return new_channel

# コマンドに対応するリストデータを取得する関数を定義
def get_data(message):
    command = re.search(r'-\w+',message.content)
    data_table = {
        '-members': message.guild.members, # メンバーのリスト
        '-roles': message.guild.roles, # 役職のリスト
        '-text_channels': message.guild.text_channels, # テキストチャンネルのリスト
        '-voice_channels': message.guild.voice_channels, # ボイスチャンネルのリスト
        '-category_channels': message.guild.categories, # カテゴリチャンネルのリスト
    }
    return data_table.get(command.group(), '無効なコマンドです')



# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return


    # 話しかけられたかの判定
    if client.user in message.mentions:
        await reply(message) # 返信する非同期関数を実行


    # --------------以下、特定のチャンネルにのみ反応---------------------
    if message.channel.id not in [CHANNEL_ID_BOTROOM,CHANNEL_ID_GENERAL]:
        return


    # 管理者のみ「/clear」と発言したらテキストチャンネル内のログの全削除
    if message.content == '/clear':
        if message.author.guild_permissions.administrator:
            await message.channel.purge()
            await message.channel.send('お掃除終わりました！')
        else:
            await message.channel.send('管理者専用コマンドだよ！')

    if message.channel.id != CHANNEL_ID_BOTROOM:
        return


    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')


    # waitforの使用例コピペ
    if message.content.startswith('$thumb'):
        channel = message.channel
        await channel.send('Send me that 👍 reaction, mate')

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '👍'
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('👎')
        else:
            await channel.send('👍')
            return


    # じゃんけん
    if message.content == '/rsp':
        rsp   = ['ぐー','ちょき','ぱー']
        judge = ['引き分けです！','あなたの勝ちです！','わたしの勝ちです！']
        await message.channel.send(f'10秒以内に{rsp[0]}、{rsp[1]}、{rsp[2]}のどれかで返してね！')
        await message.channel.send('最初はぐー！じゃんけん！')

        def rsp_check(m):
            return m.author == message.author and m.content in rsp

        try:
            player = await client.wait_for("message", timeout=10.0 , check=rsp_check)
        except asyncio.TimeoutError:
            await message.channel.send('たいむあうと！')
        else:
            bot = random.randint(0,2)
            await message.channel.send(f'あなた：{player.content}')
            await message.channel.send(f'わたし：{rsp[bot]}')
            await message.channel.send(judge[(bot  - rsp.index(player.content) + 3)%3])
            return




    # ロール「Bot管理者」が「!stop」と発言したらログアウト処理
    if "!stop" in message.content:
        if "Bot管理者" in [users_role.name for users_role in message.author.roles]:
            await message.channel.send("ばいばーい！")
            await client.close()
        else:
            await message.channel.send("Bot管理者専用コマンドだよ！")


    # チャンネルの作成「/mkch」 /mkch example のようにチャンネル名の指定も可
    if message.content.startswith('/mkch'):
        channel_name = 'new'
        if (len('/mkch')+1) < len(message.content):
            channel_name = message.content[len('/mkch')+1:]
        # チャンネルを作成する非同期関数を実行して Channel オブジェクトを取得
        new_channel = await create_channel(message, channel_name)
        # チャンネルのリンクと作成メッセージを送信
        text = f'{new_channel.mention} を作成しました'
        await message.channel.send(text)

    # 時刻の取得
    # タイムゾーンの生成
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    date = datetime.datetime.now(JST)
    if message.content == '今は？':
        await message.channel.send(f'{date}です！')
    if message.content == '何時？':
        await message.channel.send(f'{date.hour}時です！')
    if message.content == '何分？':
        await message.channel.send(f'{date.minute}分です！')
    if message.content == '何時何分？':
        await message.channel.send(f'{date.hour}時{date.minute}分です！')

    # データテーブルの表示
    if message.content.startswith('/get_data'):
        await message.channel.send(get_data(message))

    if '/join' == message.content:
        #join(message)
        if message.author.voice is None:
            await message.channel.send("あなたはボイスチャンネルに接続していません。")
            return
        await message.author.voice.channel.connect()

    if '/leave' == message.content:
        #leave(message)
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()

    if message.content == "/play":
        if not discord.opus.is_loaded():
            await message.channel.send("libopusをロードします")
            #もし未ロードだったら
            discord.opus.load_opus("heroku-buildpack-libopus")
        await message.channel.send("準備完了")
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        message.guild.voice_client.play(discord.FFmpegPCMAudio("greeting.mp3"))



# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
