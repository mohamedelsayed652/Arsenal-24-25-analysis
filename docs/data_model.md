# Data Model & Lineage

## Fact Table: `arsenal_matches`
- **Grain**: One row per Arsenal fixture.
- **Columns**
  - `match_id` (int) – API fixture id (primary key).
  - `date` (timestamp) – fixture date/time (UTC).
  - `opponent` (string) – opposing team name.
  - `home_or_away` (string) – `Home` or `Away`.
  - `goals_for` (int) – Arsenal goals scored.
  - `goals_against` (int) – Goals conceded.
  - `goal_difference` (int) – `goals_for - goals_against`.
  - `result` (string) – `W`, `D`, `L`.
  - `rolling_goals_for_5` (float) – 5-match rolling average of `goals_for`.
  - `rolling_goal_diff_5` (float) – 5-match rolling average of `goal_difference`.

## Derived / Sample Views
- `vw_arsenal_avg_by_venue`: average `goals_for` and `goal_difference` grouped by `home_or_away`.
- `vw_arsenal_form_last5`: last 5 matches with rolling averages and results.

## Lineage
API-Football (`fixtures`) → `arsenal_matches.csv` (extract) → `arsenal_matches` Parquet (transform) → Redshift table `arsenal_matches` (load) → downstream views/queries.

## Data Quality Expectations
- `match_id`: not null, unique.
- `date`: not null, valid timestamp.
- `home_or_away`: in {`Home`, `Away`}.
- `result`: in {`W`, `D`, `L`}.
- Numeric columns are ints/floats without nulls post-transform (coerced to 0 where API missing).
