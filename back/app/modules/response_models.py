from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserAuthentication(BaseModel):
    email: str
    password: str
    returnSecureToken : Optional[bool] = None

class UserRefreshToken(BaseModel):
    refresh_token : str

class MachineUpdate(BaseModel):
    name: str

class MachineCreate(BaseModel):
    id : str
    state : Optional[int] = None
    type : Optional[int] = None
    name : str


class ReportPreparation(BaseModel):
    preparation_id : str



class Coffee(BaseModel):
    id: Optional[str] = None
    name: str
    description: str



class CreatePreparation(BaseModel):
    coffee_id: str
    days_of_week : Optional[List[int]] = None
    hours : Optional[List[str]] = None
    machine_id : str
    name : Optional[str] = None
    next_time : Optional[str] = None
    saved : bool

class UpdatePreparationSaved(BaseModel):
    name : str
    coffee_id : str
    machine_id : str
    days_of_week : List[int]
    hours : list



class Machine(BaseModel):
    id : str
    name : str
    state : int
    type  : int
    last_update : datetime
    creation_date : datetime


class Preparation(BaseModel):
        coffee : Coffee
        creation_date : datetime
        last_update : datetime
        machine : Machine
        id : str
        saved : bool
        state : int
        next_time : datetime


class PreparationSaved(Preparation,BaseModel):
        days_of_week : List[int]
        hours : List[str]
        last_time : datetime
        name : str