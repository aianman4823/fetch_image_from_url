from api_modules import Images, Cameras
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
import uuid
from api_modules import SessionLocal


def get_camera_by_id(db: Session, camera_id: str) -> Cameras:
    return db.query(Cameras).filter(Cameras.camera_id == camera_id).first()


def get_unique_cameraIds(db: Session):
    camera_ids = db.query(Cameras.camera_id).all()
    return camera_ids


def get_latest_image_by_cameraid(db: Session, camera_id: str) -> Images:
    return db.query(Images).filter(Images.camera_id == camera_id).order_by(desc(Images.created_at)).first()


def get_images_by_cameraid(db: Session, camera_id: str) -> Cameras:
    return db.query(Images).filter(Images.camera_id == camera_id).all()

# def get_all_user(camera_url: str,
#                  camera_id: str,
#                  db: Session = Depends(get_db)):

#     return


# def get_image_by_name(db: Session, image_name: int):
#     return db.query(Images).filter(Images.file_name == image_name).first()


# def get_image_by_image_id(db: Session, image_id: str):
#     return db.query(Images).filter(Images.image_id == image_id).first()


# def upload_image(db: Session, image_id: str, image_name: str, file_path: str, static_file_path: str):
#     db_image = Images(
#         image_id=image_id,
#         image_name=image_name,
#         image_path=file_path,
#         static_image_path=static_file_path,
#         status=False)

#     db.add(db_image)
#     db.commit()
#     db.refresh(db_image)
#     return db_image
