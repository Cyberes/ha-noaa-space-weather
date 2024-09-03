import re
from datetime import datetime

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

"""
https://github.com/daniestevez/jupyter_notebooks/blob/master/IONEX.ipynb
"""


def parse_ionex_datetime(s: str):
    match = re.match(r'\s*(\d{4})\s*(\d{1,2})\s*(\d{1,2})\s*(\d{1,2})\s*(\d{1,2})\s*(\d{1,2})', s)
    if match:
        year, month, day, hour, minute, second = map(int, match.groups())
        return datetime(year, month, day, hour, minute, second)
    else:
        raise ValueError("Invalid date format")


def parse_map(tecmap, exponent=-1):
    tecmap = re.split('.*END OF TEC MAP', tecmap)[0]
    return np.stack([np.fromstring(l, sep=' ') for l in re.split('.*LAT/LON1/LON2/DLON/H\\n', tecmap)[1:]]) * 10 ** exponent


def get_tecmaps(ionex: str):
    for tecmap in ionex.split('START OF TEC MAP')[1:]:
        lines = tecmap.split('\n')
        epoch = lines[1].strip() if len(lines) > 1 else None
        yield parse_map(tecmap), epoch


def plot_tec_map(tecmap, lon_range: list, lat_range: list, timestamp: datetime = None):
    proj = ccrs.PlateCarree()
    f, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj))

    # Create arrays of latitudes and longitudes to match the geographical grid of the TEC map data.
    # This is hard coded and should never change.
    lat = np.arange(-87.5, 87.5, 2.5)
    lon = np.arange(-180, 180, 5.0)

    # Create a mask for the data in the lat/lon range
    lon_mask = (lon >= lon_range[0]) & (lon < lon_range[1])
    lat_mask = (lat >= lat_range[0]) & (lat < lat_range[1])
    mask = np.ix_(lat_mask, lon_mask)

    # Select only the data in the lat/lon range
    tecmap_ranged = tecmap[mask]

    # Plot the TEC map
    h = plt.imshow(tecmap_ranged, cmap='viridis', vmin=0, vmax=100, extent=(lon_range[0], lon_range[1], lat_range[0], lat_range[1]), transform=proj)

    # Make graph pretty
    ax.coastlines()
    if timestamp:
        plt.title(timestamp.strftime('%H:%M %d-%m-%Y'), fontsize=12, y=1.04)
    plt.suptitle('Vertical Total Electron Count', fontsize=16, y=0.87)
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    f.add_axes(ax_cb)
    cb = plt.colorbar(h, cax=ax_cb)
    plt.rc('text', usetex=True)
    cb.set_label('TECU ($10^{16} \\mathrm{el}/\\mathrm{m}^2$)')

    return tecmap_ranged, plt
