
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, Form, Depends
import json

# from app.Security.dependencies import get_current_user
from app.services.ExcelAnylyzer import ExcelAnalyzer
from app.db.session import get_db
from app.dependencies.services import get_lead_service
from app.services.Bulk_Upload import LeadImporter

router = APIRouter(
    prefix="/leads",
    tags=["Lead Import"],
)

excel_analyzer = ExcelAnalyzer()


@router.post("/analyzer")
async def analyze_excel(
    file: Annotated[UploadFile, File(...)],
    workbook: Annotated[
        str | None,
        Query(description="Worksheet name, e.g. Sheet1")
    ] = None,
):
    filename = (file.filename or "").lower()

    if not filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx and .xls files are supported.",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        return excel_analyzer.analyze(
            file_bytes=file_bytes,
            workbook=workbook,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

@router.post("/import")
async def import_excel_leads(
    file: Annotated[UploadFile, File(...)],
    workbook: Annotated[str, Form(...)],
    mapping: Annotated[str, Form(...)],
    db =Depends(get_db),
        lead_service=Depends(get_lead_service)
    # Use your existing authenticated-user dependency here.
    # current_user=Depends(get_current_user),
):
    filename = (file.filename or "").lower()

    if not filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx and .xls files are supported.",
        )

    try:
        try:
            column_mapping = json.loads(mapping)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid mapping JSON.",
            ) from exc

        if not isinstance(column_mapping, dict) or not all(
            isinstance(k, str) and isinstance(v, str)
            for k, v in column_mapping.items()
        ):
            raise HTTPException(
                status_code=400,
                detail="Mapping must be a JSON object of field names to column names.",
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        importer = LeadImporter(
            db=db,
            lead_service=lead_service,
        )

        return await importer.import_excel(
            file_bytes=file_bytes,
            user_id=UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"),
            workbook=workbook,
            mapping=column_mapping,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()
