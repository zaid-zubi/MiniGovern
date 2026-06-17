from pydantic import BaseModel


class CreateScanJob(BaseModel):
    datasource_id: int
