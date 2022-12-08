from datetime import datetime
from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        Boolean,
                        Text,
                        Float,
                        ForeignKey)
from sqlalchemy.orm import relationship
from api_modules import Base


class Cameras(Base):
    __tablename__ = "cameras"
    __table_args__ = ({"mysql_charset": "utf8mb3", "mysql_row_format": "DYNAMIC"})

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    camera_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=False)
    url = Column(String(255), nullable=False, unique=False)
    # TODO: マスク画像とオーバーレイ画像も
    latest_image_path = Column(String(255), nullable=False, unique=False)
    static_latest_image_path = Column(String(255), nullable=False, unique=False)
    pt_lefttop_lon = Column(Float, nullable=True)
    pt_lefttop_lat = Column(Float, nullable=True)
    pt_leftbottom_lon = Column(Float, nullable=True)
    pt_leftbottom_lat = Column(Float, nullable=True)
    pt_righttop_lon = Column(Float, nullable=True)
    pt_righttop_lat = Column(Float, nullable=True)
    pt_rightbottom_lon = Column(Float, nullable=True)
    pt_rightbottom_lat = Column(Float, nullable=True)
    sea_direction = Column(Float, nullable=True)
    images = relationship("Images", back_populates="camera")


class Images(Base):
    __tablename__ = "images"
    __table_args__ = ({"mysql_charset": "utf8mb3", "mysql_row_format": "DYNAMIC"})

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(String(255), nullable=False, unique=True)
    # image_name = Column(String(255), nullable=True)
    image_path = Column(String(255), nullable=False)
    static_image_path = Column(String(255), nullable=False)
    # mask_image_path = Column(String(255), nullable=True)
    # static_mask_image_path = Column(String(255), nullable=True)
    # overlay_image_path = Column(String(255), nullable=True)
    # static_overlay_image_path = Column(String(255), nullable=True)
    # trashes = Column(Text, nullable=True)
    # status = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    camera_id = Column(String(255), ForeignKey("cameras.camera_id"))
    camera = relationship("Cameras", back_populates="images")
