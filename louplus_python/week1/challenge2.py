#!/usr/bin/env python3

import sys

def tax_num(ontax):
    tax = 0
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

def main():

    salary_list_map = {}
    tax_list = []
    try:
        if len(sys.argv) < 2:
            raise ValueError
        for item in sys.argv[1:]:
            w_id, salary = item.split(':')
            salary_list_map[w_id] = int(salary)
    except ValueError:
        print("Parameter Error")
        return {}

    total_ins_per = 0.08 + 0.02 + 0.005 + 0.06
    for w_id, salary in salary_list_map.items():
        salary_afterins = salary - salary * total_ins_per
        if(salary_afterins > 3500):
            salary_list_map[w_id] = salary_afterins - tax_num(salary_afterins - 3500)
        else:
            salary_list_map[w_id] = salary_afterins

    return salary_list_map

if __name__ == '__main__':

    salary_list = main()
    if salary_list == {}:
        pass
    else:
        for w_id, salary in salary_list.items():
            print('%s:%.2f' % (w_id, salary))
