# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:23:51 2020

@author: L0GYKAL
"""

import requests
import pandas as pd
import time
import ccxt

# https://docs.loopring.io/en/GLOSSARY.html
CONST_privateKey = "1005676814035256533987646371479355094628244752324989559972073875260254660477"
CONST_BaseToken = "ETH"
CONST_QoteToken = "USDT"
orderId = 0
orderBook = dict()


def getUserInfo(userAddress: str):
    return requests.get("https://api.loopring.io/api/v2/account?owner=" + userAddress).json()["data"]

def getTokensInfo() -> pd.Dataframe:
    rDict = requests.get("https://api.loopring.io/api/v2/exchange/tokens").json()
    rPD = pd.DataFrame.from_dict(rDict["data"])
    return rPD

def parseTokenInfo(ticker: str) -> dict:
    for crypto in CONST_tokensInfo:
        if crypto["symbol"] == ticker:
            return crypto["symbol"]

def getExchangeInfo() -> dict:
    return requests.get("https://api.loopring.io/api/v2/exchange/info").json()["data"]

def getExchangeId() -> int:
    return getExchangeInfo()["exchangeId"]
    
def getOrderBook(baseToken: str, qoteToken: str):
    return requests.get("https://api.loopring.io/api/v2/depth?market=" + baseToken + "-" + qoteToken + "&level=2&limit=20")["data"]
    
def getBids(orderBookData: dict) -> pd.DataFrame:
    return pd.DataFrame(orderBookData["bids"], columns = ["price","size","volume","number of orders aggregated"]) 
    
def getAsks(orderBookData: dict) -> pd.DataFrame:
    return pd.DataFrame(orderBookData["asks"], columns = ["price","size","volume","number of orders aggregated"]) 
    
def getAvailableBalance(accountId: str, tokenId: str) -> float:
    data = requests.get("https://api.loopring.io/api/v2/user/balances?accountId=" + accountId + "&tokens=" + tokenId).json()["data"]
    return float(data["totalAmount"]) - float(data["amountLocked"])

def findMarketSide(baseToken: str, qoteToken: str):
    bidsSum = int()
    asksSum = int()
    for index, row in getBids(baseToken, qoteToken).iterrows():
        bidsSum += row["price"]
        
    for index, row in getAsks(baseToken, qoteToken).iterrows():
        asksSum += row["price"]
    if bidsSum > asksSum:
        return "buy"
    else:
        return "sell"
 
def placeOrder(tokenS: int, tokenB: int, sizeTokenS: int, price: int, lastOrderId: int):
    global orderId
    global exchangeID
    global accountID
    """
    newOrder = {
    "tokenSId": 2,  // LRC
    "tokenBId": 0,  // ETH
    "amountS": sizeTokenS * 10**18,
    "amountB": sizeTokenS * price * 10**18,
    "buy": "false", //string
    "exchangeId": str(exchangeID),
    "accountId": accountID,
    "allOrNone": "false", // Must be "false" for now
    "maxFeeBips": 5,
    "label": 211,  
    "orderId": orderId,
    "hash": "14504358714580556901944011952143357684927684879578923674101657902115012783290",
    "signatureRx": "15179969700843231746888635151106024191752286977677731880613780154804077177446",
    "signatureRy": "8103765835373541952843207933665617916816772340145691265012430975846006955894",
    "signatureS" : "4462707474665244243174020779004308974607763640730341744048308145656189589982",
    "clientOrderId": str(orderId), #label pour le client, n'impacte pas le trading
    "channelId": "channel1::maker1"
}
    """
    #save the order in the logs
    return lastOrderId+1
    
    
def cancelAllOders(ordersList: list, CONST_accountId):
    orderString = ""
    for orderId in ordersList:
        orderString += "," + orderId
    requests.get("https://api.loopring.io/api/v2/orders/byClientOrderId?accountId=" + CONST_accountId + "&clientOrderId=" + orderString)
    return list()

def getBitmexPrice(token: str):
    bitmex = ccxt.bitmex()
    bitmex.load_markets(True)
    return bitmex.markets['ETH/USD']['info']['lastPrice']
    

    
    
if __name__ == "__main__":
    userInfo = {
      "exchangeName": "LoopringDEX: Beta 1",
      "exchangeAddress": "0x944644Ea989Ec64c2Ab9eF341D383cEf586A5777",
      "exchangeId": 2,
      "accountAddress": "0x8eBed0FF2B0232B0AedbFe6e9c0f72AC72577869",
      "accountId": 1760,
      "apiKey": "vqK6oipMToYmTQ4KQJ5gj12K0Za1yEbwz91bJgS5n5J6h81tD4rRfCEySN6fUHe7",
      "publicKeyX": "14582686989080833254648890987308401501121907597323295132168485362559382425737",
      "publicKeyY": "7115218688717453567281436772063098657161262408532849335047287243205241225977",
      "privateKey": "1005676814035256533987646371479355094628244752324989559972073875260254660477"
    }
    
    CONST_publicKeyX = userInfo["publicKeyX"]
    CONST_publicKeyY = userInfo["publicKeyY"]
    CONST_accountId  = userInfo["accountId"]
    CONST_exchangeId = userInfo["exchangeId"]
    CONST_tokensInfo = getTokensInfo()
    CONST_EthInfo = parseTokenInfo("ETH")
    CONST_UsdtInfo = parseTokenInfo("USDT")
    tokensId = [CONST_EthInfo["tokenId"], CONST_UsdtInfo["tokenId"]]
    ordersList = list()
    
    while True:
        ordersList = cancelAllOders(ordersList, CONST_accountId)
        orderBookData = getOrderBook()    
        balances = dict()
        for tokenId in tokensId:
            balances[tokenId] = getAvailableBalance(CONST_accountId, tokenId)
            if balances[tokenId] > 0:
                bitmexPrice = getBitmexPrice()
                for index, row in getBids(orderBookData).iterrows():
                    if row["size"] > 0.1 :
                        if tokenId == tokensId[1] and bitmexPrice > row["price"] *0.93:
                            ordersList.append(placeOrder(tokensId[0], tokensId[1], balances[tokensId[0]], row["price"] *0.93))
                            break
                        if tokenId == tokensId[0] and bitmexPrice <row["price"] *1.07:
                            ordersList.append(placeOrder(tokensId[0], tokensId[1], balances[tokensId[0]], row["price"] *1.07))
                            break
        time.sleep(15)
        
    

    
    
    
    
    
