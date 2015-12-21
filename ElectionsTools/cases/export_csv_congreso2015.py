
"""
Exporting to csv the results of the elections 2015

arg: -folder we want to export the data
"""

from build_csv_congress_2015 import *
import sys

folder = sys.argv[1]

if __name__ == "__main__":
    csv_builder('estado', folder)
    csv_builder('comunidad', folder)
    csv_builder('provincia', folder)
