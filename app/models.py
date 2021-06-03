from django.db import models


# Create your models here.

class Stock(models.Model):
    title=models.CharField(max_length=20,blank=False)
    start_date=models.DateField(blank=False)
    end_date=models.DateField(blank=False)
    position=models.CharField(max_length=4,blank=False)
    profit=models.DecimalField(max_digits=6,decimal_places=2,blank=False)

    def __str__(self):
        return f'Stock: {self.title}\nPostion:{self.position}'


