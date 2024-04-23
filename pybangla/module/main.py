
import re
import time
import datetime
from .config import Config as cfg
from .parser import DateParser, TextParser, NumberParser
dp, tp, np = DateParser(), TextParser(), NumberParser()
data = cfg.data

class Normalizer:
    def __init__(self):

        self.bn_regex = cfg.bn_regex
    
    def today(self, language="bn"):

        """
        It return today date if may Bangla and English
        
        """
        current_date_object = datetime.date.today()
        formatted_date = [current_date_object.day, current_date_object.month, current_date_object.year]

        weekday = np.get_weekday(formatted_date, language)
        formatted_date = list(map(str, formatted_date))
        day   = np._digit_converter(formatted_date[0], language)
        month = np.search_month(formatted_date[1], language)
        year  =  np._digit_converter(formatted_date[2], language)

        return {"date":day, "month": month[0], "year": year, "weekday" : weekday, "ls_month": month[1], "seasons" : month[2]}
    
    def weekdays(self, language="", day=""):
        """
        Weekday return or pair of weekday
        """
        if day:
            day = day.lower().strip()
            bn_weakday, en_weakday = data["bn"]["weekdays"], data["en"]["weekdays"]
            if day in bn_weakday:
                return {day: en_weakday[bn_weakday.index(day)]}
            if day in en_weakday:
                return {day: bn_weakday[en_weakday.index(day)]}
        if language:
            return {language : data[language]["weekdays"]}
        weekdays_map = {
            "bn" : data["bn"]["weekdays"], 
            "en": data["en"]["weekdays"]
            }
        return weekdays_map

    def seasons(self, language="", seasons=""):
        """
        seasons return or pair of seasons

        """
        if seasons:
            seasons = seasons.lower().strip()
            bn_seasons, en_seasons = data["bn"]["seasons"], data["en"]["seasons"]
            if seasons in bn_seasons:
                return {seasons: en_seasons[bn_seasons.index(seasons)]}
            if seasons in en_seasons:
                return {seasons: bn_seasons[en_seasons.index(seasons)]}
        if language in data[language]["seasons"]:
            return data[language]["seasons"]
        
        bn_en_seasons = {
            "bn":data["bn"]["seasons"], 
            "en" : data["bn"]["seasons"]
            }
        return bn_en_seasons
    
    def months(self, language="", month=""):

        """
        months return or pair of months
        
        """
        if month:
            month = month.lower().strip()
            bn_months, option_name, en_months = data["bn"]["months"], data["bn"]["option_name"], data["en"]["months"]
            if month in bn_months:
                return {month: en_months[bn_months.index(month)], "bangla" : option_name[bn_months.index(month)]}
            if month in option_name:
                return {month: en_months[option_name.index(month)], "bangla" : bn_months[option_name.index(month)]}
            if month in en_months:
                return {month: bn_months[en_months.index(month)], "bangla" : option_name[en_months.index(month)]}
        if language in data:
            return {language : data[language]["months"]}
        months_map = {
            "bn": data["bn"]["months"],
            "bn_name": data["bn"]["option_name"],
            "en": data["en"]["months"]
        }
        return months_map

    def date_format(self, date_, language="bn"):
        """
        Process the date from input and return format date

        Arg:
            data_{str or list} :  date may string or list of list like ["dd", "mm", "yyyy"]
            language{str}      : specific language format, support bangla and english

        return : 
                Dictonary :  {"date":day, "month": month[0], "year": year, "weekday" : weekday, "ls_month": month[1], "seasons" : month[2]}       
        """
        if isinstance(date_, list):
            if len(date_):
                formatted_date = date_
        else:
            split_date = dp.data_splitter(date_)
            split_date = [i for i in split_date if i]

            if len(split_date) == 1:
                formatted_date = dp.format_non_punctuation(split_date)
            else:
                formatted_date = dp.get_date_indexes(split_date)

        if formatted_date[0] == None and formatted_date[1] == None and formatted_date[2] == None:
            current_date_object = datetime.date.today()
            formatted_date = [current_date_object.day, current_date_object.month, current_date_object.year]

        weekday = np.get_weekday(formatted_date, language)
        day   = np._digit_converter(str(formatted_date[0]), language)
        month = np.search_month(str(formatted_date[1]), language)
        year  =  np._digit_converter(str(formatted_date[2]), language)

        return {"date":day, "month": month[0], "year": year, "weekday" : weekday, "ls_month": month[1], "seasons" : month[2]}

    def number_convert(self, number, language="bn"):
        """
        Convert the number digits English -> Bangla  or Bangla -> English

        Arg:
            number{str}  :  number string
            language{str}: specific language format, support bangla and english

        return: string
        
        """
        number   = np._digit_converter(number, language)
        number_string = np.number_to_words(number)
        digit_word = np.digit_number_to_digit_word(number)

        data = {"digit": number, "digit_word":digit_word , "number_string": number_string}
        return data

    def text_normalizer(self, text):
        """
        this is the text normalizer fucntion
        """
        text = tp.processing(text)
        return text
    
if __name__ == "__main__":


    # Testing Date format
    date_list = [
        "০১-এপ্রিল/২০২৩",
        "১ এপ্রিল ২০২৩" 
        "2023-04-05",  
        "06-04-2023", 
        "04/01/2023",  
        "07 April, 2023", 
        "Apr 1, 2023",  
        "2023/04/01", 
        "01-Apr-2023", 
        "01-Apr/2023",  
        "20230401",  
        "20042024",
        ["1", "4", "2025"]
    ]
    # number = "123456" or "২০২৩"
    number = "২০২৩"
    nmlr = Normalizer()
    print("++++++++++++++++++++ Date testing ++++++++++++++++++++++")
    print("Date format Testing : ", end ="", flush=True)
    for date_ in date_list:
        start_time = time.time()
        formated_date = nmlr.date_format(date_, language="bn")
        print(formated_date)
    print("++++++++++++++++++++ end of Date testing ++++++++++++++++++++++")

    print("++++++++++++++++++++ en number to bn number convert ++++++++++++++++++++++")
    number = nmlr.number_convert(number, language="bn")

    print("Bn Number : ", number)
    print("++++++++++++++++++++ stop number convert ++++++++++++++++++++++")

    print("++++++++++++++++ Today +++++++++++++++++++++")
    today_date = nmlr.today(language="bn")
    # today_date = nmlr.today(language="en")
    print(today_date)

    print("++++++++++++++++ End Today +++++++++++++++++++++")
    # print(today_date)
    print("++++++++++++++++ weekdays +++++++++++++++++++++")
    # weekdays = nmlr.weekdays()
    # weekdays = nmlr.weekdays(language="bn")
    # weekdays = nmlr.weekdays(language="en")
    # weekdays = nmlr.weekdays(day = "সোমবার")
    weekdays = nmlr.weekdays(day = "Monday")
    print(weekdays)

    print("++++++++++++++++ end weekdays +++++++++++++++++++++")
    # print(weekdays)
    print("+++++++++++++++ seasons ++++++++++++++++++++++++")
    # seasons = nmlr.seasons()
    # seasons = nmlr.seasons(language="bn")
    # seasons = nmlr.seasons(language="en")
    seasons = nmlr.seasons(seasons = "গ্রীষ্ম")
    print(seasons)

    print("+++++++++++++++ end seasons ++++++++++++++++++++++++")

    print("+++++++++++++++++ months +++++++++++++++++++++++++++")
    month = nmlr.months()
    month = nmlr.months(month="মার্চ")
    print(month)


    text = "রাহিম ক্লাস ওয়ান এ ১ম, ১১তম ২২ তম ৩৩ তম, ১২৩৪ শতাব্দীতে ¥২০৩০.১২৩৪ বিবিধ  বাকেরগঞ্জ উপজেলার প্রায় 40 ভাগের পেশাই চাষাবাদ 80 and 40 ২২"
    
    text = nmlr.text_normalizer(text)

    print(text)