import telebot
import lib.database as DataBase
from lib.compile import run, compile
import os
import tempfile
from lib.path import Path

token = ''#SET YOUR TOKEN HERE
emoji = '\U00002714'
mode = "Normal"
start_text = 'Hello, this is bot which tests your work.\n To start as student send me /contest <id_of_contest>.\n'+"After that send me your code file and i'll process it and tell if there any plagiarism.\n"+"To start as teacher send me some secret command.\nTo check your current mode and contest send me /info\n"
container = {}
langs = {".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp", ".h": "cpp", ".txt": "text"}
db = DataBase.Data()
bot = telebot.TeleBot(token)
paths = Path(os.path.abspath(os.getcwd()))
exist, directory_creator = paths.restore()
container[directory_creator] = [mode, paths]
if(not exist):
    if(directory_creator):
        bot.send_message(directory_creator, "Your directory is deleted. Pls create a new one")

def step(step):
    def decorator(func):
        def aux(msg, *args):
            bot.edit_message_text(step, msg.chat.id, msg.message_id)
            result = func(*args)
            return result
        return aux
    return decorator

def get_fcontent(fname):
    with open(fname, 'r') as f:
        result = f.read()
    return result

def get_result(compiled_name, lang, test_filepath, result_filepath):
    output_name = run(compiled_name, lang, test_filepath, result_filepath)
    return get_fcontent(output_name)

@step("Guessing language")
def guess_language_from_extension(ext):
    return  langs.get(ext)

@step("Downloading your file")
def download_file(file_id, user_id):
    filepath = bot.get_file(file_id).file_path
    _, ext = os.path.splitext(filepath)
    content = bot.download_file(filepath)
    fd, path = tempfile.mkstemp(ext, f"code.{user_id}.", container[user_id][1].cur_PATH.codes_path, True)
    os.close(fd)
    with open(path, 'wb') as f:
        f.write(content)
    return content, path, ext
        
@step("Finding plagiarism")
def find_best_match(file):
    return db.find_best_match(file)

@step("Compiling your programm")
def compile_file(lang, path):
    return compile(lang, path)

@step("Creating homework directory")
def create_directory():
    os.mkdir(paths.cur_PATH.PATH)
    os.mkdir(paths.cur_PATH.tests_path)
    os.mkdir(paths.cur_PATH.answers_path)
    os.mkdir(paths.cur_PATH.codes_path)
    os.mkdir(paths.cur_PATH.results_path)

@step("Getting content")
def get_content(file_id):
    filepath = bot.get_file(file_id).file_path
    return bot.download_file(filepath).decode()

@step("Building test file")
def build_test(content, user_path):
    ntests = len(os.listdir(user_path.cur_PATH.tests_path))
    with open(user_path.cur_PATH.cur_smth_path('test', ntests), 'w') as f:
        f.write(content)

@step("Building result file")
def build_result(content, user_path):
    nresults = len(os.listdir(user_path.cur_PATH.results_path))
    with open(user_path.cur_PATH.cur_smth_path('answer', nresults), 'w') as f:
        f.write(content)

@bot.message_handler(commands = ['admin'])
def Admin_command(message):
    bot.send_message(message.chat.id, "Yes sir?")
    container[message.from_user.id][0] = "Admin"

@bot.message_handler(commands = ['contest'])
def contest_command(message):
    mode = container[message.from_user.id][0]
    cntn = message.text[9:]
    if(mode == "Normal"):
        if(container[message.from_user.id][1].set_cnt(cntn)):
            bot.send_message(message.chat.id, f"You working in:{cntn} contest now. Waiting for your work")
            container[message.from_user.id][0] = "Normal"
        else: 
            bot.send_message(message.chat.id, "There is no contest with such name")
    if(mode == "Admin"):
        container[message.from_user.id][1].set_cnt(cntn)
        bot.send_message(message.chat.id, f"You are now working with contest {message.text[9:]}")

@bot.message_handler(commands = ['start'])
def starting_command(message):
    bot.send_message(message.chat.id, start_text)
    container[message.from_user.id] = [mode, paths]

@bot.message_handler(commands = ['info'])
def help_command(message):
    mode = container[message.from_user.id][0]
    cntn = container[message.from_user.id][1].cntn

    if(cntn == ""): cntn = "None"
    bot.send_message(message.chat.id, f"Your mode is: {mode}\nYou are working in: {cntn}")

@bot.message_handler(commands = ['clear'])
def clear_command(message):

    if (container[message.from_user.id][0] == "Admin"):
        bot.send_message(message.chat.id, "DB is cleared")
        db.empty()

    else:
        bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")

@bot.message_handler(commands = ['add_test'])
def add_test(message):

    if (container[message.from_user.id][0] == "Admin"): 
        container[message.from_user.id][0] = "Await_test"
        bot.send_message(message.chat.id, "BOT NOW IN AWAITING TEST MODE")

    else:
        bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")

@bot.message_handler(commands = ['new_contest'])
def new_contest(message):
    mode = container[message.from_user.id][0]

    if (mode ==  "Admin"):
        msg = bot.send_message(message.chat.id, "Got your command")
        if(container[message.from_user.id][1].new_cnt_paths(message.text[13:], message.from_user.id)):
            create_directory(msg)
            bot.edit_message_text("Done", msg.chat.id, msg.id)
        else: bot.edit_message_text("There is a contest with such name", msg.chat.id, msg.id)

    else:
        bot.send_message(message.chat.id, "Hey, you don't have enough rights to use this command!")

""" @bot.message_handler(content_types = ['text'])
def load_text(message):
    file = message.text
    text, score = db.find_best_match(file)
    if text:
        bot.send_message(message.chat.id, f"This text {text} is similar by {score}")
    else:
        bot.send_message(message.chat.id, "DB is empty :(") """

@bot.message_handler(content_types = ['document'])
def load_file(message):
    mode = container[message.from_user.id][0]
    user_path = container[message.from_user.id][1]

    if(mode ==  "Normal"):
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
        ntests = len(os.listdir(user_path.cur_PATH.tests_path))
        bot.edit_message_text("Getting results", my_msg.chat.id, my_msg.message_id)

        for i in range (ntests):
            cur_test_path = user_path.cur_PATH.cur_smth_path('test', i)
            cur_result_path = user_path.cur_PATH.cur_smth_path('result', i)
            cur_answer_path = user_path.cur_PATH.cur_smth_path('answer', i)
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

    elif(mode ==  "Await_test"):
        my_msg = bot.send_message(message.chat.id, text =  "I've got your test\n")
        content =  get_content(my_msg, message.document.file_id)
        build_test(my_msg, content, user_path)
        container[message.from_user.id][0] = "Await_result"
        bot.send_message(message.chat.id, "BOT NOW IN AWAITING RESULT MODE")
        bot.send_message(message.chat.id, "Your file is completely processed")

    elif(mode ==  "Await_result"):
        my_msg = bot.send_message(message.chat.id, text =  "I've got your result\n")
        content = get_content(my_msg , message.document.file_id)
        build_result(my_msg, content, user_path)
        container[message.from_user.id][0] = "Admin"
        bot.send_message(message.chat.id, "Your file is completely processed")

    elif(mode ==  "Select"):
        bot.send_message(message.chat.id, "Pls choose your mode")
    
bot.polling()