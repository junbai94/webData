# -*- coding:utf-8 -*-
import dbaccess
import workdays
import datetime
from dateutil.relativedelta import relativedelta

import math
import copy
from base import *
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import sqlite3

BDAYS_PER_YEAR = 245.0
ORDER_BUY = '0'
ORDER_SELL = '1'
OPT_MARKET_ORDER = '1'
OPT_LIMIT_ORDER = '2'
OPT_FAK_ORDER = 'FA'
OPT_FOK_ORDER = 'FO'
OF_OPEN = '0'
OF_CLOSE = '1'
OF_CLOSE_TDAY = '3'
OF_CLOSE_YDAY = '4'
OST_ALL_TRADED = '0'  # 全部成交
OST_PF_QUEUE = '1'  # 部分成交还在队列中
OST_PF_NOQUE = '2'  # 部分成交不在队列中
OST_NOTRADE_QUEUE = '3'  # 未成交还在队列中
OST_NOTRADE_NOQUE = '4'  # 未成交不在队列中
OST_CANCELED = '5'  # 撤单
OST_UNKNOWN = 'a'  # 未知
OST_NOTOUCH = 'b'  # 尚未触发
OST_TOUCHED = 'c'  # 已触

AMERICAN_OPTION_STEPS = 40
MKT_DATA_BIGNUMBER = 10000000
NO_ENTRY_TIME = datetime.datetime(1970, 1, 1, 0, 0, 0)

sign = lambda x: math.copysign(1, x)

month_code_map = {'f': 1,
                  'g': 2,
                  'h': 3,
                  'j': 4,
                  'k': 5,
                  'm': 6,
                  'n': 7,
                  'q': 8,
                  'u': 9,
                  'v': 10,
                  'x': 11,
                  'z': 12}

CHN_Holidays = [datetime.date(2014, 1, 1), datetime.date(2014, 1, 2), datetime.date(2014, 1, 3),
                datetime.date(2014, 1, 31), datetime.date(2014, 2, 3), datetime.date(2014, 2, 4),
                datetime.date(2014, 2, 5), datetime.date(2014, 2, 6), datetime.date(2014, 4, 7),
                datetime.date(2014, 5, 1), datetime.date(2014, 5, 2), datetime.date(2014, 6, 2),
                datetime.date(2014, 9, 8), datetime.date(2014, 10, 1), datetime.date(2014, 10, 2),
                datetime.date(2014, 10, 3), datetime.date(2014, 10, 6), datetime.date(2014, 10, 7),
                datetime.date(2015, 1, 1), datetime.date(2015, 1, 2), datetime.date(2015, 2, 18),
                datetime.date(2015, 2, 19),
                datetime.date(2015, 2, 20), datetime.date(2015, 2, 23), datetime.date(2015, 2, 24),
                datetime.date(2015, 4, 6), datetime.date(2015, 5, 1), datetime.date(2015, 6, 22),
                datetime.date(2015, 9, 3), datetime.date(2015, 9, 4), datetime.date(2015, 10, 1),
                datetime.date(2015, 10, 2), datetime.date(2015, 10, 5), datetime.date(2015, 10, 6),
                datetime.date(2015, 10, 7),
                datetime.date(2016, 1, 1), datetime.date(2016, 2, 8), datetime.date(2016, 2, 9),
                datetime.date(2016, 2, 10), datetime.date(2016, 2, 11), datetime.date(2016, 2, 12),
                datetime.date(2016, 4, 4), datetime.date(2016, 5, 2), datetime.date(2016, 6, 9),
                datetime.date(2016, 6, 10), datetime.date(2016, 9, 15), datetime.date(2016, 9, 16),
                datetime.date(2016, 10, 3), datetime.date(2016, 10, 4), datetime.date(2016, 10, 5),
                datetime.date(2016, 10, 6), datetime.date(2016, 10, 7),
                datetime.date(2017, 1, 2), datetime.date(2017, 1, 27), datetime.date(2017, 1, 30),
                datetime.date(2017, 1, 31), datetime.date(2017, 2, 1), datetime.date(2017, 2, 2),
                datetime.date(2017, 4, 3), datetime.date(2017, 4, 4), datetime.date(2017, 5, 1),
                datetime.date(2017, 5, 29), datetime.date(2017, 5, 30),
                datetime.date(2017, 10, 2), datetime.date(2017, 10, 3), datetime.date(2017, 10, 4),
                datetime.date(2017, 10, 5), datetime.date(2017, 10, 6),
                datetime.date(2018, 1, 1), datetime.date(2018, 2, 16), datetime.date(2018, 2, 19),
                datetime.date(2018, 2, 20), datetime.date(2018, 2, 21),
                datetime.date(2018, 4, 5), datetime.date(2018, 5, 1), datetime.date(2018, 6, 18),
                datetime.date(2018, 9, 24), datetime.date(2018, 10, 1), datetime.date(2018, 10, 2),
                datetime.date(2018, 10, 3), datetime.date(2018, 10, 4), datetime.date(2018, 10, 5)]

PLIO_Holidays = [datetime.date(2014, 1, 1),
                datetime.date(2015, 1, 1),
                datetime.date(2016, 1, 1),
                datetime.date(2017, 1, 2),
                datetime.date(2018, 1, 1),]

WASDE_Dates = [datetime.date(2010, 1, 12), datetime.date(2010, 2, 9), datetime.date(2010, 3, 10), \
               datetime.date(2010, 4, 9), datetime.date(2010, 5, 11), datetime.date(2010, 6, 10), \
               datetime.date(2010, 7, 9), datetime.date(2010, 8, 12), datetime.date(2010, 9, 10), \
               datetime.date(2010, 10, 8), datetime.date(2010, 11, 9), datetime.date(2010, 12, 10), \
               datetime.date(2011, 1, 12), datetime.date(2011, 2, 9), datetime.date(2011, 3, 10), \
               datetime.date(2011, 4, 8), datetime.date(2011, 5, 11), datetime.date(2011, 6, 9), \
               datetime.date(2011, 7, 12), datetime.date(2011, 8, 11), datetime.date(2011, 9, 12), \
               datetime.date(2011, 10, 12), datetime.date(2011, 11, 9), datetime.date(2011, 12, 9), \
               datetime.date(2012, 1, 12), datetime.date(2012, 2, 9), datetime.date(2012, 3, 9), \
               datetime.date(2012, 4, 10), datetime.date(2012, 5, 10), datetime.date(2012, 6, 12), \
               datetime.date(2012, 7, 11), datetime.date(2012, 8, 10), datetime.date(2012, 9, 12), \
               datetime.date(2012, 10, 11), datetime.date(2012, 11, 9), datetime.date(2012, 12, 11), \
               datetime.date(2013, 1, 11), datetime.date(2013, 2, 8), datetime.date(2013, 3, 8), \
               datetime.date(2013, 4, 10), datetime.date(2013, 5, 10), datetime.date(2013, 6, 12), \
               datetime.date(2013, 7, 11), datetime.date(2013, 8, 12), datetime.date(2013, 9, 12), \
               datetime.date(2013, 11, 8), datetime.date(2013, 12, 10), datetime.date(2014, 1, 10), \
               datetime.date(2014, 2, 10), datetime.date(2014, 3, 10), datetime.date(2014, 4, 9), \
               datetime.date(2014, 5, 9), datetime.date(2014, 6, 11), datetime.date(2014, 7, 11), \
               datetime.date(2014, 8, 12), datetime.date(2014, 9, 11), datetime.date(2014, 10, 10), \
               datetime.date(2014, 11, 10), datetime.date(2014, 12, 10), datetime.date(2015, 1, 12), \
               datetime.date(2015, 2, 10), datetime.date(2015, 3, 10), datetime.date(2015, 4, 9), \
               datetime.date(2015, 5, 12), datetime.date(2015, 6, 10), datetime.date(2015, 7, 10), \
               datetime.date(2015, 8, 12), datetime.date(2015, 9, 11), datetime.date(2015, 10, 9), \
               datetime.date(2015, 11, 10), datetime.date(2015, 12, 9), datetime.date(2016, 1, 12), \
               datetime.date(2016, 2, 9), datetime.date(2016, 3, 9), datetime.date(2016, 4, 12), \
               datetime.date(2016, 5, 10), datetime.date(2016, 6, 10), datetime.date(2016, 7, 12), \
               datetime.date(2016, 8, 12), datetime.date(2016, 9, 12), datetime.date(2016, 10, 12), \
               datetime.date(2016, 11, 9), datetime.date(2016, 12, 9), datetime.date(2017, 1, 12), \
               datetime.date(2017, 2, 9), datetime.date(2017, 3, 9), datetime.date(2017, 4, 11), \
               datetime.date(2017, 5, 10), datetime.date(2017, 6, 9), datetime.date(2017, 7, 12), \
               datetime.date(2017, 8, 10), datetime.date(2017, 9, 12), datetime.date(2017, 10, 12), \
               datetime.date(2017, 11, 9), datetime.date(2017, 12, 12)]


Holiday_Map = { 'CHN': CHN_Holidays, 'PLIO': PLIO_Holidays}

product_code = {'SHFE': ['cu', 'al', 'zn', 'pb', 'wr', 'rb', 'fu', 'ru', 'bu', 'hc', 'ag', 'au', 'sn', 'ni'],
                'CFFEX': ['IF', 'TF', 'IO', 'T', 'IH', 'IC'],
                'DCE': ['c', 'cs', 'j', 'jd', 'a', 'b', 'm', 'm_Opt', 'y', 'p', 'l', 'v', 'jm', 'i', 'fb', 'bb', 'pp'],
                'CZCE': ['ER', 'RO', 'WS', 'WT', 'WH', 'PM', 'CF', 'CY', 'SR', 'SR_Opt', 'TA', 'OI', 'RI', 'ME', 'FG',
                         'RS', 'RM', 'TC', 'JR', 'LR', 'MA', 'SM', 'SF', 'ZC'],
                'SGX': ['fef'], }

CHN_Stock_Exch = {
    'SSE': ["000300", "510180", "510050", "11000011", "11000016", "11000021", "11000026", "000002", "000003", "000004",
            "000005", "000006", "11000031", "11000036", "10000036"],
    'SZE': ['399001', '399004', '399007']}

option_market_products = ['Stock_Opt', 'ETF_Opt', 'IO', 'm_Opt', 'SR_Opt']

night_session_markets = {'cu': 1,
                         'al': 1,
                         'zn': 1,
                         'pb': 1,
                         'rb': 3,
                         'hc': 3,
                         'bu': 3,
                         'sn': 1,
                         'ni': 1,
                         'ag': 2,
                         'au': 2,
                         'p': 4,
                         'j': 4,
                         'a': 4,
                         'b': 4,
                         'm': 4,
                         'm_Opt': 4,
                         'y': 4,
                         'jm': 4,
                         'i': 4,
                         'ru': 3,
                         'CF': 4,
                         'CY': 4,
                         'SR': 4,
                         'SR_Opt': 4,
                         'RM': 4,
                         'TA': 4,
                         'MA': 4,
                         'ME': 4,
                         'OI': 4,
                         'TC': 4,
                         'ZC': 4,
                         'FG': 4,
                         }

night_trading_hrs = {1: (300, 700),
                     2: (300, 830),
                     3: (300, 500),
                     4: (300, 530),
                     }

bar_shift_table1 = {1: [(1630, -15), (1800, -120)],
                    2: [(1500, -390), (1630, -15), (1800, -120)],
                    3: [(1630, -15), (1800, -120)],
                    4: [(1500, -570), (1630, -15), (1800, -120)],
                    }
product_lotsize = {'zn': 5,
                   'cu': 5,
                   'ru': 10,
                   'rb': 10,
                   'fu': 50,
                   'al': 5,
                   'au': 1000,
                   'wr': 10,
                   'pb': 25,
                   'ag': 15,
                   'bu': 10,
                   'hc': 10,
                   'WH': 20,
                   'PM': 50,
                   'CF': 5,
                   'CY': 5,
                   'SR': 10,
                   'SR_Opt': 10,
                   'TA': 5,
                   'OI': 10,
                   'RI': 20,
                   'ME': 50,
                   'MA': 10,
                   'FG': 20,
                   'RS': 10,
                   'RM': 10,
                   'TC': 200,
                   'ZC': 100,
                   'JR': 20,
                   'LR': 20,
                   'SM': 5,
                   'SF': 5,
                   'c': 10,
                   'j': 100,
                   'jd': 10,
                   'a': 10,
                   'b': 10,
                   'm': 10,
                   'm_Opt': 10,
                   'y': 10,
                   'p': 10,
                   'l': 5,
                   'v': 5,
                   'jm': 60,
                   'i': 100,
                   'fb': 500,
                   'bb': 500,
                   'pp': 5,
                   'IF': 300,
                   'IH': 300,
                   'IC': 200,
                   'TF': 10000,
                   'T': 10000,
                   'IO': 100
                   }

product_ticksize = {'zn': 5,
                    'cu': 10,
                    'ru': 5,
                    'rb': 1,
                    'fu': 1,
                    'al': 5,
                    'au': 0.01,
                    'wr': 1,
                    'pb': 5,
                    'ag': 1,
                    'bu': 2,
                    'hc': 2,
                    'WH': 1,
                    'PM': 1,
                    'CF': 5,
                    'CY': 5,
                    'SR': 1,
                    'SR_Opt': 0.5,
                    'TA': 2,
                    'OI': 2,
                    'RI': 1,
                    'ME': 1,
                    'MA': 1,
                    'FG': 1,
                    'RS': 1,
                    'RM': 1,
                    'TC': 0.2,
                    'ZC': 0.2,
                    'JR': 1,
                    'LR': 1,
                    'SF': 2,
                    'SM': 2,
                    'c': 1,
                    'j': 1,
                    'jd': 1,
                    'a': 1,
                    'b': 1,
                    'm': 1,
                    'm_Opt': 0.5,
                    'y': 2,
                    'p': 2,
                    'l': 5,
                    'v': 5,
                    'jm': 1,
                    'i': 1,
                    'fb': 0.05,
                    'bb': 0.05,
                    'pp': 1,
                    'IF': 0.2,
                    'IH': 0.2,
                    'IC': 0.2,
                    'TF': 0.005,
                    'T': 0.005,
                    'IO': 0.1
                    }


def reverse_direction(direction):
    return ORDER_SELL if direction == ORDER_BUY else ORDER_BUY


def date2xl(d):
    return (d - datetime.date(1970, 1, 1)).days + 25569.0


def datetime2xl(dt):
    t = dt - datetime.datetime(1970, 1, 1, 0, 0, 0)
    return 25569.0 + t.days + t.seconds / 60.0 / 60.0 / 24.0

def time2exp(opt_expiry, curr_time):
    curr_date = curr_time.date()
    exp_date = opt_expiry.date()
    if curr_time > opt_expiry:
        return 0.0
    elif exp_date < curr_date:
        return workdays.networkdays(curr_date, exp_date, CHN_Holidays) / BDAYS_PER_YEAR
    else:
        delta = opt_expiry - curr_time
        return (delta.hour * 3600 + delta.min * 60 + delta.second) / 3600.0 / 5.5 / BDAYS_PER_YEAR

def conv_expiry_date(curr_date, expiry, accrual = 'act365', hols = []):
    if expiry < curr_date:
        return 0.0
    year_conv = int(accrual[-3:])
    if year_conv >= 360:
        return float((expiry - curr_date).days + 1)/year_conv
    else:
        return workdays.networkdays(curr_date, expiry, hols) / float(year_conv)

def merge_dict(src_dict, dest_dict, w_src = 1, w_dest = 1):
    for key, value in src_dict.items():
        if isinstance(value, dict):
            # get node or create one
            node = dest_dict.setdefault(key, {})
            merge_dict(value, node, w_src, w_dest)
        else:
            if key not in dest_dict:
                dest_dict[key] = 0.0
            dest_dict[key] = dest_dict[key] * w_dest + value * w_src
    return dest_dict


def min2time(min_id):
    return int((min_id / 100 - 6) % 24) / 24.0 + (min_id % 100) / 1440.0


def get_tick_id(dt):
    return ((dt.hour + 6) % 24) * 100000 + dt.minute * 1000 + dt.second * 10 + dt.microsecond / 100000


def is_workday(d, calendar, we_cutoff = 5):
    return (d.weekday() < we_cutoff) and (d not in Holiday_Map.get(calendar, []))


def filter_main_cont(sdate, filter=False):
    insts, prods = dbaccess.load_alive_cont(sdate)
    if not filter:
        return insts
    main_cont = {}
    for pc in prods:
        main_cont[pc], exch = dbaccess.prod_main_cont_exch(pc)
    main_insts = []
    for inst in insts:
        pc = inst2product(inst)
        mth = int(inst[-2:])
        if mth in main_cont[pc]:
            main_insts.append(inst)
    return main_insts


def trading_hours(product, exch):
    hrs = [(1500, 1615), (1630, 1730), (1930, 2100)]
    if exch in ['SSE', 'SZE']:
        hrs = [(1530, 1730), (1900, 2100)]
    elif product in ['TF', 'T']:
        hrs = [(1515, 1730), (1900, 2115)]
    elif product in ['IF', 'IH', 'IC']:
        hrs = [(1530, 1730), (1900, 2100)]
    else:
        if product in night_session_markets:
            night_idx = night_session_markets[product]
            hrs = [night_trading_hrs[night_idx]] + hrs
    return hrs


def spreadinst2underlying(inst_name):
    spread_keys = inst_name.split(' ')
    instIDs = spread_keys[1].split('&')
    units = [1, -1]
    return (instIDs, units)


def inst2product(inst):
    if inst[2].isalpha():
        key = inst[:3]
    elif inst[1].isalpha():
        key = inst[:2]
    else:
        key = inst[:1]
    if len(inst) > 8 and (('C' in inst[5:]) or ('P' in inst[5:])):
        key = key + '_Opt'
    return key


def inst2contmth(instID):
    exch = inst2exch(instID)
    cont_mth = 0
    if exch == 'CZCE':
        cont_mth = 201000 + int(instID[-3:])
    else:
        cont_mth = 200000 + int(instID[-4:])
    return cont_mth

def inst2cont(instID):
    cont_mth = inst2contmth(instID)
    year = int(cont_mth /100)
    mth = cont_mth % 100
    return datetime.date(year, mth, 1)

def inst2exch(inst):
    if inst.isdigit():
        return "SSE"
    key = inst2product(inst)
    for exch in product_code.keys():
        if key in product_code[exch]:
            return exch
    return "NA"


def inst_to_exch(inst):
    key = inst2product(inst)
    cnx = dbaccess.connect(**dbaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange from trade_products where product_code='{prod}' ".format(prod=key)
    cursor.execute(stmt)
    out = [exchange for exchange in cursor]
    cnx.close()
    return str(out[0][0])


def get_option_map(products):
    option_map = {}
    for under in products:
        for cont_mth in products[under]:
            for strike in products[under][cont_mth]:
                for otype in ['C', 'P']:
                    key = (str(under), cont_mth, otype, strike)
                    option_map[key] = get_opt_name(under, otype, strike)
    return option_map


def get_opt_name(fut_inst, otype, strike):
    cont_mth = inst2contmth(fut_inst)
    key = (str(fut_inst), cont_mth, otype, strike)
    instID = fut_inst
    exch = inst2exch(instID)
    if instID[:2] == "IF":
        instID = instID.replace('IF', 'IO')
    if exch == 'CZCE':
        instID = instID + otype + str(int(strike))
    else:
        instID = instID + '-' + otype + '-' + str(int(strike))
    return instID


def get_opt_expiry(fut_inst, cont_mth, exch=''):
    cont_yr = int(cont_mth / 100)
    cont_mth = cont_mth % 100
    expiry_month = datetime.date(cont_yr, cont_mth, 1)
    wkday = expiry_month.weekday()
    if fut_inst[:6].isdigit():
        nbweeks = 4
        if wkday <= 2:
            nbweeks = 3
        expiry = expiry_month + datetime.timedelta(days=nbweeks * 7 - wkday + 1)
        expiry = workdays.workday(expiry, 1, CHN_Holidays)
    elif fut_inst[:2] == 'IF' or exch == 'CFFEX':
        nbweeks = 2
        if wkday >= 5:
            nbweeks = 3
        expiry = expiry_month + datetime.timedelta(days=nbweeks * 7 - wkday + 3)
        expiry = workdays.workday(expiry, 1, CHN_Holidays)
    elif fut_inst[:2] == 'SR' or fut_inst[:2] == 'CF' or exch == 'CZCE':
        if cont_mth > 1:
            expiry_month = datetime.date(cont_yr, cont_mth - 1, 1)
        else:
            expiry_month = datetime.date(cont_yr - 1, 12, 1)
        expiry = workdays.workday(expiry_month, -5, CHN_Holidays)
    elif fut_inst[:1] == 'm' or exch == 'DCE':
        if cont_mth > 1:
            expiry_month = datetime.date(cont_yr, cont_mth - 1, 1) + datetime.timedelta(days=-1)
        else:
            expiry_month = datetime.date(cont_yr - 1, 11, 30)
        expiry = workdays.workday(expiry_month, 5, CHN_Holidays)
    return datetime.datetime.combine(expiry, datetime.time(15, 0))


def nearby(prodcode, n, start_date, end_date, roll_rule, freq, need_shift=False, database='C:/Users/j291414/Desktop/market_data.db'):
    if start_date > end_date:
        return None
    cont_mth, exch = dbaccess.prod_main_cont_exch(prodcode)
    contlist = contract_range(prodcode, exch, cont_mth, start_date, day_shift(end_date, roll_rule[1:]))
    exp_dates = [day_shift(contract_expiry(cont), roll_rule) for cont in contlist]
    # print contlist, exp_dates
    sdate = start_date
    is_new = True
#    dbconf = copy.deepcopy(dbaccess.dbconfig)
#    dbconf['database'] = database
#    cnx = dbaccess.connect(**dbconf)
    cnx = sqlite3.connect(database)
    for idx, exp in enumerate(exp_dates):
        if exp < start_date:
            continue
        elif sdate > end_date:
            break
        nb_cont = contlist[idx + n - 1]

        if freq == 'd':
            new_df = dbaccess.load_daily_data_to_df(cnx, 'fut_daily', nb_cont, sdate, min(exp, end_date))
        else:
            minid_start = 1500
            minid_end = 2114
            if prodcode in night_session_markets:
                minid_start = 300
            new_df = dbaccess.load_min_data_to_df(cnx, 'fut_min', nb_cont, sdate, min(exp, end_date), minid_start,
                                                  minid_end)
        if len(new_df.shape) == 0:
            continue
        nn = new_df.shape[0]
        if nn > 0:
            new_df['contract'] = pd.Series([nb_cont] * nn, index=new_df.index)
        else:
            continue
        if is_new:
            df = new_df
            is_new = False
        else:
            if need_shift:
                if isinstance(df.index[-1], datetime.datetime):
                    last_date = df.index[-1].date()
                else:
                    last_date = df.index[-1]
                tmp_df = dbaccess.load_daily_data_to_df(cnx, 'fut_daily', nb_cont, last_date, last_date)
                shift = tmp_df['close'][-1] - df['close'][-1]
                for ticker in ['open', 'high', 'low', 'close']:
                    df[ticker] = df[ticker] + shift
            df = df.append(new_df)
        sdate = min(exp, end_date) + datetime.timedelta(days=1)
    cnx.close()
    return df


def rolling_hist_data(product, n, start_date, end_date, cont_roll, freq, win_roll='-20b', database='hist_data'):
    if start_date > end_date:
        return None
    cnx = dbaccess.connect(**dbaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange, contract from trade_products where product_code='{prod}' ".format(prod=product)
    cursor.execute(stmt)
    out = [(exchange, contract) for (exchange, contract) in cursor]
    exch = str(out[0][0])
    cont = str(out[0][1])
    cont_mth = [month_code_map[c] for c in cont]
    cnx.close()
    contlist = contract_range(product, exch, cont_mth, start_date, end_date)
    exp_dates = [day_shift(contract_expiry(cont), cont_roll) for cont in contlist]
    # print contlist, exp_dates
    sdate = start_date
    all_data = {}
    i = 0
    dbconfig = copy.deepcopy(dbaccess.dbconfig)
    dbconfig['database'] = database
    cnx = dbaccess.connect(**dbconfig)
    for idx, exp in enumerate(exp_dates):
        if exp < start_date:
            continue
        elif sdate > end_date:
            break
        nb_cont = contlist[idx + n - 1]
        if freq == 'd':
            df = dbaccess.load_daily_data_to_df(cnx, 'fut_daily', nb_cont, day_shift(sdate, win_roll),
                                                min(exp, end_date))
        else:
            df = dbaccess.load_min_data_to_df(cnx, 'fut_min', nb_cont, day_shift(sdate, win_roll), min(exp, end_date))
        all_data[i] = {'contract': nb_cont, 'data': df}
        i += 1
        sdate = min(exp, end_date) + datetime.timedelta(days=1)
    cnx.close()
    return all_data


def day_shift(d, roll_rule):
    if 'b' in roll_rule:
        days = int(roll_rule[:-1])
        shft_day = workdays.workday(d, days)
    elif 'm' in roll_rule:
        mths = int(roll_rule[:-1])
        shft_day = d + relativedelta(months=mths)
    elif 'd' in roll_rule:
        days = int(roll_rule[:-1])
        shft_day = d + datetime.timedelta(days=days)
    elif 'y' in roll_rule:
        years = int(roll_rule[:-1])
        shft_day = d + relativedelta(years=years)
    elif 'w' in roll_rule:
        weeks = int(roll_rule[:-1])
        shft_day = d + relativedelta(weeks=weeks)
    return shft_day


def contract_expiry(cont, hols='db'):
    if type(hols) == list:
        exch = inst2exch(cont)
        mth = int(cont[-2:])
        if cont[-4:-2].isdigit():
            yr = 2000 + int(cont[-4:-2])
        else:
            yr = 2010 + int(cont[-3:-2])
        cont_date = datetime.date(yr, mth, 1)
        if exch == 'DCE' or exch == 'CZCE':
            expiry = workdays.workday(cont_date - datetime.timedelta(days=1), 10, CHN_Holidays)
        elif exch == 'CFFEX':
            wkday = cont_date.weekday()
            expiry = cont_date + datetime.timedelta(days=13 + (11 - wkday) % 7)
            expiry = workdays.workday(expiry, 1, CHN_Holidays)
        elif exch == 'SHFE':
            expiry = datetime.date(yr, mth, 14)
            expiry = workdays.workday(expiry, 1, CHN_Holidays)
        elif exch in ['SGX', 'OTC']:
            expiry = workdays.workday(cont_date + relativedelta(months = 1), -1, PLIO_Holidays)
        else:
            expiry = 0
    else:
        cnx = dbaccess.connect(**dbaccess.dbconfig)
        cursor = cnx.cursor()
        stmt = "select expiry from contract_list where instID='{inst}' ".format(inst=cont)
        cursor.execute(stmt)
        out = [exp for exp in cursor]
        if len(out) > 0:
            expiry = out[0][0]
        else:
            expiry = contract_expiry(cont, CHN_Holidays)
        cnx.close()
        
        if type(expiry) != datetime.datetime and type(expiry) != datetime.date:
            expiry = datetime.datetime.strptime(expiry, '%Y-%m-%d').date()
    return expiry


def contract_range(product, exch, cont_mth, start_date, end_date):
    st_year = start_date.year
    cont_list = []
    for yr in range(st_year, end_date.year + 2):
        for mth in range(1, 13):
            if (mth in cont_mth):
                if (datetime.date(yr, mth, 28) > start_date) and (datetime.date(yr - 1, mth, 1) <= end_date):
                    if exch == 'CZCE' and datetime.date(yr, mth, 1) >= datetime.date(2010, 1, 1):
                        contLabel = product + "%01d" % (yr % 10) + "%02d" % mth
                    else:
                        contLabel = product + "%02d" % (yr % 100) + "%02d" % mth
                    cont_list.append(contLabel)
    return cont_list


def contract_range2(product, exch, cont_mth, start_date, end_date):
    st_year = start_date.year
    cont_list = []
    for yr in range(st_year, end_date.year + 2):
        for mth in range(1, 13):
            if (mth in cont_mth):
                if (datetime.date(yr, mth, 1) >= start_date) and (datetime.date(yr, mth, 1) <= end_date):
                    if exch == 'CZCE' and datetime.date(yr, mth, 1) >= datetime.date(2010, 1, 1):
                        contLabel = product + "%01d" % (yr % 10) + "%02d" % mth
                    else:
                        contLabel = product + "%02d" % (yr % 100) + "%02d" % mth
                    cont_list.append(contLabel)
    return cont_list


def get_asset_tradehrs(asset):
    exch = 'SHFE'
    for ex in product_code:
        if asset in product_code[ex]:
            exch = ex
            break
    hrs = [(1500, 1615), (1630, 1730), (1930, 2100)]
    if exch in ['SSE', 'SZE']:
        hrs = [(1530, 1730), (1900, 2100)]
    elif asset in ['TF', 'IF']:
        hrs = [(1515, 1730), (1900, 2115)]
    else:
        if asset in night_session_markets:
            night_idx = night_session_markets[asset]
            hrs = [night_trading_hrs[night_idx]] + hrs
    return hrs


def cleanup_mindata(df, asset, index_col='datetime', skip_hl=True):
    cond = None
    if index_col == None:
        xdf = df.set_index('datetime')
    else:
        xdf = df
    tradehrs = get_asset_tradehrs(asset)
    for idx, hrs in enumerate(tradehrs):
        if idx == 0:
            cond = (xdf.min_id >= tradehrs[idx][0]) & (xdf.min_id < tradehrs[idx][1])
        else:
            cond = cond | (xdf.min_id >= tradehrs[idx][0]) & (xdf.min_id < tradehrs[idx][1])
    if asset in ['a', 'b', 'p', 'y', 'm', 'i', 'j', 'jm']:
        cond = cond | (
        (xdf.index < datetime.datetime(2015, 5, 12, 15, 0, 0)) & (xdf.min_id >= 300) & (xdf.min_id < 830))
    if asset in ['rb', 'hc', 'bu']:
        cond = cond | ((xdf.index < datetime.datetime(2016, 5, 1, 15, 0, 0)) & (xdf.min_id >= 300) & (xdf.min_id < 700))
    if asset in ['IF', 'IH', 'IC']:
        cond = cond | (
        (xdf.index < datetime.datetime(2016, 1, 1, 15, 0, 0)) & (xdf.min_id >= 1515) & (xdf.min_id < 1530))
        cond = cond | (
        (xdf.index < datetime.datetime(2016, 1, 1, 15, 0, 0)) & (xdf.min_id >= 2100) & (xdf.min_id < 2115))
    xdf = xdf.ix[cond]
    xdf = xdf[(xdf.close > 0) & (xdf.high > 0) & (xdf.open > 0) & (xdf.low > 0)]
    if skip_hl:
        xdf = xdf[xdf.high > xdf.low]
    if index_col == None:
        xdf = xdf.reset_index()
    return xdf

def send_mail(mail_account, to_list, sub, content):
    mail_host = mail_account['host']
    mail_user = mail_account['user']
    mail_pass = mail_account['passwd']
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = mail_user
    msg['To'] = ';'.join(to_list)
    try:
        smtp = smtplib.SMTP(mail_host, 587)
        # smtp.ehlo()
        smtp.starttls()
        # smtp.ehlo()
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(mail_user, to_list, msg.as_string())
        smtp.close()
        return True
    except Exception, e:
        print "exception when sending e-mail %s" % str(e)
        return False
