import flask
import datetime
from kiteconnect import KiteConnect
from flask_cors import CORS, cross_origin
from flask import request
import os
import json
import pandas as pd
from flask_pymongo import PyMongo
import pymongo
from scipy.stats import norm
import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.config["MONGO_URI"] = "mongodb://tathagat:tathagat2000@ds139844.mlab.com:39844/heroku_lns9vp7k?retryWrites=false"
mongo = PyMongo(app)    


# myclient = pymongo.MongoClient("mongodb://localhost:27017/")

# mydb = myclient["python"]

# mycol = mydb["demo1"]

CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
cors=CORS(app, resources={
           r"/*" : { "origin" : "*"}	
})
#def _corsify_actual_response(response):
#    response.headers.add("Access-Control-Allow-Origin", "*")
#    return response

def getltp(x,kite) : #FUNCTION TO GET LAST TRADING PRICE OF FUTURE CONTRACT
  Exchange = x['exchange']
  Symbol = x['tradingsymbol']
  Symbol = Exchange + ':' + Symbol
  return kite.ltp([Symbol])[Symbol]['last_price']

def roundoffnumbers(FINAL) :
  FINAL['CE_Vega'] = round(FINAL['CE_Vega'] * 100)/100
  FINAL['CE_Vol'] = round(FINAL['CE_Vol']/10000)
  FINAL['CE_Vol'] = FINAL['CE_Vol'].astype(int)
  FINAL['CE_Bid'] = round(FINAL['CE_Bid'] * 10)/10
  FINAL['CE_Offer'] = round(FINAL['CE_Offer'] * 10)/10
  FINAL['CE_Theta'] = round(FINAL['CE_Theta'] * 100)/100
  FINAL['CE_Delta'] = round(FINAL['CE_Delta'] * 100)/100
  FINAL['CE_IV'] = round(FINAL['CE_IV'] * 100)/100
  FINAL['Smile'] = round(FINAL['Smile'] * 100)/100
  FINAL['SynFut'] = round(FINAL['SynFut'] * 100)/100
  FINAL['PE_Vega'] = round(FINAL['PE_Vega'] * 100)/100
  FINAL['PE_Theta'] = round(FINAL['PE_Theta'] * 100)/100
  FINAL['PE_Delta'] = round(FINAL['PE_Delta'] * 100)/100
  FINAL['PE_IV'] = round(FINAL['PE_IV'] * 100)/100
  FINAL['CE_Gamma'] = round(FINAL['CE_Gamma']*1000000)/100
  FINAL['PE_Gamma'] = round(FINAL['PE_Gamma']*1000000)/100
  FINAL['PE_Bid'] = round(FINAL['PE_Bid'] * 10)/10
  FINAL['PE_Offer'] = round(FINAL['PE_Offer'] * 10)/10
  FINAL['PE_Vol'] = round(FINAL['PE_Vol']/10000)
  FINAL['PE_Vol'] = FINAL['PE_Vol'].astype(int)
  FINAL['SynFut'] = round(FINAL['SynFut']/1)*1
  FINAL['strike'] = FINAL['strike'].astype(int)
  FINAL['SynFut'] = FINAL['SynFut'].astype(int)

  return FINAL



def get_strikes(All_Strikes , NoofContracts , LTP) : #FUNCTION TO GET +-VAL STRIKES FROM ATM
  list=[]
  temp_list=[]
  val1=NoofContracts+1
  val2=NoofContracts
  for i in All_Strikes :
    if(i>=LTP and val1>0) :
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

def fetch_data(SCRIPT , Expirydate , NoofContracts , Strikedifference , accessToken) :

  api_key = "tg48gdykr12ezopp"
  api_secret = "wgwq9kgfly6ky19j43w2g5kvxpdjb44g"

  kite = KiteConnect(api_key=api_key) 
  kite.set_access_token(accessToken)
  
  y = mongo.db.instruments.find_one()
  del(y['_id'])
  df = pd.read_json(y["instrument"],orient='records')
  for i in range(0,len(df['expiry'])):
    new_val = datetime.datetime.strptime(df.expiry.loc[i],'%Y-%m-%d').date()
    df.expiry.loc[i] = new_val
  
  Script_CE = df[(df.name==SCRIPT) & (df.expiry==Expirydate) & (df.instrument_type=='CE')]
  Script_PE = df[(df.name==SCRIPT) & (df.expiry==Expirydate) & (df.instrument_type=='PE')]
  Script_FUT = df[(df.name==SCRIPT) & (df.instrument_type=='FUT')]

  

  Script_CE = Script_CE.sort_values(by=['strike'])
  Script_PE = Script_PE.sort_values(by=['strike'])
  Script_FUT = Script_FUT.sort_values(by=['expiry'])

  FUT_LTP = getltp(Script_FUT.iloc[0],kite)
  FUT_LTP = round(FUT_LTP/Strikedifference)*Strikedifference 
  All_Strikes = Script_CE.strike
  All_Strikes = All_Strikes[All_Strikes%Strikedifference==0]


  reqd_strikes = get_strikes(All_Strikes , NoofContracts , FUT_LTP) 
  Script_CE = Script_CE[Script_CE.strike.isin(reqd_strikes) ]
  Script_PE = Script_PE[Script_PE.strike.isin(reqd_strikes)]
  Script_CE = Script_CE[['strike' , 'tradingsymbol' , 'exchange']]
  Script_PE = Script_PE[['strike' , 'tradingsymbol' , 'exchange']]


  Script_CE['CE_Bid'] = 0
  Script_CE['CE_Offer'] = 0
  Script_CE['CE_Mid'] = 0
  Script_CE['CE_IV'] = 0
  Script_CE['CE_Delta'] = 0
  Script_CE['CE_Gamma'] = 0
  Script_CE['CE_Vega'] = 0
  Script_CE['CE_Theta'] = 0
  Script_CE['CE_OI']=0
  Script_CE['CE_Vol']=0
  Script_CE['SynFut']=0

  Script_PE['PE_Bid'] = 0
  Script_PE['PE_Offer'] = 0
  Script_PE['PE_Mid'] = 0
  Script_PE['PE_IV'] = 0
  Script_PE['PE_Delta'] = 0
  Script_PE['PE_Gamma'] = 0
  Script_PE['PE_Vega'] = 0
  Script_PE['PE_Theta'] = 0
  Script_PE['PE_OI']=0
  Script_PE['PE_Vol']=0
  Script_PE['PE_SyntheticFut']=0

  Script_CE.tradingsymbol = Script_CE.exchange + ':' + Script_CE.tradingsymbol
  Script_PE.tradingsymbol = Script_PE.exchange + ':' + Script_PE.tradingsymbol
  Script_CE.reset_index(drop=True , inplace=True)
  Script_PE.reset_index(drop=True , inplace=True)
  list=[]
  list.extend(Script_CE['tradingsymbol'].values.tolist())
  list.extend(Script_PE['tradingsymbol'].values.tolist())
  temp = kite.quote(list)

  for i in Script_CE.tradingsymbol :
    z = temp[i]['depth']['buy'][0]['price']
    x = temp[i]['depth']['sell'][0]['price']
    y = temp[i]['oi']
    q = temp[i]['volume']
    Script_CE.loc[Script_CE.tradingsymbol == i , ['CE_Bid' , 'CE_Offer' , 'CE_OI' , 'CE_Vol']] = [z,x,y,q]

  for i in Script_PE.tradingsymbol :
    z = temp[i]['depth']['buy'][0]['price']
    x = temp[i]['depth']['sell'][0]['price']
    y = temp[i]['oi']
    q = temp[i]['volume']
    Script_PE.loc[Script_PE.tradingsymbol == i , ['PE_Bid' , 'PE_Offer' , 'PE_OI' , 'PE_Vol']] = [z,x,y,q]

  Script_CE.CE_Mid = (Script_CE.CE_Bid + Script_CE.CE_Offer)/2
  Script_PE.PE_Mid = (Script_PE.PE_Bid + Script_PE.PE_Offer)/2


  for i in Script_CE.strike:
    putprice = Script_PE[Script_PE.strike==i].PE_Mid
    callprice = Script_CE[Script_CE.strike==i].CE_Mid
    Script_CE.loc[Script_CE.strike==i , 'SynFut'] = i+callprice-putprice

  Script_PE.PE_SyntheticFut = Script_CE.SynFut

  from datetime import date
  today = (datetime.datetime.now())
  Expirydate = datetime.datetime(Expirydate.year , Expirydate.month , Expirydate.day , 15 , 30 , 00)
  Days_To_Expiry =  ((Expirydate-today).total_seconds()) / 86400

  FUT_LTP
  RoundedFuture = round(FUT_LTP/Strikedifference)*Strikedifference
  Futprice = Script_CE[Script_CE.strike==RoundedFuture].SynFut

  import mibian 
  for i in Script_CE.strike :
    interestrate=0
    callprice = Script_CE.loc[Script_CE.strike==i , 'CE_Mid'].values[0]
    c = mibian.BS([Futprice, i , 0 , Days_To_Expiry] , callPrice = callprice)
    Script_CE.loc[Script_CE.strike==i , 'CE_IV'] = c.impliedVolatility

  for i in Script_PE.strike :
    putprice = Script_PE.loc[Script_PE.strike==i , 'PE_Mid'].values[0]
    c = mibian.BS([Futprice , i , 0 , Days_To_Expiry ] ,putPrice=putprice)
    Script_PE.loc[Script_PE.strike==i , 'PE_IV'] = c.impliedVolatility



  for i in Script_CE.strike :
    interestrate=0
    Volatility = Script_CE.loc[Script_CE.strike==i , 'CE_IV'].values[0]
    c = mibian.BS([Futprice , i , 0 , Days_To_Expiry ] ,volatility=Volatility)
    Script_CE.loc[Script_CE.strike==i , ['CE_Delta' , 'CE_Gamma' , 'CE_Vega' , 'CE_Theta']] = [c.callDelta , c.gamma , c.vega , c.callTheta]


  for i in Script_PE.strike :
    interestrate=0
    Volatility = Script_PE.loc[Script_PE.strike==i , 'PE_IV'].values[0]
    c = mibian.BS([Futprice , i , 0 , Days_To_Expiry ] ,volatility=Volatility)
    Script_PE.loc[Script_PE.strike==i , ['PE_Delta' , 'PE_Gamma' , 'PE_Vega' , 'PE_Theta']] = [c.putDelta , c.gamma , c.vega , c.putTheta]



  del Script_CE['tradingsymbol']
  del Script_CE['exchange']
  del Script_PE['tradingsymbol']
  del Script_PE['exchange']
  del Script_PE['PE_SyntheticFut']
  FINAL = pd.merge(Script_CE , Script_PE , on='strike')

  FINAL['Smile']=0
  FINAL['Mnes']=0

  for i in FINAL.strike :
    FINAL.loc[FINAL.strike==i  , 'Mnes'] = round((i*100)/Futprice.values[0],1)
    if(i>=RoundedFuture) :
      FINAL.loc[FINAL.strike==i , 'Smile'] = FINAL[FINAL.strike==i].CE_IV

    else :
      FINAL.loc[FINAL.strike==i , 'Smile'] = FINAL[FINAL.strike==i].PE_IV


  FINAL.loc[FINAL.strike==RoundedFuture, 'Smile'] = (FINAL[FINAL.strike==RoundedFuture].CE_IV + FINAL[FINAL.strike==RoundedFuture].PE_IV)/2
  ColumnsList = [ 'CE_OI' , 'CE_Vol' , 'CE_Bid' , 'CE_Offer' , 'CE_Vega' , 'CE_Theta' , 'CE_Gamma' , 'CE_Delta' , 'CE_IV' , 'SynFut'  , 'strike' , 'Mnes', 'Smile' , 'PE_IV' , 'PE_Delta' , 'PE_Gamma' , 'PE_Theta' , 'PE_Vega'  , 'PE_Bid' , 'PE_Offer' , 'PE_Vol' , 'PE_OI']
  FINAL = FINAL[ColumnsList]

  FINAL = roundoffnumbers(FINAL)
  
  print(FINAL)
  JSONOBJECT = FINAL.to_json(orient='records')	

  return JSONOBJECT


#@cross_origin()
@app.route('/quotes', methods=['GET'])
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
    
    data = fetch_data(ticker,expiry,totContracts,strikeDistance,accessToken)
    print("END")
    
    
    return data

@app.route('/expiry', methods=['GET'])
def home2() :
  y = mongo.db.instruments.find_one()
  del(y['_id'])
  df = pd.read_json(y["instrument"],orient='records')
  Expiry = df[(df.name=='NIFTY')].expiry.unique()
  Expiry.sort()
  Expiry = Expiry.tolist()
  expiry = json.dumps(Expiry)
  return expiry
  
  
@app.route('/instruments', methods=['GET'])
def home3() :

  y = mongo.db.instruments.find_one()
  del(y['_id'])
  
  todayDate = datetime.datetime.now().date()
  
  today = todayDate.strftime('%Y-%m-%d') 
  
  if(today==y['date']):
    df = pd.read_json(y["instrument"],orient='records')
    Expiry = df[(df.name=='NIFTY')].expiry.unique()
    Expiry.sort()
    Expiry = Expiry.tolist()
    expiry = json.dumps(Expiry)
    return expiry
  
  mongo.db.instruments.delete_many({})

  api_key = "tg48gdykr12ezopp"
  api_secret = "wgwq9kgfly6ky19j43w2g5kvxpdjb44g"

  kite = KiteConnect(api_key=api_key) 
  if 'accessToken' in request.args:
        accessToken = str(request.args['accessToken'])
        print(accessToken)
  kite.set_access_token(accessToken)
  instrument=kite.instruments()
  

  
  
  from scipy.stats import norm
  df = pd.DataFrame(instrument)
  
  dataTemp = df[((df.name=='NIFTY') | (df.name=='BANKNIFTY'))]
    
  #dataInsert = dataTemp.to_json(orient='records')
  
  dataInsert = dataTemp.to_dict('records')
  
  data = json.dumps(dataInsert, indent=4, sort_keys=True, default=str)
  
  todayDate = datetime.datetime.now().date()
  
  today = todayDate.strftime('%Y-%m-%d') 
  
  mydict = {"instrument":data,"date":today}
  
  #mycol.insert_one(mydict)
  
  mongo.db.instruments.insert_one(mydict)
  
  
  
  
  
  Expiry = df[(df.name=='NIFTY')].expiry.unique()
  Expiry.sort()
  for i in range(0,len(Expiry)) :
    Expiry[i] = Expiry[i].strftime('%Y-%m-%d')
  Expiry = Expiry.tolist()
  expiry = json.dumps(Expiry)
  return expiry


port = int(os.environ.get('PORT',5000))
app.run(host = '0.0.0.0', port=port)

