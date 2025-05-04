from pydantic import BaseModel
from typing import List,Dict
from langchain_core.messages import BaseMessage

class chatData(BaseModel):
    data:List[Dict]