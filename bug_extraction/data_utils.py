import pandas as pd
from pathlib import Path
import dataclasses
import study_enums
from collections import ChainMap

def get_csv(path, nullable=True, strict=True):
    if isinstance(path, str):
        path = Path(path)
    sf_1 = dataclasses.fields(study_enums.StudyPhase1Field)
    sf_2 = dataclasses.fields(study_enums.StudyPhase2Field)
    s1 = { f.name: f.type for f in sf_1 }
    s2 = { f.name: f.type for f in sf_2 }

    def col_mapper(_type):
        if _type == int:
            return pd.Int32Dtype()
        else:
            return _type

    all_cols = ChainMap(s1, s2)

    df = pd.read_csv(path, dtype={ k: col_mapper(t) for k, t in all_cols.items() })
    if strict:
        assert set(df.columns).issubset(set(df.columns))
    return df
