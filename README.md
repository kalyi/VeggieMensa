# VeggieMensa
Shows the vegetarian/vegan/complete menu of STWNO canteens
with default to vegetarian.
Optionally also displays marked ingredients and allergens.

Currently works for Mensa Uni Passau, Uni Passau Cafeteria Nikolakloster,
Mensa Uni Regensburg.

## How to use
```
$ ./veggieMensa -h
usage: veggieMensa.py [-h] [-c {pa-nk,rgbg,pa}] [-a] [-v] [-o] [-m MARKED]
                      [-l ALLERGEN] [-w WEEK] [-s] [-e] [-g]
                      [{mon,tue,wed,thu,fri,today,tomorrow,curweek,nextweek}]

Retrieves and filters menus of STWNO canteens.

positional arguments:
  {mon,tue,wed,thu,fri,today,tomorrow,curweek,nextweek}
                        Show menu only for specified day(s). Defaults to
                        curweek.

optional arguments:
  -h, --help            show this help message and exit
  -c {pa-nk,rgbg,pa}, --canteen {pa-nk,rgbg,pa}
                        Select canteen. Type pa-nk for Uni Passau Cafeteria
                        Nikolakloster, rgbg for Mensa Uni Regensburg
                        (mittags), pa for Mensa Uni Passau. Defaults to Mensa
                        Uni Passau.
  -a, --all             Do not filter non-vegetarian dishes.
  -v, --vegan           Show only vegan dishes.
  -o, --organic         Show only organic dishes.
  -m MARKED, --marked MARKED
                        Show specified marked ingredient. Use 'all' to show
                        all.
  -l ALLERGEN, --allergen ALLERGEN
                        Show specified allergen. Use 'all' to show all.
  -w WEEK, --week WEEK  Show menu for specified week. Defaults to current
                        week.
  -s, --student         Show student prices.
  -e, --employee        Show employee prices.
  -g, --guest           Show guest prices.
```
