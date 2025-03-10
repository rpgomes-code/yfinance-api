import pandas as pd
import numpy as np
import json
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from typing import Any

# Custom JSON encoder that properly handles problematic values
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.number, np.integer, np.floating, np.bool_)):
            return obj.item()
        elif pd.isna(obj) or (isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj))):
            return None
        elif isinstance(obj, pd.DataFrame):
            return obj.reset_index().replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict(orient='records')
        elif isinstance(obj, pd.Series):
            return obj.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super().default(obj)


# Function to clean data recursively before serialization
def clean_data_for_json(data):
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, (np.number, np.integer, np.floating, np.bool_)):
        return data.item()
    elif pd.isna(data) or (isinstance(data, float) and (np.isnan(data) or np.isinf(data))):
        return None
    elif isinstance(data, pd.DataFrame):
        return clean_data_for_json(
            data.reset_index().replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict(orient='records'))
    elif isinstance(data, pd.Series):
        return clean_data_for_json(data.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict())
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    return data


# Override FastAPI's default JSONResponse
class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        # Clean the data before JSON serialization
        cleaned_content = clean_data_for_json(content)

        # Use FastAPI's jsonable_encoder first to handle models
        json_content = jsonable_encoder(cleaned_content)

        # Then use our custom encoder for any remaining problematic values
        return json.dumps(
            json_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder
        ).encode("utf-8")