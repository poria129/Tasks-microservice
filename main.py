from fastapi import FastAPI


from Auth.routers import routers

app = FastAPI()

app.include_router(routers.router)
