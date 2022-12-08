from typing import List, Union
from pydantic import BaseModel
from datetime import datetime


class ImagesBase(BaseModel):
    image_id: str
    image_name: Union[str, None] = None
    image_path: str
    static_image_path: str
    mask_image_path: Union[str, None] = None
    static_mask_image_path: Union[str, None] = None
    overlay_image_path: Union[str, None] = None
    static_overlay_image_path: Union[str, None] = None
    trashes: Union[str, None] = None
    status: bool
    created_at: datetime


# class Images(ImagesBase):
#     camera_id: str

#     class Config:
#         orm_mode = True


class CamerasBase(BaseModel):
    name: str
    url: str
    pt_lefttop_lon: Union[float, None] = None
    pt_lefttop_lat: Union[float, None] = None
    pt_leftbottom_lon: Union[float, None] = None
    pt_leftbottom_lat: Union[float, None] = None
    pt_righttop_lon: Union[float, None] = None
    pt_righttop_lat: Union[float, None] = None
    pt_rightbottom_lon: Union[float, None] = None
    pt_rightbottom_lat: Union[float, None] = None
    sea_direction: Union[float, None] = None

    # images: List[Images] = []

    class Config:
        orm_mode = True


class CamerasCreate(CamerasBase):
    pass
