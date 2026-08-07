"""JSON serialization utilities for numpy and pandas types"""

import json
import numpy as np
import pandas as pd
from typing import Any
import math

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy and pandas types"""
    
    def default(self, obj: Any) -> Any:
        """Convert numpy/pandas types to Python types"""
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return super().default(obj)


def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy/pandas types to Python types
    
    Args:
        obj: Object to convert
        
    Returns:
        Converted object with native Python types
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        val = float(obj)

        # Handle NaN and Infinity
        if math.isnan(val) or math.isinf(val):
            return 0

        if val.is_integer():
            return int(val)

        return round(val, 4)
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj
