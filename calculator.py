import sys
import csv
from collections import namedtuple

IncomTaxQuickLookupItem = namedtuple(
    'IncomeTaxQuickLookupItem',
    ['start_point','tax_rate','quick_subtractor']
)
#起征点常量
INCOME_TAX_START_POINT = 5000

#税率表
INCOME_TAX_QUICK_LOOKUP_TABLE = [
    IncomTaxQuickLookupItem(80000,0.45,15160),
    IncomTaxQuickLookupItem(55000,0.35,7160),
    IncomTaxQuickLookupItem(35000,0.30,4410),
    IncomTaxQuickLookupItem(25000,0.25,2660),
    IncomTaxQuickLookupItem(12000,0.2,210),
    IncomTaxQuickLookupItem(0,0.03,0)
]

#处理命令行参数的类
class Args(object):

    def __init__(self):
        self.args = sys.argv[1:]
    
    def _value_after_option(self,option):
        
        try:
            index = self.args.index(option)
            return self.args[index + 1]
        except (ValueError,IndexError):
            print('Parameter Error')
            exit()
    
    @property
    def config_path(self):
        #获取配置文件路径
        return self._value_after_option("-c")

    @property
    def userdata_path(self):
        #获取用户信息
        return self._value_after_option("-d")

    @property
    def export_path(self):
        #获取输出文件路径
        return self._value_after_option("-o")

#创建实例化对象供后续使用
args = Args()

#配置文件类
class Config(object):

    def __init__(self):
        self.config = self._read_config()

    #配置文件内部函数
    def _read_config(self):
        config = {}
        with open(args.config_path) as f:
            for line in f.readlines():
                key, value = line.strip.split('=')
                try:
                    config[key.strip()] = float(value.strip())
                except ValueError:
                    print('Parameter Error')
                    exit()
        return config
    
    def _get_config(self, key):
        try:
            return self.config[key]
        except KeyError:
            print('Config Error')
            exit()
    @property
    def social_insurance_baseline_low(self):
        '''
        获取社保下限
        '''
        return self._get_config('JiShuL')
    
    @property
    def social_insurance_baseline_high(self):
        '''
        获取社保上限
        '''
        return self._get_config('JiShuH')
    
    @property
    def social_insurance_total_rate(self):
        '''
        获取社保总费率
        '''
        return sum([
            self._get_config('YangLao'),
            self._get_config('YiLiao'),
            self._get_config('ShiYe'),
            self._get_config('GongShang'),
            self._get_config('ShengYu'),
            self._get_config('GongJiJin')
        ])

config = Config()

#用户数据类
class UserData(object):
    def __init__(self):
        self.userdata = self._read_users_data()

    def _read_users_data(self):
        
        userlist = []
        with open(args.userdata_path) as f:
            for line in f.readlines():
                employee_id, income_string = line.strip().split(',')
                try:
                    income = int(income_string)
                except ValueError:
                    print('Parameter Error')
                    exit()
                userlist.append((employee_id,income))
        return userlist

    def get_userlist(self):
        return self.userlist

class IncomeTaxCalculator(object):
    #计算税后收入

    def __init__(self, userdata):
        self.userdata = userdata

    @classmethod
    #计算保险金额
    def calc_social_insurance_money(cls, income):
        if income < config.social_insurance_baseline_low:
            return config.social_insurance_baseline_low * \
                config.social_insurance_total_rate
        elif income > config.social_insurance_baseline_high:
            return config.social_insurance_baseline_high * \
                config.social_insurance_total_rate
        else:
            return income * config.social_insurance_total_rate
    
    @classmethod
    def calc_income_tax_and_remain(cls, income):
        #计算税后工资

        #计算社保金额
        social_insurance_money = cls.calc_social_insurance_money(income)

        #计算应税工资
        real_incom = income - social_insurance_money
        taxable_part = real_incom - INCOME_TAX_START_POINT

        for item in INCOME_TAX_QUICK_LOOKUP_TABLE:
            if taxable_part > item.start_point:
                tax = taxable_part * item.tax_rate - item.quick_subtractor
                return '{:.2f}'.format(tax), '{:.2f}'.format(real_incom - tax)
            
            return '0.00', '{:.2f}'.format(real_incom)
    
    def calc_for_all_userdata(self):
        '''
        计算所有用户
        '''

        result = []

        for employee_id, income in self.userdata.gat_userlist():
            social_insurance_money = '{:.2f}'.format(
                self.calc_social_insurance_money(income))
            
            #计算税后工资
            tax, remain = self.calc_income_tax_and_remain(income)

            #添加到结果集
            result.append(
                [employee_id, income, social_insurance_money, tax, remain]
            )
        return result

    def export(self):
        result = self.calc_for_all_userdata()

        with open(args.export_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(result)


if __name__ == '__main__':
    calculator = IncomeTaxCalculator(UserData())
    calculator.export()
    