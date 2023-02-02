#unique links database
import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            link TEXT UNIQUE,
            file_id TEXT,
            download_num INTEGER,
            caption TEXT,
            media_type TEXT,
            admin INTEGER,
            date_time TEXT,
            password TEXT,
            size TEXT,
            row INTEGER)''')

    with conn:
        c.execute('''CREATE TABLE IF NOT EXISTS members (
            chat_id INTEGER UNIQUE,
            status TEXT,
            upload_num INTEGER,
            download_num INTEGER,
            name TEXT,
            enterPassword TEXT,
            isCorrectPassword TEXT,
            deleteFile TEXT,
            setPassword TEXT,
            newPassword TEXT,
            trackingFile TEXT,
            forwardToAll TEXT,
            sendToAll TEXT,
            addAdmin TEXT,
            addChannel TEXT,
            encryptedFile TEXT,
            savedLink TEXT,
            correctPasswordId TEXT,
            replyMessageId TEXT,
            setPasswordFile Text,
            isActiveCondition TEXT

        )''')

    with conn:
        c.execute('''CREATE TABLE IF NOT EXISTS channels (
            name TEXT,
            channel_id TEXT UNIQUE,
            channel_link TEXT
        )''')
    conn.close()

def add_file(link , file_id, type, admin, date_time , size, row , password = None , caption = None):
    'link is UNIQUE!'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)',(link, file_id, 0, caption, type, admin,date_time,password,size,row))
    conn.close()

def add_password(link,password):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE files SET password=(:pass) WHERE link=(:link)',{'pass':password,'link':link})
    conn.close()

def update_file_download(link):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE files SET download_num = download_num+1 WHERE link =(:link)',{'link':link})
    conn.close()

def total_files() -> int:
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM files''')
    total_file = c.fetchone()
    conn.close()
    return total_file[0]

def delete_file(link):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''DELETE FROM files WHERE link=(:link)''',{'link':link})
    conn.close()

def file_details(link) -> tuple:
    '''0\tfile_id\n
    1\tdownload_num\n
    2\tcaption\n
    3\ttype\n
    4\tadmin\n
    5\tdate_time\n
    6\tpassword\n
    7\tsize\n
    8\tlink ( ID )'''

    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT file_id,download_num,caption,media_type,admin,date_time,password,size,link FROM files WHERE link=(:link)',{'link':link})
    data=c.fetchone()
    conn.close()
    return data

def admin_all_files(admin) -> list:
    '''list [ tuple ( ... ) , . . . ]\n
    0\tlink\n
    1\tfile_id\n
    2\tdownload_num\n
    3\tcaption\n
    4\tmedia_type\n
    5\tadmin\n
    6\tdate_time\n
    7\tpassword\n
    8\tsize\n
    9\trow'''

    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files WHERE admin=(:admin) ORDER BY row DESC LIMIT 100' , {'admin':admin})
    file = c.fetchall()
    conn.close()
    return file

def all_files() -> list:
    '''list [ tuple ( ... ) , . . . ]\n
    0\tlink\n
    1\tfile_id\n
    2\tdownload_num\n
    3\tcaption\n
    4\tmedia_type\n
    5\tadmin\n
    6\tdate_time\n
    7\tpassword\n
    8\tsize\n
    9\trow'''

    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files ORDER BY row DESC LIMIT 100')
    file = c.fetchall()
    conn.close()
    return file

def add_member(chat_id , name):
    '''chat_id | status | upload | download | name\n
    status: \'member\' --> by default
    \n caht_id is UNIQUE!'''
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (chat_id,'member',0,0,name,'F','F','F','F','F','F','F','F','F','F','F','F','F','F','F','F'))
    conn.close()

def update_member_upload(chat_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''UPDATE members SET upload_num=upload_num+1 WHERE chat_id=(:id)''',{'id':chat_id})
    conn.close()

def decrease_member_upload(chat_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''UPDATE members SET upload_num=upload_num-1 WHERE chat_id=(:id)''',{'id':chat_id})
    conn.close()

def update_member_download(chat_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''UPDATE members SET download_num=download_num+1 WHERE chat_id=(:id)''',{'id':chat_id})
    conn.close()

def member_down_up(chat_id) -> tuple:
    'download number | upload number'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT download_num,upload_num FROM members WHERE chat_id=(:id)',{'id':chat_id})
    down_up = c.fetchone()
    conn.close()
    return down_up

def add_admin(chat_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''UPDATE members SET status="admin" WHERE chat_id=(:id)''',{'id':chat_id})
    conn.close()

def delete_admin(chat_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''UPDATE members SET status="member" WHERE chat_id=(:id)''',{'id':chat_id})
    conn.close()

def database_admins() -> list:
    '''[('chat_id_1','name_1'), ('chat_id_2','name_2'),...]'''
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('''SELECT chat_id,name FROM members WHERE status=(:status) ''',{'status':'admin'})
    admins = c.fetchall()
    conn.close()
    return admins

def total_admins() -> int:
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM members WHERE status=(:status)',{'status':'admin'})
    admins_num = c.fetchone()
    conn.close()
    return admins_num[0]

def total_members() -> int:
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM members')
    members_num = c.fetchone()
    conn.close()
    return members_num[0]

def all_members() -> list:
    "[ ( ' chat_id_1 ' , ) , ( ' chat_id_2 ' , ) , ... ]"
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM members')
    all_ids = c.fetchall()
    conn.close()
    return all_ids

def enterPassword(chat_id):
    'enterPassword = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET enterPassword = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def isCorrectPassword(chat_id):
    'isCorrectPassword = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET isCorrectPassword = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def encryptedFile(chat_id , ID):
    'encryptedFile = ID'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET encryptedFile = (:ID) WHERE chat_id = (:chat_id)',{'ID':ID ,'chat_id':chat_id})
    conn.close()

def savedLink(chat_id , ID):
    'savedLink = ID'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET savedLink = (:ID) WHERE chat_id = (:chat_id)',{'ID':ID ,'chat_id':chat_id})
    conn.close()

def setPasswordFile(chat_id , ID):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET setPasswordFile = (:ID) WHERE chat_id = (:chat_id)',{'ID':ID ,'chat_id':chat_id})
    conn.close()

def correctPasswordId(chat_id , message_id):
    'correctPasswordId = message_id'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET correctPasswordId = (:message_id) WHERE chat_id = (:chat_id)',{'message_id':message_id ,'chat_id':chat_id})
    conn.close()

def replyMessageId(chat_id , message_id):
    'replyMessageId = message_id'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET replyMessageId = (:message_id) WHERE chat_id = (:chat_id)',{'message_id':message_id ,'chat_id':chat_id})
    conn.close()

def deleteFile(chat_id):
    'deleteFile = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET deleteFile = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def setPassword(chat_id):
    'setPassword = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET setPassword = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def newPassword(chat_id):
    'newPassword = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET newPassword = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def trackingFile(chat_id):
    'trackingFile = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET trackingFile = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def forwardToAll(chat_id):
    'forwardToAll = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET forwardToAll = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def sendToAll(chat_id):
    'sendToAll = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET sendToAll = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def addAdmin(chat_id):
    'addAdmin = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET addAdmin = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def addChannel(chat_id , command):
    'addChannel = command'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET addChannel = (:command) WHERE chat_id = (:chat_id)',{'command':command , 'chat_id':chat_id})
    conn.close()

def isActiveCondition(chat_id):
    'isActiveCondition = "T"'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('UPDATE members SET isActiveCondition = "T" WHERE chat_id = (:chat_id)',{'chat_id':chat_id})
    conn.close()

def checkCommand(message:str) -> tuple:
    '''Checks whether the channel message is in the database\n
    ( chat_id , command )'''
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT chat_id , addChannel FROM members WHERE addChannel =(:message)' , {'message':message})
    info = c.fetchone()
    conn.close()
    return info


def getInfo(chat_id) -> tuple:
    '''0->chat_id ( integer )\n
    1->enterPassword ( T/F )\n
    2->isCorrectPassword ( T/F )\n
    3->encryptedFile ( ID/F )\n
    4->savedLink ( ID/F )\n
    5->correctPasswordId ( Message_id/F )\n
    6->replyMessageId ( Message_id/F )\n
    7->deleteFile ( T/F )\n
    8->setPassword ( T/F )\n
    9->newPassword ( T/F )\n
    10->setPasswordFile ( ID/F )\n
    11->trackingFile ( T/F )\n
    12->forwardToAll ( T/F )\n
    13->sendToAll ( T/F )\n
    14->addAdmin ( T/F )\n
    15->isActiveCondition ( T/F )\n
    16->addChannel ( Command/F )
    '''
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('''
    SELECT
    chat_id,
    enterPassword,
    isCorrectPassword,
    encryptedFile,
    savedLink,
    correctPasswordId,
    replyMessageId,
    deleteFile,
    setPassword,
    newPassword,
    setPasswordFile,
    trackingFile,
    forwardToAll,
    sendToAll,
    addAdmin,
    isActiveCondition,
    addChannel
    FROM
    members
    WHERE
    chat_id = (:chat_id)
    ''',{'chat_id':chat_id})
    info=c.fetchone()
    conn.close()
    return info

def resetAll(chat_id):
    'resets all conditions'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''
        UPDATE members
        SET
        enterPassword = "F" ,
        isCorrectPassword = "F" ,
        encryptedFile = "F" ,
        savedLink = "F" ,
        correctPasswordId = "F" ,
        replyMessageId = "F" ,
        deleteFile = "F" ,
        setPassword = "F" ,
        newPassword = "F" ,
        setPasswordFile = "F" ,
        trackingFile = "F" ,
        forwardToAll = "F" ,
        sendToAll = "F" ,
        addAdmin = "F" ,
        addChannel = "F" ,
        isActiveCondition = "F"
        WHERE
        chat_id = (:chat_id)
        ''',{'chat_id':chat_id})

    conn.close()


def add_channel(name,channel_id,channel_link):
    'channel_id standard format: -1001005076171\nchannel_id is UNIQUE!'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''INSERT INTO channels VALUES (?,?,?)''',(name,channel_id,channel_link))

def delete_channel(channel_id):
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    with conn:
        c.execute('''DELETE FROM channels WHERE channel_id=(:id)''',{'id':channel_id})
    conn.close()

def total_channels() -> int:
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM channels''')
    total_channel = c.fetchone()
    conn.close()
    return total_channel[0]

def all_channels() -> list:
    'list [ tuple ( name , channel_id , channel_link ) , . . . ]'
    conn = sqlite3.connect('uploader_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM channels')
    info = c.fetchall()
    conn.close()
    return info
