
from io import BytesIO
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO


class LeadImporter:

    ALLOWED_FIELDS = {"name", "email", "phone","message"}

    def __init__(self, db: Session, lead_service):
        self.db = db
        self.lead_service = lead_service

    @staticmethod
    def _clean_value(value: Any) -> str | None:
        if value is None or pd.isna(value):
            return None

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        value = str(value).strip()
        return value or None

    async def import_excel(
        self,
        file_bytes: bytes,
        user_id: UUID,
        workbook: str,
        mapping: dict[str, str],
    ) -> dict:

        invalid_fields = set(mapping) - self.ALLOWED_FIELDS
        if invalid_fields:
            raise ValueError(
                f"Unsupported lead fields: {sorted(invalid_fields)}"
            )

        if not mapping:
            raise ValueError("At least one field mapping is required.")

        try:
            excel = pd.ExcelFile(BytesIO(file_bytes))
            if workbook not in excel.sheet_names:
                raise ValueError(
                    f"Worksheet '{workbook}' not found."
                )

            df = pd.read_excel(
                excel,
                sheet_name=workbook,
                dtype=object,
            )
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Unable to read Excel file.") from exc

        missing_columns = [
            source
            for source in mapping.values()
            if source not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Mapped columns not found: {missing_columns}"
            )

        imported = 0
        failed = 0
        skipped = 0
        row_results = []

        try:
            for index, row in df.iterrows():
                excel_row = int(index) + 2

                try:
                    lead_values = {
                        target: self._clean_value(row[source])
                        for target, source in mapping.items()
                    }

                    if not any(lead_values.values()):
                        skipped += 1
                        continue

                    lead_data = CreateManualLeadDTO(
                        name=lead_values.get("name"),
                        email=lead_values.get("email"),
                        phone_number=lead_values.get("phone"),
                    )

                    # Isolate a failed row so later rows can continue.
                    # Requires a transaction-capable SQLAlchemy session.
                    with self.db.begin_nested():
                        result = (
                            await self.lead_service.create_manual_lead_without_commit(
                                user_id=user_id,
                                lead_data=lead_data,
                            )
                        )
                        lead_id = str(result.id)

                    imported += 1
                    row_results.append({
                        "row": excel_row,
                        "status": "success",
                        "lead_id": lead_id,
                    })

                except Exception as exc:
                    failed += 1
                    row_results.append({
                        "row": excel_row,
                        "status": "failed",
                        "error": str(exc),
                    })

            # One final commit for all successful rows.
            self.db.commit()

        except Exception as exc:
            self.db.rollback()
            raise RuntimeError(
                "Import transaction failed; changes were rolled back."
            ) from exc

        return {
            "total_rows": len(df),
            "imported": imported,
            "failed": failed,
            "skipped": skipped,
            "results": row_results,

        }
