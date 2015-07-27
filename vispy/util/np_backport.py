# backports of newer numpy features
import numpy as np


if not hasattr(np, 'nanmean'):
    def nanmean(data, *args, **kwargs):
        d = np.ma.masked_array(data, mask=np.isnan(data))
        return d.mean(*args, **kwargs)
else:
    nanmean = np.nanmean
