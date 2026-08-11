from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

class EAN13Field(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 13
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(
            regex=r'^[0-9]{13}$',
            message=_("Il barcode deve essere di 13 cifre.")
        ))

########## MeasureUnit ################
## ##
#######################################
    
class MeasureUnit(models.Model):
    name = models.CharField(max_length=20, unique=True) # Es: Kilogrammo
    symbol = models.CharField(max_length=5, unique=True) # Es: kg
    is_decimal = models.BooleanField(default=False) # Se False, non permetti 1.5 pezzi

    def __str__(self):
        return f"{self.name} {self.symbol}"

########## Inv_masterdata #############
## ##
#######################################

class Inv_masterdata(models.Model):

    sku = models.CharField(max_length=255)
    barcode = EAN13Field(unique=True)
    desc = models.CharField(max_length=255)
    #id_category = models.ForeignKey(Inv_category)
    measureUnit = models.ForeignKey(MeasureUnit, on_delete=models.PROTECT)
    price = models.DecimalField(
       max_digits=10, 
       decimal_places=2,
       verbose_name=_("Price")
    )

    measure_value = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       verbose_name=_("measure_value"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.desc
    # measure = models.DecimalField(
    #     max_digits = 10,
    #     decimal_places=2,
    #     verbose_name=_("Measure"
    # )
    
########## Inventory ##################
##  ##
#######################################

class Inventory(models.Model):
    inv_masterdata = models.OneToOneField(Inv_masterdata, on_delete=models.PROTECT)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("quantity"),
    )
    
    def __str__(self):
        return self.inv_masterdata.desc

    #Service methods
    
    def get_unit_measure(self):
        return self.inv_masterdata.measureUnit
    
    def get_sku(self):
        return self.inv_masterdata.sku
     
    def is_allowed_decimal_value(self):
        return self.inv_masterdata.measureUnit.is_decimal


########## Movement ###################
##  ##
#######################################

class Movement(models.Model):
    inventory_id = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("quantity"),
    )

    def get_inventory_item(self):
        return self.inventory_id

