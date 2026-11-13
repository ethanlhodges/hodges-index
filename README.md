# HodgesIndex

2026–27 NCAA Division I Tempo-Free College Basketball Ratings & Daily Matchup Projections.

## Methodology
- **Simultaneous Weighted Ridge Regression** across all 365 D-I teams (`AdjO`, `AdjD`, `AdjEM`, `AdjT`)
- **Empirical Bayes 3-Point Luck Filtering** (15% regression toward 34.0% D-I mean)
- **Soft Garbage-Time Margin Cap** (35.0 pts/100 possessions)
- **Fading Preseason Priors** (`0.90 ×` prior year, decaying linearly to `0` at 14 games/team) + live toggle for `2026–27 only`
- **Two-Tier Home Court Advantage** (`+4.0` standard + `+1.55` high-altitude boost)

## Automated Daily Updates
GitHub Actions runs `python3 update_2027_season.py` every morning at 6:00 AM ET and publishes the updated `index.html` via GitHub Pages.
