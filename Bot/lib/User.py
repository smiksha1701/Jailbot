from lib.compile import run
from lib.path import Path
class User():
    def __init__(self, PATH):
        self.path = Path(PATH)
        self.id = None
        self.mode = "normal"

    def backup(self):
        with open(self.path.BACKUP,'w') as f:
            f.write(self.path.cur_path)
            f.write(f'\n{self.id}')
            f.write(f'\n{self.mode}')

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def set_cnt(self, contest_name):
        if(self.path.set_contest_by_name(contest_name)):
            self.backup()
            return True
        return False