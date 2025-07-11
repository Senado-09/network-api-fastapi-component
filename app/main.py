from fastapi import FastAPI
from networks.app.router.networks import router as networks_router

app = FastAPI(
    title="Network API",
    description="A FastAPI backend component to manage user networks, members, and tree structures.",
    version="0.1.0"
)

# Include the router from your network module
app.include_router(networks_router, prefix="/network", tags=["Network"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Network FastApi Component"}
