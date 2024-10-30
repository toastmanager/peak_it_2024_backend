from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from src.media.dependencies import get_s3_repository
from src.media.repositories import MediaRepository

# This is EXAMPLE delete or change it

router = APIRouter(tags=["Media"])


def get_media_repository():
    yield get_s3_repository(bucket_name="sample-bucket")


media_depend: MediaRepository = Depends(get_media_repository)


@router.post(path="/")
async def upload_object(file: UploadFile = File(), media_repository=media_depend):
    try:
        if not file.filename:
            raise Exception('filename not provided')
        key = await media_repository.upload_object(
            object_key=file.filename, file=file.file
        )
        return {"message": "successfully loaded object", "key": key}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to upload file",
        )


@router.delete(path="/{object_key}")
async def delete_object_by_id(object_key: str, media_repository=media_depend):
    try:
        await media_repository.delete_objects(objects_keys=[{"Key": object_key}])
        return {"message": "successfully deleted object"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to delete file: " + str(e),
        )


@router.get(path="/{object_key}")
async def get_object_by_id(object_key: str, media_repository=media_depend):
    try:
        file = await media_repository.get_object(object_key=object_key)
        return Response(content=file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to get file: " + str(e),
        )


@router.put(path="/{object_key}")
async def replace_object_by_id(object_key: str, file: UploadFile = File(), media_repository=media_depend):
    try:
        key = await media_repository.replace_object(object_key=object_key, file=file.file)
        return {"message": "successfully replaced object", "key": key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to update file: " + str(e),
        )


@router.get(path="/")
async def get_all_objects(media_repository=media_depend):
    try:
        objects = await media_repository.get_all()
        return objects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to upload file: " + str(e),
        )
