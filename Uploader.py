from telegram.ext import *
from telegram import *
from telegram.error import *
import logging
from CreateUniqueLink import gen
from LinkDatabase import *
import datetime
import math
import asyncio
import pytz

# #when (and why) things don't work as expected
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

token = 'Your_Token_Key'
bot=Bot(token)
bot_admin = 123456789
bot_username = 'Bot_Username'

def date_and_time() -> tuple:
    '''
    date: YY:mm:dd\n
    time: HH:MM:SS
    '''
    #iran standard time
    ist = pytz.timezone('Asia/Tehran')
    datetime_ist = datetime.datetime.now(ist)
    date = datetime_ist.strftime(r'%Y/%m/%d')
    time_ir = datetime_ist.strftime('%H:%M:%S')
    return date,time_ir

def all_admins() -> list:
    n = total_admins()
    if n > 0:
        admins_list = database_admins()
        database_admin_s = []
        for i in range(n):
            database_admin_s.append(admins_list[i][0])
        database_admin_s.append(bot_admin)
        return database_admin_s
    else:
        return [bot_admin]

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def membership(update:Update , context:CallbackContext):
    n = total_channels()
    allowed_users = ['creator','owner','administrator','member','CREATOR','OWNER','ADMINISTRATOR','MEMBER']
    if n > 0:
        for i in range(n):
            channel_ID = all_channels()[i][1]
            info = context.bot.get_chat_member(chat_id = channel_ID , user_id = update.effective_chat.id)
            status = info['status']
            if status not in allowed_users:
                return False
        return True
    else:
        return True

def add_to_database(file_id,media_type,admin,date_time,size,row,password='این فایل بدون رمز عبور است ... !',caption=None) -> tuple:
    'link , link_for_send'
    while True:
        link = gen(12)
        link_for_send = 'https://t.me/{username}?start={link}'.format(username=bot_username,link=link)
        try:
            add_file(link,file_id,media_type,admin,date_time,size,row,password, caption)
            break
        except:
            continue
    return link , link_for_send

management_keyboard = [
                [KeyboardButton('👤 امار ربات')],
                [KeyboardButton('📪 ارسال به همه'),KeyboardButton('📪 فوروارد به همه')],
                [KeyboardButton('📥 اضافه کردن کانال'),KeyboardButton('📤 حذف کردن کانال')],
                [KeyboardButton('➕ افزودن ادمین'),KeyboardButton('➖ حذف ادمین')],
                [KeyboardButton('🔙')]
            ]  


def send_file(link , chat_id , correct_password_id , message_id, update: Update , context : CallbackContext):
    if membership(update ,context):
        try:
            #checks if file in database
            file = file_details(link)
            file_password = file[6]
            encryptedFile(chat_id , link)
            
            if file_password == 'این فایل بدون رمز عبور است ... !' or getInfo(chat_id)[2] == 'T':
                update_file_download(link)
                file = file_details(link)
                file_id = file[0]
                file_caption = file[2]
                file_type = file[3]
                file_download = file[1]
                try:
                    context.bot.delete_message(chat_id,correct_password_id)
                except:
                    pass

                msg = '''📥 تعداد دانلود :<code>{download}</code>\n{caption}'''.format(
                download = file_download,
                caption = file_caption
            )
                if file_type != 'sticker':
                    if file_type == 'video':
                        context.bot.send_video(chat_id = chat_id , video=file_id,caption=msg,parse_mode=ParseMode.HTML)
                    elif file_type == 'photo':
                        context.bot.send_photo(chat_id = chat_id , photo=file_id,caption=msg,parse_mode=ParseMode.HTML)
                    elif file_type == 'document':
                        context.bot.send_document(chat_id = chat_id , document=file_id,caption=msg,parse_mode=ParseMode.HTML)
                    elif file_type == 'animation':
                        context.bot.send_animation(chat_id = chat_id , animation=file_id,caption=msg,parse_mode=ParseMode.HTML)
                    elif file_type == 'audio':
                        context.bot.send_audio(chat_id = chat_id , audio=file_id,caption=msg,parse_mode=ParseMode.HTML)
                    elif file_type == 'voice':
                        context.bot.send_voice(chat_id = chat_id , voice=file_id,caption=msg,parse_mode=ParseMode.HTML)
                else:
                    stk = context.bot.send_sticker(chat_id = chat_id , sticker=file_id)
                    context.bot.send_message(chat_id = chat_id , text =msg,parse_mode=ParseMode.HTML,reply_to_message_id=stk.message_id)
                update_member_download(chat_id)
                resetAll(chat_id)
            else:
                keyboard = [[KeyboardButton('🔙 بازگشت')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
                msg = '▪️ لطفا رمز فایل را ارسال کنید تا فایل برای شما ارسال شود :'
                context.bot.send_message(chat_id = chat_id, text= msg , reply_markup= reply_markup , reply_to_message_id= message_id)
                enterPassword(chat_id)
                isActiveCondition(chat_id)

        except:
            pass
    #else if not member of channels
    else:
        n = total_channels()
        key = []
        all_channel = all_channels()
        channel_num = list(range(1,n+1))
        for i in range(n):
            key.append(
                [InlineKeyboardButton(text = '🔒 کانال {}'.format(channel_num[i]), url = all_channel[i][2])]
            )
        key.append([InlineKeyboardButton(text = 'عضو شدم ✅' , callback_data= 'join')])
        msg = '''💡 ابتدا باید وارد کانال زیر شوید 

☑️ بعد از عضو شدن در کانال ها دکمه { عضو شدم ✅ } را بزنید .'''
        reply_markup = InlineKeyboardMarkup(key)
        context.bot.send_message(chat_id = chat_id , text = msg , reply_markup= reply_markup , reply_to_message_id= message_id)

def text(update:Update , context: CallbackContext):
    admins = all_admins()
    isMember = True
    try:
        chat_id = update.effective_chat.id
        message_text = update.message.text
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
    except:
        try:
            
            chat = update.channel_post
            if chat != None:
                chat_id = chat.chat_id
            channel_name = update.effective_chat.title
            message_text = update.channel_post.text
            message_id = update.channel_post.message_id
            isMember = False
        except:
            pass

    #for adding channel
    #if isMember --> else

    global management_keyboard

    if isMember:
        try:
            add_member(chat_id , chat_name)
        except:
            pass

        if chat_id  in admins:
            main_keyboard = [
                    [KeyboardButton('📂 تاریخچه اپلود'),KeyboardButton('🎫 حساب کاربری')],
                    [KeyboardButton('🔐 تنظیم پسورد'),KeyboardButton('🗑 حذف فایل')],
                    [KeyboardButton('👤 مدیریت'),KeyboardButton('🗂 کد پیگیری فایل')]
                    ]

            management_keyboard = [
                [KeyboardButton('👤 امار ربات')],
                [KeyboardButton('📪 ارسال به همه'),KeyboardButton('📪 فوروارد به همه')],
                [KeyboardButton('📥 اضافه کردن کانال'),KeyboardButton('📤 حذف کردن کانال')],
                [KeyboardButton('➕ افزودن ادمین'),KeyboardButton('➖ حذف ادمین')],
                [KeyboardButton('🔙')]
            ]
        else:
            main_keyboard =[[KeyboardButton('🎫 حساب کاربری')]]

        if message_text in ['/start','🔙']:
                
            msg = '''👤 سلام {}
🤖 به ربات آپلودر ما خوش آمدی !
'''.format(update.effective_chat.first_name)

            reply_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
            context.bot.send_message(chat_id,text=msg,reply_markup=reply_markup,reply_to_message_id = message_id)
            resetAll(chat_id)
        
        elif message_text == '🔙 بازگشت':
            
            resetAll(chat_id)
            msg='''🌼 به منوی اصلی ربات برگشتیم 

🎉 برای استفاده از ربات از دکمه های زیر استفاده کنید'''
            reply_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
            update.message.reply_text(text=msg,reply_markup=reply_markup,reply_to_message_id=message_id)

        elif message_text == 'برگشت 🔙':
            resetAll(chat_id)
            reply_markup = ReplyKeyboardMarkup(management_keyboard , resize_keyboard=True)
            msg = '▪️ به منوی مدیریت بازگشتید :'
            update.message.reply_text(text=msg , reply_markup =reply_markup , reply_to_message_id= message_id)
        #enterPassword   
        elif getInfo(chat_id)[1] == 'T':

            if message_text == file_details(getInfo(chat_id)[3])[6]:
                isCorrectPassword(chat_id)
                correctPasswordId(chat_id ,message_id)
            else:
                msg = 'لطفا پسورد صحیح را وارد کنید:'
                update.message.reply_text(text = msg , reply_to_message_id=message_id)

        #Check Membership
        start = '/start' in message_text
        get = '/get' in message_text

        if start or get or getInfo(chat_id)[2] == 'T':
            if start:
                link_list = message_text.split(' ')
                if len(link_list) > 1 :
                    link = link_list[1]
                    savedLink(chat_id , link)
                    replyMessageId(chat_id , message_id)
                    correct_password_id = getInfo(chat_id)[5]
                    send_file(link , chat_id , correct_password_id , message_id, update, context)
            elif get:
                link_list = message_text.split('_')
                if len(link_list) >1 :
                    link = link_list[1]
                    savedLink(chat_id , link)
                    correct_password_id = getInfo(chat_id)[5]
                    send_file(link , chat_id , correct_password_id , message_id, update, context)                    

            elif getInfo(chat_id)[2] == 'T':
                link = getInfo(chat_id)[3]
                savedLink(chat_id , link)
                correct_password_id = getInfo(chat_id)[5]
                send_file(link , chat_id , correct_password_id , message_id, update, context)
            

        if chat_id in admins:
            def Alert():
                msg = '''▪️ خطا , این فایل در دیتابیس موجود نمیباشد یا فایل مال شخص دیگری میباشد و  شما اجازه دسترسی به این فایل را ندارید ... !'''
                update.message.reply_text(text=msg,reply_to_message_id=message_id)
            #deleteFile
            if getInfo(chat_id)[7] == 'T':
                try:
                    admin = file_details(message_text)[4]
                    if chat_id == admin or chat_id == bot_admin:

                        msg = '✔️ فایل با موفقیت حذف شد ... !'
                        reply_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
                        delete_file(message_text)
                        decrease_member_upload(admin)
                        update.message.reply_text(text=msg,reply_markup=reply_markup,reply_to_message_id=message_id)
                        resetAll(chat_id)
                    else:
                        Alert()
                except:
                    Alert()
            #trackingFile
            elif getInfo(chat_id)[11] == 'T':
                try:
                    file = file_details(message_text)
                    file_admin = file[4]
                    if chat_id == file_admin or chat_id == bot_admin:
                        file_ID = file[8]
                        size = file[7]
                        media_type = file[3]
                        password = file[6]
                        caption = file[2]
                        date_time = file[5]
                        link_for_share = 'https://t.me/{bot_username}?start={ID}'.format(bot_username = bot_username , ID = file_ID)
                        msg = '''▪️ شناسه فایل شما : <code>{ID}</code>

➖ بقیه اطلاعات فایل شما : 

💾  حجم فایل : {size}
▪️ نوع فایل : {media_type}
🔐 رمز فایل : <code>{password}</code>
📝 توضیحات ویدیو : 
<code>{caption}</code>
🕓 تاریخ و زمان اپلود : {date_time}
لینک شتراک گذاری فایل:

📥 {share}'''.format(ID = file_ID,
        size = size ,
        media_type = media_type ,
        password = password,
        caption = caption ,
        date_time = date_time,
        share = link_for_share)
                
                        reply_markup = ReplyKeyboardMarkup(main_keyboard , resize_keyboard=True)
                        update.message.reply_text(text = msg , reply_to_message_id=message_id , parse_mode=ParseMode.HTML,reply_markup=reply_markup)
                        resetAll(chat_id)
                    else:
                        Alert()
                except:
                    Alert()
            #newPassword
            elif getInfo(chat_id)[9] == 'T':
                passwordFile = getInfo(chat_id)[10]
                add_password(passwordFile , message_text)
                msg_2 = '✔️ فایل شما با موفقیت قفل شد ... !'
                reply_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
                update.message.reply_text(text = msg_2 , reply_to_message_id= message_id , reply_markup= reply_markup)
                resetAll(chat_id)

            #setPassword
            elif getInfo(chat_id)[8] == 'T':
                try:
                    admin = file_details(message_text)[4]
                    if chat_id == admin or chat_id == bot_admin:
                        newPassword(chat_id)
                        isActiveCondition(chat_id)
                        setPasswordFile(chat_id , message_text)
                        msg_1 = '▪️لطفا پسورد دلخواه رو بفرستید تا فایل شما قفل شود :'
                        update.message.reply_text(text = msg_1 , reply_to_message_id= message_id)
                        
                    else:
                        Alert()
                except:
                    Alert()

            #forwardToAll
            elif getInfo(chat_id)[12] == 'T':
                resetAll(chat_id)
                asyncio.run(forward_all(message_id,update,context))
            
            #sendToAll
            elif getInfo(chat_id)[13] == 'T':
                resetAll(chat_id)
                asyncio.run(send_all(message_id , update, context))

            #addChannel
            elif getInfo(chat_id)[16] != 'F':
                msg = '❗️ لطفاً راهنمای افزودن کانال را دوباره با دقت مطالعه کنید.'
                update.message.reply_text(text = msg , reply_to_message_id= message_id)


            #addAdmin
            elif getInfo(chat_id)[14] == 'T':
                try:
                    msg = '''✅ شما به لیست ادمین ها اضافه شدید
لطفا /start رو بزنید'''
                    context.bot.send_message(chat_id = message_text , text = msg)
                    admin_id = int(message_text)
                    add_admin(admin_id)
                    msg2 = 'کاربر با موفقیت به لیست ادمین ها اضافه شد ✅'
                    reply_markup = ReplyKeyboardMarkup(management_keyboard,resize_keyboard=True)
                    update.message.reply_text(text = msg2 , reply_markup= reply_markup ,reply_to_message_id= message_id)
                    resetAll(chat_id)
                except:
                    msg = '▪️خطا : آیدی عددی وارد شده صحیح نمی باشد یا ربات توسط کاربر مسدود شده است ...'
                    update.message.reply_text(text = msg , reply_to_message_id= message_id)

            #admin buttons not works until entering correct password
            elif getInfo(chat_id)[1] == 'T':
                pass

            elif message_text == '📂 تاریخچه اپلود':
                upload = member_down_up(chat_id)[1]
                all_file = total_files()

                def tarikhcheh(n:int , files: list , first_msg : str , upload: int):
                    line = '➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖'
                    def history(start,end):
                        'Maximum can be showed is 100'
                        msg = '''
❗️توجه داشته باشید حداکثر 100 فایل اخیر قابل نمایش است...
📂 تاریخچه اپلود های شما :
📍 {first_msg} : {upload}
➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'''.format(first_msg = first_msg ,upload = upload)
                        for i in range(start,end):
                            blank = '{num}.📥: /get_{get}\n💾 حجم فایل: {size}\n▪️ نوع فایل: {file_type}\n 🔐 رمز فایل: <code>{password}</code>\n🕓 تاریخ و زمان اپلود: {date_time}\n{line}\n'.format(
                                    num = i+1,
                                    get = files[i][0],
                                    size = files[i][8],
                                    file_type = files[i][4],
                                    password = files[i][7],
                                    date_time = files[i][6],
                                    line = line
                                )
                            msg += blank
                        update.message.reply_text(text = msg, parse_mode=ParseMode.HTML, reply_to_message_id=message_id)
                    
                    div = n // 20
                    remain = n - div *20

                    for j in range(div):
                        history(j*20 , (j+1)*20)
                    if remain > 0 :
                        #start
                        s = div * 20
                        #end
                        e = s + remain
                        history(s , e)

                if chat_id == bot_admin:
                    
                    if all_file > 0:
                        files = all_files()
                        n = len(files)
                        f_msg = 'تعداد کل فایل های دیتابیس'
                        tarikhcheh(n ,files,f_msg ,all_file)
                    else:
                        msg = '❗️ هیچ فایلی در دیتابیس موجود نمی باشد.'
                        update.message.reply_text(text = msg , reply_to_message_id= message_id)   
                        
                else:
                    if upload > 0:

                        files = admin_all_files(chat_id)
                        n = len(files)
                        f_msg = 'تعداد فایل های اپلود شده ی شما'
                        tarikhcheh(n , files , f_msg , upload)
                    else:
                        msg = '❗️ تاریخچه آپلود شما خالی است.'
                        update.message.reply_text(text = msg , reply_to_message_id= message_id)




            elif message_text == '👤 امار ربات':
                members = total_members()
                adminha = len(all_admins())
                files = total_files()
                channels = total_channels()
                date = date_and_time()[0]
                time = date_and_time()[1]

                msg = '''🤖 امار شما در ساعت <code>{time}</code> و تاریخ <code>{date}</code> به این صورت میباشد :

👥 تعداد اعضا : <code>{members}</code> 
🗂 تعداد فایل ها : <code>{files}</code>
👨🏻‍💻 تعداد ادمین ها : <code>{admins}</code>
📢 تعداد کانال ها :<code>{channels}</code>'''.format(
                members = members,
                files = files,
                admins = adminha,
                channels = channels,
                date = date,
                time = time)

                update.message.reply_text(text = msg , parse_mode=ParseMode.HTML,reply_to_message_id=message_id)



            elif message_text == '👤 مدیریت':
                
                msg='👤 به منوی مدیریت ربات خود خوش امدید'

                reply_markup = ReplyKeyboardMarkup(management_keyboard)
                context.bot.send_message(chat_id,text = msg, reply_markup=reply_markup,reply_to_message_id = message_id)

            elif message_text == '🎫 حساب کاربری':
                
                photoes = bot.get_user_profile_photos(chat_id)
                photo_to_send = photoes.photos[0][-1]
                uploaded = member_down_up(chat_id)[1]
                downloaded = member_down_up(chat_id)[0]
                inline_keyboard = [
                    [InlineKeyboardButton('📤 تعداد آپـلود',callback_data='u'),InlineKeyboardButton('{}'.format(uploaded),callback_data='u')],
                    [InlineKeyboardButton('📥 تعداد دانلود',callback_data='u'),InlineKeyboardButton('{}'.format(downloaded),callback_data='u')]
                ]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                name = update.effective_chat.first_name
                username = update.effective_chat.username
                msg = '''
    💭 حساب کاربری شما در ربات ما :

👤 نام اکانت شما : <code>{name}</code>
🌟 یوزنیم اکانت شما : <code>{username}</code>
🆔 ایدی عددی شما : <code>{chat_id}</code>'''.format(name = name, username = username,chat_id = chat_id)
                update.message.reply_photo(photo = photo_to_send.file_id, caption=msg,reply_markup=reply_markup,parse_mode=ParseMode.HTML)

            elif message_text == '🗑 حذف فایل':
                
                keyboard = [[KeyboardButton('🔙 بازگشت')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
                msg = '''▪️لطفا شناسه فایل خود را ارسال کنید :
📍 توجه کنید که بعد از فرستادن شناسه , فایل همان لحظه پاک میشود پس لطفا الکی شناسه فایلتون رو ارسال نکنید و فقط در صورت نیاز استفاده بکنید از این بخش ... !'''
                update.message.reply_text(text = msg , reply_markup=reply_markup, reply_to_message_id=message_id)
                deleteFile(chat_id)
                isActiveCondition(chat_id)
            
            elif message_text == '🔐 تنظیم پسورد':
                setPassword(chat_id)
                isActiveCondition(chat_id)
                keyboard = [[KeyboardButton('🔙 بازگشت')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
                msg = '''▪️ لطفا شناسه فایل خود را ارسال کنید :'''
                update.message.reply_text(text = msg , reply_markup=reply_markup, reply_to_message_id=message_id)
            
            elif message_text == '🗂 کد پیگیری فایل':
                msg = '▪️لطفا شناسه فایل خود را ارسال کنید :'
                keyboard = [[KeyboardButton('🔙 بازگشت')]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True)
                update.message.reply_text(text = msg , reply_markup=reply_markup , reply_to_message_id= message_id)
                trackingFile(chat_id)
                isActiveCondition(chat_id)
            
            elif message_text == '📪 فوروارد به همه':
                forwardToAll(chat_id)
                isActiveCondition(chat_id)
                msg = '▪️ لطفا پیام خود را ارسال کنید :'
                keyboard = [[KeyboardButton('برگشت 🔙')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard= True)
                update.message.reply_text(text = msg , reply_markup= reply_markup , reply_to_message_id= message_id)

            elif message_text == '📪 ارسال به همه':
                sendToAll(chat_id)
                isActiveCondition(chat_id)
                msg = '▪️ لطفا پیام خود را ارسال کنید :'
                keyboard = [[KeyboardButton('برگشت 🔙')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard= True)
                update.message.reply_text(text = msg , reply_markup= reply_markup , reply_to_message_id= message_id)
            
            elif message_text == '📥 اضافه کردن کانال':
                command = gen(13)
                #Important Format String
                addChannel(chat_id , '/channel_{}'.format(command))
                msg = '''🔘 برای افزودن کانال میتوانید از روش زیر استفاده کنید.

🔹 نحوه اضافه کردن کانال :
1️⃣ ربات را در کانال مورد نظر ادمین کنید
2️⃣ دستور زیر را کپی و در کانال ارسال کنید
-> <code>/channel_{}</code>
☑️ اگر پیام شما حذف شد به معنای اضافه شدن کانال شما است.'''.format(command)

                keyboard = [[KeyboardButton('برگشت 🔙')]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard= True)
                update.message.reply_text(text = msg , reply_markup= reply_markup ,
                reply_to_message_id= message_id , parse_mode=ParseMode.HTML)

            elif message_text == '📤 حذف کردن کانال':
                msg = '☑️ برای حذف هر کدام از کانال های زیر روی همان کانال کلیک کنید'
                n = total_channels()
                channels = all_channels()
                if n > 0:
                    keyboard = []
                    for i in range(n):
                        channel_name = channels[i][0]
                        channel_id = channels[i][1]
                        channel_url = channels[i][2]
                        keyboard.append([InlineKeyboardButton(text =channel_name,url=channel_url),
                        InlineKeyboardButton(text = '🗑 حذف', callback_data= channel_id)])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(text = msg , reply_markup= reply_markup , reply_to_message_id= message_id)
                else:
                    msg = '❗️ هیچ کانالی در دیتابیس ذخیره نشده است .'
                    update.message.reply_text(text = msg , reply_to_message_id= message_id)

            elif message_text == '➕ افزودن ادمین':
                if chat_id == bot_admin:
                    addAdmin(chat_id)
                    isActiveCondition(chat_id)
                    msg = '▪️لطفاً ایدی عددی کاربری که میخواهید به عنوان ادمین اضافه کنید بفرستید:'
                    keyboard = [[KeyboardButton('برگشت 🔙')]]
                    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard= True)
                    update.message.reply_text(text = msg ,reply_markup=reply_markup ,reply_to_message_id= message_text)

                else:
                    msg = '❌ فقط ادمین اصلی میتواند ادمین جدیدی را به ادمین های ربات اضافه کند'
                    update.message.reply_text(text = msg , reply_to_message_id= message_id)

            elif message_text == '➖ حذف ادمین':
                if chat_id == bot_admin:
                    n = total_admins()
                    if n > 0 :
                        msg = '☑️ برای حذف هر کدام از ادمین های زیر روی همان ادمین کلیک کنید'
                        adminha = database_admins()
                        keyboard = []
                        for i in range(n):
                            admin_chat_id = adminha[i][0]
                            admin_name = adminha[i][1]
                            keyboard.append([InlineKeyboardButton(text = admin_name ,callback_data='a'),
                            InlineKeyboardButton(text = '🗑 حذف' , callback_data= admin_chat_id)
                            ])

                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_text(text = msg , reply_markup= reply_markup , reply_to_message_id= message_id)
                    else:
                        msg = '❗️ لیست ادمین ها خالی است .'
                        update.message.reply_text(text = msg , reply_to_message_id= message_id)

                else:
                    msg = '❌ تنها ادمین اصلی میتواند ادمین ها را حذف کند.'
                    update.message.reply_text(text = msg , reply_to_message_id= message_id)

        else:

            if message_text == '🎫 حساب کاربری':
                photoes = bot.get_user_profile_photos(chat_id)
                photo_to_send = photoes.photos[0][-1]
                downloaded = member_down_up(chat_id)[0]
                uploaded = member_down_up(chat_id)[1]
                inline_keyboard = [
                    [InlineKeyboardButton('📤 تعداد آپـلود',callback_data='u'),InlineKeyboardButton('{}'.format(uploaded),callback_data='u')],
                    [InlineKeyboardButton('📥 تعداد دانلود',callback_data='u'),InlineKeyboardButton('{}'.format(downloaded),callback_data='u')]
                ]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                name = update.effective_chat.first_name
                username = update.effective_chat.username
                msg = '''
💭 حساب کاربری شما در ربات ما :

👤 نام اکانت شما : <code>{name}</code>
🌟 یوزنیم اکانت شما : <code>{username}</code>
🆔 ایدی عددی شما : <code>{chat_id}</code>'''.format(name = name, username = username,chat_id = chat_id)
                update.message.reply_photo(photo = photo_to_send.file_id, caption=msg,reply_markup=reply_markup,parse_mode=ParseMode.HTML)

    else:
        cmd = checkCommand(message_text)
        if cmd != None:
            invite_link = context.bot.create_chat_invite_link(chat_id).invite_link
            try:
                add_channel(channel_name , chat_id , invite_link)
                context.bot.delete_message(chat_id , message_id)
                msg = '''✅ کانال شما با مشخصات زیر با موفقیت در دیتابیس ذخیره شد:

🔹 آیدی عددی کانال: <code>{ID}</code>
🔸 اسم کانال : <code>{name}</code>
🔹 لینک کانال:
{invite_link}'''.format(ID = chat_id , name = channel_name , invite_link = invite_link)
                context.bot.send_message(chat_id = cmd[0] ,
                    text = msg , parse_mode=ParseMode.HTML , disable_web_page_preview = True,
                    reply_markup = ReplyKeyboardMarkup(management_keyboard, resize_keyboard=True))
            except:
                pass
            resetAll(cmd[0])

async def forward_all(message_id ,update:Update , context:CallbackContext):
    'message_id = id of message to forward'
    sender_id = update.effective_chat.id
    msg = '''پیام شما در حال فروارد شدن میباشد:\n({}%)'''.format(0)
    #reply_markup = ReplyKeyboardMarkup(management_keyboard,resize_keyboard=True)
    alert=update.message.reply_text(text = msg , reply_to_message_id= message_id) #, reply_markup= reply_markup)
    alert_id = alert.message_id
    members = all_members()
    n = total_members() - 1
    sent = 0
    count = 0
    for id_tuple in members:
        chat_id = id_tuple[0]
        if chat_id != sender_id:
            try:

                sent += 1
                count += 1
                if count == 1:
                    count = 1
                    await asyncio.sleep(5)
                percent = '{:.2f}'.format((sent/n)*100)
                new_text = '''پیام شما در حال فروارد شدن میباشد:\n({}%)'''.format(percent)
                context.bot.edit_message_text(text = new_text,chat_id = sender_id, message_id = alert_id)
                context.bot.forward_message(chat_id = chat_id , from_chat_id = sender_id , message_id = message_id)
            except Unauthorized:
                continue

            except RetryAfter:
                context.bot.send_message(chat_id = 1304484370 , text = 'RetryAfter Exception')



    finish_alert = 'پیام شما با موفقیت فوروارد شد ...! ✅'
    reply_markup = ReplyKeyboardMarkup(management_keyboard , resize_keyboard= True)
    update.message.reply_text(text = finish_alert , reply_to_message_id= alert_id ,reply_markup=reply_markup)


async def send_all(message_id , update:Update , context:CallbackContext):
    'message_id = id of message to send'
    sender_id = update.effective_chat.id
    msg = '''پیام شما در حال ارسال شدن میباشد:\n({}%)'''.format(0)
   
    alert=update.message.reply_text(text = msg , reply_to_message_id= message_id)
    alert_id = alert.message_id
    members = all_members()
    n = total_members() - 1
    sent = 0
    count = 1
    for id_tuple in members:
        chat_id = id_tuple[0]
        if chat_id != sender_id:
            try:
                sent += 1
                count += 1
                if count == 20:
                    count = 1
                    await asyncio.sleep(1)
                percent = '{:.2f}'.format((sent/n)*100)
                new_text = '''پیام شما در حال ارسال شدن میباشد:\n({}%)'''.format(percent)
                context.bot.edit_message_text(text = new_text,chat_id = sender_id, message_id = alert_id)
                context.bot.copy_message(chat_id = chat_id , from_chat_id = sender_id , message_id = message_id)
                
            except Unauthorized:
                continue

            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)

    finish_alert = 'پیام شما با موفقیت ارسال شد ...! ✅'
    reply_markup = ReplyKeyboardMarkup(management_keyboard , resize_keyboard= True)
    update.message.reply_text(text = finish_alert , reply_to_message_id= alert_id ,reply_markup=reply_markup)

def errors(msg_id , update:Update , context:CallbackContext):
    chat_id = update.effective_chat.id
    incorrect_id = '''▪️خطا , این فایل در دیتابیس موجود نمیباشد یا فایل مال شخص دیگری میباشد و  شما اجازه دسترسی به این فایل را ندارید ... !'''

    #forwardToAll
    if getInfo(chat_id)[12] == 'T':
        resetAll(chat_id)
        asyncio.run(forward_all(msg_id , update , context))
    #sendToAll
    elif getInfo(chat_id)[13] == 'T':
        resetAll(chat_id)
        asyncio.run(send_all(msg_id , update , context))
    #deleteFile
    elif getInfo(chat_id)[7] == 'T':
        update.message.reply_text(text=incorrect_id ,reply_to_message_id=msg_id)
    #newPassword
    elif getInfo(chat_id)[9] == 'T':
        alert = '❌ پسورد باید شمامل حروف و کاراکتر باشد...!'
        update.message.reply_text(text = alert , reply_to_message_id= msg_id)
    #setPassword
    elif getInfo(chat_id)[8] == 'T':
        update.message.reply_text(text = incorrect_id , reply_to_message_id= msg_id)
    #enterPassword
    elif getInfo(chat_id)[1] == 'T':
        alert = 'لطفا پسورد صحیح را وارد کنید:'
        update.message.reply_text(text = alert , reply_to_message_id= msg_id)
    #trackingFile
    elif getInfo(chat_id)[11] == 'T':
        update.message.reply_text(text = incorrect_id , reply_to_message_id= msg_id)
    #addChannel
    elif getInfo(chat_id)[16] != 'F':
        alert = '❗️ لطفاً راهنمای افزودن کانال را دوباره با دقت مطالعه کنید.'
        update.message.reply_text(text = alert , reply_to_message_id= msg_id)
    #addAdmin
    elif getInfo(chat_id)[15] == 'T':
        alert = '❌ آیدی عددی وارد شده صحیح نمی باشد ...!'
        update.message.reply_text(text = alert , reply_to_message_id= msg_id)

def video(update:Update , context: CallbackContext):
    admins = all_admins()
    #try and except: checks if message is for member or channel
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.video.file_id
                file_size = update.message.video.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files()+1
                file = add_to_database(file_id,'video',chat_id,str(curr_datetime),converted_size , row ,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])

                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_video(video= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)

    except:
        pass

def photo(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.photo[-1].file_id
                file_size = update.message.photo[-1].file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'photo',chat_id,str(curr_datetime),converted_size , row ,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_photo(photo= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)
    except:
        pass

def document(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.document.file_id
                file_size = update.message.document.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'document',chat_id,str(curr_datetime),converted_size,row,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size , row )
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_document(document= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)
        
    except:
        pass

def animation(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            admins = all_admins()
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.animation.file_id
                file_size = update.message.animation.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'animation',chat_id,str(curr_datetime),converted_size,row,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_animation(animation= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)

    except:
        pass

def audio_func(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.audio.file_id
                file_size = update.message.audio.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'audio',chat_id,str(curr_datetime),converted_size,row,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_audio(audio= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)
        
    except:
        pass

def voice(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.voice.file_id
                file_size = update.message.voice.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'voice',chat_id,str(curr_datetime),converted_size,row,caption=caption)
                l1 = '✔️ فایل شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                update.message.reply_voice(voice= file_id ,caption=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)
       
    except:
        pass

def sticker(update:Update , context: CallbackContext):
    admins = all_admins()
    try:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        chat_name = update.effective_chat.full_name
        if getInfo(chat_id)[15] == 'T':
            errors(message_id , update , context)
        else:
            if chat_id in admins:
                try:
                    add_member(chat_id , chat_name)
                except:
                    pass
                update_member_upload(chat_id)
                file_id = update.message.sticker.file_id
                file_size = update.message.sticker.file_size
                converted_size = convert_size(file_size)
                curr_datetime = date_and_time()[0] +' | '+ date_and_time()[1]
                caption = update.message.caption
                if caption == None:
                    caption = 'توضیحاتی وجود ندارد ...'
                row = total_files() + 1
                file = add_to_database(file_id,'sticker',chat_id,str(curr_datetime),converted_size,row,caption=caption)
                l1 = '✔️ استیکر شما با موفقیت داخل دیتابیس ذخیره شده ... !\n'
                l2 ='▪️ شناسه فایل شما : <code>{}</code>\n\n'.format(file[0])
                l3 = '➖ بقیه اطلاعات عکس شما : \n\n'
                l4 = '💾  حجم فایل : {}\n'.format(converted_size)
                l5 = '📝 توضیحات فایل :\n<code>{}</code>\n'.format(caption)
                l6 = 'لینک اشتراک گذاری فایل:\n'
                l7 = '📥{}'.format(file[1])
                
                send_caption = '{l1}{l2}{l3}{l4}{l5}{l6}{l7}'.format(
                    l1 = l1,
                    l2 = l2,
                    l3 = l3,
                    l4 = l4,
                    l5 = l5,
                    l6 = l6,
                    l7 = l7
                )

                message=update.message.reply_sticker(sticker=file_id)
                message_id = message.message_id
                update.message.reply_text(text=send_caption,
                parse_mode=ParseMode.HTML,reply_to_message_id=message_id)
       
    except:
        pass

def button(update:Update , context: CallbackContext):
    query = update.callback_query
    msg_id = query.message.message_id
    usr_id = query.message.chat.id

    n = total_channels()
    IDs = []
    if n > 0:
        channels = all_channels()
        
        for i in range(n):
            IDs.append(channels[i][1])

    k = total_admins()
    user_IDs = []
    if k > 0 :
        admins = database_admins()
        
        for j in range(k):
            user_IDs.append('{}'.format(admins[j][0]))

    if query.data == 'join':
        if not membership(update,context):
            alert ='❌ شما عضو کانال های ربات نیستید.'
            context.bot.answer_callback_query(callback_query_id = query.id , text=alert,show_alert= True)
        else:
            try:
                context.bot.delete_message(usr_id,msg_id)
                correct_password_id = getInfo(usr_id)[5]
                saved_link = getInfo(usr_id)[4]
                reply_message_id = getInfo(usr_id)[6]
                send_file(saved_link , usr_id , correct_password_id , reply_message_id , update , context)
            except:
                pass
  
    if query.data in IDs:
        try:
            delete_channel(query.data)
            msg = 'کانال با موفقیت حذف شد ✅'
            context.bot.answer_callback_query(callback_query_id = query.id , text = msg)
            context.bot.delete_message(usr_id , msg_id)
        except:
            pass

    if query.data in user_IDs:
        chat_id = int(query.data)
        try:
            delete_admin(chat_id)
            msg = 'ادمین با موفقیت حذف شد ✅'
            context.bot.answer_callback_query(callback_query_id = query.id , text = msg)
            context.bot.delete_message(usr_id , msg_id)
        except:
            pass
            
    else:
        query.answer()

def main():
    updater = Updater(token = token , use_context = True)
    dp = updater.dispatcher

    vid = MessageHandler(Filters.video ,callback=video)
    dp.add_handler(vid)

    pic = MessageHandler(Filters.photo ,callback=photo)
    dp.add_handler(pic)

    ani = MessageHandler(Filters.animation ,callback=animation)
    dp.add_handler(ani)

    doc = MessageHandler(Filters.document ,callback=document)
    dp.add_handler(doc)

    #audio --> a
    a = MessageHandler(Filters.audio ,callback=audio_func)
    dp.add_handler(a)

    #voice --> v
    v = MessageHandler(Filters.voice ,callback=voice)
    dp.add_handler(v)

    #sticker --> stk
    stk = MessageHandler(Filters.sticker ,callback=sticker)
    dp.add_handler(stk)

    txt = MessageHandler(Filters.text ,callback=text , run_async= True)
    dp.add_handler(txt)

    dp.add_handler(CallbackQueryHandler(callback= button))

    # channel_post = MessageHandler(filters=Filters.update, callback=channel)
    # dp.add_handler(channel_post)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    create_tables()
    main()