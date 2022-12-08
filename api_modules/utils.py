from fastapi.routing import APIRoute
from fastapi import Request, Response
from typing import Callable
import json
import logging
from pathlib import Path
import numpy as np
import os
from urllib.request import urlopen
from urllib.error import URLError


def download_image_file(url, dst_path):
    try:
        with urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except URLError as e:
        print(e)

