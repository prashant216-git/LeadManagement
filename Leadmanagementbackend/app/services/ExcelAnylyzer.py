
import re
from io import BytesIO
from typing import Any
from uuid import UUID

import pandas as pd

from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO

FIELD_ALIASES = {
    "name": [
        "name",
        "full name",
        "lead name",
        "customer name",
        "contact name",
        "person name",
        "first name",
    ],
    "email": [
        "email",
        "email address",
        "e mail",
        "work email",
        "contact email",
        "lead email",
    ],
    "phone": [
        "phone",
        "phone number",
        "mobile",
        "mobile no",
        "mobile number",
        "contact number",
        "telephone",
        "whatsapp number","no"
    ],
    "message": [
        "message",
        "enquiry",
        "enquiry details",
        "enquiry detail",
        "inquiry",
        "inquiry details",
        "description",
        "query",
        "remarks",
        "lead message",
    ],
}


def normalize(value: Any) -> str:
    if value is None:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"[_\-]+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def suggest_mapping(columns: list[str]) -> dict[str, str | None]:
    mapping = {}

    for target_field, aliases in FIELD_ALIASES.items():
        normalized_aliases = {normalize(alias) for alias in aliases}

        mapping[target_field] = next(
            (
                column for column in columns
                if normalize(column) in normalized_aliases
            ),
            None,
        )

    return mapping


class ExcelAnalyzer:

    def analyze(
        self,
        file_bytes: bytes,
        workbook: str | None = None,
        sample_size: int = 5,
    ) -> dict:
        """Detect worksheets and analyze the selected worksheet."""

        try:
            excel = pd.ExcelFile(BytesIO(file_bytes))
        except Exception as exc:
            raise ValueError("Unable to read Excel file.") from exc

        if not excel.sheet_names:
            raise ValueError("The Excel file contains no worksheets.")

        # First detect available worksheets.
        available_workbooks = excel.sheet_names

        # If no worksheet is selected, use the first one.
        selected_workbook = workbook or available_workbooks[0]

        if selected_workbook not in available_workbooks:
            raise ValueError(
                f"Worksheet '{selected_workbook}' not found. "
                f"Available worksheets: {available_workbooks}"
            )

        df = pd.read_excel(
            excel,
            sheet_name=selected_workbook,
            nrows=sample_size,
            dtype=object,
        )

        columns = [
            str(column).strip()
            for column in df.columns
            if not str(column).startswith("Unnamed:")
            and str(column).strip()
        ]
        mapping = suggest_mapping(columns)

        sample_data = []

        for _, row in df.iterrows():
            sample_row = {}

            for target_field, source_column in mapping.items():
                if source_column is None:
                    continue

                value = row[source_column]

                sample_row[target_field] = (
                    None if pd.isna(value) else str(value)
                )

            sample_data.append(sample_row)

        return {
            "available_workbooks": available_workbooks,
            "selected_workbook": selected_workbook,
            "columns": columns,
            "suggested_mapping": suggest_mapping(columns),
            "sample_data": sample_data,
        }

    


