from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import DownloadLog, Article
from app.schemas.download_log import DownloadLogFilter
from app.schemas.response import success


def get_download_log_page(
        db: Session,
        query: DownloadLogFilter
):
    q = (
        db.query(
            DownloadLog.id.label("id"),
            DownloadLog.tid.label("tid"),
            DownloadLog.downloader.label("downloader"),
            DownloadLog.save_path.label("save_path"),
            DownloadLog.create_time.label("download_time"),

            Article.section.label("section"),
            Article.category.label("category"),
            Article.website.label("website"),
            Article.title.label("title"),
            Article.size.label("size"),
            Article.preview_images.label("preview_images"),
        )
        .join(Article, Article.tid == DownloadLog.tid)
    )

    # ---------- 条件过滤 ----------
    if query.downloader:
        q = q.filter(DownloadLog.downloader == query.downloader)

    if query.save_path:
        q = q.filter(DownloadLog.save_path.ilike(f"%{query.save_path}%"))

    total = q.count()

    # ---------- 分页 ----------
    page = query.page
    page_size = query.page_size
    offset = (page - 1) * page_size

    rows = (
        q.order_by(desc(DownloadLog.create_time))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ---------- 是否还有下一页 ----------
    has_more = len(rows) == page_size

    return success({
        "page": page,
        "pageSize": page_size,
        "hasMore": has_more,
        "total": total,
        "items": [
            {
                "id": r.id,
                "tid": r.tid,
                "section": r.section,
                "category": r.category,
                "website": r.website,
                "title": r.title,
                "size": r.size,
                "img_list": ','.join(
                    [f'/api/v1/img-proxy/?url={url}' for url in
                     r.preview_images]) if r.preview_images and r.website == 'x1080x' else r.preview_images,
                "downloader": r.downloader,
                "save_path": r.save_path,
                "download_time": r.download_time,
            }
            for r in rows
        ],
    })


def get_download_state(db: Session):
    download_count = db.query(DownloadLog).count()
    rows = (
        db.query(
            Article.section,
            func.count(Article.tid).label("count")
        )
        .join(DownloadLog, DownloadLog.tid == Article.tid)
        .group_by(Article.section)
        # .having(func.count(Article.tid) > 5)
        .all()
    )

    new_rows = [row._mapping for row in rows]
    return success({
        "download_count": download_count,
        "section_count": new_rows,
    })
