import datetime
from typing import List
from collections import Counter
from fastapi import HTTPException
from tortoise import transactions
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction
from datamodels import *

##################################################Medicine#######################################################


async def getMidList(
    med=None,
    brand=None,
    pom=None,
    country=None,
    manufacturer=None,
    ta=None,
    cursor=0,
    limit=None,
):

    query = MedList.all()

    if med:
        query = query.filter(Med__startswith=med)

    if brand:
        query = query.filter(Brand=brand)

    if pom:
        query = query.filter(POM=pom)

    if manufacturer:
        query = query.filter(Manufacturer__startswith=manufacturer)

    if country:
        query = query.filter(Country__startswith=country)

    if ta:
        med_ids = await Medid_TA.filter(TA__startswith=ta).values_list(
            "MED_id", flat=True
        )
        query = query.filter(MED_id__in=med_ids)

    query = query.filter(MED_id__gt=cursor)

    if limit:
        query = query.limit(limit)

    results = await query.all().values(
        "MED_id", "Med", "Brand", "POM", "Manufacturer", "Country"
    )

    return results


async def get_med_details_by_id(med_id: int):
    data = await MedDetails.filter(Med_id=med_id).values(
        "Med_id",
        "Med",
        "POM",
        "effSystems",
        "TAs",
        "TA_ids",
        "Addiction",
        "concentrations",
        "units",
        "Brand",
        "country",
        "manufacturer",
        "Form",
        "Obsolete",
    )
    if data:
        result = data[0]
        for field in [
            "effSystems",
            "TAs",
            "TA_ids",
            "Addiction",
            "concentrations",
            "units",
        ]:
            if result.get(field):
                result[field] = result[field].split(",")

        if result.get("TA_ids"):
            result["TA_ids"] = [int(value) for value in result["TA_ids"]]

        return result
    else:
        raise HTTPException(status_code=456, detail="data intity not found")


async def get_TaDetails_byid(ta_id: int):
    result = await TherapeuticAgent.filter(TA_id=ta_id).values("TA", "SE", "CC", "FC")
    return result[0] or None


async def get_ta_ddis(ta_id: int):
    result = await TA_DDI.filter(TA_id=ta_id).values("Interaction")

    if result:
        ta_list = [item["Interaction"] for item in result]
        return ta_list
    else:
        return None


async def get_TaDetails(ta_id: int):

    ta_details = await get_TaDetails_byid(ta_id)
    if ta_details:
        for field in ["SE", "CC", "FC"]:
            if ta_details.get(field):
                ta_details[field] = ta_details[field].split(",")

        ddi_details = await get_ta_ddis(ta_id)
        if ddi_details:
            ta_details["DDI"] = ddi_details
        else:
            ta_details["DDI"] = []

        return ta_details
    else:
        return None


#####################################################Mobile App(Pharmacy App)###############################################################


async def get_branches(ids: list[int]):
    result = await Pharmacies.filter(PH_id__in=ids).values("Name")
    return [var["Name"] for var in result]


async def retrive_profile_info(acid, phid):
    print(acid)
    print(phid)
    prof = await Account_Details.get(AC_id=acid, PH_id=phid).values(
        "user", "manager", "phname", "email"
    )
    if prof:
        return {
            "user_name": prof["user"],
            "pharmacy": prof["phname"],
            "email": prof["email"],
            "position": prof["manager"],
        }
    else:
        return {"success": False, "message": "User not found", "status_code": 404}


async def getAssistants(phids: List[int]):
    result = (
        await Account_Details.filter(PH_id__in=phids, manager=Flag.No)
        .all()
        .values("FB_id", "user", "phname", "email", "PH_id")
    )

    return result or []


async def getStockList(
    phid,
    med=None,
    brand=None,
    pom=None,
    country=None,
    manufacturer=None,
    ta=None,
    cursor=None,
    limit=None,
):

    query = StockList.filter(Ph_id=phid)

    if med:
        query = query.filter(Med__startswith=med)

    if brand:
        query = query.filter(Brand=brand)

    if pom:
        query = query.filter(Pom=pom)

    if manufacturer:
        query = query.filter(Manufacturer__startswith=manufacturer)

    if country:
        query = query.filter(Country__startswith=country)

    if ta:
        med_ids = await Medid_TA.filter(TA__startswith=ta).values_list(
            "MED_id", flat=True
        )
        query = query.filter(Med_id__in=med_ids)
    print(cursor)
    query = query.filter(Item_id__gt=cursor)

    if limit:
        query = query.limit(limit)

    results = await query.all().values(
        "Item_id",
        "Med_id",
        "Med",
        "Brand",
        "Pom",
        "Manufacturer",
        "Country",
        "Price",
        "Obsolete",
    )

    return results


async def get_batches(item_id: int):
    batches = await Batches.filter(item_id=item_id).values("EXDate", "count")
    return batches


async def insert_item(med: str, ph_id: int, price: int, med_id: int):
    async with transactions.in_transaction():
        try:
            item = await StockItems.create(Ph_id=ph_id, price=price, Med_id=med_id)

            await UpdateLog.create(
                ph_id=ph_id,
                date=datetime.datetime.now(),
                content=f"Added new item (Med: {med}, Price: {price})",
            )

            return item

        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="duplicate item",
            )


async def remove_item(med: str, item_id: int, ph_id: int):
    async with transactions.in_transaction():
        try:

            result = await StockItems.filter(Item_id=item_id).delete()
            if result:
                await UpdateLog.create(
                    ph_id=ph_id,
                    date=datetime.datetime.now(),
                    content=f"Removed item (Med: {med})",
                )
            return result

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="Failed to delete Item")
        except Exception as e:
            raise e


async def insert_batch(
    item_id: int, ex_date: datetime.date, count: int, med: str, ph_id: int
):
    async with in_transaction():
        try:
            batch = await Batches.filter(item_id=item_id, EXDate=ex_date).first()
            action = "Updated" if batch else "Added"

            print(action)

            if batch:
                print("hello2")
                await Batches.filter(item_id=item_id, EXDate=ex_date).update(
                    count=batch.count + count
                )

            else:
                print("hello")
                batch = await Batches.create(
                    item_id=item_id, EXDate=ex_date, count=count
                )

            await UpdateLog.create(
                ph_id=ph_id,
                date=datetime.datetime.now(),
                content=f"{action} batch (med :{med}, Expiry: {ex_date}, Count: {batch.count})",
            )

            return batch

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="Failed to insert/update batch")
        except Exception as e:
            raise e


async def remove_batch(item_id: int, ex_date: datetime.date, med: str, ph_id: int):
    async with transactions.in_transaction():
        try:

            result = await Batches.filter(item_id=item_id, EXDate=ex_date).delete()
            if result:
                await UpdateLog.create(
                    ph_id=ph_id,
                    date=datetime.datetime.now(),
                    content=f"Removed batch. (Med: {med})",
                )
            return result

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="Failed to delete batch")
        except Exception as e:
            raise e


async def changePrice(item_id: int, newPrice: int, med=str, ph_id=int):
    async with in_transaction():
        try:
            result = await StockItems.filter(Item_id=item_id).update(price=newPrice)
            if result:
                await UpdateLog.create(
                    ph_id=ph_id,
                    date=datetime.datetime.now(),
                    content=f"price changed to {newPrice} (Med: {med})",
                )
            return result

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="Failed to update price")
        except Exception as e:
            raise e


async def sell(
    item_ids: List[int], exdates: List[datetime.date], content: str, ph_id: int
):
    async with in_transaction():
        try:
            sales_count = Counter(zip(item_ids, exdates))

            updates = []
            deletes = []

            for (item_id, exdate), sold_quantity in sales_count.items():
                batch = await Batches.filter(item_id=item_id, EXDate=exdate).first()

                if not batch:
                    raise ValueError(
                        f"No batch found for item_id {item_id} with EXDate {exdate}"
                    )

                if batch.count < sold_quantity:
                    raise ValueError(
                        f"Insufficient stock for item_id {item_id} (EXDate {exdate})"
                    )

                if batch.count > sold_quantity:
                    updates.append((item_id, exdate, batch.count - sold_quantity))
                else:
                    deletes.append((item_id, exdate))

            for item_id, exdate, new_count in updates:
                await Batches.filter(item_id=item_id, EXDate=exdate).update(
                    count=new_count
                )

            for item_id, exdate in deletes:
                await Batches.filter(item_id=item_id, EXDate=exdate).delete()

            return await SellLog.create(
                ph_id=ph_id,
                date=datetime.datetime.now(),
                content=content,
            )

        except IntegrityError as e:
            raise HTTPException(
                status_code=409, detail="Sell Opreation coudn't be completed"
            )
        except Exception as e:
            raise e


async def get_update_logs(
    ph_id: int, from_date=None, to_date=None, cursor=None, limit=None
):
    query = UpdateLog.filter(ph_id=ph_id).order_by("-date")

    if from_date:
        query = query.filter(date__gte=from_date)
    if to_date:
        query = query.filter(date__lte=to_date)

    if cursor:
        query = query.filter(date__lt=cursor)

    if limit:
        query = query.limit(limit)

    return await query.values("date", "content")


async def get_sell_logs(
    ph_id: int, from_date=None, to_date=None, cursor=None, limit=None
):
    query = SellLog.filter(ph_id=ph_id).order_by("-date")

    if from_date:
        query = query.filter(date__gte=from_date)
    if to_date:
        query = query.filter(date__lte=to_date)

    if cursor:
        query = query.filter(date__lt=cursor)

    if limit:
        query = query.limit(limit)

    return await query.values("date", "content")


async def newTicket(content, AccountID: str, PharmacyID: 0, MedID: 0):
    try:
        await Ticket.create(
            Content=content,
            Date=datetime.date.today(),
            Account=AccountID,
            Pharmacy=PharmacyID,
            Med=MedID,
            State=State.Wait,
        )

    except Exception as e:
        raise HTTPException(status_code=409, detail="Failed to submit a ticket")


##########################################################Desktop App(Admin Tool)###############################################################


async def TicketNextPage(cursor, Limit=None):
    query = Ticket.filter(TK_id__lt=cursor, State="Wait").order_by("-TK_id")

    if Limit:
        query = query.limit(Limit)

    result = await query

    return result


async def TicketPreviousPage(cursor, Limit=None):
    query = Ticket.filter(TK_id__gt=cursor, State="Wait").order_by("TK_id")

    if Limit:
        query = query.limit(Limit)

    result = await query

    return result


async def changeTicketState(TK_id: int, State: str):
    await Ticket.filter(TK_id=TK_id).update(State=State)


async def get_user(fb_id: str) -> dict:

    print(id)
    user = await Account_Details.filter(FB_id=fb_id).values(
        "user", "email", "manager", "PH_id", "phname"
    )

    if user:
        result = {
            "user": user[0]["user"],
            "email": user[0]["email"],
            "Manager": user[0]["manager"].value,
            "pharmaciesID": [var["PH_id"] for var in user if var["PH_id"] is not None]
            or None,
            "pharmaciesN": [var["phname"] for var in user if var["phname"] is not None]
            or None,
        }

        return result

    else:
        raise HTTPException(status_code=456, detail="User doesn't exist")


async def getPharmaDetails(phid: int):
    pharma = (
        await Pharma_Details.filter(PH_id=phid)
        .all()
        .values("phname", "FB_id", "user", "manager")
    )

    if pharma:
        result = {
            "phmame": pharma[0]["phname"],
            "workers": [var["user"] for var in pharma if var["user"] is not None],
            "workersIds": [var["FB_id"] for var in pharma if var["FB_id"] is not None],
            "status": [
                var["manager"].value for var in pharma if var["manager"] is not None
            ],
        }
        return result
    else:
        raise HTTPException(status_code=456, detail="pharmacy doesn't exist")


async def DeletePharmacy(id: int):
    result = await Pharmacies.filter(PH_id=id).delete()

    if not result:
        raise HTTPException(status_code=409, detail="Failed to Delete pharmacy")


async def AddBranch(FB_id: str, ph_name: str):

    try:
        async with in_transaction():
            account = await Accounts.filter(FB_ID=FB_id).first()

            pharma = await Pharmacies.create(Name=ph_name)

            await AccountPharmacy.create(PH_id=pharma.PH_id, AC_id=account.AC_id)

    except Exception as e:
        raise HTTPException(status_code=409, detail="Failed to add branch")


async def getTAList():
    result = await TherapeuticAgent.all().values("TA_id", "TA")
    return result or None


async def AddMedTa(MedID: int, TaID: int, unit: str, concetration: int):
    try:
        await Dosage.create(
            MED_id=MedID, TA_id=TaID, unit=unit, concetration=concetration
        )
    except Exception as e:
        raise HTTPException(status_code=409, detail="Failed to add dosage")


async def RemoveMedTa(MedID: int, TaID: int):
    result = await Dosage.filter(MED_id=MedID, TA_id=TaID).delete()
    if not result:
        raise HTTPException(status_code=409, detail="Failed to remove dosage")


async def ChangeState(Med_id: int):
    try:
        med = await Med.filter(MED_id=Med_id).first()
        new_state = Flag.No if med.Obsolete == Flag.Yes else Flag.Yes
        await Med.filter(MED_id=Med_id).update(Obsolete=new_state)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=409, detail="Failed to change State")


async def getManufacturerList():
    result = await Manufacturer.all().values("Manufacturer_id", "Manufacturer")
    return result or None


async def addMed(
    Description: str,
    Brand: str,
    med: str,
    Manufacturer_id: int,
    POM: str,
    DosageForm: str,
):

    try:

        result = await Med.create(
            Description=Description,
            Brand=Brand,
            Med=med,
            Manufacturer_id=Manufacturer_id,
            POM=POM,
            DosageForm=DosageForm,
            Obsolete="Yes",
        )
        return {"message":"med added successfully",
                "Med_id":result.MED_id}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=409, detail="Failed to add Med")
