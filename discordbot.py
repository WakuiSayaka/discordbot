# 環境変数用 標準ライブラリなのでインストール不要
import os
import subprocess
# インストールした discord.py を読み込む
import discord

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORDBOT_TOKEN_ID']


# 接続に必要なオブジェクトを生成
client = discord.Client()


# 反応するチャンネルのID
CHANNEL_ID = 872481513504124970

async def greet():
    channel = client.get_channel(CHANNEL_ID)
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
    else :
        reply = f'{message.author.mention} {extract_reply(message.clean_content)}\nってにゃに？' # 返信メッセージの作成
    await message.channel.send(reply) # 返信メッセージを送信

# 発言したチャンネルのカテゴリ内にチャンネルを作成する非同期関数
async def create_channel(message, channel_name):
    category_id = message.channel.category_id
    category = message.guild.get_channel(category_id)
    new_channel = await category.create_text_channel(name=channel_name)
    return new_channel


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # 話しかけられたかの判定
    if client.user in message.mentions:
        await reply(message) # 返信する非同期関数を実行

    # 管理者のみ「/clear」と発言したらテキストチャンネル内のログの全削除
    if message.content == '/clear':
        if message.author.guild_permissions.administrator:
            await message.channel.purge()
            await message.channel.send('お掃除終わりました！')
        else:
            await message.channel.send('悪い事しちゃダメです！')

    # --------------以下、特定のチャンネルにのみ反応---------------------
    # 複数指定する場合は
    # if message.channel.id not in [チャンネルID, チャンネルID2]:
    if message.channel.id != CHANNEL_ID:
        return

    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')

    # ロール「Bot管理者」が「!stop」と発言したらログアウト処理
    if "!stop" in message.content:
        if "Bot管理者" in [users_role.name for users_role in message.author.roles]:
            await message.channel.send("ばいばーい！")
            await client.close()
        else:
            await message.channel.send("管理者専用コマンドだよ！")

    # チャンネルの作成「/mkch」 (startswith... /mkchから始まる文字列に反応)
    if message.content.startswith('/mkch'):
        channel_name = 'new'
        if (len('/mkch')+1) < len(message.content):
            channel_name = message.content[len('/mkch')+1:]
        # チャンネルを作成する非同期関数を実行して Channel オブジェクトを取得
        new_channel = await create_channel(message, channel_name)

        # チャンネルのリンクと作成メッセージを送信
        text = f'{new_channel.mention} を作成しました'
        await message.channel.send(text)




# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
