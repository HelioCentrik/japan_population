# prewarm.py
from app.data import figure_cache
from app.viz.maps import build_japan_map_fig
from app.viz.pyramid import build_pyramid_fig, get_pyramid_axis_max
from app.viz.timeseries import build_ts_population_fig, build_ts_aging_index_fig, build_ts_pop_share_fig
from app.viz.kpi import build_kpi_data
from app.aesthetics.config import MAP_METRIC_DEFAULT
from startup import CENSUS_YEARS

_prewarm_axis_max = get_pyramid_axis_max(None)

if figure_cache.is_valid():
    print("Loading figure cache from disk...")
    figure_cache.load_all()
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)
    print(f"  Disk cache loaded — {len(CENSUS_YEARS)} years ready.")
else:
    print("Building figure cache...")
    figure_cache.clear()
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)
        fig = build_japan_map_fig(year=_yr, metric=MAP_METRIC_DEFAULT)
        figure_cache.save(figure_cache.make_key("map", _yr, MAP_METRIC_DEFAULT), fig)
        fig = build_pyramid_fig(year=_yr, area_estat=None, axis_max=_prewarm_axis_max)
        figure_cache.save(figure_cache.make_key("pyramid", _yr, None, _prewarm_axis_max), fig)
        fig = build_ts_population_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("population", _yr, None), fig)
        fig = build_ts_aging_index_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("timeseries", _yr, None), fig)
        fig = build_ts_pop_share_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("pop_share", _yr, None), fig)
    figure_cache.write_fingerprint()
    print(f"  Cache built and saved — {len(CENSUS_YEARS)} years × 3 builders.")
