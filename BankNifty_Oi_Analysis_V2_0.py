

"""
# -*- coding: utf-8 -*-

#Created on Mon Apr  3 14:16:46 2023

#@author: 91875
"""

import requests
import json
import pandas as pd
from requests import sessions
import xlwings as xw
from time import sleep
from datetime import datetime, time, timedelta
import os
import heapq
import numpy as np
from zoneinfo import ZoneInfo

#Setting up the Width, Max Columns and Max Rows for displaying the results

pd.set_option('display.width', 1500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows',20)

#NSE URL and Expirty
url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
expiry = "13-Dec-2023" #Dec 13, 20, 28, Jan 03

excel_file = "OptionChain_Analysis_BN.xlsx"
wb = xw.Book(excel_file)
main_sht = wb.sheets('OI_Data')
sht_live = wb.sheets('Data')
#pe_sht = wb.sheets('PE_Data')
#ce_sht = wb.sheets('CE_Data')
Underlying_Man_BN =     47421  #+/- 1200


#Headers for WebScrapper
headers = {
    'user-agent'      : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78",
    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-US,en;q=0.9'
}

cookies = {
    "bm_sv" : "D6B2AB980F922C484578437A17524F65~YAAQTpUvF2cPGHmJAQAAD2vblxQ0YCSbMy687xFCiNHQE2McMaEZyVJtwg/fymDh1zcHH2HSy4mcxhg0XCPyrElo+6HcyzqQbBJgHsp3yQQ/+FqomHQzESW1KUzEJJiUJJBdEudR5PEvtO2gH+xcJZTDnVVyehjs+V7G09154uHdgd6rMlGbpe3KfzrVBzKm/TPhSFUMk7Pe6V4K24H29xTb623WiI1qJsGUJs3YXvTe3o7C36otwFKP/P3y+eYBglw=~1"
}

currdttime = datetime.now().strftime("%d%m%y")
print(currdttime)
#dflist = []
mp_list = []

#Defining filename statement for the json files
oi_filename = os.path.join("Files","oi_data_records_BN_{0}.json".format(currdttime))
mp_filename = os.path.join("Files","mp_data_records_BN_{0}.json".format(currdttime))

def fetch_oi(df,mp_df):
    #removed df4, dfce and dfpe in above step
    tries =1
    max_tries =3
    while tries <= max_tries:
        try:
            session = requests.Session()
            response = session.get(url,headers=headers,cookies=cookies).json()

    #Converting repsponse to Pandas DataFrame
            dfr = pd.DataFrame(response)
            

    #Extracting Call and Put options chain details by Expirty in LIST Format in the Output
            if expiry:
                ce_values = [data['CE'] for data in dfr['records']['data'] if "CE" in data and
                                str(data['expiryDate']).lower() == str(expiry).lower()]
                pe_values = [data['PE'] for data in dfr['records']['data'] if "PE" in data and
                                str(data['expiryDate']).lower() == str(expiry).lower()]
    #pe_values = [data['PE'] for data in dfr['records']['data'] if "PE" in data]
            else:
                ce_values = [data['CE'] for data in dfr['filtered']['data'] if "CE" in data]
                pe_values = [data['PE'] for data in dfr['filtered']['data'] if "PE" in data]
    #"Provider=Microsoft.ACE.OLEDB.12.0;Data Source=xx.xls;Extended Properties='Excel 12.0 Xml;HDR=YES;'"

    #Converting List Ouput into DataFrame
            ce_data = pd.DataFrame(ce_values)
            pe_data = pd.DataFrame(pe_values)
            
    #Filtering Options Chain
            print("Error in 1st instance, if error below")
            uplimit = (Underlying_Man_BN + 1200)
            lowlimit = (Underlying_Man_BN - 1200)
            ce_data2 = ce_data.loc[(ce_data['strikePrice'] < uplimit) & (ce_data['strikePrice'] > lowlimit)]
            pe_data2 = ce_data.loc[(pe_data['strikePrice'] < uplimit) & (pe_data['strikePrice'] > lowlimit)]


    #Sortnig the DataFrame by StrikePRice
            ce_srt = ce_data2.sort_values(['strikePrice'])
            pe_srt = pe_data2.sort_values(['strikePrice'])

    #Writing DataFrame into Excel
            main_sht.range("A2").options(index =False,header=False).value = ce_srt.drop(
                ['askPrice','askQty','bidQty','bidprice','expiryDate','identifier',
                'totalBuyQuantity','totalSellQuantity','totalTradedVolume','underlying','underlyingValue'],axis=1)[
                ['openInterest','changeinOpenInterest','pchangeinOpenInterest','impliedVolatility','lastPrice','change','pChange','strikePrice']]
            main_sht.range("I2").options(index =False,header=False).value = pe_srt.drop(['askPrice','askQty','bidQty',
                'bidprice','expiryDate','identifier','totalBuyQuantity','totalSellQuantity','totalTradedVolume','underlying','underlyingValue'],axis=1)[
                ['openInterest','changeinOpenInterest','pchangeinOpenInterest','impliedVolatility','lastPrice','change','pChange']]

    #Duplicate Check to avoid duplicates due to delay in refresh - as we fetch every 3minute

            ce_data['type'] = "CE"
            pe_data['type'] = "PE"
            df1 = pd.concat(objs=[ce_data, pe_data],axis=0)


            if len(dflist) > 0:
                #C
                df1['Time'] = dflist[-1][0]['Time']
            if len(dflist) > 0 and df1.to_dict('records') == dflist[-1]:
                print("Duplicates , Not Recording")
                sleep(2)
                tries += 1
                continue
            df1['Time'] = datetime.now().strftime("%H:%M")
            pcr = pe_data['totalTradedVolume'].sum()/ce_data['totalTradedVolume'].sum()
            mp_dict = {datetime.now().strftime("%H:%M") : {'underlying': (df1['underlyingValue'].iloc[-1]).astype(int),
                                                           'MaxPain' : wb.sheets("Dashboard").range("H8").value,
                                                           'pcr': pcr,
                                                           'call_decay' : ce_data.nlargest(10,'openInterest',keep='last')['change'].mean(),
                                                           'put_decay'  : pe_data.nlargest(10,'openInterest',keep='last')['change'].mean(),
                                                           },}
            df3 = pd.DataFrame(mp_dict).transpose()

            mp_df = pd.concat([mp_df,df3])
            wb.sheets['MPData'].range('A2').options(header=False).value = mp_df

            with open(mp_filename, 'w') as files:
                files.write(json.dumps(mp_df.to_dict(), indent=4, sort_keys=True))

            if not df.empty:
                df = df[
                         ['strikePrice', 'expiryDate', 'underlying','identifier','openInterest','changeinOpenInterest',
                        'pchangeinOpenInterest', 'totalTradedVolume','impliedVolatility', 'lastPrice', 'change','pChange'
                        ,'totalBuyQuantity','totalSellQuantity','bidQty', 'bidprice', 'askQty', 'askPrice','underlyingValue','type','Time'
                             ]]
            df1 = df1[
                      ['strikePrice', 'expiryDate', 'underlying', 'identifier', 'openInterest', 'changeinOpenInterest',
                     'pchangeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice', 'change', 'pChange'
                        , 'totalBuyQuantity', 'totalSellQuantity', 'bidQty', 'bidprice', 'askQty', 'askPrice',
                     'underlyingValue', 'type', 'Time'
                       ]]


    #df is the empty dataset in first run and it will be appended to df1 new dataset
            df = pd.concat([df,df1])
            #Dropping NaN and Inf values (INVALID values)
            mp_df = mp_df.dropna(axis=1)
            #print('after dropna', mp_df)
            #Conveting the flaot data type to int data type
            mp_df = mp_df.astype({'MaxPain': int})
            #print('after dropna', mp_df)
           # print("MP_DF",mp_df['MaxPain'])
            #maxpain_index = mp_df.columns.get_loc('MaxPain')
            #print("maxpain_index",maxpain_index)

            #Mmp_df.iloc[-1, 'maxpain_index'])
            #print("MP_DF Value: ",mp_df.iloc[-1,'maxpain_index'])
            #Creating new DF df4 with upper and lower limits.
            print("Error in 2nd instance, if error below")
            uplimit = (Underlying_Man_BN + 1200)
            lowlimit = (Underlying_Man_BN - 1200)
            #Getting the column(axis =1) index for uplimit and lower limit
            #uplimit_index = df4.columns.get_loc('uplimit')
            #lowlimit_index = df4.columns.get_loc('lowlimit')
            #print('lowlimit_index',lowlimit_index,'uplimit_index',uplimit_index)
            #Filtering strike prices between upper and lower limits
            df = df.loc[(df['strikePrice'] < uplimit) & (df['strikePrice'] > lowlimit)]
            #print("Up limit", df4['uplimit'], "Low limit", df4['lowlimit'])
         #   dfce = df[df['type']=='CE']
         #   dfpe = df[df['type']=='PE']
            df = df.drop_duplicates()
            dflist.append(df.to_dict('records'))
            with open (oi_filename,'w') as files:
                files.write(json.dumps(dflist, indent= 4, sort_keys=True))
            return df,mp_df
        #removed df4, dfce and dfpe in above step
        except Exception as err:
            print("Error {0}".format(err))
            tries += 1
            sleep(10)
            continue
    if tries >= max_tries:
        print("Max tries reached. No new data at time {0}",format(datetime.now()))
        return df,mp_df
    #removed df4, dfce and dfpe in above step


def main():
    global dflist
    #global df4
    #global uplimit
    #global lowlimit
    try:
        dflist = json.loads(open(oi_filename).read())

    except Exception as error:
        print("Error reading data. Error: {}".format(error))
        dflist =[]
    if dflist:
        df = pd.DataFrame()
       # df4 = pd.DataFrame()
        #dfce = pd.DataFrame()
        #dfpe = pd.DataFrame()

        #uplimit = 20000

        #lowlimit = 15000
        for items in dflist:
            df = pd.concat([df, pd.DataFrame(items)])
            #print(df)
    else:
        df = pd.DataFrame()
      #  df4 = pd.DataFrame()
        #dfce = pd.DataFrame()
        #dfpe = pd.DataFrame()
        #uplimit = 20000
        #lowlimit =15000
    try:
        mp_list = json.loads(open(mp_filename).read())
        mp_df   = pd.DataFrame().from_dict(mp_list)
    except Exception as errorr:
        print("Error reading data. Error: {0}".format(errorr))
        mp_list = []
        mp_df = pd.DataFrame()
    timeframe = 3
    while time(9,15) <= datetime.now().time() <= time(15,30):
        timenow = datetime.now()
        check = True if timenow.minute/timeframe in list(np.arange(0.0,60.0)) else False
        if check:
            nextscan = timenow + timedelta(minutes=timeframe)
            df,mp_df = fetch_oi(df,mp_df)
            #removed df4, dfce and dfpe in above step
    #To replace zeros in the df dataframe and to have a clean chart

    #print("DF4 table",df4)
            if not df.empty:
                df['impliedVolatility'] = df['impliedVolatility'].replace(to_replace=0, method='bfill').values
                df['identifier']  = df['strikePrice'].astype(str)+df['type']
                df_dedup = df.drop_duplicates()                
                #fil_df= df.query('strikePrice < uplimit & strikePrice > lowlimit')
                sht_live.range("A1").value = df_dedup[['Time','askPrice','askQty','bidQty','bidprice','change','changeinOpenInterest','expiryDate','identifier','impliedVolatility',
                                                'openInterest','pChange','pchangeinOpenInterest','strikePrice','totalBuyQuantity','totalSellQuantity','totalTradedVolume',
                                                'type','underlying','underlyingValue','lastPrice']]

               # ce_sht.range("A2").value = dfce
               # pe_sht.range("A2").value = dfpe
                wb.api.RefreshAll()
                waitsecs = int((nextscan - datetime.now()).seconds)
                print("Waiting for {0} seconds ** nextscan {1} ** datetimenow {2}".format(waitsecs,nextscan,datetime.now()))
                if waitsecs > 180:
                    waitsecs = 25
                sleep(waitsecs) if waitsecs > 0 else sleep(0)
            else:
                print("No data received")
                sleep(30)



if __name__ == '__main__':
   main()
