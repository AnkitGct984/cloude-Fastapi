from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

# FastAPI Application Initialization
app = FastAPI(
    title="Cloud Infrastructure Manager API",
    description="A high-performance cloud resource monitoring and management API built with FastAPI.",
    version="1.0.0"
)

# Pydantic Models for Data Validation
class CloudResourceCreate(BaseModel):
    resource_name: str = Field(..., min_length=2, max_length=50, description="Name of the cloud instance")
    service_type: str = Field(..., description="e.g., EC2, S3, Lambda, Database")
    region: str = Field(..., description="Cloud region e.g., us-east-1, ap-south-1")
    is_active: bool = True

class CloudResourceResponse(CloudResourceCreate):
    id: int
    created_at: str

# In-Memory Database for Fast Execution
database: List[CloudResourceResponse] = []
id_counter = 1

# 1. Root Endpoint
@app.get("/", tags=["System Status"])
def health_check():
    return {
        "status": "online",
        "framework": "FastAPI",
        "language": "Python",
        "message": "Cloud API is running successfully!"
    }

# 2. Get All Cloud Resources (GET)
@app.get("/resources", response_model=List[CloudResourceResponse], tags=["Cloud Resources"])
def get_all_resources():
    return database

# 3. Create a New Cloud Resource (POST)
@app.post("/resources", response_model=CloudResourceResponse, status_code=status.HTTP_201_CREATED, tags=["Cloud Resources"])
def create_resource(resource: CloudResourceCreate):
    global id_counter
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = CloudResourceResponse(
        id=id_counter,
        created_at=current_time,
        **resource.dict()
    )
    database.append(new_entry)
    id_counter += 1
    return new_entry

# 4. Get Resource by ID (GET)
@app.get("/resources/{resource_id}", response_model=CloudResourceResponse, tags=["Cloud Resources"])
def get_resource_by_id(resource_id: int):
    for item in database:
        if item.id == resource_id:
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cloud resource with ID {resource_id} not found."
    )

# 5. Delete Resource (DELETE)
@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cloud Resources"])
def delete_resource(resource_id: int):
    for index, item in enumerate(database):
        if item.id == resource_id:
            database.pop(index)
            return None
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cloud resource with ID {resource_id} not found."
    )