import { Component } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms'
import { StockService } from './stock.service';
import {Stock} from './stock'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  stockForm:FormGroup;
  ticker:string="";
  startDate:Date=null;
  endDate:Date=null;
  model:string="";
  isLoading:boolean=false;
  baseImage:string='./../assets/images/';
  image1:string='';
  image2:string='';
  image3:string='';
  ready:boolean=false;
  position:string='';
  profit:number=null;
  constructor(private fb: FormBuilder,private stockService:StockService){
    this.stockForm=fb.group({
      'ticker':[null,Validators.required],
      'startDate': [null,Validators.required],
      'endDate':[null,Validators.required],
      'model':[null,Validators.required]
    })
  }
  submit(){
    this.ready=true
    this.isLoading=false;
    console.log(this.stockForm.value)
    this.stockService.fetchStock(this.stockForm.value).subscribe((response:any)=>{
      console.log(response)
      this.image1=this.baseImage.concat(response.image1)
      this.image2=this.baseImage.concat(response.image2)
      this.image3=this.baseImage.concat(response.image3)
      if(response.position==1){
        this.position='Buy'
      }
      else{
        this.position='Sell'
      }
      this.profit=response.profit;
      this.isLoading=true;
    },err=>{
      console.log(err)
    });
    
  }
}
