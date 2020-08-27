#!/usr/bin/env python
# coding: utf-8

# In[1]:


import flask
import datetime
from kiteconnect import KiteConnect
from flask_cors import CORS, cross_origin
from flask import request
import json
import pandas as pd
import datetime
from datetime import date
import numpy as np
from scipy.stats import norm
import os
import re

# In[2]:
app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
cors=CORS(app, resources={
           r"/*" : { "origin" : "*"}	
})
#def _corsify_actual_response(response):
#    response.headers.add("Access-Control-Allow-Origin", "*")
#    return response


# In[3]:


def getltp(x,kite) : #FUNCTION TO GET LAST TRADING PRICE OF FUTURE CONTRACT
    Exchange = x['exchange']
    Symbol = x['tradingsymbol']
    Symbol = Exchange + ':' + Symbol
    return kite.ltp([Symbol])[Symbol]['last_price']


# In[4]:


def roundoffnumbers(FINAL) :
    FINAL['CE'] = round(FINAL['CE'] * 10)/10
    #FINAL['CE_Offer'] = round(FINAL['CE_Offer'] * 10)/10
    FINAL['PE'] = round(FINAL['PE'] * 10)/10
    #FINAL['PE_Offer'] = round(FINAL['PE_Offer'] * 10)/10
    
    return FINAL


# In[5]:


def get_strikes(All_Strikes , NoofContracts , LTP) : #FUNCTION TO GET +-VAL STRIKES FROM ATM
    list=[]
    temp_list=[]
    val1=NoofContracts+1
    val2=NoofContracts
    for i in All_Strikes :
        if(i>=LTP and val1>0):
            list.append(i)
            val1=val1-1

        elif(i<LTP):
            temp_list.append(i)

    temp_list.sort(reverse=True)
    
    for i in temp_list :
        if(val2>0) :
            list.append(i)
            val2=val2-1

    list.sort()
    
    return list


# In[6]:


class Straddle() : 
    
    @staticmethod
    def operate(FINAL,parameter):
        columnName = 'straddle'
        FINAL[columnName] = FINAL['CE'] + FINAL['PE']

class Strangle() :
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'strangle' + str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if(index < multiplier or (FINAL.shape[0]-index-1) < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['CE'][index+multiplier] + FINAL['PE'][index-multiplier]

class IronFly() :                
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'IF' + str(multiplier)
        strangle = FINAL['CE'] + FINAL['PE']
        for index in FINAL.index : 
            if(index < multiplier or (FINAL.shape[0]-index-1) < multiplier): 
                strangle[index] = np.nan
            else :
                strangle[index] = strangle[index] - (FINAL['CE'][index+multiplier] + FINAL['PE'][index-multiplier])
        FINAL[columnName] = strangle
    
    
class PutButterFly() :
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'PBF' + str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if(index < multiplier or (FINAL.shape[0]-index-1) < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['PE'][index-multiplier] + FINAL['PE'][index+multiplier] - FINAL['PE'][index]*2


class CallButterFly() :
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'CBF' + str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if(index < multiplier or (FINAL.shape[0]-index-1) < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['CE'][index-multiplier] + FINAL['CE'][index+multiplier] - FINAL['CE'][index]*2

                
class PutSpread() :
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'PS' + str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if(index < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['PE'][index-multiplier] - FINAL['PE'][index]

class CallSpread() :
    @staticmethod
    def operate(FINAL,parameter):
        multiplier = int(parameter[1])
        columnName = 'CS' + str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if((FINAL.shape[0]-index-1) < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['CE'][index+multiplier] - FINAL['CE'][index]
    
class PutRatio() :
    @staticmethod
    def operate(FINAL,parameter):
        ratio_numerator = int(parameter[1])
        ratio_denominator = int(parameter[2])
        multiplier = int(parameter[3])
        columnName = 'PR'+str(ratio_numerator)+'/'+str(ratio_denominator)+'-'+str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if(index < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['PE'][index-multiplier]*ratio_denominator - FINAL['PE'][index]*ratio_numerator

class CallRatio() :
    @staticmethod
    def operate(FINAL,parameter):
        ratio_numerator = int(parameter[1])
        ratio_denominator = int(parameter[2])
        multiplier = int(parameter[3])
        columnName = 'CR'+str(ratio_numerator)+'/'+str(ratio_denominator)+'-'+str(multiplier)
        FINAL[columnName] = 0
        for index in FINAL.index : 
            if((FINAL.shape[0]-index-1) < multiplier): 
                FINAL[columnName][index] = np.nan
            else :
                FINAL[columnName][index] = FINAL['CE'][index+multiplier]*ratio_denominator - FINAL['CE'][index]*ratio_numerator


# In[ ]:





# In[7]:


def fetch_data(SCRIPT , Expirydate , NoofContracts , Strikedifference , accessToken, strategies , api_key) :
    
    #api_key = "tg48gdykr12ezopp"
    #api_secret = "wgwq9kgfly6ky19j43w2g5kvxpdjb44g"

    kite = KiteConnect(api_key=api_key) 
    kite.set_access_token(accessToken)
    instrument=kite.instruments()
   
    from scipy.stats import norm
    df = pd.DataFrame(instrument)
    
    Script_CE = df[(df.name==SCRIPT) & (df.expiry==Expirydate) & (df.instrument_type=='CE')]
    Script_PE = df[(df.name==SCRIPT) & (df.expiry==Expirydate) & (df.instrument_type=='PE')]
    Script_FUT = df[(df.name==SCRIPT) & (df.instrument_type=='FUT')]
    
    Script_CE = Script_CE.sort_values(by=['strike'])
    Script_PE = Script_PE.sort_values(by=['strike'])
    Script_FUT = Script_FUT.sort_values(by=['expiry'])
    
    All_Strikes = Script_CE.strike
    All_Strikes = All_Strikes[All_Strikes%Strikedifference==0]
    FUT_LTP = getltp(Script_FUT.iloc[0],kite)
    FUT_LTP = round(FUT_LTP/Strikedifference)*Strikedifference 
    
    reqd_strikes = get_strikes(All_Strikes , NoofContracts , FUT_LTP) 
    Script_CE = Script_CE[Script_CE.strike.isin(reqd_strikes) ]
    Script_PE = Script_PE[Script_PE.strike.isin(reqd_strikes)]
    Script_CE = Script_CE[['strike' , 'tradingsymbol' , 'exchange']]
    Script_PE = Script_PE[['strike' , 'tradingsymbol' , 'exchange']]
    
    Script_CE['CE_Bid'] = 0
    Script_CE['CE_Offer'] = 0
    Script_CE['CE']=0

    Script_PE['PE_Bid'] = 0
    Script_PE['PE_Offer'] = 0
    Script_PE['PE']=0
    
    Script_CE.tradingsymbol = Script_CE.exchange + ':' + Script_CE.tradingsymbol
    Script_PE.tradingsymbol = Script_PE.exchange + ':' + Script_PE.tradingsymbol
    Script_CE.reset_index(drop=True , inplace=True)
    Script_PE.reset_index(drop=True , inplace=True)
    list=[]
    list.extend(Script_CE['tradingsymbol'].to_list())
    list.extend(Script_PE['tradingsymbol'].to_list())
        
    temp = kite.quote(list)
    
    for i in Script_CE.tradingsymbol :
        y = temp[i]['depth']['buy'][0]['price']
        x = temp[i]['depth']['sell'][0]['price']
        Script_CE.loc[Script_CE.tradingsymbol == i , ['CE_Bid' , 'CE_Offer']] = [y,x]

    for i in Script_PE.tradingsymbol :
        y = temp[i]['depth']['buy'][0]['price']
        x = temp[i]['depth']['sell'][0]['price']
        Script_PE.loc[Script_PE.tradingsymbol == i , ['PE_Bid' , 'PE_Offer']] = [y,x]

    Script_CE.CE = (Script_CE.CE_Bid + Script_CE.CE_Offer)/2
    Script_PE.PE = (Script_PE.PE_Bid + Script_PE.PE_Offer)/2

    del Script_CE['tradingsymbol']
    del Script_CE['exchange']
    del Script_PE['tradingsymbol']
    del Script_PE['exchange']
    del Script_CE['CE_Bid']
    del Script_CE['CE_Offer']
    del Script_PE['PE_Bid']
    del Script_PE['PE_Offer']
    
    FINAL = pd.merge(Script_CE , Script_PE , on='strike')
    FINAL = roundoffnumbers(FINAL)
    
    registry = {'straddle' : Straddle(), 'strangle' : Strangle(), 
                'ironFly' : IronFly(), 'putButterfly' : PutButterFly(),
                'callButterfly' : CallButterFly(), 'putSpread' : PutSpread(), 'callSpread' : CallSpread(),
                'putRatio' : PutRatio(), 'callRatio' : CallRatio()}
    
    for strategy,parameters in strategies.items() :
        #print(strategy)
        #print(parameters)
        temp = re.compile("([a-zA-Z]+)([0-9]+)") 
        strategyName = temp.match(strategy).groups()[0]
        if(strategyName == "IF"):
            strategyName = "ironFly"
        elif(strategyName == "PBF"):
            strategyName = "putButterfly"
        elif(strategyName == "CBF"):
            strategyName = "callButterfly"
        elif(strategyName == "PS"):
            strategyName = "putSpread"
        elif(strategyName == "CS"):
            strategyName = "callSpread"
        elif(strategyName == "PR"):
            strategyName = "putRatio"
        elif(strategyName == "CR"):
            strategyName = "callRatio"
        
        registry[strategyName].operate(FINAL, parameters)
        #print(strategy, parameters)
        #for i in parameters:
        #    print(parameters)
        #    registry[strategy].operate(FINAL, i)
    
    JSONOBJECT = FINAL.to_json(orient='records')
    return JSONOBJECT


# In[8]:


@app.route('/expiry', methods=['GET'])
def home2() :
    #api_key = "tg48gdykr12ezopp"
    #api_secret = "wgwq9kgfly6ky19j43w2g5kvxpdjb44g"

    
    if 'accessToken' in request.args:
        accessToken = str(request.args['accessToken'])
        print(accessToken)

    if 'API_Key' in request.args :
        api_key = str(request.args['API_Key'])
        print(api_key)

    kite = KiteConnect(api_key=api_key) 
    kite.set_access_token(accessToken)
    instrument=kite.instruments()
    
    df = pd.DataFrame(instrument)
    Expiry = df[(df.name=='NIFTY')].expiry.unique()
    Expiry.sort()
    for i in range(0,len(Expiry)) :
        Expiry[i] = Expiry[i].strftime('%Y-%m-%d')
        #print(Expiry)
    Expiry = Expiry.tolist()
    expiry = json.dumps(Expiry)
    return expiry


# In[9]:


@app.route('/strategies', methods=['GET'])
def home():

    print("START")
    if 'ticker' in request.args:
        ticker = str(request.args['ticker'])
        print(ticker)
    if 'expiry' in request.args:
        expiryTemp = str(request.args['expiry'])
        expiry = datetime.datetime.strptime(expiryTemp,'%Y-%m-%d').date()
        print(expiry)
    if 'strikeDistance' in request.args:
        strikeDistance = int(request.args['strikeDistance'])
        print(strikeDistance)
    if 'totContracts' in request.args:
        totContracts = int(request.args['totContracts'])
        print(totContracts)
    if 'accessToken' in request.args:
        accessToken = str(request.args['accessToken'])
        print(accessToken)
    if 'strategies' in request.args:
        strategies = request.args['strategies']
        strategiesJSON = json.loads(strategies)
        print(strategiesJSON)

    if 'API_Key' in request.args :
        api_key = str(request.args['API_Key'])
        print(api_key)
    
    data = fetch_data(ticker,expiry,totContracts,strikeDistance,accessToken, strategiesJSON , api_key)
    print("END")
    
    return data
    
port = int(os.environ.get('PORT',5000))
app.run(host = '0.0.0.0', port=port)


# In[10]:


#strategies = {
#   'strangle' : [[1],[2]]
#}


# In[11]:


#x = fetch_data("NIFTY", datetime.date(2020,8,20), 20, 50, "Dsn7nhMlhdrMPxcfDQtVJkPJjmkXezqB", strategies)


# In[12]:


#x


# In[ ]:

#Dsn7nhMlhdrMPxcfDQtVJkPJjmkXezqB - 21-8-2020


