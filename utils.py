import pandas as pd

@staticmethod
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(
            file,
            low_memory=False
        )
    elif file.name.endswith(".parquet"):
        return pd.read_parquet(file)
    else:
        raise ValueError("Unsupported file format")
