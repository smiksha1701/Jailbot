import subprocess
import sys
def compile(lang, path):
    if(lang == 'cpp'):
        subprocess.run(['g++','-o','main',f'{path}'])
        return 'main'
    else:
        return None
def run(compiled, lang, test_filepath, result_filepath):
    if(lang == 'cpp'):
        subprocess.run([f'./{compiled} < {test_filepath} > {result_filepath}'], shell=True)
    return result_filepath

        