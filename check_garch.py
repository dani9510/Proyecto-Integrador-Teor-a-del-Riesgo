import sys; sys.path.append('market-api')
from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from modules.garch import compute_garch
import pandas as pd

raw = get_data(['IBM','AVAL'])
for tk, df in raw.items():
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
ret = calculate_returns(raw)
ind = compute_indicators(ret)
g = compute_garch(ind)

for ticker in ['IBM', 'AVAL']:
    if ticker in g and 'GARCH_Vol' in g[ticker].columns:
        vol = g[ticker]['GARCH_Vol'].dropna()
        print(f'=== {ticker} GARCH ===')
        print(f'Length: {len(vol)}')
        print(f'First 5: {[round(x,6) for x in vol.head().tolist()]}')
        print(f'Last 5:  {[round(x,6) for x in vol.tail().tolist()]}')
        print(f'Min: {vol.min():.6f}  Max: {vol.max():.6f}  Mean: {vol.mean():.6f}')
        print(f'Nunique: {vol.nunique()}')
        print(f'Std of vol: {vol.std():.6f}')
        idx = g[ticker].index
        print(f'Index dtype: {idx.dtype}')
        print(f'Index first 3: {idx[:3].tolist()}')
        print()
