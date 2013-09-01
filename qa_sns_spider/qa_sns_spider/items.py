# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst, Compose
from scrapy.utils.markup import remove_entities

# filter the category, cleaning the home and all categories
def filter_home(x):
    x_lower = x.lower()
    if x_lower == "home" or x_lower == "all categories":
        return None
    else:
        return x

def add_yahoo_baseurl(x):
    return ''.join([
        "http://answers.yahoo.com",
        x
        ])

def get_number_from_string(x):
    if x.strip(' ()') == '':
        return 0
    else:
        return int(x.strip(' '))


class YahooUser(Item):
    user_id = Field(
            output_processor = Join()
            )
    user_name = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    user_url = Field(
            input_processor=MapCompose(add_yahoo_baseurl, remove_entities, unicode.strip),
            output_processor = Join()
            )

class YahooAnswer(Item):
    question_id = Field(
            output_processor = Join()
            )
    answer_id = Field(
            output_processor = Join()
            )
    answering_date = Field(
            output_processor = Join()
            )
    is_best_answer = Field(
            output_processor = TakeFirst()
            ) # 0 or 1
    rating_by_the_asker = Field()
#help fields
    marks = Field(
            output_processor = Join()
            )
    number_of_good_marks = Field(
            output_processor = Compose(Join(),get_number_from_string)
            )
    number_of_bad_marks = Field()
    answer_content = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    answerer = Field(
            output_processor = TakeFirst()
            )

def get_answers_number(x):
    return int(x.strip(' ()').split(' ')[-1])

class YahooQuestion(Item):
    question_id = Field(
            output_processor = Join()
            )
    question_url = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    asker = Field(
            output_processor = TakeFirst()
            )
    asking_date = Field(
            output_processor = Join()
            )
    number_of_answers = Field(
            input_processor = MapCompose(remove_entities, get_answers_number),
            output_processor = TakeFirst()
            )
    number_of_interesting_marks = Field(
            output_processor = Compose(Join(), get_number_from_string)
            )
    status = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    import_date = Field(
            output_processor = Join()
            )
    question_user = Field(
            output_processor = TakeFirst()
            )
    question_title = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    question_content = Field(
            input_processor=MapCompose(remove_entities, unicode.strip),
            output_processor = Join()
            )
    category =  Field(
            input_processor = MapCompose(filter_home)
            )

