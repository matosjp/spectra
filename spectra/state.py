"""
S.P.E.C.T.R.A. - Centralized State & Data Management Module
Copyright (C) 2026 João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira

Provides thread-safe dataset encapsulation, column validation, and session management.
"""

from typing import Optional, List, Dict, Any, Union
import threading
import pandas as pd
import numpy as np


class DataManager:
    """
    Centralized, thread-safe data manager for loaded stellar datasets and calculation results.

    Attributes:
        _table_data (Optional[pd.DataFrame]): Active dataset held in memory.
        _lock (threading.Lock): Thread lock for concurrency control.
    """

    _table_data: Optional[pd.DataFrame] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def set_dataset(cls, df: Optional[pd.DataFrame]) -> None:
        """
        Sets the active table dataset held in memory.

        Args:
            df (Optional[pd.DataFrame]): DataFrame to store as active dataset.
        """
        with cls._lock:
            cls._table_data = df.copy() if df is not None else None

    @classmethod
    def get_dataset(cls) -> Optional[pd.DataFrame]:
        """
        Retrieves the active dataset.

        Returns:
            Optional[pd.DataFrame]: Active DataFrame or None if not loaded.
        """
        with cls._lock:
            return cls._table_data

    @classmethod
    def has_dataset(cls) -> bool:
        """
        Checks whether a dataset is currently loaded.

        Returns:
            bool: True if active dataset is not None, False otherwise.
        """
        with cls._lock:
            return cls._table_data is not None

    @classmethod
    def update_column(cls, col_name: str, values: Union[np.ndarray, List[Any], pd.Series]) -> None:
        """
        Updates or adds a column in the active dataset.

        Args:
            col_name (str): Column name to set.
            values (Union[np.ndarray, List[Any], pd.Series]): Values to assign.
        """
        with cls._lock:
            if cls._table_data is not None:
                cls._table_data[col_name] = values

    @classmethod
    def has_columns(cls, columns: List[str]) -> bool:
        """
        Verifies if all specified columns exist in the active dataset.

        Args:
            columns (List[str]): List of column names to check.

        Returns:
            bool: True if all columns exist, False otherwise.
        """
        with cls._lock:
            if cls._table_data is None:
                return False
            return all(col in cls._table_data.columns for col in columns)

    @classmethod
    def clear(cls) -> None:
        """Clears the active dataset from memory."""
        with cls._lock:
            cls._table_data = None
