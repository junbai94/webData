# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 17:15:54 2017

@author: Junbai

+++++++++++++++++                MANUAL                +++++++++++++++++++++++

This file create a standard database for storing Cargill metal data. Change 
dbPath variable to destination you prefer. For loading data, please refer to
python script <histdata_xlloader>
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

import dbaccess

DB_PATH = "C:/dev/pycmqlib/market_data.db"

#------------------------------CREATE TABLES-----------------------------------
fut_daily = \
'''
CREATE TABLE fut_daily (
    instID       VARCHAR (30)     NOT NULL,
    exch         VARCHAR (10)     NOT NULL,
    date         DATE             NOT NULL,
    open         DECIMAL (12, 4),
    close        DECIMAL (12, 4),
    high         DECIMAL (12, 4),
    low          DATETIME (12, 4),
    volume       INTEGER (11),
    openInterest INTEGER (11),
    PRIMARY KEY (
        instID,
        exch,
        date
    )
    ON CONFLICT REPLACE
);
'''

spot_daily = \
'''
CREATE TABLE spot_daily (
    spotID VARCHAR (30)    NOT NULL,
    date   DATE            NOT NULL,
    close  DECIMAL (12, 4),
    PRIMARY KEY (
        spotID,
        date
    )
    ON CONFLICT REPLACE
);
'''

fx_daily = \
'''
CREATE TABLE fx_daily (
    date  DATE,
    ccy   VARCHAR,
    tenor VARCHAR,
    rate  DECIMAL,
    src   VARCHAR,
    PRIMARY KEY (
        date,
        ccy,
        tenor
    )
    ON CONFLICT REPLACE
);
'''
def create_db( db_path = DB_PATH):
    conn = dbaccess.connect(database =  db_path)
    cursor = conn.cursor()
    cursor.execute(fut_daily)
    cursor.execute(spot_daily)
    cursor.execute(fx_daily)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    pass