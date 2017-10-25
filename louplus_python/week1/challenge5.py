#!/usr/bin/env python3

import sys
import os
import configparser
import getopt
from multiprocessing import Process, Queue, Lock
from datetime import datetime, date

queue1 = Queue()
queue2 = Queue()
#lock1 = Lock()
#lock2 = Lock()

class UserData(object):

    def __init__(self, datafile):

        self._datafile = datafile
        self._userdata = {}
        
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
        print('parse over')

    @property
    def userdata(self):
        return self._userdata

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
    try:
        JiShuL = float(conf['JiShuL'])
        JiShuH = float(conf['JiShuH'])
        YangLao = float(conf['YangLao'])
        YiLiao = float(conf['YiLiao'])
        ShiYe = float(conf['ShiYe'])
        GongShang = float(conf['GongShang'])
        ShengYu = float(conf['ShengYu'])
        GongJiJin = float(conf['GongJiJin'])
    except:
        print("configfile format error")
        sys.exit(-1)

    for w_id, salary in userdata.items():

        now = datetime.now()
        strtime = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')

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
        person_data['cal_time'] = strtime

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

        outstr = '%s,%d,%.2f,%.2f,%.2f,%s\n' % (item['work_id'], item['raw_salary'], \
                                            item['social_ins'],item['personal_tax'], \
                                            item['real_salary'], item['cal_time'])
        o_file.write(outstr)
    o_file.close()

def p_data_parse(datafile):

    print("Begin data parse")
    data = UserData(datafile)
    data.parseDataFile()
    if data.userdata == {}:
        sys.exit(-1)

    #conn1.send(data.userdata)
    #lock1.release()
    #with lock1:
    queue1.put(data.userdata)
    print('parse_over')

def p_calculate(config):

    #data = conn2.recv()
    print("Begin get data to calculate")
    #with lock1:
    data = queue1.get()

    print("Begin calculate")
    resultdata = calculator(config, data)
    #conn3.send(resultdata)
    #lock2.release()
    #with lock2:
    queue2.put(resultdata)

def p_dump_file(outputfile):

    #result = conn4.recv()
    print("Begin get data to dump")
   # with lock2:
    result = queue2.get()
    print("Begin to dump")
    dumptofile(result, outputfile)

def usage():
    print("Usage: calculator.py -C cityname -c configfile -d userdata -o resultdata")
 

if __name__ == '__main__':

    '''
    if len(sys.argv) != 7:
        
        print("Usage: python3 calculator.py -c test.cfg -d user.csv -o gongzi.csv")
        sys.exit(-1)

    config_file, data_file, out_file = parse_args(sys.argv[1:])
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hC:c:d:o:',['help',])
    except getopt.GetoptError as e:
        print(e)
        usage()
        sys.exit(-1)
    if len(args) != 0:
        usage()
        sys.exit(-2)
    for option, arg in opts:
        if option in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif option == '-C':
            city = arg.upper()
        elif option == '-c':
            config_file = arg
        elif option == '-d':
            data_file = arg
        elif option == '-o':
            out_file = arg
        else:
            print("Parameter Error")
            sys.exit(-1)

    cf = configparser.ConfigParser()
    try:
        with open(config_file) as f:
            cf.read_file(f)
    except FileNotFoundError:
        print("config file not found")
        sys.exit(-1)
    if not city in cf.sections():
        print("cannot get the city's data")
        sys.exit(-1)
#    user_data = UserData(data_file)
#    user_data.config = tax_config
#    user_data.calculator()
#    user_data.dumptofile(out_file)
    p1 = Process(target=p_data_parse, args=(data_file,))
    p2 = Process(target=p_calculate, args=(cf[city],))
    p3 = Process(target=p_dump_file, args=(out_file,))
    p1.start()
    p2.start()
    p3.start()
