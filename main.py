import pandas as pd
import numpy as np
import datetime

def gen_portfolio(recordfile, startdate, enddate, capital):
    rec=pd.read_csv(recordfile);
    #读取Portfolio文件
    rec.sort_values(by='Date');
    #交易记录按日期排序
    
    rec['Date'] = rec.Date.apply(lambda x: datetime.datetime.strptime(x , "%Y-%m-%d"))
    #转换rec的Date的Type，使之可以操作
    #lambda x是提取出来Date里的值，非常有用！（名义函数）
    rec=rec[(rec.Date>=startdate) & (rec.Date<=enddate)]
    #切出来需要的时段    
    rec["Total"]=rec["Quantity"]*rec["Price"]+rec["Commission"]
    #计算总交易价格
    
    stocklist=rec.Quote
    stocklist.drop_duplicates(keep='first',inplace=True)
    stocklist=stocklist.reset_index(drop=True)
    #提取出来一个持仓的股票列表，并重置index
    
    StockPrice=get_price(list(stocklist), start_date=startdate, end_date=enddate,fields='ClosingPx',frequency='1D')
    date_index=StockPrice.index
    #提取出来持仓股票的价格（收盘价），并抽取这个列表附带的时间index（自然是交易日）
    
    datequote_index=pd.MultiIndex.from_product([date_index,stocklist],names=['Date','Quote'])
    #做一个Date为第一轴，Quote为第二轴的multiindex
    stocks=pd.DataFrame({'Quantity':0.,'Cost':0.,'Value':0.,'ClosePrice':0.,},index=datequote_index)
    #并用这个index建造一个持仓情况列表
    
    stocks=stocks.T
    for i in range (0,len(date_index)):
        for j in range (0,len(stocklist)):
            stocks[date_index[i],stocklist[j]].Cost=rec[(rec.Date<=date_index[i]) & (rec.Quote==stocklist[j])].Total.sum()
            stocks[date_index[i],stocklist[j]].Quantity=rec[(rec.Date<=date_index[i]) & (rec.Quote==stocklist[j])].Quantity.sum()
            stocks[date_index[i],stocklist[j]].ClosePrice=StockPrice.at[date_index[i],stocklist[j]]
    #依靠for循环和交易记录把持仓信息填满
    stocks=stocks.T
    stocks['Value']=stocks['ClosePrice']*stocks['Quantity']
    stocks['AvgCost']=stocks['Cost']/stocks['Quantity']
    #再计算出来每只股票持仓的当日价值和摊薄成本
    
    portfolio=pd.DataFrame({'StockValue':0.,'StockCost':0.,'Cash':0.,'Total':0.,'Gain':0.,},index=date_index)
    
    stocks=stocks.T
    portfolio=portfolio.T
    portfolio[date_index[0]].Cash=capital
    portfolio[date_index[0]].Total=capital
    #这一句对第一天初始化
    for i in range (1,len(date_index)):
        if date_index[i] in list(rec.Date):
            portfolio[date_index[i]].Cash=portfolio[date_index[i-1]].Cash-rec[rec.Date==date_index[i]].Total.sum()
        else:
            portfolio[date_index[i]].Cash=portfolio[date_index[i-1]].Cash
        portfolio[date_index[i]].StockValue=stocks[date_index[i]].T.Value.sum()
        portfolio[date_index[i]].Total=portfolio[date_index[i]].Cash+portfolio[date_index[i]].StockValue
        portfolio[date_index[i]].Gain=portfolio[date_index[i]].Total-capital
        portfolio[date_index[i]].StockCost=stocks[date_index[i]].T.Cost.sum()
    portfolio=portfolio.T
    stocks=stocks.T
    
    return portfolio, stocks
    
def pctgain_calc(portfolio):
    portfolio['PctGain']=0.0
    portfolio=portfolio.T
    for i in range (1,len(portfolio.Total)):
        portfolio[date_index[i]].PctGain=portfolio[date_index[i]].Gain/capital
    portfolio=portfolio.T
    return portfolio
    
def stockpctgain_calc(portfolio):
    portfolio['StockPctGain']=0.0
    portfolio=portfolio.T
    for i in range (1,len(portfolio.Total)):
        portfolio[date_index[i]].StockPctGain=(portfolio[date_index[i]].StockValue-portfolio[date_index[i]].StockCost)/portfolio[date_index[i]].StockCost
    portfolio=portfolio.T
    return portfolio
    
#初始化，需要输入起止日期和起始资本
STARTDATE="2017-03-14"
ENDDATE="2017-05-17"
CAPITAL=1000000

startdate=datetime.datetime.strptime(STARTDATE, "%Y-%m-%d")
enddate=datetime.datetime.strptime(ENDDATE, "%Y-%m-%d")
#将起止日期转换成datetime格式

#生成Portfolio和stocks的DataFrame
portfolio,stocks=gen_portfolio(recordfile="TradeRecord.csv", startdate=startdate, enddate=enddate, capital=CAPITAL)

portfolio=stockpctgain_calc(portfolio)
