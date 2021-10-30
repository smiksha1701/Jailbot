import os
class Path():
    def __init__(self, path):
        self.PATH = path
        self.BACKUP =  os.path.join(self.PATH,"backup")
        self.cur_PATH = path
        self.cntn = ''
    def restore(self):
        try:
            with open(self.BACKUP,'r')as f:
                BUI = f.readline()[:-1]
                creator = f.readline()
            if BUI != '' and creator != '':
                if(self.check_path(BUI)):
                    self.cur_PATH = ContestPath(BUI)
                    self.cur_PATH.ess_cntd()
                    return True, 0
                else: 
                    return False, int(creator)
        except: return False, None
        finally: return False, None
    @staticmethod
    def check_path(path):
        return os.path.isdir(path)

    def get_cnt_path(self, cnt):
        return os.path.join(self.PATH,f'Contest_{cnt}')
    def new_cnt_paths(self, cntn, creator):
        self.cntn = cntn
        new_cntp = self.get_cnt_path(cntn)
        if(self.check_path(new_cntp)):
            return False
        with open(self.BACKUP,'w') as f:
            f.write(new_cntp)
            f.write(f'\n{creator}')
        self.cur_PATH = ContestPath(new_cntp)
        self.cur_PATH.ess_cntd()
        return True

    def set_cnt(self, cntn):
        self.cntn = cntn
        new_cntp = self.get_cnt_path(cntn)
        if(not self.check_path(new_cntp)):
            return False
        self.cur_PATH = ContestPath(new_cntp)
        self.cur_PATH.ess_cntd()
        return True
class ContestPath(Path):
    def ess_cntd(self):
        self.tests_path = os.path.join(self.PATH, "tests")
        self.answers_path = os.path.join(self.PATH, "answers")
        self.codes_path = os.path.join(self.PATH, "codes")
        self.results_path = os.path.join(self.PATH,"results")
    def cur_smth_path(self, smth, index):
        return os.path.join(os.path.join(self.PATH, f"{smth}s"), f'{smth}{str(index).zfill(5)}')
