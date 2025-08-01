from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    ...


@app.post("/logout")
async def logout(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    ...


@app.get("/logoutall")
async def logoutall(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    ...
