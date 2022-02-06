"""
This modules generates a map
"""

import sys
from geopy.geocoders import Nominatim
import geopy.distance
import folium
import random
from functools import lru_cache
import argparse
import time


@lru_cache()
def locate(location):
    """
    Gets the name of a city and returns its coordinates
    """
    geolocator = Nominatim(user_agent="Movie_Map")
    location = geolocator.geocode(location)
    location = (location.latitude, location.longitude)
    return location


def readfile(file, year, number=70):
    """
    Reads the file and returns a dictionary of locations as keys,
    and lists of movies as values. Only searches for movies of a specified year
    and only fills the dictionary to a specified length.
    """
    dct = {}
    with open(file, encoding='utf-8', errors='ignore') as data:
        for line in data:
            if year in line:
                try:
                    name, location = line.strip().split('\t')
                except ValueError:
                    continue
                try:
                    location = locate(location)
                except:
                    continue
                if location not in dct:
                    dct[location] = [name.replace('{#', '#')]
                else:
                    dct[location].append(name.replace('{#', '#'))
            if len(dct) == number:
                break
    return dct


def put_on_map(dct, starting_coords):
    """
    Puts a Marker of user coordinates on the map,
    puts markers of movies and connect user with
    locations with lines that specify the distance between
    those two objects
    """
    my_map = folium.Map(location=[starting_coords[0],
                                  starting_coords[1]], zoom_start=10)
    fg = folium.FeatureGroup(name="Movies")
    colors = ['darkpurple', 'cadetblue', 'darkred', 'green', 'lightgray', 'darkgreen',
              'pink', 'purple', 'beige', 'lightgreen', 'red', 'darkblue', 'lightblue',
              'gray', 'blue', 'white', 'orange', 'black', 'lightred']
    for location in dct:
        for movie in dct[location]:
            fg.add_child(folium.Marker(location=[location[0]
                                                 - 0.001 * random.uniform(-20, 20),
                                                 location[1] + 0.001 * random.uniform(-20, 20)],
                                       popup=movie,
                                       icon=folium.Icon(color=random.choice(colors))))
    fg_lines = folium.FeatureGroup(name="Distances")
    for location in dct:
        folium.PolyLine([starting_coords, location],
                        popup=geopy.distance.distance(location,
                                                      starting_coords)).add_to(fg_lines)
    fg_lines.add_child(folium.CircleMarker(location=starting_coords,
                                           radius=10,
                                           popup="This is you!",
                                           fill_color='black',
                                           color='red',
                                           fill_opacity=1))
    my_map.add_child(fg)
    my_map.add_child(fg_lines)
    my_map.add_child(folium.LayerControl())
    my_map.save(outfile='Movie_map.html')


def find_closest(user_coords, dct):
    """
    Finds 10 closest locations
    where movies where filmed to the user
    >>> find_closest((48.56, 25.61), {(43.41, 27.65): ['Movie']})
    {(43.41, 27.65): ['Movie']}
    """
    list_of_locations = []
    for coords in dct:
        list_of_locations.append(tuple((float(str(geopy.distance.distance(user_coords,
                                                                          coords)).split()[0]),
                                        coords)))
    list_of_locations.sort(key=lambda x: x[0])
    new_dct = {}
    for elem in list_of_locations[0:10]:
        new_dct[elem[1]] = dct[elem[1]]
    return new_dct


def main_worker(file='locations.list', coordinates=(48.314775, 25.082925), year='2015', num_of_films=70):
    """
    Receives the needed information after it's parsed and
    sends it to the functions that calculate it
    """
    year = '(' + year + ')'
    dct = readfile(file, year, num_of_films)
    new_dct = find_closest(coordinates, dct)
    put_on_map(new_dct, coordinates)


def main():
    """
    Main function of the program.
    Gets the arguments and calls other functions ton create the map.
    """
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('year', help='The year when the movies close to you were filmed')
    parser.add_argument('latitude', type=float, help='Your latitude')
    parser.add_argument('longitude', type=float, help='Your longitude')
    parser.add_argument('path', type=str, help='Path to your dataset')
    parser.add_argument('--number', '-n', type=int, help='Number of movies to check')
    args = parser.parse_args()
    if not args.number:
        args.number = 70
    print('Please wait, program is working...')
    main_worker(args.path,
                tuple((args.latitude, args.longitude)),
                args.year, args.number)
    end = time.time()
    print(f'Program has completed its work in {end - start} seconds')
    sys.exit()


if __name__ == '__main__':
    main()
