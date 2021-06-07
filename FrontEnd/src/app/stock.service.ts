import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Stock } from './stock';

@Injectable({
  providedIn: 'root'
})
export class StockService {

  constructor(private http:HttpClient) { }
  public fetchStock(form):Observable<Stock>{
    return this.http.post<Stock>('http://localhost:8000/api/stocks/predict',{'ticker':form.ticker,'startDate':form.startDate,'endDate':form.endDate,'model':form.model})
  }
}
