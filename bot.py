import telebot
import requests
import time

# --- CONFIG ---
API_TOKEN = '8643339511:AAFPeezy3CixlEPIqi_jAJwIifwQ7UUQVa0'
GROUP_ID = '@kingtrader_56' 
# 1-Minute Game API
GAME_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

bot = telebot.TeleBot(API_TOKEN)

stats = {"win": 0, "loss": 0}
msg_memory = [] 
active_pred = None
last_period = 0

# Stickers
STICKER_WIN = 'CAACAgUAAxkBAAERJURp9GS9xqThsQODJek49lXFJUczGwAC3xQAApDy-VSDmVQMBRLwnTsE'
STICKER_LOSS = 'CAACAgUAAxkBAAERJUhp9GThL2yGRI1bVjxu1gdQTreVNgACJQMAAj8BAVUpyCGBerBuEDsE'

def get_weighted_prediction(nums):
    """1.8x Weighted Trend Logic"""
    big_weight = 0
    small_weight = 0
    power = 1
    
    # Last 10 results check (1-minute game trends)
    analysis_list = nums[:10]
    for n in reversed(analysis_list):
        if n >= 5:
            big_weight += power
        else:
            small_weight += power
        power *= 1.8
        
    return "BIG" if big_weight >= small_weight else "SMALL"

def get_super_single_logic():
    try:
        # Timestamp add kiya taake cache issue na ho
        res = requests.get(f"{GAME_API}?t={int(time.time())}", timeout=10).json()
        list_data = res['data']['list']
        nums = [int(i['number']) for i in list_data]
        current_period = int(list_data[0]['issueNumber'])

        p_val = get_weighted_prediction(nums)

        # Jackpot Numbers Calculation
        n1 = (nums[0] * 2 + 5) % 10
        n2 = (nums[0] * 8 + 1) % 10

        return {
            "period": current_period + 1,
            "prediction": p_val,
            "nums": f"{n1} , {n2}",
            "last_num": nums[0],
            "last_size": "BIG" if nums[0] >= 5 else "SMALL"
        }
    except:
        return None

print("🚀 1-MINUTE BOT STARTING...")

while True:
    try:
        data = get_super_single_logic()
        if data and data['period'] != last_period:
            
            # 1. Previous Result Check
            if active_pred:
                is_win = active_pred['prediction'] == data['last_size']
                
                if is_win:
                    stats["win"] += 1
                    s = bot.send_sticker(GROUP_ID, STICKER_WIN)
                    msg_memory.append(s.message_id)
                    status_text = f"✅ **WIN CONFIRMED**\nPeriod: `{data['period']-1}`\nResult: `{data['last_num']} ({data['last_size']})`"
                    res_msg = bot.send_message(GROUP_ID, status_text, parse_mode="Markdown")
                    msg_memory.append(res_msg.message_id)
                else:
                    stats["loss"] += 1
                    # Clean group on loss
                    for mid in msg_memory:
                        try: bot.delete_message(GROUP_ID, mid)
                        except: pass
                    msg_memory = []
                    bot.send_sticker(GROUP_ID, STICKER_LOSS)

            # 2. New 1-Minute Signal
            msg_text = f"""
🕹️ 𝐆𝐀𝐌𝐄   : 𝐖𝐈𝐍𝐆𝐎 𝟏-𝐌𝐈𝐍𝐔𝐓𝐄
🆔 𝐏𝐄𝐑𝐈𝐎𝐃 : `{data['period']}`
▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭
🎯 𝐒𝐈𝐆𝐍𝐀𝐋 : 🔵 {data['prediction']}
🔢 𝐍𝐔𝐌𝐁𝐄𝐑 : 🎰 {data['nums']}
▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭
📊 𝐒𝐓𝐀𝐓𝐒   : 🏆 WIN: {stats['win']} | 💀 LOSS: {stats['loss']}
🛡️ 𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐌𝐑. 𝐇𝐔𝐒𝐍𝐀𝐈𝐍
"""
            sent_sig = bot.send_message(GROUP_ID, msg_text, parse_mode="Markdown")
            msg_memory = [sent_sig.message_id] 
            
            last_period = data['period']
            active_pred = data
            
        time.sleep(5) # 1-min game ke liye 5s check interval kaafi hai
    except Exception as e:
        time.sleep(5)
