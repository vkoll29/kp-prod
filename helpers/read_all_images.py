import os
# import re
from dateutil.parser import parse
from typing import List, Dict
from pprint import pprint
from glob import glob

from helpers.read_image import read_img

# Using local image here. In production, this will be a remote image either directly from twitter or downloaded and
# stored online
images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
# img_path = os.path.join(images_folder, "E__ACseXoAgOQV5.png")
# img_path = os.path.join(images_folder, "E_GQOtTWUAUvG0c.png")
# image = open(img_path, "rb")

img_folder = glob("C:/Dev/kenya-power/data/*.*")
def read_multiple_images(pth):
    for file in pth:
        image = open(file, "rb")
        return image

# read_multiple_images(img_folder)


# this is the result of Azure CS extracting text from the image
# results_list = read_img(image)

# this list contains all the areas that will be affected by maintenance i.e, the entire content of the image


def find_whole_word(w, s):
    """
    This helper function looks for certain words or phrases within a sentence.
     Should be refactored outside as a standalone func
    E.g in the sentence, 'The quick fox jumps over the lazy dog' if looking for 'fox jumps', the result is true. However,
    if looking for fox jump, it returns false
    :param w: the word or phrase to look for
    :param s: the string within which to search for w
    :return: true or false
    """
    return (' ' + w.lower() + ' ') in (' ' + s.lower() + ' ')


affected_places = []

def populate_area(region, county, date, area, locations):

    area_info = {
                    'region':region,
                    'county': county,
                    'date': date,
                    'area': area,
                    'locations': locations,

                }
    affected_places.append(area_info)


def format_image_text(unformatted_text):
    """
    Here, the result of the image text which is now a list is to be parsed and each text categorized.
    The data definition is as follows:
    Region and county can be empty

    [
       {
            'region': str,
            'county': str
            'date': str
            'area': str
            'locations': [str]
        },
        { another area...}
    ]

    :return: the data definition above
    """

    # some of these values are initialized globally within the function to avoid errors
    area = ''
    locations = []
    region = ''
    county = ''
    date = ''
    date_key = 'date not defined'

    for i, line in enumerate(unformatted_text):
        # print(f'{i+1}: {line}')

        # if find_whole_word("PLANNED", line) or:
        #     pass

        if find_whole_word('REGION', line):

            # here if region is an empty string is defined atop, it means this is the first region found i.e it is at
            # the top of list/image and no other values have been saved. in that case, just assign region and move to
            # the next item
            if not locations:
                region = line
            else:
                populate_area(region, county, date, area, locations)
                region = line
                locations = []

            # the fist time that is executed is after finding one region and collecting all its data. so this is true for second to the very last region available
            # the first thing is to assign the value currently stored in the variable region i.e the previous region in the iteration
            # then whatever values that are still currently held in the vars county, area, locations & date should be saved to the area_info dictionary.
            # these values still belong to the previous region. append them to the areas key (which is an array).
            # at this point, we've collected all the info for previous region so append to our overall list of affected_places

                # and only now do we start dealing with and collecting info for the current region, i.e the one that returned true for this condition here.
                # save the value to region, i.e overwrite previously saved region.
                # empty the locations array since we're collecting locations for new array. the rest of the variables will simply be overwritten: county and date
                # region = line
                # locations = []

                # print(f'After first {region}')

            # whenever we find a new region, always clean up the values stored in the areas key of region_dict.
            # this is because I'm not reassigning values here but simply appending to it.
            # if it isn't emptied, it will persist values for previous regions
            # region_dict = {}
            # region_dict['areas'] = []

        elif find_whole_word('AREA:', line):

            # this will be true in three instances:
            # 1. for the first region/county ever since location is initialized as an empty string
            # 2. When we find a new area -- as is shown in the else statement below -- since locations is set to empty whenever a new area's info has been completely collected
            # 3. When we've only began collecting info for a new region. locations is also emptied at that point as shown above.
            if not locations:
                area = line

            # this only returns true when we'e traversed the list and collected all the locations/info for a the previous area
            # so I need to save that info first before beginning collecting info for the area that returned true here - the same logic as in region
            # append each area to the areas key in region_dict
            # then empty locations to start collecting locations info for current area
            else:
                populate_area(region, county, date, area, locations)

                area = line
                locations = []
                date = ''

        elif find_whole_word('DATE:', line):
            # date = parse(line, fuzzy=True)[0]
            date = line

        elif find_whole_word('COUNTY', line):
            if not locations:
                county = line
            else:
                populate_area(region, county, date, area, locations)
                county = line
                locations = []
                date = ''

        else:
            if i == 0 & find_whole_word('DATE:', line) :
                try:
                    date_key = parse(line, fuzzy_with_tokens=True)[0]
                    date_key = date_key.strftime("%d-%m-%Y")
                    print(date_key)
                except Exception as e:
                    date_key = line
                    print(f"Date parsing error: {e}")

            # this checks if it is the last item in the iteration.
            elif i + 1 == len(unformatted_text):
                # some of the images contain the word 'end of document' which is also extracted. if that sentence is
                # found then don't append it to locations, just create the area_info then region_dict and append to
                # affected_places.
                if not line == 'End of document':
                    locations.append(line)
                    populate_area(region, county, date, area, locations)

                else:
                    populate_area(region, county, date, area, locations)

            else:
                locations.append(line)
    schema = {
        'date': date_key,
        'areas': affected_places
    }
    return schema


def format_locations(areas_dict: Dict) -> Dict:
    """
    Three things to be done:
    - look for & sign and replace with 'and' to avoid url issues. this is just a failsafe since url is already encoded
    - look for words cut short by - sign and combine them into one.
    - recreate location list items such that they are separated by comma and not the default newline as they were extracted from the image

    :param areas_dict: the dictionary that contains affected areas
    :return: list with locations formatted
    """

    for area in areas_dict['areas']:
        # use list comprehension to replace the & with and
        if not area['locations']:
            print("No locations to add")
        else:
            area['locations'] = [location.replace('&', 'and') for location in area['locations']]

            # combine the two items then delete each individual item before adding the newly created item
            for i, location in enumerate(area['locations']):
                if location.endswith('-'):
                    try:
                        combined_name = location.replace('-', '') + area['locations'][i+1]
                        del area['locations'][i: i+2]
                        area['locations'].insert(i, combined_name)
                    except IndexError as e:
                        print(f"List index error: {e}")
                        print(location)

            # create a string from the entire list then split to create individual locations.
            locations_str = ' '.join([str(location) for location in area['locations']])
            area['locations'] = locations_str.split(', ')
    return areas_dict


def generate_data_schema(unformated_text):
    print('********************************************')
    areas = format_image_text(unformated_text)
    # areas = format_locations(areas)
    pprint(areas)
    print("data schema created successfully")
    # pprint(locations_formatted)
    return areas

# generate_data_schema(results_list)