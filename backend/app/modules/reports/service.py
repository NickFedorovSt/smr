"""Reports service — orchestration + caching in ReportCache + MinIO.

Flow (Раздел 6.7):
  1. Hash params → check ReportCache
  2. Cache hit → return MinIO file_path
  3. Cache miss → build report → upload to MinIO → insert ReportCache → return path
  4. Delete → remove from MinIO + ReportCache
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.reports.excel_builder import EXCEL_BUILDERS
from app.modules.reports.models import ReportCache
from app.modules.reports.pdf_builder import PDF_BUILDERS
from app.modules.reports.schemas import ReportType

try:
    from minio import Minio
except ImportError:
    Minio = None  # type: ignore[assignment,misc]


# ═══════════════════════════════════════════════════════════════
# MinIO helpers
# ═══════════════════════════════════════════════════════════════

def _get_minio_client() -> Any:
    """Create MinIO client from settings."""
    if Minio is None:
        raise RuntimeError("minio package not installed")
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=False,
    )


def _ensure_bucket(client: Any, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def _upload_to_minio(data: bytes, object_name: str, content_type: str) -> str:
    """Upload bytes to MinIO bucket, return full object path."""
    client = _get_minio_client()
    bucket = settings.minio_bucket_reports
    _ensure_bucket(client, bucket)
    client.put_object(
        bucket,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return f"{bucket}/{object_name}"


def _download_from_minio(file_path: str) -> bytes:
    """Download bytes from MinIO. file_path = 'bucket/object_name'."""
    client = _get_minio_client()
    parts = file_path.split("/", 1)
    bucket = parts[0]
    obj = parts[1] if len(parts) > 1 else ""
    response = client.get_object(bucket, obj)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def _delete_from_minio(file_path: str) -> None:
    """Delete object from MinIO."""
    client = _get_minio_client()
    parts = file_path.split("/", 1)
    bucket = parts[0]
    obj = parts[1] if len(parts) > 1 else ""
    client.remove_object(bucket, obj)


# ═══════════════════════════════════════════════════════════════
# Params hashing
# ═══════════════════════════════════════════════════════════════

def _hash_params(report_type: str, params: dict[str, Any]) -> str:
    """Deterministic MD5 of report type + sorted params."""
    payload = json.dumps({"type": report_type, **params}, sort_keys=True, default=str)
    return hashlib.md5(payload.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════
# File extension / content-type helpers
# ═══════════════════════════════════════════════════════════════

# Reports that produce PDF (primarily print forms)
_PDF_TYPES = {"KS2", "KS3", "M29_REPORT", "WORK_JOURNAL_PRINT", "EXECUTIVE_DASHBOARD"}


def _get_ext_and_ct(report_type: str) -> tuple[str, str]:
    """Return (file_extension, content_type) for a report type."""
    if report_type in _PDF_TYPES:
        return ".pdf", "application/pdf"
    return ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ═══════════════════════════════════════════════════════════════
# ReportService
# ═══════════════════════════════════════════════════════════════

class ReportService:
    """Orchestrates report generation with caching."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate(
        self,
        report_type: ReportType,
        params: dict[str, Any],
    ) -> tuple[bytes, str, str]:
        """Generate or retrieve cached report.

        Returns:
            (file_bytes, filename, content_type)
        """
        rt = report_type.value
        params_hash = _hash_params(rt, params)

        # 1. Check cache
        cached = await self._get_cache(rt, params_hash)
        if cached:
            ext, ct = _get_ext_and_ct(rt)
            filename = f"{rt}_{params_hash}{ext}"
            try:
                data = _download_from_minio(cached.file_path)
                return data, filename, ct
            except Exception:
                # Stale cache entry — file missing in MinIO; regenerate
                await self._delete_cache_entry(cached.id)

        # 2. Build report
        data = await self._build_report(rt, params)
        ext, ct = _get_ext_and_ct(rt)
        filename = f"{rt}_{params_hash}{ext}"

        # 3. Upload to MinIO
        object_name = f"reports/{filename}"
        file_path = _upload_to_minio(data, object_name, ct)

        # 4. Save to ReportCache
        await self._save_cache(rt, params_hash, file_path)

        return data, filename, ct

    async def list_reports(self, project_id: UUID | None = None) -> list[dict[str, Any]]:
        """List cached reports, optionally filtered by project_id in params_hash."""
        stmt = select(ReportCache).order_by(ReportCache.generated_at.desc())
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return [
            {
                "id": r.id,
                "report_type": r.report_type,
                "params_hash": r.params_hash,
                "file_path": r.file_path,
                "generated_at": r.generated_at,
            }
            for r in rows
        ]

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete from MinIO + ReportCache."""
        cached = await self.session.get(ReportCache, report_id)
        if not cached:
            return False

        # Delete from MinIO (ignore errors if file already gone)
        try:
            _delete_from_minio(cached.file_path)
        except Exception:
            pass

        await self.session.execute(
            delete(ReportCache).where(ReportCache.id == report_id)
        )
        await self.session.flush()
        return True

    # ── private ──────────────────────────────────────────────

    async def _build_report(self, rt: str, params: dict[str, Any]) -> bytes:
        """Dispatch to the correct builder and produce bytes."""
        # PDF builders take priority for types that have both (e.g. M29)
        if rt in PDF_BUILDERS:
            builder = PDF_BUILDERS[rt]()
            return await builder.build(self.session, params)
        if rt in EXCEL_BUILDERS:
            builder_xl = EXCEL_BUILDERS[rt]()  # type: ignore[assignment]
            return await builder_xl.build(self.session, params)
        raise ValueError(f"No builder registered for report type '{rt}'")

    async def _get_cache(self, report_type: str, params_hash: str) -> ReportCache | None:
        result = await self.session.execute(
            select(ReportCache).where(
                ReportCache.report_type == report_type,
                ReportCache.params_hash == params_hash,
            )
        )
        return result.scalar_one_or_none()

    async def _save_cache(self, report_type: str, params_hash: str, file_path: str) -> ReportCache:
        entry = ReportCache(
            report_type=report_type,
            params_hash=params_hash,
            file_path=file_path,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def _delete_cache_entry(self, entry_id: UUID) -> None:
        await self.session.execute(
            delete(ReportCache).where(ReportCache.id == entry_id)
        )
        await self.session.flush()
