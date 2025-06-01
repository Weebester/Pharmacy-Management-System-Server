import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import datetime
import secrets
from Logic import (
    Account_Details,
    AccountPharmacy,
    Accounts,
    Admins,
    Flag,
    Pharmacies,
    UpdateLog,
)
from tortoise import transactions


###########################################################Tokens##############################################################

secret_key = secrets.token_hex(32)


# token gen
def gen_access_token(account: list[Account_Details]):
    payload = {
        "pharmacies": [var["PH_id"] for var in account],  # List of pharmacies
        "user_id": account[0]["AC_id"],
        "Manager": account[0]["manager"].value,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=100),
    }
    try:
        print(payload)
        token = jwt.encode(payload, secret_key, algorithm="HS256")
    except jwt.PyJWTError as e:
        raise RuntimeError(f"Token generation failed: {e}")
    return token


def gen_refresh_token(FB_id: str):
    payload = {
        "FB_id": FB_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=7),
    }
    try:
        token = jwt.encode(payload, secret_key, algorithm="HS256")
    except jwt.PyJWTError as e:
        raise RuntimeError(f"Token generation failed: {e}")
    return token


# token refresh
async def TokRefresh(refresh_token: str):
    try:
        decoded_token = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])
        FB_id = decoded_token.get("FB_id")

        if FB_id is None:
            raise HTTPException(status_code=400, detail="FB_id not found in token")

        user = await Account_Details.filter(FB_id=FB_id).values(
            "AC_id", "manager", "PH_id"
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return gen_access_token(user)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# token check
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def tokenCheck(token: str = Depends(oauth2_scheme)):
    # print(token)
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(payload)
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


#########################################################Login################################################################


async def Login_user(FB_id: str) -> dict:
    print("request received")
    print(FB_id)
    user = await Account_Details.filter(FB_id=FB_id).values("AC_id", "manager", "PH_id")
    if user:

        token = gen_access_token(user)

        return {
            "RefreshToken": gen_refresh_token(FB_id),
            "Token": token,
            "success": True,
        }

    else:
        return {"success": False, "message": "User not found", "status_code": 456}


####################################################LoginAdmin#################################################################


async def Login_Admin(AdminID: str, AdminPass: str) -> dict:
    print("request received")
    try:
        Admin = await Admins.get(Admin_id=AdminID)
    except:
        raise HTTPException(status_code=456, detail="Admin not Found")

    if bcrypt.checkpw(AdminPass.encode(), Admin.Password.encode()):

        payload = {
            "AdminID": Admin.Admin_id,
            "MedAccess": Admin.medAccess.value,
            "PharmaAccess": Admin.pharmaAccess.value,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=12),
        }
        try:
            print(payload)
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            return token
        except jwt.PyJWTError as e:
            raise RuntimeError(f"Token generation failed: {e}")

    else:
        raise HTTPException(status_code=403, detail="invalid password")


#####################################################Signup####################################################################


async def sign_up(name: str, pharmacyName: str, email: str, FB_id: str):

    async with transactions.in_transaction():

        pharmacy = await Pharmacies.create(Name=pharmacyName)

        account = await Accounts.create(
            user=name, Manager=Flag.Yes, email=email, FB_ID=FB_id
        )

        await AccountPharmacy.create(PH_id=pharmacy.PH_id, AC_id=account.AC_id)

        return {
            "message": "Account and pharmacy created successfully",
            "account_id": account.AC_id,
        }

##################################################################Assistants register/remove(Manager)########################################################

async def addAssistance(name: str, ph_id: int, email: str, FB_id: str):

    async with transactions.in_transaction():

        account = await Accounts.create(
            user=name, Manager=Flag.No, email=email, FB_ID=FB_id
        )

        await AccountPharmacy.create(PH_id=ph_id, AC_id=account.AC_id)

        await UpdateLog.create(
            ph_id=ph_id,
            date=datetime.datetime.now(),
            content=f"new assistant added ({name}) ",
        )

        return {
            "message": "Assistance Account created successfully",
            "account_id": account.AC_id,
        }


async def deleteAssistance(name: str, ph_id: int, FB_id: str):

    try:
        async with transactions.in_transaction():

            await Accounts.filter(FB_ID=FB_id).delete()

            await UpdateLog.create(
                ph_id=ph_id,
                date=datetime.datetime.now(),
                content=f"assistant deleted ({name}) ",
            )

            return {
                "message": "Assistance Account deleted successfully",
            }
    except:
        raise


#########################################################Users register/remove(App Admin)################################################

async def AddUser(
    name: str, ph_id: int | None, ph_name: str | None, email: str, FB_id: str
):
    try:
        flag=Flag.No
        async with transactions.in_transaction():
            if not ph_id:
                if not ph_name:
                    raise HTTPException(
                        status_code=400,
                        detail="Pharmacy name is required when no pharmacy ID is provided.",
                    )
                ph = await Pharmacies.create(Name=ph_name)
                ph_id = ph.PH_id
                flag=Flag.Yes

            account = await Accounts.create(
                user=name, Manager=flag, email=email, FB_ID=FB_id
            )

            await AccountPharmacy.create(PH_id=ph_id, AC_id=account.AC_id)

            return {
                "message": "Account created successfully",
                "FB_id": account.FB_ID,
            }
    except:
        raise


async def DeleteUser(uid: str):
    result = await Accounts.filter(FB_ID=uid).delete()

    if not result:
        raise HTTPException(status_code=409, detail="Failed to Delete user")
