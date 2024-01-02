from fastapi import FastAPI
from app.routers.customer import router as customer_router
import uvicorn

app = FastAPI()

# Include the customer router from app.customer module
app.include_router(customer_router)

@app.get("/")
def read_root():
    return {"Welcome to Customer API for the EnergySage Interview"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

# docker run -dit --rm -p 3000:3000 --name energysage_api_run energysage_fast_api
# docker build -t energysage_fast_api .
    
# pytest myproj test --cov=myproj --cov-report=html --cov-report=xml --cov-context=test --doctest-modules
