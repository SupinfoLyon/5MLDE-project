from fastapi import FastAPI, Response
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from pydantic import BaseModel
import json
import ast

class Payload(BaseModel):
    GROSS_SQUARE_FEET: int = None
    LAND_SQUARE_FEET: int = None
    YEAR_BUILT: int = None
    NEIGHBORHOOD: str = None
    BUILDING_CLASS_CATEGORY: str = None
    TAX_CLASS_AT_PRESENT: str = None
    BLOCK: str = None
    LOT: str = None
    BUILDING_CLASS_AT_PRESENT: str = None
    ZIP_CODE: str = None
    RESIDENTIAL_UNITS: str = None
    COMMERCIAL_UNITS: str = None
    TOTAL_UNITS: str = None
    TAX_CLASS_AT_TIME_OF_SALE: str = None
    BUILDING_CLASS_AT_TIME_OF_SALE: str = None
    SALE_DATE: str = None

class ResponsePredict(BaseModel):
    prediction: int

app = FastAPI(title="NYC rolling sales prediction",
              description="This is a simple API for NYC rolling sales prediction",
              version="0.0.1")

mlflow.set_tracking_uri("http://mlflow:5000") 
client = MlflowClient()

# allow CORS
@app.middleware("http")
async def add_cors_headers(request, call_next):
    if request.method == "OPTIONS":
        response = Response()
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, Authorization"
    return response

@app.post("/predict", status_code=200)
def predict(payload: Payload):
    model_uri = client.get_latest_versions("NYC Rolling Sales", stages=["Production"])[0].source
    pipeline = mlflow.sklearn.load_model(model_uri)

    # rename payload keys ( replace "-" with "_" )
    payload = payload.dict()
    payload = {k.replace("_", " "): v for k, v in payload.items()}

    # convert payload to dataframe
    df = pd.DataFrame(payload, index=[0])

    return {"prediction": pipeline.predict(df).tolist()}

@app.get("/params", status_code=200)
def get_params():
    model_uri = client.get_latest_versions("NYC Rolling Sales", stages=["Production"])[0].source
    params = client.get_run(client.get_latest_versions("NYC Rolling Sales", stages=["Production"])[0].run_id).data.params
    quantitative_variables = ast.literal_eval(params["quantitative_variables"])
    categorical_variables = ast.literal_eval(params["categorical_variables"])
    combined_variables = quantitative_variables + categorical_variables

    return {k: "int" if k in quantitative_variables else "str" for k in combined_variables}