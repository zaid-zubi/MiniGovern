from pydantic import BaseModel, Field

class CreateScanJob(BaseModel):
    datasource_id: int