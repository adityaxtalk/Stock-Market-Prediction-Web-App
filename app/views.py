from django.core.checks.messages import Error
from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
import app.stockDRL as DRL




@api_view(['POST'])
def predict(request):
    try:
        stock_data=JSONParser().parse(request)
        print(stock_data)
        stock_DRL=DRL.Stock(stock_data.get('ticker'),stock_data.get('startDate'),stock_data.get('endDate'))
        print(1)
        stock_DRL.load_dataset()
        print(2)
        stock_DRL.add_technical_indicator()
        print(3)
        path=stock_DRL.visulaize()
        print(4)
        stock_DRL.extractAnalysis()
        print(5)
        path1=stock_DRL.sentimentAnalysis()
        print(6)
        stock_DRL.merge()
        print(7)
        result=DRL.prediction(stock_DRL.data,stock_data.get('model'),stock_DRL.ticker)
        print(result)
        return JsonResponse({'image1':path,'image2':path1,'image3':result[0],'profit':result[1].get('total_profit'),'position':result[1].get('position')},safe=False)
        
    except:
        return JsonResponse('Error while accessing data',status=status.HTTP_400_BAD_REQUEST,safe=False)
