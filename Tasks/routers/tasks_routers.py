from fastapi import APIRouter, HTTPException, Body, Path
from bson import ObjectId
from Tasks.models.models import CreateTasks, UpdateTasks, JoinTask
from database import MongoDBManager

router = APIRouter()


def get_collection():
    with MongoDBManager() as db_manager:
        task_collection = db_manager.tasks
        return task_collection


@router.post("/")
def create_tasks(task: CreateTasks):
    get_collection().insert_one(dict(task))


@router.get("/")
def get_tasks():
    pipeline = [{"$match": {}}]

    tasks = list(get_collection().aggregate(pipeline))

    tasks_list = [{**task, "_id": str(task["_id"])} for task in tasks]

    return tasks_list


@router.put("/tasks/{id}/update-fields", response_model=UpdateTasks)
def update_task(
    id: str = Path(..., title="Task ID"),
    fields: UpdateTasks = Body(..., title="Fields to Update"),
):
    pipeline = [
        {"$match": {"_id": ObjectId(id)}},
        {
            "$project": {
                "subject": 1,
                "status": 1,
                "project": 1,
                "is_group": 1,
                "priority": 1,
                "detail": 1,
                "updated_at": 1,
            }
        },
    ]

    result = list(get_collection().aggregate(pipeline))

    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    existing_fields = result[0]

    updated_fields = {
        key: value
        for key, value in fields.model_dump().items()
        if key in existing_fields
    }

    get_collection().update_one({"_id": ObjectId(id)}, {"$set": updated_fields})

    return updated_fields


@router.put("/join/{id}")
def join_the_task(id: str, task: JoinTask):
    pass


@router.delete("/{id}")
def delete_task(id: str):
    pass