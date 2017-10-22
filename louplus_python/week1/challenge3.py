#!/usr/bin/env python3

import sys
import os

def parse_args(args):
    """
    parse_args using the commandline, raise Exception when format is error
    """
    try:
        c_index = args.index('-c')
        if args[c_index + 1].startswith('-'):
            raise ValueError
        configfile = args[c_index + 1]
        d_index = args.index('-d')
        if args[d_index + 1].startswith('-'):
            raise ValueError
        datafile = args[d_index + 1]
        o_index = args.index('-o')
        if args[o_index + 1].startswith('-'):
            raise ValueError
        outfile = args[o_index + 1]
    except:
        print("Parameter Error")
        sys.exit(-1)

    return configfile, datafile, outfile

class Config(object):

    def __init__(self, configfile):
        
        self._configfile = configfile
        self._config = {}

        self.parseConfig()

    def parseConfig(self):

        configKey = ['JiShuL', 'JiShuH', 'YangLao', 'YiLiao', \
                        'ShiYe', 'GongShang', 'ShengYu', 'GongJiJin']
        try:
            c_file = open(self._configfile,'r')
        except FileNotFoundError:
            print("ConfigFile not Found, make sure you have input the right path")
            sys.exit(-1)
        while True:
            line = c_file.readline()
            if not line:
                break
            try:
                item = line.split('=')
                if len(item) != 2:
                    raise ValueError
                key, value = item
                key = key.strip()
                value = value.strip()
                #print(key,value)
                if not key in configKey:
                    raise ValueError
                self._config[key] = float(value)
            except ValueError as e:
                print("ConfigFile format error")
                c_file.close()
                sys.exit(-1)
        c_file.close()
        return

    def get_config(self, key):
        
        try:
            return self._config[key]
        except KeyError:
            print("Error request config information")

class UserData(object):

    def __init__(self, datafile):

        self._datafile = datafile
        self._userdata = {}
        self.parseDataFile()
        self._config = None
        self._output = None
        self._resultdata = []
        
    def parseDataFile(self):
        try:
            d_file = open(self._datafile, 'r')
        except FileNotFoundError:
            print("DataFile not found")
            sys.exit(-1)
        while True:
            line = d_file.readline()
            if not line:
                break
            try:
                item = line.split(',')
                if len(item) != 2:
                    raise ValueError
                w_id, salary = item
                w_id.strip()
                salary.strip()
                self._userdata[w_id] = int(salary)
            except ValueError:
                print("ConfigFile Format Error")
                d_file.close()
                sys.exit(-1)

        d_file.close()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def tax_num(self, ontax):
        tax = 0.0
        tax_per = 0.0
        minus = 0
        if(ontax <= 1500):
            tax_per = 0.03
            minus = 0
        elif(ontax > 1500 and ontax <= 4500):
            tax_per = 0.1
            minus = 105
        elif(ontax > 4500 and ontax <= 9000):
            tax_per = 0.2
            minus = 555
        elif(ontax > 9000 and ontax <= 35000):
            tax_per = 0.25
            minus = 1005
        elif(ontax > 35000 and ontax <= 55000):
            tax_per = 0.3
            minus = 2755
        elif(ontax > 55000 and ontax <= 80000):
            tax_per = 0.35
            minus = 5505
        else:
            tax_per = 0.45
            minus = 13505

        tax = ontax * tax_per - minus

        return tax

    def calculator(self):

        person_data = {}
        total_ins_per = 0.08 + 0.02 + 0.005 + 0.06
        conf = self.config
        JiShuL = conf.get_config('JiShuL')
        JiShuH = conf.get_config('JiShuH')
        YangLao = conf.get_config('YangLao')
        YiLiao = conf.get_config('YiLiao')
        ShiYe = conf.get_config('ShiYe')
        GongShang = conf.get_config('GongShang')
        ShengYu = conf.get_config('ShengYu')
        GongJiJin = conf.get_config('GongJiJin')

        for w_id, salary in self._userdata.items():
            person_data['work_id'] = w_id
            person_data['raw_salary'] = salary

            if salary < JiShuL:
                ins = JiShuL * total_ins_per
            elif salary > JiShuH:
                ins = JiShuH * total_ins_per
            else:
                ins = salary * total_ins_per

            ontax = salary - ins

            if ontax <= 3500:
                tax = 0.0
            else:
                tax = self.tax_num(ontax)

            real_salary = ontax - tax

            person_data['social_ins'] = ins
            person_data['personal_tax'] = tax
            person_data['real_salary'] = real_salary

            self._resultdata.append(person_data)
            person_data = {}

    def dumptofile(self, outputfile):
        
        try:
            o_file = open(outputfile, 'w+')
        except:
            print("OutputFile open failed")
            sys.exit(-1)
        def work_id_s(x):
            return x['work_id']
        self._resultdata.sort(key=work_id_s)
        for item in self._resultdata:

            outstr = '%s,%d,%.2f,%.2f,%.2f\n' % (item['work_id'], item['raw_salary'], \
                                                item['social_ins'],item['personal_tax'], \
                                                item['real_salary'])
            o_file.write(outstr)
        o_file.close()

        
if __name__ == '__main__':

    if len(sys.argv) != 7:
        
        print("Usage: python3 calculator.py -c test.cfg -d user.csv -o gongzi.csv")
        sys.exit(-1)

    config_file, data_file, out_file = parse_args(sys.argv[1:])
    tax_config = Config(config_file)
    user_data = UserData(data_file)
    user_data.config = tax_config
    user_data.calculator()
    user_data.dumptofile(out_file)
