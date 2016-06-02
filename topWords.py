import os  
import csv
for fn in os.listdir('.'):
    x = ""
    if os.path.isfile(fn):
        with open(fn, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                try:
                    x += row
                except:
                    print "Gah"
                    pass
    print x
