import os
# import re
# from dateutil.parser import parse
from typing import List, Dict
from helpers.read_image import read_img

# Using local image here. In production, this will be a remote image either directly from twitter or downloaded and
# stored online
images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
img_path = os.path.join(images_folder, "FA35VgdWEBsGCza.png")
image = open(img_path, "rb")

# this is the result of Azure CS extracting text from the image
results_list = read_img(image)

# this list contains all the areas that will be affected by maintenance i.e, the entire content of the image
affected_places = []


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
    return (' ' + w + ' ') in (' ' + s + ' ')


def format_image_text():
    """
    Here, the result of the image text which is now a list is to be parsed and each text categorized.
    The data definition is as follows:

    [
       {
            'region': str,
            'areas': [
                {
                    'county': str,
                    'area': str,
                    'locations': [str],
                    'date': str
                },
                {another area...}
            ]
        },
        { another region...}
    ]

    :return: the data definition above
    """

    # some of these values are initialized globally within the function to avoid errors
    area = {}
    locations = []
    region_dict = {
        'areas': []
    }
    region = ''
    county = ''

    for i, line in enumerate(results_list):
        if find_whole_word('REGION', line):

            # here if region is an empty string is defined atop, it means this is the first region found i.e it is at
            # the top of list/image and no other values have been saved. in that case, just assign region and move to
            # the next item

            if not region:
                region = line
                # print(f' FIRST {region}')


            # the fist time that is executed is after finding one region and collecting all its data. so this is true for second to the very last region available
            # the first thing is to assign the value currently stored in the variable region i.e the previous region in the iteration
            # then whatever values that are still currently held in the vars county, area, locations & date should be saved to the area_info dictionary.
            # these values still belong to the previous region. append them to the areas key (which is an array).
            # at this point, we've collected all the info for previous region so append to our overall list of affected_places

            else:
                region_dict['region'] = region
                area_info = {'county': county, 'area': area, 'locations': locations, 'date': date}
                region_dict['areas'].append(area_info)
                # print(region_dict)

                affected_places.append(region_dict)


                # and only now do we start dealing with and collecting info for the current region, i.e the one that returned true for this condition here.
                # save the value to region, i.e overwrite previously saved region.
                # empty the locations array since we're collecting locations for new array. the rest of the variables will simply be overwritten: county and date
                region = line
                locations = []

                # print(f'After first {region}')

            # whenever we find a new region, always clean up the values stored in the areas key of region_dict.
            # this is because I'm not reassigning values here but simply appending to it.
            # if it isn't emptied, it will persist values for previous regions
            region_dict = {}
            region_dict['areas'] = []

        elif find_whole_word('AREA:', line):

            # this will be true in three instances:
            # 1. for the first region ever since location is initialized as an empty string
            # 2. When we find a new area -- as is shown in the else statement below -- since locations is set to empty whenever a new area's info has been completely collected
            # 3. When we've only began collecting info for a new region. locations is also emptied at that point as shown above.
            if not locations:
                area = line

            # this only returns true when we'e traversed the list and collected all the locations/info for a the previous area
            # so I need to save that info first before beginning collecting info for the area that returned true here - the same logic as in region
            # append each area to the areas key in region_dict
            # then empty locations to start collecting locations info for current area
            else:
                area_info = {'county': county, 'area': area, 'locations': locations, 'date': date}
                region_dict['areas'].append(area_info)
                # print(region_dict)

                area = line
                locations = []

        elif find_whole_word('DATE:', line):
            # date = parse(line, fuzzy=True)[0]
            date = line

        elif find_whole_word('PARTS OF', line) and not find_whole_word('AREA', line):
            if not locations:
                county = line
            else:
                area_info = {'county': county, 'area': area, 'locations': locations, 'date': date}
                region_dict['areas'].append(area_info)
                locations = []

                county = line




        else:
            # this checks if it is the last item in the iteration.
            if i + 1 == len(results_list):
                # some of the images contain the word 'end of document' which is also extracted. if that sentence is
                # found then don't append it to locations, just create the area_info then region_dict and append to
                # affected_places.
                if not line == 'End of document':
                    locations.append(line)
                    area_info = {'county': county, 'area': area, 'locations': locations, 'date': date}
                    region_dict['region'] = region
                    region_dict['areas'].append(area_info)
                    affected_places.append(region_dict)
                    # print(area_info)
                    # print(region_dict)
                else:
                    area_info = {'county': county, 'area': area, 'locations': locations, 'date': date}
                    region_dict['region'] = region
                    region_dict['areas'].append(area_info)
                    affected_places.append(region_dict)
                    # print(area_info)
                    # print(region_dict)
            else:
                locations.append(line)

    # for place in affected_places:
    #     print(place)
    print("data schema created successfully")

    return affected_places


def format_locations(list_of_areas: List) -> List:
    """
    Three things to be done:
    - look for & sign and replace with 'and' to avoid url issues. this is just a failsafe since url is already encoded
    - look for words cut short by - sign and combine them into one.
    - recreate location list items such that they are separated by comma and not the default newline as they were extracted from the image

    :param list_of_areas: the list of affected areas
    :return: list with locations formatted
    """
    for region in list_of_areas:
        for area in region['areas']:
            # use list comprehension to replace the & with and
            area['locations'] = [location.replace('&', 'and') for location in area['locations']]

            # combine the two items then delete each individual item before adding the newly created item
            for i, location in enumerate(area['locations']):
                if location.endswith('-'):
                    combined_name = location.replace('-', '') + area['locations'][i+1]
                    del area['locations'][i: i+2]
                    area['locations'].insert(i, combined_name)

            # create a string from the entire list then split to create individual locations.
            locations_str = ' '.join([str(location) for location in area['locations']])
            area['locations'] = locations_str.split(', ')
    return list_of_areas


def generate_data_schema():
    areas = format_image_text()
    locations_formatted = format_locations(areas)
    print(locations_formatted)
    return locations_formatted

# generate_data_schema()