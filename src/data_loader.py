from __future__ import annotations

import pandas as pd
from typing import Dict, Any, Literal, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from io import BytesIO

# ---------------------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# CONSTANTS (ENTERPRISE SAFETY)
# ---------------------------------------------------------------------
MAX_FILE_SIZE_MB = 200
MAX_ROWS = 5_000_000
MAX_COLUMNS = 2_000

# ---------------------------------------------------------------------
# CUSTOM EXCEPTIONS
# ---------------------------------------------------------------------
class DataLoaderError(Exception):
    """Raised when dataset loading or validation fails."""
    pass

# ---------------------------------------------------------------------
# SCHEMA CONTAINER
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class SchemaInfo:
    """
    Immutable container for dataset schema information.
    """
    rows: int
    columns: int
    numeric_columns: tuple[str, ...]
    categorical_columns: tuple[str, ...]
    missing_cells: int
    dtypes: Dict[str, str]
    memory_usage_mb: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "numeric_columns": list(self.numeric_columns),
            "categorical_columns": list(self.categorical_columns),
            "missing_cells": self.missing_cells,
            "dtypes": self.dtypes,
            "memory_usage_mb": self.memory_usage_mb
        }

# ---------------------------------------------------------------------
# DATA LOADER
# ---------------------------------------------------------------------
class DataLoader:
    """
    Enterprise-grade dataset loader with:
    - Multi-format support
    - File size & shape validation
    - Schema inference
    - Production-safe error handling
    """

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet", ".feather"}

    # -----------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------
    @classmethod
    def load_dataset(
        cls,
        uploaded_file,
        file_type: Literal["auto", "csv", "excel", "parquet"] = "auto"
    ) -> pd.DataFrame:

        try:
            filename = getattr(uploaded_file, "name", "uploaded_file")
            extension = Path(filename).suffix.lower()

            logger.info(f"Loading dataset: {filename}")

            # ---------- FILE SIZE CHECK ----------
            if hasattr(uploaded_file, "size"):
                size_mb = uploaded_file.size / (1024 ** 2)
                if size_mb > MAX_FILE_SIZE_MB:
                    raise DataLoaderError(
                        f"File size {size_mb:.1f}MB exceeds "
                        f"maximum allowed {MAX_FILE_SIZE_MB}MB"
                    )

            parser = extension if file_type == "auto" else file_type

            # ---------- DISPATCH ----------
            if parser in {".csv", "csv"}:
                df = cls._load_csv(uploaded_file)
            elif parser in {".xlsx", ".xls", "excel"}:
                df = cls._load_excel(uploaded_file)
            elif parser in {".parquet", ".feather", "parquet"}:
                df = cls._load_binary(uploaded_file, extension)
            else:
                raise DataLoaderError(
                    f"Unsupported file format: {extension}. "
                    f"Supported formats: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
                )

            # ---------- VALIDATION ----------
            df = cls._validate_and_clean(df)
            cls._validate_shape(df)

            logger.info(f"Dataset loaded successfully: {df.shape}")
            return df

        except DataLoaderError:
            raise
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            logger.error(f"Parsing error: {e}")
            raise DataLoaderError("The file appears to be empty or malformed.")
        except Exception as e:
            logger.exception("Unexpected error during data loading")
            raise DataLoaderError(str(e))

    @classmethod
    def infer_schema(cls, df: pd.DataFrame) -> SchemaInfo:
        try:
            numeric_cols = df.select_dtypes(include=["number"]).columns
            categorical_cols = df.select_dtypes(
                exclude=["number", "datetime", "timedelta"]
            ).columns

            memory_mb = round(
                df.memory_usage(deep=True).sum() / (1024 ** 2), 2
            )

            return SchemaInfo(
                rows=df.shape[0],
                columns=df.shape[1],
                numeric_columns=tuple(numeric_cols),
                categorical_columns=tuple(categorical_cols),
                missing_cells=int(df.isna().sum().sum()),
                dtypes=df.dtypes.astype(str).to_dict(),
                memory_usage_mb=memory_mb
            )

        except Exception as e:
            logger.exception("Schema inference failed")
            raise DataLoaderError(f"Schema inference failed: {str(e)}")

    @classmethod
    def load_dataset_with_schema(
        cls,
        uploaded_file,
        **kwargs
    ) -> Tuple[pd.DataFrame, SchemaInfo]:
        df = cls.load_dataset(uploaded_file, **kwargs)
        schema = cls.infer_schema(df)
        return df, schema

    # -----------------------------------------------------------------
    # INTERNAL LOADERS
    # -----------------------------------------------------------------
    @staticmethod
    def _load_csv(file_obj) -> pd.DataFrame:
        return pd.read_csv(
            file_obj,
            low_memory=False,
            na_values=["", "NA", "NULL", "NaN", "None"],
            keep_default_na=True,
            encoding_errors="replace"
        )

    @staticmethod
    def _load_excel(file_obj) -> pd.DataFrame:
        return pd.read_excel(
            file_obj,
            na_values=["", "NA", "NULL", "NaN", "None"],
            keep_default_na=True
        )

    @staticmethod
    def _load_binary(file_obj, ext: str) -> pd.DataFrame:
        raw_bytes = (
            file_obj.read()
            if hasattr(file_obj, "read")
            else file_obj
        )

        buffer = BytesIO(raw_bytes)

        if ext == ".parquet":
            return pd.read_parquet(buffer)
        elif ext == ".feather":
            return pd.read_feather(buffer)
        else:
            raise DataLoaderError("Unsupported binary format")

    # -----------------------------------------------------------------
    # VALIDATION HELPERS
    # -----------------------------------------------------------------
    @staticmethod
    def _validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise DataLoaderError("Dataset contains no rows.")

        df = df.dropna(how="all").dropna(axis=1, how="all")

        if df.empty:
            raise DataLoaderError("All data removed after cleaning.")

        df.columns = DataLoader._clean_column_names(df.columns)
        return df

    @staticmethod
    def _validate_shape(df: pd.DataFrame):
        if df.shape[0] > MAX_ROWS:
            raise DataLoaderError(
                f"Dataset has {df.shape[0]:,} rows. "
                f"Maximum supported is {MAX_ROWS:,}."
            )

        if df.shape[1] > MAX_COLUMNS:
            raise DataLoaderError(
                f"Dataset has {df.shape[1]} columns. "
                f"Maximum supported is {MAX_COLUMNS}."
            )

    @staticmethod
    def _clean_column_names(columns: pd.Index) -> list[str]:
        return [
            str(col)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "_")
            .replace("(", "")
            .replace(")", "")
            for col in columns
        ]
