import httpx
from fastapi import Depends, HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from .. import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
IAM_SERVICE_DEV = "http://localhost:8000/get_current_user"
IAM_SERVICE_PROD = "https://iam.forge-code.com/get_current_user"

async def authenticate_with_iam(token: str):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(IAM_SERVICE_PROD, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user_data = response.json()
        return models.User(**user_data)

async def auth_required(token: str = Depends(oauth2_scheme)):
    return await authenticate_with_iam(token)