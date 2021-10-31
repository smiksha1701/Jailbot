import os
class Path():
    def __init__(self, path):
        self.PATH = path
        self.BACKUP =  os.path.join(self.PATH,"backup")
        self.cur_Contest_path = None
        self.cur_path = path
        self.cntn = ''
    def set_contest_by_path(self, contest_path):
        self.cntn = contest_path.split('/').pop()[8:]
        self.cur_path = contest_path
        self.cur_Contest_path = ContestPath(contest_path)
        self.cur_Contest_path.ess_cntd()
    @staticmethod
    def check_path(path):
        return os.path.isdir(path)

    def get_cnt_path(self, cnt):
        return os.path.join(self.PATH,f'Contest_{cnt}')
    def new_cnt_paths(self, cntname):
        self.cntn = cntname
        new_cntp = self.get_cnt_path(cntname)
        if(self.check_path(new_cntp)):
            return False
        self.cur_Contest_path = ContestPath(new_cntp)
        self.cur_Contest_path.ess_cntd()
        self.cur_path = new_cntp
        return True

    def set_contest_by_name(self, cntn):
        self.cntn = cntn
        new_cntp = self.get_cnt_path(cntn)
        if(not self.check_path(new_cntp)):
            return False
        self.set_contest_by_path(new_cntp)
        return True
class ContestPath(Path):
    def ess_cntd(self):
        self.tests_path = os.path.join(self.PATH, "tests")
        self.answers_path = os.path.join(self.PATH, "answers")
        self.codes_path = os.path.join(self.PATH, "codes")
        self.results_path = os.path.join(self.PATH,"results")
    def cur_smth_path(self, smth, index):
        return os.path.join(os.path.join(self.PATH, f"{smth}s"), f'{smth}{str(index).zfill(5)}')
