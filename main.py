import logging
import asyncio
from api_modules import (SessionLocal,
                         engine,
                         Base,
                         ImagesBase,
                         CamerasBase,
                         CamerasCreate,
                         Cameras,
                         get_camera_by_id,
                         get_unique_cameraIds,
                         download_image_file,
                         get_latest_image_by_cameraid,
                         get_images_by_cameraid,
                         Images)


from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import FastAPI, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
import os
from io import BytesIO
import zipfile
import shutil
import uvicorn
from pathlib import Path
import uuid

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


from dotenv import load_dotenv
load_dotenv()

osCurrentDirectory = os.getcwd()
STATIC_FILES_DIR_NAME = os.environ["STATIC_FILES_DIR_NAME"]
STATIC_URL = os.environ["STATIC_URL"]

STATIC_LATEST_DIR_NAME = os.environ["STATIC_LATEST_DIR_NAME"]
STATIC_LATEST = os.environ["STATIC_LATEST"]


Base.metadata.create_all(bind=engine)

app = FastAPI()

tmp_image_dir = os.path.join(osCurrentDirectory, STATIC_FILES_DIR_NAME)
if not Path(tmp_image_dir).exists():
    os.makedirs(tmp_image_dir)
    try:
        app.mount(f"/{STATIC_FILES_DIR_NAME}",
                  StaticFiles(directory=tmp_image_dir, html=True),
                  name=STATIC_FILES_DIR_NAME)
    except Exception as e:
        print(e)

tmp_latest_dir = os.path.join(osCurrentDirectory, STATIC_LATEST_DIR_NAME)
if not Path(tmp_latest_dir).exists():
    os.makedirs(tmp_latest_dir)
    try:
        app.mount(f"/{STATIC_LATEST_DIR_NAME}",
                  StaticFiles(directory=tmp_latest_dir, html=True),
                  name=STATIC_LATEST_DIR_NAME)
    except Exception as e:
        print(e)


origins = [
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(e)
    finally:
        db.close()



user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
database = os.environ["DATABASE"]



@app.on_event("startup")
async def startup():
    @repeat_every(seconds=60 * 2, wait_first=True)
    async def get_all_camera():
        print("done")
        # TODO: 
        SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)
        db = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
        cameras_all = db.query(Cameras).all()
        print(cameras_all)
        for camera in cameras_all:
            await register_image(camera.url, camera.camera_id, db)
    await get_all_camera()


@app.post("/api/v1/register_camera", response_class=JSONResponse)
async def register_camera(camera: CamerasCreate,
                          background_tasks: BackgroundTasks,
                          db: Session = Depends(get_db)):
    camera_id = None
    try:
        camera_id = str(uuid.uuid4())
        db_camera = Cameras()
        db_camera.name = camera.name
        db_camera.url = camera.url
        db_camera.pt_lefttop_lat = camera.pt_lefttop_lat
        db_camera.pt_lefttop_lon = camera.pt_lefttop_lon
        db_camera.pt_leftbottom_lat = camera.pt_leftbottom_lat
        db_camera.pt_leftbottom_lon = camera.pt_leftbottom_lon
        db_camera.pt_righttop_lat = camera.pt_righttop_lat
        db_camera.pt_righttop_lon = camera.pt_righttop_lon
        db_camera.pt_rightbottom_lat = camera.pt_rightbottom_lat
        db_camera.pt_rightbottom_lon = camera.pt_rightbottom_lon
        db_camera.sea_direction = camera.sea_direction
        db_camera.camera_id = camera_id

        download_image_file(camera.url,
                            # TDOO: 本当はディレクトリをユーザごとに分けるとかしたいな
                            dst_path=os.path.join(tmp_latest_dir, f"{camera_id}.jpg"))

        db_camera.latest_image_path = os.path.join(tmp_latest_dir, f"{camera_id}.jpg")
        db_camera.static_latest_image_path = os.path.join(STATIC_LATEST, f"{camera_id}.jpg")

        db.add(db_camera)
        db.commit()
        db.flush()
    except Exception as e:
        print(e)
        raise e

    try:
        background_tasks.add_task(register_image, camera.url, camera_id, db)
    except Exception as e:
        print(e)

    # try:
    #     background_tasks.add_task(update_latest_image, camera_id, db)
    # except Exception as e:
    #     print(e)

    response = {
        "camera_id": camera_id,
        "name": camera.name,
        "url": camera.url,
    }
    return response


@ app.get("/api/v1/camera/camera_ids={camera_ids}", response_class=JSONResponse)
def get_cameras_by_camera_ids(camera_ids: str, db: Session = Depends(get_db)):
    camera_ids_list = camera_ids.split(",")
    db_cameras = []
    for camera_id in camera_ids_list:
        db_camera: Cameras = get_camera_by_id(db=db, camera_id=camera_id)
        if db_camera is None:
            raise HTTPException(status_code=404, detail="camera id not found")
        db_cameras.append(db_camera)

    responses = []
    for db_camera in db_cameras:
        response = {
            "name": db_camera.name,
            "url": db_camera.url,
            "pt_lefttop_lat": db_camera.pt_lefttop_lat,
            "pt_lefttop_lon": db_camera.pt_lefttop_lon,
            "pt_leftbottom_lat": db_camera.pt_leftbottom_lat,
            "pt_leftbottom_lon": db_camera.pt_leftbottom_lon,
            "pt_righttop_lat": db_camera.pt_righttop_lat,
            "pt_righttop_lon": db_camera.pt_righttop_lon,
            "pt_rightbottom_lat": db_camera.pt_rightbottom_lat,
            "pt_rightbottom_lon": db_camera.pt_rightbottom_lon,
            "sea_direction": db_camera.sea_direction,
            "camera_id": db_camera.camera_id
        }
        responses.append(response)
    return responses


# TODO: ログインしているユーザの登録しているカメラIDを取得
# @repeat_every(seconds=2 * 60)
async def register_image(camera_url: str,
                         camera_id: str,
                         db: Session = Depends(get_db)):
    print(camera_url)
    print(camera_id)
    image_id = str(uuid.uuid4())
    download_image_file(camera_url,
                        # TDOO: 本当はディレクトリをユーザごとに分けるとかしたいな
                        dst_path=os.path.join(tmp_image_dir, f"{image_id}.jpg"))
    image_db = Images()
    image_db.image_id = image_id
    image_db.image_path = os.path.join(tmp_image_dir, f"{image_id}.jpg")
    image_db.static_image_path = os.path.join(STATIC_URL, f"{image_id}.jpg")
    image_db.camera_id = camera_id
    db.add(image_db)
    db.commit()
    db.flush()

    shutil.copyfile(image_db.image_path,
                    os.path.join(STATIC_LATEST_DIR_NAME, f"{camera_id}.jpg"))
    return

# 1.登録されているユーザ全取得
# 2.各ユーザごとに登録されているカメラ全取得
# 3.一つ一つ更新するかどうかをチェック(どれくらいの頻度で更新するかどうかを決められるように。
# もし決めた期間より時間が経過していたら、is_update=Trueにし、Trueのカメラのみ更新)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8001)
