import sys
import csv

#处理命令行参数的类
class Args(object):

    def __init__(self):
        self.args = sys.argv[1:]


#配置文件类
class Config(object):

    def __init__(self):
        self.config = self._read_config()

        #配置文件内部函数
        def _read_config(self):
            Config = {}

#用户数据类
class UserData(object):
    def __init__(self):
        self.userdata = self._read_users_data()

    #用户数据读取内部函数
    def _read_users_data(self):
        userdata = []

#税后工资计算及输出类
class IncomeTaxCalculator(object):
    def calc_for_all_userdata(self):

    #输出CSV文件函数
    def export(self, default='csv'):
        result = self.calc_for_all_userdata()
        with open("输出文件路径") as f:
            writer = csv.writer(f)
            writer.writerows(result)

if __name__ == '__main__':
    