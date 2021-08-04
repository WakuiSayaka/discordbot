# 環境変数用 標準ライブラリなのでインストール不要
import os
import subprocess
# インストールした discord.py を読み込む
import discord

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORDBOT_TOKEN_ID']


# 接続に必要なオブジェクトを生成
client = discord.Client()


# 一般チャンネルのID
CHANNEL_ID = 872192669965754451

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


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    # 管理者のみ「/clear」と発言したらテキストチャンネル内のログの全削除
    if message.content == '/clear':
        if message.author.guild_permissions.administrator:
            await message.channel.purge()
            await message.channel.send('お掃除終わりました！')
        else:
            await message.channel.send('悪い事しちゃダメです！')
    # ロール「Bot管理者」が「!stop」と発言したらログアウト処理
    if "!stop" in message.content:
        if "Bot管理者" in [users_role.name for users_role in message.author.roles]:
            await message.channel.send("ばいばーい！")
            await client.close()
        else:
            await message.channel.send("管理者専用コマンドだよ！")
    # 話しかけられたかの判定
    if client.user in message.mentions:
        await reply(message) # 返信する非同期関数を実行

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
