from fastapi import FastAPI


from Auth.routers import auth_routers
from Tasks.routers import tasks_routers

app = FastAPI()

app.include_router(auth_routers.router)
app.include_router(tasks_routers.router)
