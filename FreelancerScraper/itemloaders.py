from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity , TakeFirst , MapCompose

# The result of input processors will be appended to an internal list (in the Loader)
# containing the collected values (for that field). 
# The result of the output processors is the value that will be finally assigned
# to the item.


# def days_left_processor(value):
#     try:
#         days_left = str.split(value)[0]
#         days_left = int(days_left)
#         return days_left   
#     except ValueError:
#         return 0

def verified_processor(value):
    return True if value != None else False


class JobLoader(ItemLoader):

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    
    # title_in = MapCompose(str.strip)
    # title_out = TakeFirst()

    # description_in = MapCompose(str.strip)
    # description_out = TakeFirst()

    # skills_in = MapCompose(str.strip)
    skills_out = Identity()

    # remaining_time_in = MapCompose(str.strip , days_left_processor)
    # remaining_time_out = TakeFirst()

    # bid_in = MapCompose(str.strip)
    # bid_out = TakeFirst()

    verified_in = MapCompose(verified_processor)
    # verified_out = TakeFirst()
   