import io

import requests
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.core.config import config_manager
from app.utils.log import logger

router = APIRouter()


@router.get("/")
def image_proxy(url: str):
    proxies = {
        "http": config_manager.get().PROXY,
        "https": config_manager.get().PROXY
    }
    headers = {
        'Referer': 'https://agaghhh.cc/'
    }
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=10)
        if response.ok:
            return StreamingResponse(io.BytesIO(response.content),
                                     media_type=response.headers.get('content-type', 'image/jpeg'))
        else:
            logger.error(f"下载图片失败：{response.status_code}")
    except Exception as e:
        logger.error(f"下载图片失败：{e}")
    return url
