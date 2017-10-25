#!/usr/bin/env python3

import sys
import os
from multiprocessing import Process, Queue, Lock

queue1 = Queue()
queue2 = Queue()
lock1 = Lock()
lock2 = Lock()

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
        #self.parseDataFile()
#       self._config = None
#       self._output = None
#       self._resultdata = []
        
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
                self.userdata = {}

        d_file.close()

    @property
    def userdata(self):
        return self._userdata

#    @userdata.setter
#    def userdata(self, value):
#        self._userdata = value

def tax_num(ontax):
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

def calculator(conf,userdata):

    person_data = {}
    resultdata = []
    total_ins_per = 0.08 + 0.02 + 0.005 + 0.06
    JiShuL = conf.get_config('JiShuL')
    JiShuH = conf.get_config('JiShuH')
    YangLao = conf.get_config('YangLao')
    YiLiao = conf.get_config('YiLiao')
    ShiYe = conf.get_config('ShiYe')
    GongShang = conf.get_config('GongShang')
    ShengYu = conf.get_config('ShengYu')
    GongJiJin = conf.get_config('GongJiJin')

    for w_id, salary in userdata.items():
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
            tax = tax_num(ontax - 3500)

        real_salary = ontax - tax

        person_data['social_ins'] = ins
        person_data['personal_tax'] = tax
        person_data['real_salary'] = real_salary

        resultdata.append(person_data)
        person_data = {}
    return resultdata


def dumptofile(resultdata,outputfile):
    
    try:
        o_file = open(outputfile, 'w+')
    except:
        print("OutputFile open failed")
        sys.exit(-1)
    def work_id_s(x):
        return x['work_id']
    resultdata.sort(key=work_id_s)
    for item in resultdata:

        outstr = '%s,%d,%.2f,%.2f,%.2f\n' % (item['work_id'], item['raw_salary'], \
                                            item['social_ins'],item['personal_tax'], \
                                            item['real_salary'])
        o_file.write(outstr)
    o_file.close()

def p_data_parse(datafile):

    data = UserData(datafile)
    data.parseDataFile()
    if data.userdata == {}:
        sys.exit(-1)

    #conn1.send(data.userdata)
    with lock1:
        queue1.put(data.userdata)

def p_calculate(config):

    #data = conn2.recv()
    with lock1:
        data = queue1.get()

    resultdata = calculator(config, data)
    #conn3.send(resultdata)
    with lock2:
        queue2.put(resultdata)

def p_dump_file(outputfile):

    #result = conn4.recv()
    with lock2:
        result = queue2.get()
    dumptofile(result, outputfile)
    
if __name__ == '__main__':

    if len(sys.argv) != 7:
        
        print("Usage: python3 calculator.py -c test.cfg -d user.csv -o gongzi.csv")
        sys.exit(-1)

    config_file, data_file, out_file = parse_args(sys.argv[1:])
    tax_config = Config(config_file)
#    user_data = UserData(data_file)
#    user_data.config = tax_config
#    user_data.calculator()
#    user_data.dumptofile(out_file)
    p1 = Process(target=p_data_parse, args=(data_file,))
    p2 = Process(target=p_calculate, args=(tax_config,))
    p3 = Process(target=p_dump_file, args=(out_file,))
    p1.start()
    p2.start()
    p3.start()
