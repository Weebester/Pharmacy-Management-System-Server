
from enum import Enum
from tortoise import fields, Model, fields

class Flag(Enum):
    Yes = "Yes"
    No = "No"


class Unit(str, Enum):
    G = "g"
    ML_G = "ml/g"
    ML_ML = "ml/ml"
    G_G = "g/g"
    MEQ_ML = "meq/ml"
    MCG_ML = "mcg/ml"
    MCG_G = "mcg/g"
    MG = "mg"
    MCG = "mcg"
    MG_ML = "mg/ml"
    MG_G = "mg/g"
    WW_PERCENT = "W/W %"
    WV_PERCENT = "W/V %"
    VV_PERCENT = "V/V %"
    UI = "UI"


class State(Enum):
    Wait = "Wait"
    Complete = "Complete"
    Discard = "Discard"


#########################################################Tables#############################################################


class Med(Model):
    MED_id = fields.IntField(pk=True)
    Description = fields.CharField(max_length=1024, default=" ")
    Brand = fields.CharEnumField(enum_type=Flag)
    Med = fields.CharField(max_length=100, unique=True)
    Manufacturer_id = fields.IntField()
    POM = fields.CharEnumField(enum_type=Flag)
    DosageForm = fields.CharField(max_length=100)
    Obsolete = fields.CharEnumField(enum_type=Flag)

    class Meta:
        table = "med"


class Dosage(Model):
    MED_id = fields.IntField()
    TA_id = fields.IntField()
    unit = fields.CharEnumField(enum_type=Unit)
    concetration = fields.IntField()

    class Meta:
        table = "dosage"
        unique_together = (("MED_id", "TA_id"),)


class TherapeuticAgent(Model):
    TA_id = fields.IntField(pk=True)
    SystemEffect = fields.CharField(max_length=100)
    DrugofAbuse = fields.CharEnumField(enum_type=Flag)
    TA = fields.CharField(max_length=100)
    SE = fields.CharField(max_length=1024, null=True)
    CC = fields.CharField(max_length=1024, null=True)
    FC = fields.CharField(max_length=1024, null=True)

    class Meta:
        table = "ta"


class Manufacturer(Model):
    Manufacturer_id = fields.IntField(pk=True)
    Manufacturer = fields.CharField(max_length=100, unique=True)
    country = fields.CharField(max_length=50)

    class Meta:
        table = "manufacturer"


class Admins(Model):
    Admin_id = fields.CharField(max_length=128, pk=True)
    Password = fields.CharField(max_length=64)
    medAccess = fields.CharEnumField(enum_type=Flag)
    pharmaAccess = fields.CharEnumField(enum_type=Flag)

    class Meta:
        table = "admins"


class Accounts(Model):
    AC_id = fields.IntField(pk=True)
    user = fields.CharField(max_length=50)
    Manager = fields.CharEnumField(enum_type=Flag)
    email = fields.CharField(max_length=128)
    FB_ID = fields.CharField(max_length=128)

    class Meta:
        table = "accounts"


class Pharmacies(Model):
    PH_id = fields.IntField(pk=True)
    Name = fields.CharField(max_length=50)

    class Meta:
        table = "pharmacies"


class AccountPharmacy(Model):
    PH_id = fields.IntField()
    AC_id = fields.IntField()

    class Meta:
        table = "ph_ac"
        unique_together = ("PH_id", "AC_id")


class StockItems(Model):
    Item_id = fields.BigIntField(pk=True)
    Ph_id = fields.IntField()
    price = fields.IntField()
    Med_id = fields.IntField()

    class Meta:
        table = "stockitems"
        unique_together = (("Ph_id", "Med_id"),)


class Batches(Model):
    item_id = fields.BigIntField(pk=True)
    EXDate = fields.DateField()
    count = fields.IntField()

    class Meta:
        table = "batch"
        unique_together = (("item_id", "EXDate"),)


class UpdateLog(Model):
    UP_id = fields.BigIntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    ph_id = fields.IntField(index=True)
    content = fields.TextField()

    class Meta:
        table = "updatelog"


class SellLog(Model):
    SELL_id = fields.BigIntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    ph_id = fields.IntField(index=True)
    content = fields.TextField()

    class Meta:
        table = "selllogs"


class Ticket(Model):
    TK_id = fields.BigIntField(pk=True)
    Content = fields.TextField()
    Date = fields.DateField(auto_now_add=True)
    Account = fields.CharField(max_length=128)
    Pharmacy = fields.IntField()
    Med = fields.IntField()
    State = fields.CharEnumField(enum_type=State)

    class Meta:
        table = "ticket"


##########################################################Views############################################################


class MedList(Model):
    MED_id = fields.IntField(pk=True)
    Med = fields.CharField(max_length=100)
    Brand = fields.CharEnumField(Flag)
    POM = fields.CharEnumField(Flag)
    Country = fields.CharField(max_length=50)
    Manufacturer = fields.CharField(max_length=50)

    class Meta:
        table = "medList"
        managed = False


class Medid_TA(Model):
    MED_id = fields.IntField(pk=True)
    TA = fields.CharField(max_length=100)

    class Meta:
        table = "medid_ta"
        managed = False


class MedDetails(Model):
    Med_id = fields.IntField(pk=True)
    Med = fields.CharField(max_length=100)
    POM = fields.CharEnumField(Flag)
    effSystems = fields.TextField()  # (comma-separated)
    TAs = fields.TextField()  # (comma-separated)
    TA_ids = fields.TextField()  # (comma-separated)
    Addiction = fields.TextField()  # (comma-separated)
    concentrations = fields.TextField()  # (comma-separated)
    units = fields.TextField()  # (comma-separated)
    Brand = fields.CharEnumField(Flag)
    country = fields.CharField(max_length=50)
    manufacturer = fields.CharField(max_length=50)
    Form = fields.CharField(max_length=50)
    Obsolete = fields.CharEnumField(Flag)

    class Meta:
        table = "med_details"
        managed = False


class TA_DDI(Model):
    TA_id = fields.CharField(max_length=100)
    Interaction = fields.CharField(max_length=100)

    class Meta:
        table = "ta_ddi"
        managed = False


class Account_Details(Model):
    AC_id = fields.IntField()
    FB_id = fields.CharField(pk=True, max_length=128)
    user = fields.CharField(max_length=50)
    phname = fields.CharField(max_length=50)
    manager = fields.CharEnumField(enum_type=Flag)
    email = fields.CharField(max_length=100)
    PH_id = fields.IntField()

    class Meta:
        table = "account_details"
        managed = False


class Pharma_Details(Model):
    AC_id = fields.IntField()
    FB_id = fields.CharField(pk=True, max_length=128)
    user = fields.CharField(max_length=50)
    phname = fields.CharField(max_length=50)
    manager = fields.CharEnumField(enum_type=Flag)
    email = fields.CharField(max_length=100)
    PH_id = fields.IntField()

    class Meta:
        table = "pharmacy_details"
        managed = False


class StockList(Model):
    Ph_id = fields.BigIntField()
    Item_id = fields.BigIntField()
    Med_id = fields.IntField()
    Med = fields.CharField(max_length=100)
    Brand = fields.CharEnumField(Flag)
    Pom = fields.CharEnumField(Flag)
    Manufacturer = fields.CharField(max_length=50)
    Country = fields.CharField(max_length=50)
    Price = fields.IntField()
    Obsolete = fields.CharEnumField(Flag)

    class Meta:
        table = "stock_list"
        managed = False
