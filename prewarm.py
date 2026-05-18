# prewarm.py
from app.data import figure_cache
from app.viz.maps import build_japan_map_fig
from app.viz.pyramid import build_pyramid_fig, get_pyramid_axis_max
from app.viz.timeseries import build_ts_pop_share_fig, build_ts_population_fig, build_ts_tfr_fig
from app.viz.kpi import build_kpi_data
from app.aesthetics.config import MAP_METRICS, MAP_METRIC_DEFAULT
from startup import CENSUS_YEARS

_prewarm_axis_max = get_pyramid_axis_max(None)

# Census years valid for each non-default metric, derived from coverage bounds
def _valid_years(metric: str) -> list[int]:
    meta     = MAP_METRICS[metric]
    min_yr   = meta.get("min_year") or 0
    max_yr   = meta.get("max_year") or 9999
    return [yr for yr in CENSUS_YEARS if min_yr <= yr <= max_yr]


if figure_cache.is_valid():
    print("Loading figure cache from disk...")
    figure_cache.load_all()
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)
    print(f"  Disk cache loaded — {len(CENSUS_YEARS)} years ready.")
else:
    print("Building figure cache...")
    figure_cache.clear()

    # ── Primary pass: all years × default metric + non-map figures ───────────
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)

        fig = build_japan_map_fig(year=_yr, metric=MAP_METRIC_DEFAULT)
        figure_cache.save(figure_cache.make_key("map", _yr, MAP_METRIC_DEFAULT), fig)

        fig = build_pyramid_fig(year=_yr, area_estat=None, axis_max=_prewarm_axis_max)
        figure_cache.save(figure_cache.make_key("pyramid", _yr, None, _prewarm_axis_max), fig)

        fig = build_ts_pop_share_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("pop_share", _yr, None), fig)

        fig = build_ts_population_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("population", _yr, None), fig)

        fig = build_ts_tfr_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("tfr", _yr, None), fig)

    # ── Secondary pass: remaining map metrics, valid years only ──────────────
    _extra_metrics = [m for m in MAP_METRICS if m != MAP_METRIC_DEFAULT]
    for _metric in _extra_metrics:
        for _yr in _valid_years(_metric):
            fig = build_japan_map_fig(year=_yr, metric=_metric)
            figure_cache.save(figure_cache.make_key("map", _yr, _metric), fig)

    figure_cache.write_fingerprint()
    n_extra = sum(len(_valid_years(m)) for m in _extra_metrics)
    print(f"  Cache built — {len(CENSUS_YEARS)} years × primary + {n_extra} extra metric figures.")