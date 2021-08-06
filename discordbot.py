# 環境変数用 標準ライブラリなのでインストール不要
import os
import subprocess

import random
# インストールした discord.py を読み込む
import discord

# Botのアクセストークン 環境変数から
TOKEN = os.environ['DISCORDBOT_TOKEN_ID']


# 接続に必要なオブジェクトを生成
client = discord.Client()


# 反応するチャンネルのID
CHANNEL_ID_BOTROOM = 872481513504124970
CHANNEL_ID_GENERAL = 872192669965754451

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
        await message.channel.send('最初はグー！じゃんけん！')
        rsp = ['ぐー','ちょき','ぱー']
        judge = ['引き分けです！','わたしの勝ちです！','あなたの勝ちです！']

        def rsp_check(m):
            return m.content in ['ぐー','ちょき','ぱー'] and m.author == message.author
        player_rsp = await client.wait_for('message', check=rsp_check)

        bot_rsp = random.randint(0,2)
        flag = (bot_rsp  - rsp.index(player_rsp.content) + 3)%3

        await channel.send(f'あなた：{player_rsp.content}')
        await channel.send(f'わたし：{rsp[bot_rsp]}')
        await channel.send(judge[flag])

    if message.content == "！じゃんけん":
        await message.channel.send("最初はぐー、じゃんけん")

        jkbot = random.choice(("ぐー", "ちょき", "ぱー"))
        draw = "引き分けだよ～"
        wn = "君の勝ち！"
        lst = random.choice(("私の勝ち！弱ｗｗｗｗｗｗｗｗｗｗｗｗやめたら？じゃんけん",
                              "私の勝ちだね(∩´∀｀)∩、また挑戦してね！"))

        def jankencheck(m):
            return (m.author == message.author) and (m.content in ['ぐー', 'ちょき', 'ぱー'])

        reply = await client.wait_for("message", check=jankencheck)
        if reply.content == jkbot:
            judge = draw
        else:
            if reply.content == "ぐー":
                if jkbot == "ちょき":
                    judge = wn
                else:
                    judge = lst

            elif reply.content == "ちょき":
                if jkbot == "ぱー":
                    judge = wn
                else:
                    judge = lst

            else:
                if jkbot == "ぐー":
                    judge = wn
                else:
                    judge = lst

        await message.channel.send(judge)

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




# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
