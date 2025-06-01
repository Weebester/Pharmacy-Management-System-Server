import shutil
import firebase_admin
from firebase_admin import credentials, auth
from contextlib import asynccontextmanager
import datetime
import os
from typing import List, Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from Logic import *
from authintication import *
from smpt import *
from ConectionPoolConfig import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        cred = credentials.Certificate(
            "pharmacy-managment-6e7d4-firebase-adminsdk-fbsvc-812a0c252b.json"
        )
        firebase_app = firebase_admin.initialize_app(cred)
        await Open_MySQLDB()
        yield

    except Exception as e:
        raise e
    finally:
        await Close_MySQLDB()


app = FastAPI(lifespan=lifespan)


# Medecine List
@app.get("/MedList")
async def medList_route(
    med: Optional[str] = None,
    pom: Optional[str] = None,
    brand: Optional[str] = None,
    country: Optional[str] = None,
    manufacturer: Optional[str] = None,
    ta: Optional[str] = None,
    cursor: Optional[int] = 0,
    limit: Optional[int] = None,
):

    data = await getMidList(med, pom, brand, country, manufacturer, ta, cursor, limit)
    return data


@app.get("/MedDetails")
async def med_details(med_id: int):
    data = await get_med_details_by_id(med_id)
    if data:
        return data
    else:
        raise HTTPException(status_code=456, detail="Medication not found")


@app.get("/TADetails")
async def ta_details_route(ta_id: int):
    data = await get_TaDetails(ta_id)

    if data:
        return data
    else:
        raise HTTPException(status_code=456, detail="Therapeutic agent not found")



@app.get("/MedIMG")
async def img_route(ImageId: str):
    path = "Assets/" + ImageId + ".png"
    if os.path.exists(path):
        return FileResponse(path)



class LoginRequest(BaseModel):
    FB_id: str

@app.post("/Login")
async def login_route(body: LoginRequest):
    result = await Login_user(FB_id=body.FB_id)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])


class RefreshTokenRequest(BaseModel):
    refreshToken: str
 

@app.post("/Refresh")
async def refresh_route(body: RefreshTokenRequest):
    refresh_token = body.refreshToken

    new_access_token = await TokRefresh(refresh_token)

    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {"newAccessToken": new_access_token}


@app.get("/Profile")
async def profile_route(pharma_index: Optional[int] = 0, token=Depends(tokenCheck)):
    profile = await retrive_profile_info(
        acid=token.get("user_id"), phid=token.get("pharmacies")[pharma_index]
    )
    if profile is None:
        raise HTTPException(status_code=456, detail="Profile not found")
    return profile


@app.get("/Stock")
async def get_stock_route(
    pharma_index: Optional[int] = 0,
    manufacturer: Optional[str] = None,
    country: Optional[str] = None,
    med: Optional[str] = None,
    ta: Optional[str] = None,
    cursor: Optional[int] = 0,
    limit: Optional[int] = None,
    token=Depends(tokenCheck),
):
    phid = token.get("pharmacies")[pharma_index]
    medicines = await getStockList(
        phid=phid,
        manufacturer=manufacturer,
        country=country,
        med=med,
        ta=ta,
        cursor=cursor,
        limit=limit,
    )
    if medicines is None:
        raise HTTPException(status_code=456, detail="Stock not found")

    for medicine in medicines:
        item_id = medicine.get(
            "Item_id"
        )  # Assuming 'medId' is the identifier for each item
        item_batches = await get_batches(item_id=item_id)

        # If no batches, attach empty list
        medicine["batches"] = item_batches if item_batches is not None else []

    return medicines


# trash
@app.get("/ItemBatches")
async def get_stock_Item_route(
    item_id: int,
    token=Depends(tokenCheck),
):

    item_details = await get_batches(
        item_id=item_id,
    )
    if item_details is None:
        raise HTTPException(status_code=456, detail="Item not found")
    return item_details


@app.get("/branches")
async def get_branchs_names_route(token=Depends(tokenCheck)):
    branches = await get_branches(token.get("pharmacies"))
    if branches is None:
        raise HTTPException(status_code=456, detail="Stock not found")
    return branches


class SignUpRequest(BaseModel):
    name: str
    pharmacyName: str
    email: str
    FB_id: str


@app.post("/sign_up")
async def sign_up_route(request: SignUpRequest):
    try:
        response = await sign_up(
            name=request.name,
            pharmacyName=request.pharmacyName,
            email=request.email,
            FB_id=request.FB_id,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to create account and pharmacy"
        )


class AddAssistancRequest(BaseModel):
    name: str
    email: str
    passW: str
    index: int


@app.post("/add_assistant")
async def add_assistant_route(
    request: AddAssistancRequest, token: dict = Depends(tokenCheck)
):
    try:
        if token.get("Manager") != "Yes":
            raise HTTPException(
                status_code=403, detail="You are not authorized to add an assistant"
            )

        phid = token.get("pharmacies")[request.index]

        try:
            user = auth.create_user(
                email=request.email, password=request.passW, display_name=request.name
            )
            FB_id = user.uid
        except auth.EmailAlreadyExistsError:
            return "Email already in use"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating user in Firebase: {str(e)}"
            )

        response = await addAssistance(
            name=request.name,
            ph_id=phid,
            email=request.email,
            FB_id=FB_id,
        )

        return response["message"]

    except Exception as e:
        raise


class deleteAssistancRequest(BaseModel):
    phid: int
    name: str
    FB_id: str


@app.delete("/delete_assistant")
async def delete_assistant_route(
    request: deleteAssistancRequest, token: dict = Depends(tokenCheck)
):
    try:
        if token.get("Manager") != "Yes":
            raise HTTPException(
                status_code=403, detail="You are not authorized to delete an assistant"
            )

        try:
            auth.delete_user(request.FB_id)
        except Exception as e:
            raise HTTPException(
                status_code=450, detail=f"Error deleting user from Firebase: {str(e)}"
            )

        response = await deleteAssistance(
            name=request.name, ph_id=request.phid, FB_id=request.FB_id
        )

        return response

    except Exception as e:
        raise


@app.get("/get_assistant")
async def get_assistant_route(token: dict = Depends(tokenCheck)):
    try:
        if token.get("Manager") == "No":
            raise HTTPException(status_code=401, detail="access not allowed")

        phids = token.get("pharmacies")
        response = await getAssistants(phids=phids)
        return response
    except Exception as e:
        raise


class ItemInsertRequest(BaseModel):
    med: str
    price: int
    med_id: int
    pharma_index: int


@app.post("/insert_item")
async def Insert_item_route(request: ItemInsertRequest, token: dict = Depends(tokenCheck)):
    try:
        phid = token.get("pharmacies")[request.pharma_index]

        result = await insert_item(
            med=request.med,
            ph_id=phid,
            price=request.price,
            med_id=request.med_id,
        )

        return {"message": "Item inserted successfully", "item_id": result.Item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


class BatchInsertRequest(BaseModel):
    item_id: int
    med: str
    ex_date: datetime.date
    count: int
    pharma_index: int


@app.post("/insert_batch")
async def insert_batch_route(request: BatchInsertRequest, token: dict = Depends(tokenCheck)):
    try:
        phid = token.get("pharmacies")[request.pharma_index]

        result = await insert_batch(
            item_id=request.item_id,
            ex_date=request.ex_date,
            count=request.count,
            med=request.med,
            ph_id=phid,
        )

        return {"message": "batch inserted successfully", "item_id": result.item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


class ItemDeleteRequest(BaseModel):
    med: str
    Item_Id: int
    pharma_index: int


@app.delete("/delete_item")
async def Delete_item_route(request: ItemDeleteRequest, token: dict = Depends(tokenCheck)):
    phid = token.get("pharmacies")[request.pharma_index]
    try:
        result = await remove_item(med=request.med, item_id=request.Item_Id, ph_id=phid)

        if result:
            return {"message": "Item deleted successfully"}
        else:
            return {"message": "Item doesn't exist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


class BatchDeleteRequest(BaseModel):
    item_id: int
    ex_date: datetime.date
    med: str
    pharma_index: int


@app.delete("/delete_batch")
async def Delete_batch_route(request: BatchDeleteRequest, token: dict = Depends(tokenCheck)):
    phid = token.get("pharmacies")[request.pharma_index]
    try:
        result = await remove_batch(
            item_id=request.item_id,
            ex_date=request.ex_date,
            med=request.med,
            ph_id=phid,
        )

        if result:
            return {"message": "batch deleted successfully"}
        else:
            return {"message": "batch doesn't exist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


class changePriceReq(BaseModel):
    item_id: int
    newPrice: int
    med: str
    index: int


@app.put("/changePrice")
async def change_price_route(request: changePriceReq, token: dict = Depends(tokenCheck)):
    phid = token.get("pharmacies")[request.index]
    try:
        result = await changePrice(
            item_id=request.item_id,
            newPrice=request.newPrice,
            med=request.med,
            ph_id=phid,
        )

        if result:
            return {"message": "item price changed successfully"}
        else:
            return {"message": "item doesn't exist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


class SellRequest(BaseModel):
    item_ids: List[int]
    ex_dates: List[datetime.date]
    content: str
    index: int


@app.put("/sell_items")
async def sell_items_route(request: SellRequest, token: dict = Depends(tokenCheck)):
    try:
        phid = token.get("pharmacies")[request.index]

        result = await sell(
            item_ids=request.item_ids,
            exdates=request.ex_dates,
            content=request.content,
            ph_id=phid,
        )

        return {"message": "Items sold successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/update_logs")
async def get_update_logs_route(
    token: dict = Depends(tokenCheck),
    pharma_index: Optional[int] = 0,
    from_date: Optional[datetime.date] = None,
    to_date: Optional[datetime.date] = None,
    cursor: Optional[datetime.datetime] = None,
    limit: Optional[int] = None,
):
    ph_id = token.get("pharmacies")[pharma_index]
    logs = await get_update_logs(ph_id, from_date, to_date, cursor, limit)
    return logs


@app.get("/sell_logs")
async def get_sell_logs_route(
    token: dict = Depends(tokenCheck),
    pharma_index: Optional[int] = 0,
    from_date: Optional[datetime.date] = None,
    to_date: Optional[datetime.date] = None,
    cursor: Optional[datetime.datetime] = None,
    limit: Optional[int] = None,
):
    ph_id = token.get("pharmacies")[pharma_index]
    logs = await get_sell_logs(ph_id, from_date, to_date, cursor, limit)
    return logs


class TicketRequest(BaseModel):
    Content: str
    UserUid: str
    PharmaIndex: int
    MedID: int = 0


@app.post("/newTicket")
async def create_ticket_route(request: TicketRequest, token: dict = Depends(tokenCheck)):

    ph_id = token.get("pharmacies")[request.PharmaIndex]

    await newTicket(
        content=request.Content,
        AccountID=request.UserUid,
        PharmacyID=ph_id,
        MedID=request.MedID,
    )
    return {"message": "Ticket submitted successfully"}


###########################################################################################################


class LoginAdminRequest(BaseModel):
    AdminID: str
    AdminPass: str


@app.post("/LoginAdmin")
async def loginAdmin_route(body: LoginAdminRequest):
    try:
        result = await Login_Admin(body.AdminID, body.AdminPass)
        return {"token": result}
    except:
        raise


@app.get("/retrieve_user")
async def retrive_user_route(FB_ID: str, token: dict = Depends(tokenCheck)):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        result = await get_user(FB_ID)
        return result
    except:
        raise


@app.delete("/delete_user")
async def delete_user_route(FB_ID: str, token: dict = Depends(tokenCheck)):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        auth.delete_user(FB_ID)
        await DeleteUser(FB_ID)
        return {
                "message": "user deleted successfully"}
    except:
        raise

class AddUserRequest(BaseModel):
    name: str
    email: str
    passW: str
    ph_id: Optional[int]= None 
    ph_name: Optional[str] = None


@app.post("/add_user")
async def add_user_route(
    request: AddUserRequest, token: dict = Depends(tokenCheck)
):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        try:
            user = auth.create_user(
                email=request.email,
                password=request.passW,
                display_name=request.name,
            )
            FB_id = user.uid
        except auth.EmailAlreadyExistsError:
            return {"detail": "Email already in use"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating user in Firebase: {str(e)}"
            )

     
        response = await AddUser(
            name=request.name,
            ph_id=request.ph_id,
            ph_name=request.ph_name,
            email=request.email,
            FB_id=FB_id,
        )

        send_email(request.email,"MyPharmacy Account Created",f"your account have been created \nuse this password to login:{request.passW}\nyou can change it later")
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/retrieve_pharma")
async def retrive_pharma_route(PhID: int, token: dict = Depends(tokenCheck)):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        result = await getPharmaDetails(PhID)
        return result
    except:
        raise

@app.delete("/delete_pharma")
async def delete_pharma_route(ID: int, token: dict = Depends(tokenCheck)):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        await DeletePharmacy(ID)
        return {
                "message": "pharmacy deleted successfully"}
    except:
        raise



class addBranchRequest(BaseModel):
    FB_id:str
    ph_name:str

@app.post("/add_branch")
async def add_branch_route(body:addBranchRequest,token: dict = Depends(tokenCheck)):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        await AddBranch(FB_id=body.FB_id, ph_name=body.ph_name)
        return {
                "message": "branch created successfully"}
    except:
        raise



@app.get("/update_Inspect")
async def inspect_update_logs_route(
    ph_id: int,
    token: dict = Depends(tokenCheck),
    from_date: Optional[datetime.date] = None,
    to_date: Optional[datetime.date] = None,
):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")
    logs = await get_update_logs(ph_id, from_date, to_date)
    return logs


@app.get("/sell_Inspect")
async def inspect_sell_logs_route(
    ph_id: int,
    token: dict = Depends(tokenCheck),
    from_date: Optional[datetime.date] = None,
    to_date: Optional[datetime.date] = None,
):
    if token["PharmaAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")
    logs = await get_sell_logs(ph_id, from_date, to_date)
    return logs


@app.get("/tickets_next")
async def get_tickets_next_route(
    cursor: int, limit: Optional[int] = None, token: dict = Depends(tokenCheck)
):

    return await TicketNextPage(cursor, limit)


@app.get("/tickets_prev")
async def get_tickets_prev_route(
    cursor: int, limit: Optional[int] = None, token: dict = Depends(tokenCheck)
):
    return await TicketPreviousPage(cursor, limit)

@app.get("/tickets_refresh")
async def get_tickets_refrsh_route(
    cursor: int, limit: Optional[int] = None, token: dict = Depends(tokenCheck)
):
    return await TicketNextPage(cursor+1, limit)

class response(BaseModel):
    FB_id:  str
    TK_ID: int
    Title: str
    Body: str

@app.put("/ticket_respond")
async def respond_ticket_route(
  body:response,  token: dict = Depends(tokenCheck)
):
    try:
        
        user = auth.get_user(body.FB_id)
        send_email(user.email, body.Title, body.Body)
        await changeTicketState(TK_id=body.TK_ID,State="Complete")
        return f"Response sent to {user.email}, ticket closed"

    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to respond: {str(e)}")


class DiscardRequest(BaseModel):
     TK_id:int

@app.put("/ticket_discard")
async def discard_ticket_route(
 body:DiscardRequest,  token: dict = Depends(tokenCheck)
):
        await changeTicketState(TK_id=body.TK_id,State="Discard")
        return {
                "message": "ticket discarded"}


class DosageIn(BaseModel):
    MedID: int
    TaID: int
    unit: str
    concetration: int

@app.get("/TAList")
async def get_TAList_route():
    return await getTAList()

@app.post("/dosage_add")
async def add_dosage_route(body: DosageIn, token: dict = Depends(tokenCheck)):
    if token["MedAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        await AddMedTa(
            MedID=body.MedID,
            TaID=body.TaID,
            unit=body.unit,
            concetration=body.concetration,
        )
        return {
                "message":  "Dosage entry added successfully" }
    except HTTPException as e:
        raise e


@app.delete("/dosage_delete")
async def remove_dosage_route(MedID: int, TaID: int, token: dict = Depends(tokenCheck)):
    if token["MedAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        await RemoveMedTa(MedID=MedID, TaID=TaID)
        return {
                "message": "Dosage entry removed successfully"}
    except HTTPException as e:
        raise e


class changeStateRequest(BaseModel):
    Med_id: int

@app.put("/change_med_state")
async def change_med_state_route(body: changeStateRequest, token: dict = Depends(tokenCheck)):
    if token["MedAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        await ChangeState(body.Med_id)
        return {"message": "Medicine state updated successfully"}

    except Exception as e:
        raise e


@app.get("/ManufacturerList")
async def get_ManufacturerList_route():
    return await getManufacturerList()


class MedRequest(BaseModel):
    Description: str = ""
    Brand: str
    med: str
    Manufacturer_id: int
    POM: str
    DosageForm: str

@app.post("/add_med")
async def add_med_route(req: MedRequest, token: dict = Depends(tokenCheck)):
    if token["MedAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return await addMed(
            Description=req.Description,
            Brand=req.Brand,
            med=req.med,
            Manufacturer_id=req.Manufacturer_id,
            POM=req.POM,
            DosageForm=req.DosageForm
        )
    except Exception as e:
        raise 


@app.post("/UploadMedIMG")
async def upload_image(image: UploadFile = File(...), Med_id: str = Form(...),token: dict = Depends(tokenCheck)):
    if token["MedAccess"] != "Yes":
        raise HTTPException(status_code=403, detail="Access denied")

    if image.content_type != "image/png":
        raise HTTPException(status_code=409, detail="faild to upload image")

    save_path = f"Assets/{Med_id}.png"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {"message": "Image saved successfully", "path": save_path}


if __name__ == "__main__":
    uvicorn.run("Api:app", host="0.0.0.0", port=8000, reload=True)
