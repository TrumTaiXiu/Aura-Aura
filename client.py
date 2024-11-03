from zlapi import ZaloAPI
from zlapi.models import *
import time
import importlib
import os
import json
import threading
import requests
import re
from datetime import datetime
import urllib.request
from zlapi.models import Message, ThreadType
import random
import threading
from zlapi.models import Mention, Message
from zlapi._message import MultiMention
import sys
from colorama import Fore, Style, init



PREFIX = ""



SELF_LISTEN = True
with open('nhay.txt', 'r', encoding='utf-8') as f:
    messages_list = [line.strip() for line in f.readlines()]

class Qkhanh(ZaloAPI):
    def __init__(self, username, password, imei, session_cookies):
        self.threads = {}
        self.poll_threads = {}
        self.bigtext_threads = {}
        self.nhay_threads = {}
        self.nhaytag_threads = {}
        self.avatar_threads = {}
        self.setnamebox_threads = {}
        self.spam_threads = {}
        self.user_money = {} 
        super().__init__(username, password, imei, session_cookies)
        self.start_time = time.time() 
        self.config = json.loads(open("config.json").read())
        self.commands = {
            "upt": self.upt,
            "ping": self.ping,
            "kick": self.kick,
            "girl": self.girl,
            "getid": self.getid,
            "hi": self.hi,
            "kiss": self.kiss,
            "all": self.all, 
            "admin": self.admin,
            "bigtext": self.bigtext, 
            "menu": self.menu,
            "creategroup": self.creategroup, 
            "createpoll": self.createpoll,
            "nhay": self.nhay,
            "nhaytag": self.nhaytag,
            "setnamebox": self.setnamebox,
            "spam": self.spam,
            "setavtbox": self.setavtbox,
            "infad": self.infad,
        }
        self.loader()

    
    def get_user_money(self, user_id):
        return self.user_money.get(user_id, 0)

    def set_user_money(self, user_id, amount):
        self.user_money[user_id] = amount
        print(f"Updated money for {user_id}: {amount}")
    
    def setConfig(self, config):
        self.config = config
        json.dump(config, open("config.json", "w"))
    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None, thread_type=ThreadType.USER):
        if(not SELF_LISTEN and author_id == self.uid): return

        if isinstance(message, str) and message.startswith(PREFIX) and (author_id in self.config["adminIds"] or author_id == self.uid):
            pluginName = message[len(PREFIX):].split(" ")[0]
            args = message[len(PREFIX) + len(pluginName):].split(" ")[1:]

            if author_id not in self.config["adminIds"] and author_id != self.uid:
                reply_message = Message("Bạn không có quyền sử dụng lệnh này!")
                self.replyMessage(reply_message, message_object, thread_id, thread_type)
                return

            plugin = self.commands.get(pluginName, lambda *args: None)

            if plugin:
                threading.Thread(target=plugin, args=(self, args, mid, author_id, message, message_object, thread_id, thread_type)).start()
        print(f"{Fore.GREEN}Received message:\n"
              "------------------------------\n"
              f"**Message Details:**\n"
              f"- **Message:** {Style.BRIGHT}{message} {Style.NORMAL}\n"
              f"- **Author ID:** {Fore.CYAN}{author_id} {Style.NORMAL}\n"
              f"- **Thread ID:** {Fore.YELLOW}{thread_id}\n"
              f"- **Thread Type:** {Fore.BLUE}{thread_type}\n"
              f"- **Message Object:** {Style.DIM}{message_object}\n"
              f"{Fore.GREEN}------------------------------\n"
              )
    

    def count(self, string: str, word: str) -> list:
        indices = []
        start = 0
        while True:
            idx = string.find(word, start)

            if idx == -1:
                break

            indices.append(idx)
            start = idx + 1

        return indices
    
    def checkmoney(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        amount = self.get_user_money(author_id)
        
        text = f"Số tiền hiện tại của bạn là: {amount}"
        client.replyMessage(Message(text), message_object, thread_id, thread_type)
        

    def spam(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        _delay = 5
        retry_delay = 60 
        max_retries = 5 
        def spam_message(stop_event, message):
            retries = 0
            while not stop_event.is_set():
                try:
                    client.send(Message(message), thread_id=thread_id, thread_type=thread_type)
                    time.sleep(_delay)
                    retries = 0
                except Exception as e:
                    print(f"Error occurred: {e}")
                    if retries < max_retries:
                        time.sleep(retry_delay)
                        retries += 1
                    else:
                        print("Max retries reached, stopping spam.")
                        break

        if "stop" in args:
            if thread_id in self.spam_threads:
                self.spam_threads[thread_id][0].set() 
                self.spam_threads[thread_id][1].join()  
                del self.spam_threads[thread_id]
                response_message = "Đã Stop lệnh spam"
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"Stopped spamming on {thread_id}.")
            else:
                response_message = "Không có hoạt động spam nào đang diễn ra để dừng."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"No active spam to stop on {thread_id}.")
        else:
            if len(args) > 0:
                custom_message = " ".join(args)
            else:
                response_message = "Bạn phải cung cấp nội dung để spam."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                return

            stop_event = threading.Event()
            thread = threading.Thread(target=spam_message, args=(stop_event, custom_message))
            thread.start()
            self.spam_threads[thread_id] = (stop_event, thread)
            print(f"Started spam on {thread_id}.")


    def setnamebox(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if "stop" in args:
            if thread_id in self.setnamebox_threads:
                self.setnamebox_threads[thread_id][0].set()
                self.setnamebox_threads[thread_id][1].join()
                del self.setnamebox_threads[thread_id]
                response_message = "Đã Stop lệnh đặt tên box"
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"Stopped đặt tên box trên {thread_id}.")
            else:
                response_message = "Không diễn ra active đặt tên box."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"No active đặt tên box to stop on {thread_id}.")
        else:
            name = message[len(PREFIX) + len("setnamebox") + 1:]  # sửa đổi cách lấy giá trị name
            if len(name) < 1:
                text = "Vui lòng nhập tên box để đặt"
            else:
                def change_name(stop_event):
                    while not stop_event.is_set():
                        try:
                            client.changeGroupName(name, thread_id)
                            print(f"Đã đặt tên box thành {name}")
                        except Exception as e:
                            print(f"Lỗi khi đặt tên box: {e}")
                        time.sleep(5)

                stop_event = threading.Event()
                thread = threading.Thread(target=change_name, args=(stop_event,))
                thread.start()
                self.setnamebox_threads[thread_id] = (stop_event, thread)
                text = "Bật chế độ Anti setnamebox"

            reply_message = Message(text)
            client.replyMessage(reply_message, message_object, thread_id, thread_type)
    def setavtbox(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        try:
            if args == ["stop"]:
                if thread_id in self.avatar_threads:
                    self.avatar_threads[thread_id][0].set()
                    self.avatar_threads[thread_id][1].join()
                    del self.avatar_threads[thread_id]
                    client.send(Message("Đã dừng lệnh đặt avatar box."), thread_id=thread_id, thread_type=thread_type)
                    print(f"Stopped setting avatar on {thread_id}.")
                else:
                    client.send(Message("Không diễn ra active đặt avatar box."), thread_id=thread_id, thread_type=thread_type)
                    print(f"No active avatar setting to stop on {thread_id}.")
                return

            if len(args) < 1:
                client.send(Message("Sai cú pháp! Vui lòng nhập đường dẫn file"), thread_id=thread_id, thread_type=thread_type)
                return

            file_path = args[0]

            def set_avatar_loop(stop_event):
                while not stop_event.is_set():
                    try:
                        group_avatar = client.changeGroupAvatar(file_path, thread_id)
                        print("Thay đổi ảnh nhóm thành công!")
                    except ZaloUserError as e:
                        print(f"Lỗi: {e}")
                    except ZaloAPIException as e:
                        print(f"Lỗi API: {e}")
                    time.sleep(5)

            stop_event = threading.Event()
            thread = threading.Thread(target=set_avatar_loop, args=(stop_event,))
            thread.start()
            self.avatar_threads[thread_id] = (stop_event, thread)

        except ValueError:
            client.send(Message("Không hợp lệ. Xin vui lòng thử lại"), thread_id=thread_id, thread_type=thread_type)

    def nhay(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        _delay = 3 
        retry_delay = 60  
        max_retries = 5  


        def nhay_message(stop_event, messages):
            current_index = 0
            retries = 0
            while not stop_event.is_set():
                try:
                    client.send(Message(messages[current_index]), thread_id=thread_id, thread_type=thread_type)
                    time.sleep(_delay)
                    current_index = (current_index + 1) % len(messages)
                    retries = 0  
                except Exception as e:
                    print(f"Error occurred: {e}")
                    if retries < max_retries:
                        time.sleep(retry_delay)
                        retries += 1
                    else:
                        print("Max retries reached, stopping nhay.")
                        break

        if "stop" in args:
            if thread_id in self.nhay_threads:
                self.nhay_threads[thread_id][0].set()
                self.nhay_threads[thread_id][1].join()
                del self.nhay_threads[thread_id]
                response_message = "Đã Stop lệnh nhay"
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"Stopped spamming on {thread_id}.")
            else:
                response_message = "Không diễn ra active Nhay."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"No active nhay to stop on {thread_id}.")
        else:
            stop_event = threading.Event()
            thread = threading.Thread(target=nhay_message, args=(stop_event, messages_list))
            thread.start()
            self.nhay_threads[thread_id] = (stop_event, thread)
            print(f"Started nhay on {thread_id}.")


    def infad(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        text = """
🎉️✨️ 🌸𝑃𝑟𝑜𝑓𝑖𝑙𝑒 𝐴𝑑𝑚𝑖𝑛 🌸 ✨️🎉️
 User Name: Quốc Khánh 
Birthday: 16/03/2015
Gender: Nam 👨️
 Url Fb:  
✉️️ icloud: quock1@icloud.com 📧️

---- 🌸𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐐.𝐊𝐡𝐚́𝐧𝐡🌸 ---- 
🤝️ Lưu ý: Thắc mắc liên hệ trực tiếp với Admin.
💕️ Cảm ơn bạn đã quan tâm! ❤️️
👋️ Nếu bạn cần giúp đỡ, hãy liên hệ với admin! 🤝️
🎨 𝘊𝘰𝘱𝘺𝘙𝘪𝘨𝘩𝘵 𝘈𝘥𝘮𝘪𝘯 𝘉𝘰𝘵 QKhánh 
    """
# hãy tôn trọng tác giả không đc xoá dòng này
        try:

            image_dir = "image/anime"
            image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

            random_image = random.choice(image_files)

            image_path = os.path.join(image_dir, random_image)
            client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=Message(text))
        except Exception as e:
            print(f"Error accessing the directory or sending the image: {e}")

    def creategroup(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):

        content = message.split("creategroup ")[1]
        

        parts = content.split(", ")
        
    
        name = parts[0]
        

        members = parts[1:]
        
        try:
            response = client.createGroup(name, members=members)
            if response.get("error_code") == 0 and response.get("error_message"):
    
                reply_message = Message(f"Tạo nhóm {name} thành công và thêm {len(members)} người vào nhóm! Đã tạo thành công.")
                client.replyMessage(reply_message, message_object, thread_id, thread_type)
    
                for member in members:
                    reply_message = Message(f"<at id='{member}'> {member}</at>", is_at=True)
                    client.replyMessage(reply_message, message_object, thread_id, thread_type)
        except ZaloAPIException as e:
            reply_message = Message(f"Lỗi tạo nhóm: {e}")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)



    def createpoll(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if args == ["stop"]:
            if thread_id in self.poll_threads:
                self.poll_threads[thread_id][0].set()
                self.poll_threads[thread_id][1].join()
                del self.poll_threads[thread_id]
                client.send(Message("Đã dừng tạo poll."), thread_id=thread_id, thread_type=thread_type)
                print(f"Stopped creating polls on {thread_id}.")
            else:
                client.send(Message("Không diễn ra tạo poll."), thread_id=thread_id, thread_type=thread_type)
                print(f"No active poll creation on {thread_id}.")
            return

        question = message.split("createpoll ")[1]
        options = question.split(", ")

        def create_poll(stop_event):
            while True:
                if stop_event.is_set():
                    break
                poll = client.createPoll(
                    question=options[0],
                    options=options[1:],
                    groupId=thread_id,
                    expiredTime=0,
                    pinAct=False,
                    multiChoices=True,
                    allowAddNewOption=True,
                    hideVotePreview=False,
                    isAnonymous=False
                )

                time.sleep(3)  

        stop_event = threading.Event()
        thread = threading.Thread(target=create_poll, args=(stop_event,))
        thread.start()
        self.poll_threads[thread_id] = (stop_event, thread)

    def upt(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)  # Tính toán thời gian uptime
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_string = f"𝘛𝘩𝘰̛̀𝘪 𝘨𝘪𝘢𝘯 𝘩𝘰𝘢̣𝘵 𝘥𝘰̣̂𝘯𝘨 :  {days} ngày, {hours} giờ, {minutes} phút và {seconds} giây."

        image_dir = "image/anime"
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        random_image = random.choice(image_files)
        image_path = os.path.join(image_dir, random_image)

        message_to_send = Message()
        message_to_send.text = uptime_string
        client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=message_to_send)




    def menu(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        text = ":\n🍭𝐼𝑛𝑓𝑜𝑟𝑚𝑎𝑡𝑖𝑜𝑛 𝐶𝑜𝑛𝑡𝑟𝑜𝑙 𝑃𝑎𝑛𝑒𝑙 𝐵𝑜𝑡 𝑍𝑎𝑙𝑜🌸\n-----------------\n"
        commands = [
            {"name": "𝗮𝗱𝗺𝗶𝗻", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐚𝐝𝐦𝐢𝐧 <𝐚𝐝𝐝|𝐫𝐞𝐦𝐨𝐯𝐞> <𝐮𝐢𝐝/𝐫𝐞𝐩𝐥𝐲>", "icon": "💬"},
            {"name": "𝗮𝗹𝗹", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐚𝐥𝐥 <𝐓𝐢𝐧 𝐍𝐡𝐚̆́𝐧>", "icon": "💬"},
            {"name": "𝘂𝗽𝘁", "description": "𝐓𝐡𝐨̛̀𝐢 𝐆𝐢𝐚𝐧 𝐇𝐨𝐚̣𝐭 𝐃𝐨̣̂𝐧𝐠 𝐂𝐮̉𝐚 𝐁𝐨𝐭 𝐋𝐨̉", "icon": "💬"},
            {"name": "𝗴𝗲𝘁𝗶𝗱", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐠𝐞𝐭𝐢𝐝 <@𝐮𝐬𝐞𝐫>", "icon": "💬"},
            {"name": "𝗻𝗵𝗮𝘆", "description": "𝐍𝐡𝐚̂𝐲 𝐌𝐚̂́𝐲 𝐓𝐤 𝐍𝐠𝐮", "icon": "💬"},
            {"name": "𝗰𝗿𝗲𝗮𝘁𝗲𝗽𝗼𝗹𝗹", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐜𝐫𝐞𝐚𝐭𝐞𝐩𝐨𝐥𝐥 <𝐪𝐮𝐞𝐬𝐭𝐢𝐨𝐧>, <𝐨𝐩𝟏>, <𝐨𝐩𝟐>", "icon": "💬"},
            {"name": "𝘀𝗺𝘀", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐬𝐦𝐬 <𝐬𝐝𝐭> <𝐬𝐨̂́ 𝐥𝐮̛𝐨̛̣𝐧𝐠>", "icon": "💬"},
            {"name": "𝗻𝗵𝗮𝘆𝘁𝗮𝗴", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐧𝐡𝐚𝐲𝐭𝐚𝐠 <@𝐮𝐬𝐞𝐫>", "icon": "💬"},
            {"name": "𝘀𝗽𝗮𝗺", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐬𝐩𝐚𝐦 <𝐜𝐨𝐧𝐭𝐞𝐧𝐭>", "icon": "💤"},
            {"name": "𝘀𝗲𝘁𝗻𝗮𝗺𝗲𝗯𝗼𝘅", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐬𝐞𝐭𝐧𝐞𝐚𝐦𝐛𝐨𝐱 <𝐧𝐚𝐦𝐞>>", "icon" :"💬"},
            {"name": "𝘀𝗲𝘁𝗮𝘃𝘁𝗯𝗼𝘅", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐬𝐞𝐭𝐚𝐯𝐭𝐛𝐨𝐱 <./𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬/𝐢𝐦𝐚𝐠𝐞/<𝐧𝐚𝐦𝐞𝐟𝐢𝐥𝐞𝐚𝐯𝐭>", "icon" :"💬"},
            {"name": "𝗶𝗻𝗳𝗮𝗱", "description": "𝐓𝐡𝐨̂𝐧𝐠 𝐭𝐢𝐧 𝐀𝐝𝐦𝐢𝐧 𝐁𝐨𝐭", "icon": "💬"},
            {"name": "𝗽𝗶𝗻𝗴", "description": "𝐊𝐢𝐞̂̉𝐦 𝐓𝐫𝐚 𝐃𝐨̣̂ 𝐓𝐫𝐞̂̃", "icon" :"💬"},
            {"name": "𝗸𝗶𝗰𝗸", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐤𝐢𝐜𝐤 <𝐢𝐝_𝐮𝐬𝐞>", "icon" :"💬"},
            {"name": "𝗴𝗶𝗿𝗹", "description": "𝐍𝐠𝐮̛́𝐚 𝐓𝐨̛̀ 𝐑𝐢𝐦 𝐓𝐡𝐢̀ 𝐃𝐮̀𝐧𝐠", "icon" :"💬"},
            {"name": "𝗯𝗶𝗴𝘁𝗲𝘅𝘁", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐁𝐢𝐠𝐭𝐞𝐱𝐭 <𝐜𝐨𝐧𝐭𝐞𝐧𝐭>", "icon" :"💬"},
            {"name": "𝗸𝗶𝘀𝘀", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐊𝐢𝐬𝐬 <@𝐮𝐬𝐞𝐫>", "icon" :"💬"},
            {"name": "𝗰𝗿𝗲𝗮𝘁𝗲𝗴𝗿𝗼𝘂𝗽", "description": "𝐔𝐬𝐚𝐠𝐞: 𝐜𝐫𝐞𝐚𝐭𝐞𝐠𝐫𝐨𝐮𝐮𝐩 <𝐧𝐚𝐦𝐞𝐛𝐨𝐱>, <𝐢𝐝𝟏>, <𝐢𝐝𝟐>", "icon" :"💬"},

        ]

        for command in commands:
            text += f"• {command['icon']} {PREFIX}{command['name']} : {command['description']}\n"

        text += "\n𝐶𝑜𝑝𝑦𝑟𝑖𝑔ℎ𝑡 𝐵𝑜𝑡 𝑍𝑎𝑙𝑜 : Quốc Khánh\n"
# hãy tôn trọng tác giả không đc xoá dòng này
        try:

            image_dir = "image/anime"
            image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

            random_image = random.choice(image_files)

            image_path = os.path.join(image_dir, random_image)
            client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=Message(text))
        except Exception as e:
            print(f"Error accessing the directory or sending the image: {e}")

    def all(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        delay = 3 #ae muốn all nhanh ntn thì ae chỉnh ở đây nhé
        try:
            if args == ["stop"]:
                if thread_id in self.threads:
                    self.threads[thread_id][0].set() 
                    self.threads[thread_id][1].join()  
                    del self.threads[thread_id]
                    client.send(Message("Đã dừng lệnh all."), thread_id=thread_id, thread_type=thread_type)
                    print(f"Stopped all on {thread_id}.")
                else:
                    client.send(Message("Không diễn ra active all."), thread_id=thread_id, thread_type=thread_type)
                    print(f"No active all to stop on {thread_id}.")
                return

            text = " ".join(args)

            def send_all(stop_event):
                while True:
                    if stop_event.is_set():
                        break
                    client.send(Message(text=text, mention=Mention(uid="-1", length=len(text))), thread_id=thread_id, thread_type=thread_type)
                    time.sleep(delay)

            stop_event = threading.Event()
            thread = threading.Thread(target=send_all, args=(stop_event,))
            thread.start()
            self.threads[thread_id] = (stop_event, thread)

        except ValueError:
            client.send(Message("Không hợp lệ. Xin vui lòng thử lại"), thread_id=thread_id, thread_type=thread_type)



    def nhaytag(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        delay = 1  #muốn ửa nhanh hay chậm chỉnh ở đây
        if "stop" in args:
            if thread_id in self.nhaytag_threads:
                self.nhaytag_threads[thread_id][0].set()  
                self.nhaytag_threads[thread_id][1].join()  
                del self.nhaytag_threads[thread_id]
                response_message = "Đã dừng lệnh nhaytag."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"Stopped nhaytag on {thread_id}.")
            else:
                response_message = "Không diễn ra active nhaytag."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"No active nhaytag to stop on {thread_id}.")
            return

        if not message_object.mentions:
            client.send(Message("No mentions found"), thread_id=thread_id, thread_type=thread_type)
            return

        mention = message_object.mentions[0]
        mention_text = "Tên hoặc chuỗi ký tự thay thế tên người được mention"
        with open('nhaytag.txt', 'r', encoding='utf-8') as f:
            tags = [line.strip() for line in f.readlines()]


        def send_nhaytag(client, thread_id, thread_type, mention_uid, mention_text, stop_event):
            mention_length = len(mention_text)
            while not stop_event.is_set():
                for tag in tags:
                    if stop_event.is_set():
                        break
                    full_message = f"{tag} @{mention_text}"
                    mention_length = len(mention_text) + 1
                    mention = Mention(uid=mention_uid, offset=len(tag) + 1, length=mention_length)
                    message = Message(text=full_message, mention=mention)
                    client.send(message, thread_id=thread_id, thread_type=thread_type)
                    time.sleep(delay)
        stop_event = threading.Event()

        if thread_id in self.nhaytag_threads:
            self.nhaytag_threads[thread_id][0].set()
            self.nhaytag_threads[thread_id][1].join()  

        thread = threading.Thread(target=send_nhaytag, args=(client, thread_id, thread_type, mention.uid, mention_text, stop_event))
        thread.start()
        self.nhaytag_threads[thread_id] = (stop_event, thread)


    def ping(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        start_time = time.time()
        reply_message = Message("Pinging Cutii Check Độ trễ >.<...🐰")
        client.replyMessage(reply_message, message_object, thread_id, thread_type)

        end_time = time.time()
        ping_time = end_time - start_time

        image_dir = "image/anime"
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        random_image = random.choice(image_files)
        image_path = os.path.join(image_dir, random_image)

        text = f"🎾 Ping Pong! Độ trễ của Bot hiện tại là: {ping_time:.2f}ms"
        client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=Message(text))


    def kick(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if len(message_object.mentions) < 1:
            reply_message = Message("Vui lòng tag người dùng cần kick")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)
            return
        
        kicked_users = []
        for mention in message_object.mentions:
            user_id = mention['uid']
            try:
                client.kickUsersFromGroup(user_id, thread_id)
                kicked_users.append(user_id)
            except ZaloAPIException as e:
                reply_message = Message(f"Lỗi khi kick người dùng {user_id}: {e}")
                client.replyMessage(reply_message, message_object, thread_id, thread_type)
        
        if kicked_users:
            reply_message = Message(f"Đã kick {', '.join(kicked_users)} ra khỏi nhóm")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)

              
    def hi(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        reply_message = Message("🔴𝑋𝑖𝑛 𝑐ℎ𝑎̀𝑜 ,  𝑇𝑜̂𝑖 𝑙𝑎̀ 𝑏𝑜𝑡 Quốc Khánh🎴")
        client.replyMessage(reply_message, message_object, thread_id, thread_type)

    def kiss(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if len(message_object.mentions) == 0:
            reply_message = Message("Vui lòng tag người dùng bạn muốn gửi nụ hôn!")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)
            return

        mentioned_user = message_object.mentions[0]
        user_id = mentioned_user['uid']

        image_dir = "image/kiss"
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        random_image = random.choice(image_files)
        image_path = os.path.join(image_dir, random_image)

        text = f"💋Bờ môi em thật quyến rũ, anh muốn chạm vào nó bằng đôi môi của anh lên chiếc lưỡi mọng nước của em!!!!"
        client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=Message(text))

    def girl(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        messages = [
            "Vợ chồng lục đục, tình dục làm hòa.",
            "Ngày Iphone mở bán… tôi mong em đừng mở háng 🙁",
            "Em có một con quỷ cái hố, anh có thể nhốt quái vật của anh vào trong này được không..",
            "Gió đưa cành trúc sau hè, Đây em nằm sẵn anh đè ngay đi",
            "Từ lâu em đã yêu anh, Hôm nay em muốn thả phanh xếp hình",
            "Bắc thang lên hỏi ông trời, Bán dâm một buổi kiếm lời bao nhiêu",
            "Ba dạy em: Nước biển làm ra muối, mía làm ra đường… và cái giường làm ra em.",
            "Theo như em được biết thì 70% cơ thể em là nước, vậy anh có thể cho em nuôi vài con nòng nọc được hong…",
            "Ngày ấy rũ em đi học đàn, không ngờ trở thành nhạc cụ để cho em thổi.",
            "Đôi khi có những mối quan hệ chỉ để quan hệ…",
            "Quy luật của tình yêu là: chụt, mút, đút, rút, phụt, cút",
            "Nhà em lấy chiếu làm giường, Tuy hơi mục nát, nhưng tường cách âm",
            "Sống nội tâm, thủ dâm là chính.",
            "Kim đâm vào thịt thì đau, Thịt đâm vào thịt nhớ nhau cả đời.",
            "Hoa hồng nào chẳng có gai, Yêu nhau thì phải có thai mới bền",
            "Ước gì anh hoá thành dưa, Để đêm em nhớ, em đưa anh vào.",
            "Yêu là sự rung động của bốn chân giường và là sự trần truồng của hai cá thể.",
            "Nếu ai đó quay lưng lại với bạn…, Hãy vỗ vào mông họ.",
            "Anh mệt hả, kiếm nhà nào nghỉ nhé!",
            "Chụp hình em không ăn ảnh, nhưng bỏ dấu hỏi thì em ăn được.",
            "Không thích history, tôi thích cậu hi story.",
            ""
        ]

        image_dir = "image/gai"
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        random_image = random.choice(image_files)
        image_path = os.path.join(image_dir, random_image)

        random_message = random.choice(messages)

        message_to_send = Message()
        message_to_send.text = random_message
        client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=message_to_send)





    def bigtext(self,client, args, mid, author_id, message, message_object, thread_id, thread_type):
        _delay = 5 
        retry_delay = 60 
        max_retries = 5 
        def bigtext_message(stop_event, message):
            retries = 0
            while not stop_event.is_set():
                try:
                    message_style = MessageStyle(offset=0, length=len(message.text), style="font", size="1000")
                    client.send(Message(text=message.text, style=message_style), thread_id=thread_id, thread_type=thread_type)
                    time.sleep(_delay)
                    retries = 0
                except Exception as e:
                    print(f"Error occurred: {e}")
                    if retries < max_retries:
                        time.sleep(retry_delay)
                        retries += 1
                    else:
                        print("Max retries reached, stopping spam.")
                        break

        if "stop" in args:
            if thread_id in self.bigtext_threads:
                self.bigtext_threads[thread_id][0].set() 
                self.bigtext_threads[thread_id][1].join()  
                del self.bigtext_threads[thread_id]
                response_message = "Stop bigtext"
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"Stopped bigtext on {thread_id}.")
            else:
                response_message = "Không có hoạt động bigtext nào đang diễn ra để dừng."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                print(f"No active bigtext to stop on {thread_id}.")
        else:
            if len(args) > 0:
                custom_text = " ".join(args)
                custom_message = Message(text=custom_text)
            else:
                response_message = "Bạn phải cung cấp nội dung để spam."
                client.replyMessage(Message(response_message), message_object, thread_id, thread_type)
                return

            stop_event = threading.Event()
            thread = threading.Thread(target=bigtext_message, args=(stop_event, custom_message))
            thread.start()
            self.bigtext_threads[thread_id] = (stop_event, thread)
            print(f"Started spam on {thread_id}.")

    def admin(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if len(args) == 0:
            reply_message = Message("Usage: admin <add|remove> <uid/reply>")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)
            return

        config = client.config

        match args[0].lower():
            case "add":
                if isinstance(message_object.quote, dict):
                    if str(message_object.quote['ownerId']) in config["adminIds"]: 
                        reply_message = Message(f"{message_object.quote['ownerId']} is already an admin")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return

                    config["adminIds"].append(str(message_object.quote['ownerId']))

                    reply_message = Message(f"Added {message_object.quote['ownerId']} to admin")
                    client.replyMessage(reply_message, message_object, thread_id, thread_type)
                else:
                    if len(args) < 2: 
                        reply_message = Message("reply/uid require")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return

                    if args[1] in config["adminIds"]:
                        reply_message = Message(f"{args[1]} is already an admin")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return

                    config["adminIds"].append(args[1])

                    reply_message = Message(f"Added {args[1]} from admin")
                    client.replyMessage(reply_message, message_object, thread_id, thread_type)
            
            case "remove":
                if isinstance(message_object.quote, dict):
                    if str(message_object.quote['ownerId']) not in config["adminIds"]: 
                        reply_message = Message(f"{message_object.quote['ownerId']} is not an admin")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return
                    config["adminIds"].remove(str(message_object.quote['ownerId']))

                    reply_message = Message(f"Removed {message_object.quote['ownerId']} to admin")
                    client.replyMessage(reply_message, message_object, thread_id, thread_type)
                else:
                    if len(args) < 2: 
                        reply_message = Message("reply/uid require")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return

                    if args[1] not in config["adminIds"]:
                        reply_message = Message(f"{args[1]} is not an admin")
                        client.replyMessage(reply_message, message_object, thread_id, thread_type)
                        return

                    config["adminIds"].remove(args[1])

                    reply_message = Message(f"Removed {args[1]} from admin")
                    client.replyMessage(reply_message, message_object, thread_id, thread_type)

            case _:
                reply_message = Message("Usage: admin <add|remove> <uid/reply>")
                client.replyMessage(reply_message, message_object, thread_id, thread_type)

        client.setConfig(config)

    def getid(self, client, args, mid, author_id, message, message_object, thread_id, thread_type):
        if len(message_object.mentions) < 1:
            reply_message = Message("Vui lòng tag người dùng cần lấy ID")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)
            return
        
        mentioned_user = message_object.mentions[0]
        user_id = mentioned_user['uid']
        
        try:
            user_info = client.fetchUserInfo(user_id)
            reply_message = Message(f"ID người dùng : {user_id}")
            
            image_dir = "image/gai"
            image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            random_image = random.choice(image_files)
            image_path = os.path.join(image_dir, random_image)
            
            client.sendLocalImage(imagePath=image_path, thread_id=thread_id, thread_type=thread_type, message=reply_message)
        except ZaloAPIException as e:
            reply_message = Message(f"Lỗi khi lấy thông tin người dùng: {e}")
            client.replyMessage(reply_message, message_object, thread_id, thread_type)



                    
    def loader(self):
        plugins = os.listdir("commands")
        for plugin in plugins:
            try:
                if(not plugin.endswith(".py")): continue

                plugin = importlib.import_module(f"commands.{plugin[:-3]}")
                self.commands[plugin.config["name"]] = plugin.run
            except Exception as e:
                print(f"Lỗi Commands: {plugin.config['name']}: {e}")
