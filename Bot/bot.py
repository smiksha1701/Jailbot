import telebot
import lib.database as DataBase
from lib.compile import run, compile
import os
import tempfile
from lib.User import User
from lib.Troubleshooting import RestoreTroubles

TOKEN = '' #SET YOUR TOKEN HERE
PASSWORD = "HP"
modes = ["normal", "admin", "await_test", "await_result", "await_password"]
emoji = '\U00002714'
start_text = 'Hello, this is bot which tests your work.\n To start as student send me /contest <id_of_contest>.\n'+"After that send me your code file and i'll process it and tell if there any plagiarism.\n"+"To start as teacher send me some secret command.\nTo check your current mode and contest send me /info\n"
container = {}
langs = {".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp", ".h": "cpp", ".txt": "text"}
db = DataBase.Data()
troubleshoot = [] 
bot = telebot.TeleBot(TOKEN)
PATH = os.path.abspath(os.getcwd())
BACKUP = os.path.join(PATH, 'backup')

def restore(BACKUP: os.path) -> tuple[RestoreTroubles, User]:
    user = User(PATH)
    troubleshoot = RestoreTroubles()
    try:
        with open(BACKUP, 'r')as f:
            last_path = f.readline()[:-1]
            id = f.readline()[:-1]
            mode = f.readline()

        if id != '':
            user.id = int(id)
        else:
            troubleshoot.add_major_troubles(1)
            return troubleshoot, user
        if mode != '':
            if(mode not in modes):
                user.mode = modes[0]
                troubleshoot.add_minor_troubles(1)
            else:
                user.mode = mode
        else:
            user.mode = modes[0]
            troubleshoot.add_minor_troubles(2)

        if  last_path != '' :
            if(user.path.check_path(last_path)):
                user.path.set_contest_by_path(last_path)

            else: 
                troubleshoot.add_minor_troubles(3)

        else: troubleshoot.add_minor_troubles(4)

    except:
        troubleshoot.add_major_troubles(0) 
        return troubleshoot, user
    return troubleshoot, user

def step(step):
    def decorator(func):
        def aux(msg, *args):
            bot.edit_message_text(step, msg.chat.id, msg.message_id)
            result = func(*args)
            return result
        return aux
    return decorator

def get_fcontent(fname: str) -> str:
    with open(fname, 'r') as f:
        result = f.read()
    return result

def get_result(compiled_name: str, lang: str, test_filepath: str, result_filepath: str) -> str:
    output_filepath = run(compiled_name, lang, test_filepath, result_filepath)
    return get_fcontent(output_filepath)

@step("Guessing language")
def guess_language_from_extension(ext: str) -> str:
    return  langs.get(ext)

@step("Downloading your file")
def download_file(file_id, user_id) -> tuple[bytes, str, str]:
    filepath = bot.get_file(file_id).file_path
    _, ext = os.path.splitext(filepath)
    content = bot.download_file(filepath)
    fd, path = tempfile.mkstemp(ext, f"code.{user_id}.", container[user_id].path.cur_Contest_path.codes_path, True)
    os.close(fd)
    with open(path, 'wb') as f:
        f.write(content)
    return content, path, ext
        
@step("Finding plagiarism")
def find_best_match(file) -> tuple[str, float]:
    return db.find_best_match(file)

@step("Compiling your programm")
def compile_file(lang, path) -> str or None:
    return compile(lang, path)


@step("Getting content")
def get_content(file_id):
    filepath = bot.get_file(file_id).file_path
    return bot.download_file(filepath).decode()

@step("Building test file")
def build_test(content, user_path):
    ntests = len(os.listdir(user_path.cur_Contest_path.tests_path))
    with open(user_path.cur_Contest_path.cur_smth_path('test', ntests), 'w') as f:
        f.write(content)

@step("Building result file")
def build_result(content, user_path):
    nresults = len(os.listdir(user_path.cur_Contest_path.results_path))
    with open(user_path.cur_Contest_path.cur_smth_path('answer', nresults), 'w') as f:
        f.write(content)

@bot.message_handler(commands = ['help'])
def help_command(message):
    bot.send_message(message.chat.id, )
@bot.message_handler(commands = ['info'])
def info_command(message):
    mode = container[message.from_user.id].mode
    cntn = container[message.from_user.id].path.cntn

    if(cntn == ""): cntn = "None"
    bot.send_message(message.chat.id, f"Your mode is: {mode}\nYou are working in: {cntn}")

@bot.message_handler(commands = ['clear'])
def clear_command(message):

    if (container[message.from_user.id].mode == modes[1]):
        bot.send_message(message.chat.id, "DB is cleared")
        db.empty()

    else:
        bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")

@bot.message_handler(commands = ['add_test'])
def add_test(message):
    cur_user = container[message.from_user.id]
    if (cur_user.mode == modes[1]): 
        cur_user.mode = modes[2]
        cur_user.backup()
        bot.send_message(message.chat.id, "Now send me test file")

    else:
        bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")

@step("Creating homework directory")
def create_directory(path) -> None:
    os.mkdir(path.cur_Contest_path.PATH)
    os.mkdir(path.cur_Contest_path.tests_path)
    os.mkdir(path.cur_Contest_path.answers_path)
    os.mkdir(path.cur_Contest_path.codes_path)
    os.mkdir(path.cur_Contest_path.results_path)

@bot.message_handler(commands = ['new_contest'])
def new_contest(message):
    if(message.from_user.id in container):
        cur_user = container[message.from_user.id]
        if (cur_user.mode ==  modes[1]):
            msg = bot.send_message(message.chat.id, "Got your command")
            if(cur_user.path.new_cnt_paths(message.text[13:])):
                create_directory(msg, cur_user.path)
                cur_user.backup()
                bot.edit_message_text("Done", msg.chat.id, msg.id)
            else: bot.edit_message_text("There is a contest with such name", msg.chat.id, msg.id)

        else:
            bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")
    else:
        bot.send_message(message.chat.id, "Sorry we have lost your status. Please type /start to start again")
@bot.message_handler(commands = ['start'])
def starting_command(message):
    bot.send_message(message.chat.id, start_text)
    cur_user = User(PATH)
    cur_user.id = message.from_user.id
    cur_user.backup()
    container[cur_user.id] = cur_user

@bot.message_handler(commands = ['admin'])
def Admin_command(message):
    if(message.from_user.id in container):
        bot.send_message(message.chat.id, "Hold on, password please?")
        container[message.from_user.id].mode = modes[4]
        container[message.from_user.id].backup()
    else: 
        bot.send_message(message.chat.id, "Sorry we have lost your status. Please type /start to start again")

@bot.message_handler(commands = ['contest'])
def contest_command(message):
    if(message.from_user.id in container):
        cur_user = container[message.from_user.id]
        mode = cur_user.mode
        cntn = message.text[9:]

        if(mode == modes[0]):
            if(cur_user.set_cnt(cntn)):
                bot.send_message(message.chat.id, f"You're working in: {cntn} contest now. Waiting for your work")
                cur_user.mode = modes[0]
                cur_user.backup()

            else: 
                bot.send_message(message.chat.id, "There is no contest with such name")

        if(mode == modes[1]):
            cur_user.set_cnt(cntn)
            bot.send_message(message.chat.id, f"You are now working with contest: {message.text[9:]}")
    else: 
        bot.send_message(message.chat.id, "Sorry we have lost your status. Please type /start to start again")

@bot.message_handler(content_types = ['text'])
def load_text(message):
    cur_user = container[message.from_user.id]
    mode = cur_user.mode
    if(mode == modes[4]):
        password = message.text
        if password ==  PASSWORD:
            bot.send_message(message.chat.id, "Awaiting your commands sir")
            cur_user.mode = modes[1]
            cur_user.backup()
        else: 
            bot.send_message(message.chat.id, "Nice try")
            cur_user.mode = modes[0]
            cur_user.backup()
    else:
        bot.send_message(message.chat.id, "Use /info command to see FAQ")

@bot.message_handler(content_types = ['document'])
def load_file(message):
    mode = container[message.from_user.id].mode
    user_path = container[message.from_user.id].path

    if(mode ==  modes[0]):
        my_msg = bot.send_message(message.chat.id, text =  "I've got your document\n")
        
        [content, fpath, ext] =  download_file(my_msg, message.document.file_id, message.from_user.id)
        file = content.decode()

        lang = guess_language_from_extension(my_msg, ext)
        if not lang:
            bot.send_message(message.chat.id, "Not supported language")
            return
        
        [code, score] =  find_best_match(my_msg, file)

        compiled_name = compile_file(my_msg, lang, fpath)

        if(not compiled_name):
            bot.send_message(message.chat.id, "Could not compile your file")
            return 
        ntests = len(os.listdir(user_path.cur_Contest_path.tests_path))
        bot.edit_message_text("Getting results", my_msg.chat.id, my_msg.message_id)

        for i in range (ntests):
            cur_test_path = user_path.cur_Contest_path.cur_smth_path('test', i)
            cur_result_path = user_path.cur_Contest_path.cur_smth_path('result', i)
            cur_answer_path = user_path.cur_Contest_path.cur_smth_path('answer', i)
            result = get_result(compiled_name, lang, cur_test_path, cur_result_path)
            true_result = get_fcontent(cur_answer_path)

            if(result !=  true_result):
                test = get_fcontent(cur_test_path)
                bot.send_message(message.chat.id, f"You got wrong answer on test : {test}\n Your answer is: {result}\n Right answer is : {true_result}")
                break

        if code:
            bot.send_message(message.chat.id, f"This text {code} is similar by {score}")
        else:
            bot.send_message(message.chat.id, "You are the first one")

        bot.delete_message(my_msg.chat.id, my_msg.id)
        bot.send_message(message.chat.id, "Your file is completely processed")

    elif(mode ==  modes[2]):
        my_msg = bot.send_message(message.chat.id, text =  "I've got your test\n")
        content =  get_content(my_msg, message.document.file_id)
        build_test(my_msg, content, user_path)
        container[message.from_user.id].mode = modes[3]
        container[message.from_user.id].backup()
        bot.edit_message_text("Your file is completely processed", my_msg.chat.id, my_msg.id)
        bot.send_message(message.chat.id, "Now send me result of test ")

    elif(mode ==  modes[3]):
        my_msg = bot.send_message(message.chat.id, text =  "I've got your result\n")
        content = get_content(my_msg , message.document.file_id)
        build_result(my_msg, content, user_path)
        container[message.from_user.id].mode = modes[1]
        container[message.from_user.id].backup()
        bot.edit_message_text("Your file is completely processed", my_msg.chat.id, my_msg.id)

if __name__=='__main__':
    troubles, USER = restore(BACKUP)
    if not any(troubles.major_occured):
        container[USER.id] = USER
        for i in troubles.minor_occured:
            bot.send_message(USER.id, i)
    bot.polling()


#Decorator function  
