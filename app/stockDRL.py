#Import Library
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.dates as dates
import numpy as np
import pandas as pd
import pandas_datareader as web
from gym_anytrading.envs import StocksEnv
import talib
import datetime
import math
from mplfinance.original_flavor import candlestick_ohlc
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import A2C,PPO2
import os
import nltk
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.porter import PorterStemmer
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Stock:
    def __init__(self,ticker,startDate,endDate):
            self.ticker=ticker
            self.startDate=startDate
            self.endDate=endDate

    def load_dataset(self):
            try:
                self.data=web.DataReader(self.ticker,data_source='yahoo',start=self.startDate,end=self.endDate)
                return
            except:
                raise ImportError('Error while importing file')   


    def add_technical_indicator(self):
        
        adjClose=self.data['Adj Close']
        
        macd,macdsignal,macdhist=talib.MACD(adjClose,fastperiod=12,slowperiod=26,signalperiod=9)
    
        rsi=talib.RSI(adjClose,timeperiod=12)
    
        upper,middle,lower=talib.BBANDS(adjClose,timeperiod=20,nbdevup=2.0,nbdevdn=2.0,matype=talib.MA_Type.EMA)
    
        ROC=talib.ROC(adjClose,timeperiod=12)
    
        self.data=self.data.assign(**{'RSI':rsi,'MACD':macd,'macd_signal':macdsignal,'macd_hist':macdhist,'UPPER_BB':upper,'LOWER_BB':lower,'MIDDLE_BB':middle,'ROC':ROC})

        self.data.fillna(0,inplace=True)    

        return True

    def visulaize(self):
        data=self.data.iloc[-math.ceil(self.data.shape[0]*0.3):]
        
        fig=plt.figure()
        
        fig.set_size_inches((20,16))
        candle=fig.add_axes((0,0.72,1,0.32))
        macd=fig.add_axes((0,0.48,1,0.2),sharex=candle)
        rsi=fig.add_axes((0,0.24,1,0.2),sharex=candle)
        bbands=fig.add_axes((0,0,1,0.2),sharex=candle)
        candle.xaxis_date()
        
        ohlc=[]
        for date,row in data.iterrows():
            _open,_high,_low,_close=row[:4]
            ohlc.append([dates.date2num(date),_open,_high,_low,_close])
        
        candle.plot(data.index,data['Close'],label='Close')
        
        candlestick_ohlc(candle,ohlc,colorup='g',colordown='r',width=0.8)
        
        candle.legend()
        
        macd.plot(data.index,data['MACD'],label="MACD")
        macd.bar(data.index,data['macd_hist']*3,label="hist")
        macd.plot(data.index,data['macd_signal'],label="signal")
        macd.legend()
        
        rsi.set_ylabel("(%)")
        rsi.plot(data.index,[70]*len(data.index),label="overbought")
        rsi.plot(data.index,[30]*len(data.index),label="oversold")
        rsi.plot(data.index,data['RSI'],label='RSI')
        rsi.legend()

        bbands.plot(data.index,data['UPPER_BB'],label='Upper Band')
        bbands.plot(data.index,data['MIDDLE_BB'],label='Middle Band')
        bbands.plot(data.index,data['LOWER_BB'],label='Lower Band')
        bbands.legend()
        
        Image_path=os.path.join(r'E:\stock\FrontEnd\src\assets','images')
        print(Image_path)
        os.makedirs(Image_path,exist_ok=True)
        
        path=self.ticker+datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")+'.png'
        final=os.path.join(Image_path,path)
        fig.savefig(final,bbox_inches='tight')
        
        return path

    def extractAnalysis(self):
        driver=webdriver.Chrome(executable_path=r'E:\stock\stock\chromedriver')
        driver.get('https://seekingalpha.com/symbol/{a}/analysis?from={b}&to={c}'.format(a=self.ticker,b=self.startDate,c=self.endDate))
        time.sleep(4)
        element=driver.find_element_by_tag_name('body')
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            element.send_keys(Keys.END)
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        elements = driver.find_elements_by_tag_name("article")   
        result=[]
        
        for element in elements:
            a,b=element.text.split('\n')            
            c=b.replace('.','')
            if re.search(r'Yesterday',c):
                d=datetime.date.today()-datetime.timedelta(days=1)
            else:
                match=re.search(r'\w{3}\s\d{1,2}\,\s\d{4}|May\s\d{1,2}\,\s\d{4}|\w{3}\s\d{1,2}|May\s\d{1,2}',c)
                if re.search(r'\w{3}\s\d{1,2}\,\s\d{4}|\w{3}\s\d{1,2}\,\s\d{4}',match[0]):
                    fulldate=match[0]
                else:
                    fulldate=match[0]+', '+str(datetime.date.today().year)
                d=datetime.datetime.strptime(fulldate,'%b %d, %Y')
            result.append((d,a))

        
        self.df=pd.DataFrame(result,columns=['Date','News'])
        self.df['News']=self.df.groupby('Date').transform(lambda x: ' '.join(x))
        self.df=self.df.drop_duplicates()
        self.df.reset_index(inplace=True,drop=True)
        c=[]
        
        ps=PorterStemmer()
        for i in range(0,len(self.df['News'])):
            news=re.sub('[^a-zA-Z]',' ',self.df['News'][i])
            news=news.lower()
            news=news.split()
            news=[ps.stem(word) for word in news if not word in set(stopwords.words('english'))]
            news=' '.join(news)
            c.append(news)
        print(len(c))  
        self.df['News']=pd.Series(c)
        return

    def sentimentAnalysis(self):
        sia=SentimentIntensityAnalyzer()
        self.df['Compound']=[sia.polarity_scores(v)['compound'] for v in self.df['News']]
        self.df['Negative']=[sia.polarity_scores(v)['neg'] for v in self.df['News']]
        self.df['Neutral']=[sia.polarity_scores(v)['neu'] for v in self.df['News']]
        self.df['Positive']=[sia.polarity_scores(v)['pos'] for v in self.df['News']]
        
        fig=self.df[:30].plot(x='Date',y=['Compound','Positive','Negative'],kind='bar',figsize=(16,10)).get_figure()
        plt.ylabel('Sentiment Scores')
        
        
        Image_path=os.path.join(r'E:\stock\FrontEnd\src\assets','images')
    
        os.makedirs(Image_path,exist_ok=True)
        
        path=self.ticker+datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")+'sia.png'
        final=os.path.join(Image_path,path)
        fig.savefig(final,bbox_inches='tight')
        return path

    def merge(self):
        self.data=pd.merge(self.data,self.df,how='left',on='Date')
        self.data=self.data.fillna(0)
        print(self.data.isna().sum())
        return 

def trainA2C(policy,env,timesteps=25000,verbose=0):
        model=A2C(policy,env,verbose)
        model.learn(total_timesteps=timesteps)
        return model

def trainPPO(env,timesteps=50000):
         model=PPO2('MlpPolicy',env,ent_coef=0.005)
         model.learn(total_timesteps=timesteps)
         return model


def add_signals(env):
        start=env.frame_bound[0]-env.window_size
        end=env.frame_bound[1]
        prices=env.df.loc[:,'Adj Close'].to_numpy()[start:end]
        signal_features=env.df.loc[:,['Adj Close','RSI','MACD','UPPER_BB','LOWER_BB','MIDDLE_BB','ROC','Compound']].to_numpy()[start:end]
        return prices,signal_features


class CustomEnv(StocksEnv):
    _process_data=add_signals

def prediction(data,modelName,ticker):
        
        env2=CustomEnv(df=data,window_size=12,frame_bound=(12,round(data.shape[0]*0.7)))
        env_maker=lambda: env2
        env=DummyVecEnv([env_maker])
        
        if modelName=='PPO':
            model=trainPPO(env=env,timesteps=40000)   
        elif modelName =='A2C':
            model=trainA2C(policy="MlpPolicy",env=env,timesteps=30000) 
        
        env = CustomEnv(df=data, window_size=12, frame_bound=(round(data.shape[0]*0.3),data.shape[0]))
        obs = env.reset()
        while True: 
            obs = obs[np.newaxis, ...]
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)
            if done:
                print("info", info)
                break
        plt.figure(figsize=(15,6))
        plt.cla()
        plt.xlabel('Nth Day')
        plt.ylabel('Adj Close')
        env.render_all()
        
        Image_path=os.path.join(r'E:\stock\FrontEnd\src\assets','images')
    
        os.makedirs(Image_path,exist_ok=True)
        
        path=ticker+datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")+'result.png'
        final=os.path.join(Image_path,path)
        plt.savefig(final,bbox_inches='tight')
        return [path,info]        
