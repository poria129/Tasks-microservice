from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from bson import ObjectId

from Tasks.services.dependencies import get_current_user, get_current_staff_user
from Tasks.models.models import CreateTasks, UpdateTasks, JoinTask
from database import MongoDBManager

router = APIRouter()


def get_collection():
    with MongoDBManager() as db_manager:
        task_collection = db_manager.tasks
        return task_collection


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_tasks(task: CreateTasks):
    get_collection().insert_one(dict(task))


@router.get("/", status_code=status.HTTP_200_OK)
def get_tasks(current_user: dict = Depends(get_current_staff_user)):
    pipeline = [{"$match": {}}]

    tasks = list(get_collection().aggregate(pipeline))

    tasks_list = [{**task, "_id": str(task["_id"])} for task in tasks]

    return tasks_list


@router.put(
    "/tasks/{id}/update-task",
    response_model=UpdateTasks,
    status_code=status.HTTP_200_OK,
)
def update_task(
    id: str = Path(..., title="Task ID"),
    fields: UpdateTasks = Body(..., title="Tasks to Update"),
    current_user: dict = Depends(get_current_staff_user),
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


@router.put("/tasks/{task_id}/update-participators", response_model=JoinTask)
def update_task_participators(
    task_id: int = Path(
        ..., title="Task ID", description="The ID of the task to update"
    ),
    current_user: dict = Depends(get_current_user),
    join_task: JoinTask = Depends(),
):
    if current_user["id"] in join_task.participators:
        raise HTTPException(status_code=409, detail="User already joined!")

    updated_task = get_collection().find_one_and_update(
        {"_id": task_id},
        {
            "$push": {"participators": current_user["id"]},
            "$set": {"updated_at": datetime.now()},
        },
        projection={"_id": False},
        return_document=False,
    )
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    return {
        "message": f"User {current_user['id']} added to participators of task {task_id}"
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: str):
    get_collection().find_one_and_delete({"_id": ObjectId(id)})
