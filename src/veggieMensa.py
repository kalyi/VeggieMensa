#!/usr/bin/env python3
# -*- coding: utf8; -*-
#
# Copyright (C) 2016 : Kathrin Hanauer, Olaf Leßenich
#
# Checks whether a file contains the specified license header and,
# if negative, tries to update it.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""Show vegetarian/vegan meals of STWNO canteens."""

################################################################################

import csv, urllib.request, datetime, argparse

################################################################################

stwnoUrl = "http://www.stwno.de/infomax/daten-extern/csv/{}/{}.csv"

canteens = {
    'pa': ('UNI-P','Mensa Uni Passau'),
    'pa-nk': ('Cafeteria Nikolakloster', 'Uni Passau Cafeteria Nikolakloster'),
    'rgbg': ('UNI-R', 'Mensa Uni Regensburg (mittags)')
}

markedIngredients = {
    '1' : 'mit Farbstoff',
    '2' : 'mit Konservierungsstoff',
    '3' : 'mit Antioxidationsmittel',
    '4' : 'mit Geschmacksverstärker',
    '5' : 'geschwefelt',
    '6' : 'geschwärzt',
    '7' : 'gewachst',
    '8' : 'mit Phosphat',
    '9' : 'mit Süßungsmittel Saccharin',
    '10': 'mit Süßungsmittel Aspartam, enthält Phenylalaninquelle',
    '11': 'mit Süßungsmittel Cyclamat',
    '12': 'mit Süßungsmittel Acesulfam',
    '13': 'chininhaltig',
    '14': 'coffeinhaltig',
    '15': 'gentechnisch verändert',
    '16': 'enthält Sulfite',
    '17': 'enthält Phenylalanin'
}

allergens = {
    'A' : 'Gluten',
    'B' : 'Krebstiere',
    'C' : 'Eier',
    'D' : 'Fisch',
    'E' : 'Erdnüsse',
    'F' : 'Soja',
    'G' : 'Milch und Milchprodukte',
    'H' : 'Schalenfrüchte',
    'I' : 'Sellerie',
    'J' : 'Senf',
    'K' : 'Sesamsamen',
    'L' : 'Schwefeldioxid und Sulfite',
    'M' : 'Lupinen',
    'N' : 'Weichtiere'
}

################################################################################
class Dish:
    def __init__(self, name, category, tags, prices):
        self.category = category
        self.tags = tags.split(',')
        self.prices = prices
        self.markedIngredients = [ ]
        self.allergens = [ ]
        self.parseName(name)

    def parseName(self,name):
        name = name.strip()
        if name.endswith(')'):
            i = name.rfind('(')
            if i > 0:
                extra = name[i+1:len(name)-1]
                name = name[0:i]
                self.parseExtra(extra)
        # clean up whitespaces
        self.name = ' '.join(name.split())

    def parseExtra(self, extra):
        items = extra.split(',')
        for i in items:
            if i.isdigit():
               self.markedIngredients.append(i)
            elif i.isalpha() and len(i) == 1:
                self.allergens.append(i)

    def isSoup(self):
        return self.category.startswith('Suppe')

    def isMain(self):
        return self.category.startswith('HG')

    def isSide(self):
        return self.category.startswith('B')

    def isDessert(self):
        return self.category.startswith('N')

    def isVegetarian(self):
        return 'V' in self.tags or self.isVegan()

    def isVegan(self):
        return 'VG' in self.tags

    def formatMarkedIngredients(self,select=None):
        if len(self.markedIngredients) == 0:
            return ''
        ing = ([ markedIngredients[i] for i in self.markedIngredients]
                if select is None else
                [ markedIngredients[i] for i in self.markedIngredients
                    if i in select ])
        return '[{}]'.format(', '.join(ing)) if len(ing) > 0 else ''

    def formatAllergens(self,select=None):
        if len(self.allergens) == 0:
            return ''
        allerg = ([ allergens[i] for i in self.allergens ] if select is None
                else [ allergens[i] for i in self.allergens if i in select ])
        return '[{}]'.format(', '.join(allerg)) if len(allerg) > 0 else ''

    def formatPrice(self,select=(True,True,True)):
        return ('EUR {}'.format('/'.join(
            [ p for (p,b) in zip(self.prices,select) if b ] ))
            if True in select else '')

    def prettyPrint(self, ingredients, allergens, prices):
        mIng = self.formatMarkedIngredients(ingredients)
        allerg = self.formatAllergens(allergens)
        price = self.formatPrice(prices)
        s = ("{} {}{}".format(self.name, mIng, allerg)
                if len(mIng) + len(allerg) > 0 else self.name)
        return '{}: {}'.format(s,price) if len(price) > 0 else s

    def __str__(self):
        mIng = self.formatMarkedIngredients()
        allerg = self.formatAllergens()
        if len(mIng) + len(allerg) > 0:
            return "{} {}{} : {}".format(
                    self.name, mIng, allerg, self.formatPrice())
        return "{} : {}".format(self.name, self.formatPrice())

################################################################################

def getCSV(canteen='pa',week=0):
    if week < 1:
        week = datetime.date.today().isocalendar()[1]
    url = stwnoUrl.format(canteens[canteen][0], week)
    with urllib.request.urlopen(url) as response:
        data = response.read()
        text = data.decode('latin1')
    return text.split('\n')

def parseCSV(lines):
    spamreader = csv.reader(lines[1:], delimiter=';')
    menu = { }
    for row in spamreader:
        if len(row)  < 5:
            continue
        date = datetime.datetime.strptime(row[0],'%d.%m.%Y')
        dish = Dish(row[3],row[2],row[4],(row[6],row[7],row[8]))
        if date in menu.keys():
            menu[date].append(dish)
        else:
            menu[date] = [ dish ]
    return menu

def prettyPrintDishes(dishes, markedIngredients, allergens, prices):
    for dish in dishes:
        print('*   {}'.format(dish.prettyPrint(markedIngredients, allergens,
            prices)))

def prettyPrintDay(menu, day, checkVegetarian, checkVegan, markedIngredients,
        allergens, prices):
    print('*** {} ***'.format(datetime.datetime.strftime(day, '%A, %d.%m.%Y')))
    byCategory = { 'soup' : [], 'main' : [], 'side': [],
            'dessert' : [], 'unknown': [] }
    for dish in menu[day]:
        if (checkVegetarian and not dish.isVegetarian()) or (
                checkVegan and not dish.isVegan()):
            continue
        if dish.isSoup():
            byCategory['soup'].append(dish)
        elif dish.isMain():
            byCategory['main'].append(dish)
        elif dish.isSide():
            byCategory['side'].append(dish)
        elif dish.isDessert():
            byCategory['dessert'].append(dish)
        else:
            byCategory['unknown'].append(dish)
    print('* Suppen:')
    prettyPrintDishes(byCategory['soup'], markedIngredients, allergens, prices)
    print('*\n* Hauptgerichte:')
    prettyPrintDishes(byCategory['main'], markedIngredients, allergens, prices)
    print('*\n* Beilagen:')
    prettyPrintDishes(byCategory['side'], markedIngredients, allergens, prices)
    print('*\n* Nachspeisen:')
    prettyPrintDishes(byCategory['dessert'], markedIngredients, allergens,
            prices)
    if len(byCategory['unknown']) > 0:
        print('*\n* Sonstiges:')
        prettyPrintDishes(byCategory['unknown'], markedIngredients, allergens,
                prices)
    print('**********\n')

def prettyPrint(menu, day, checkVegetarian, checkVegan, markedIngredients,
        allergens, prices):
    days = sorted(menu.keys())
    if day is None:
        for day in days:
            prettyPrintDay(menu, day, checkVegetarian, checkVegan,
                    markedIngredients, allergens, prices)
    else:
        if day in range(len(days)):
            prettyPrintDay(menu, days[day], checkVegetarian, checkVegan,
                    markedIngredients, allergens, prices)
        else:
            print("No menu for this day.")

def parseDay(day):
    week = datetime.date.today().isocalendar()[1]
    if day is None:
        return (None, week)
    else:
        d = day.lower()
        today = datetime.date.today().weekday()
        if d == 'today':
            return (today,week)
        elif d == 'tomorrow':
            tomorrow = today + 1
            return (tomorrow % 7, week + tomorrow / 7)
        elif d == 'curweek':
            return(None, week)
        elif d == 'nextweek':
            return(None, week + 1)
        else:
            if d.startswith('mon'):
                n = 0
            elif d.startswith('tue'):
                n = 1
            elif d.startswith('wed'):
                n = 2
            elif d.startswith('thu'):
                n = 3
            elif d.startswith('fri'):
                n = 4
            elif d.startswith('sat'):
                n = 5
            elif d.startswith('sun'):
                n = 6
            else:
                return (None, week)
            return (n, week if n >= today else week + 1)

def parseFilter(selected, options):
    if 'all' in selected:
        return list(options.keys())
    foundOptions = [ ]
    for s in selected:
        for k, v in options.items():
            if s.lower() in v.lower() and k not in foundOptions:
                foundOptions.append(k)
    return foundOptions

def main():
    parser = argparse.ArgumentParser(
            description='Retrieves and filters menus for STWNO canteens.')
    parser.add_argument('-c', '--canteen', action='store',
            choices=list(canteens.keys()), default='pa',
            help='Select canteen. Type {}. \
                    Defaults to Mensa Uni Passau.'.format(
                ', '.join(['{} for {}'.format(
                    s,canteens[s][1]) for s in canteens.keys()])))
    parser.add_argument('-a', '--all', action='store_true', default=False,
            help='Do not filter non-vegetarian dishes.')
    parser.add_argument('-v', '--vegan', action='store_true', default=False,
            help='Show only vegan dishes.')
    parser.add_argument('-m', '--marked', action='append', default=[ ],
            help='Show specified marked ingredient. Use \'all\' to show all.')
    parser.add_argument('-l', '--allergen', action='append', default=[ ],
            help='Show specified allergen. Use \'all\' to show all.')
    parser.add_argument('-w', '--week', action='store', type=int,
            help='Show menu for specified week. Defaults to current week.')
    parser.add_argument('-s', '--student', action='store_true', default=False,
            help='Show student prices.')
    parser.add_argument('-e', '--employee', action='store_true', default=False,
            help='Show employee prices.')
    parser.add_argument('-g', '--guest', action='store_true', default=False,
            help='Show guest prices.')
    parser.add_argument('day', nargs='?',
            choices=[ 'mon','tue','wed','thu','fri',
                'today','tomorrow','curweek','nextweek' ],
            help='Show menu only for specified day(s). Defaults to curweek.')
    args = parser.parse_args()
    #
    day,week = parseDay(args.day)
    if args.week is not None:
        week = args.week
    showIngredients = parseFilter(args.marked, markedIngredients)
    showAllergens = parseFilter(args.allergen, allergens)
    prices = (args.student, args.employee, args.guest)
    #
    print("{} menu for week {} at {}:".format(
        'Vegan' if args.vegan else 'Vegetarian' if not args.all else 'Complete',
        args.week, canteens[args.canteen][1]))
    if True in prices:
        print('Prices are for {}.'.format('/'.join(
            [ x for (x,b) in zip(['students','employees','guests'], prices)
                if b ])))
    print()
    prettyPrint(parseCSV(getCSV(args.canteen, week)), day,
        not args.all, args.vegan, showIngredients, showAllergens, prices)

if __name__ == "__main__":
    main()
