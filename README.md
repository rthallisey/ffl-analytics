# ESPN Fantasy Football Analytics

Some code from:
  - https://github.com/rbarton65/espnff
  - https://github.com/CMorton737/espyn

Using ESPN's Fantasy Football private API, this package interfaces with
ESPN Fantasy Football to gather data from any public league.

## Basic Usage

This gives an overview of all the features of `espnff`

### Gather data from a public league

```python3
>>> import league
>>> league_id = 123456
>>> year = 2016
>>> league = League(league_id, year)
>>> print league
League 123456, 2016 Season
```
