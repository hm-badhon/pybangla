import re
import datetime
from .config import Config as cfg
from num2words import num2words
data = cfg.data

_abbreviations = cfg._abbreviations
_symbols = cfg._symbols
_ordinal_re = cfg._ordinal_re
_whitespace_re = cfg._whitespace_re
_currency = cfg._currency

english_digits = cfg._bangla2english_digits_mapping
bangla_numeric_words = cfg._bangla_numeric_words


class NumberParser:
    def __init__(self):
        self.english_digits = english_digits
        self.bangla_numeric_words = bangla_numeric_words
        self.en_regex = cfg.en_regex
        self.bn_regex = cfg.bn_regex

    def is_english_digit_string(s):
        # Check if all characters in the string are digits (0-9)
        return all(char.isdigit() for char in s)

    def number_to_words_converting_process(self, number_string:str, lang = "bn"):
        number_string = number_string.strip()
        num = int("".join([self.english_digits[bangla_digit] if lang =="bn" else bangla_digit for bangla_digit in number_string]))
        try:
            eng_in_num_to_words = num2words(num, lang='en_IN')
            if lang =="bn":
                bangla_num_to_words_list = [self.bangla_numeric_words[word] for word in eng_in_num_to_words.replace(',', ' ').replace(' and ', ' ').split()]
            else:
                bangla_num_to_words_list = [word for word in eng_in_num_to_words.replace(',', ' ').replace(' and ', ' ').split()]
            return ' '.join(bangla_num_to_words_list)
        except Exception as e:
            print(e)
            return 
        
    def number_to_words(self, number:str, chunk_millions = 7):

        en_extraction = list(re.finditer(self.en_regex, number, re.UNICODE))
        number = number[::-1]
        chunks = [
            number[i:i+chunk_millions] 
            for i in range(0, len(number), chunk_millions)
            ]
        chunks = [c[::-1] for c in chunks]
        chunks = chunks[::-1]
        if en_extraction:
            number = " crore ".join([self.number_to_words_converting_process(chunk, lang="en") for chunk in chunks])
            number = number.replace("zero", "")
        else:
            number = " কোটি ".join([self.number_to_words_converting_process(chunk, lang="bn") for chunk in chunks])
            # print(number)
            number = number.replace("শূন্য", "")


        return " ".join(number.split())
    
    def digit_number_to_digit_word(self, number, language="bn"):

        number = re.sub(_whitespace_re, " ", number)
        s_n = ""
        for i in number:
            n = data[language]["number_mapping"][i]
            s_n += " "+n
        return s_n.strip()
    
    def year_in_number(self, year_in_number:str, language="bn"):
        """ Converts a Bangla year in numeric form to literal words.

        Args:
            number_string: Bangla year in numbers as string. Example: "১৯৯৪"

        Returns:
            Bangla year in words. Example: "উনিশশো চুরানব্বই"

        """
        # print("year_in_number[1]", year_in_number[1])
        # if (len(year_in_number) == 4 and year_in_number[1] != '০') or \
        #     (len(year_in_number) == 4 and year_in_number[1] != '0') or len(year_in_number) == 3:



        if language=="bn":
            mid_text = "শো "
        else:
            mid_text = " century "

        if (len(year_in_number) == 4 and year_in_number[1] != '০') or len(year_in_number) == 3:
            
            if year_in_number[1] != '0':
                return self.number_to_words(year_in_number)
                
            return self.number_to_words(year_in_number[:-2]) + mid_text + self.number_to_words(year_in_number[-2:])
        
        # elif (len(year_in_number) == 4 and year_in_number[1] != '0') or len(year_in_number) == 3:
        #     return self.number_to_words(year_in_number[:-2]) + mid_text + self.number_to_words(year_in_number[-2:])
        else:
            return self.number_to_words(year_in_number)

    def _replace_starting_zero(self, month):
        """
        Normalize string which start zero first
        
        """
        if month[0] == "0" or month[0] == "০":
            return month[1:]
        return month

    def _digit_converter(self, number, language="bn"):
        """
        convert the digit En to Bn or Bn to En
        
        """
        # print("number  : ", number, language)

        if language=="en":
            extracted_number = list(re.finditer(self.bn_regex, str(number), re.UNICODE))
            if extracted_number:
                number = "".join([cfg._bangla2english_digits_mapping[i] for i in number])
                # print("extracted : ", number)
        c_number = ""
        for n in number:
            if n in data[language]["number"]:
                c_number += n
            else:
                if n.strip() in data[language]["digits_mapping"]:
                    b_n = data[language]["digits_mapping"][n.strip()]
                    c_number+=b_n
        return c_number
    
    def get_weekday(self, date_:list=[], language="bn"):

        """
        Get weekday name Bangla or English
        
        """

        # print("++++++++++++++++++++ : ", date_)

        d, y = list(re.finditer(self.bn_regex, str(date_[0]), re.UNICODE)), list(re.finditer(self.bn_regex, str(date_[2]), re.UNICODE))
        
        # print("d, y : ", d, y)
        
        if d:
            date_[0] = self._digit_converter(date_[0], language="bn")
        if y:
            date_[2] = self._digit_converter(date_[2], language="bn")

        current_date_object = datetime.datetime(int(date_[2]), int(date_[1]), int(date_[0]))
        if language in data:
            weekday = data[language]["weekdays"][current_date_object.weekday()]
        else:
            print("language not handel")
            weekday = ""
        return weekday
    
    def search_month(self, search_key, language="bn"):
        """
        Search for a month or month abbreviation in the month_data dictionary.
        
        Args:
            search_key (str): The month or its abbreviation to search for.
            language (str, optional): Language identifier ("bn" for Bengali, "en" for English). 
                Defaults to "bn".
        
        Returns:
            list: A list containing additional information about the month if found, 
            formatted based on the specified language. 
            The list contains [month_name, season_name, number_of_days].
            If the month or abbreviation is not found, returns [None, None, None].
        """
        search_key = int(self._replace_starting_zero(search_key))-1
        month = data[language]["months"][search_key]
        seasons = data[language]["seasons"][search_key//2]
        option_name = data[language]["option_name"][search_key]

        return [month, option_name, seasons]
    
    def number_processing(self, text):

        # bn_regex, en_regex = r'[০-৯]+', r'[0-9]+'
        bn_matches, en_matches = list(re.finditer(self.bn_regex, text, re.UNICODE)), \
            list(re.finditer(self.en_regex, text, re.UNICODE))
        if en_matches:
            for m in en_matches:
                if m[0]:
                    bn_m= self.number_to_words(self._digit_converter(m[0]))
                    text = text.replace(m[0], bn_m)
        if bn_matches:
            for m in bn_matches:
                if m[0]:
                    bn_m= self.number_to_words(m[0])
                    text = text.replace(m[0], bn_m)
        return text

class DateParser:
    def __init__(self):
        self.samples = cfg.samples

    def data_splitter(self, date_string):
        """
        
        """
        separator_pattern = '|'.join(map(re.escape, self.samples))
        return re.split(separator_pattern, date_string)


    def month_convert_to_number(self, month):
        """
        
        """
        key = month.lower().strip()
        if key in data["en"]["months"]:
            index = data["en"]["months"].index(key)+1
        elif key in data["bn"]["months"]:
            index = data["bn"]["months"].index(key)+1
        elif key in  data["bn"]["option_name"]:
            index = data["bn"]["option_name"].index(key)+1
        elif key in data["en"]["option_name"]:
            index = data["en"]["option_name"].index(key)+1
        elif key in data["en"]["number"]:
            index = data["en"]["number"].index(key)+1
        elif key in data["bn"]["number"]:
            index = data["bn"]["number"].index(key)+1
        else:
            print("else : ", key)
            index = key
        return index


    def format_non_punctuation(self, split_date):
        """
        
        """
        if len(split_date[0]) == 8:
            if int(split_date[0][4:6]) <= 12:
                year, month, day = split_date[0][:4], split_date[0][4:6], split_date[0][6:]
            else:
                year, month, day = split_date[0][4:], split_date[0][2:4], split_date[0][:2]
            return [day, month, year]
        else:
            print("This date format is not handled yet")
        return None


    def get_day_and_month(self, year_idx, idx, date_list):
        """
        
        """
        if year_idx == 0:
            return self.get_day_and_month_helper(idx, date_list, 1, 2)
        elif year_idx == 2:
            return self.get_day_and_month_helper(idx, date_list, -1, -2)
        else:
            print("Date format not handled yet")
        return None, None


    def get_day_and_month_helper(self, idx, date_list, offset1, offset2):
        """
        
        """
        if date_list[idx + offset1].isdigit() and date_list[idx + offset2].isdigit():
            return date_list[idx + offset2], date_list[idx + offset1]
        elif not date_list[idx + offset1].isdigit() and date_list[idx + offset2].isdigit():
            return date_list[idx + offset2], self.month_convert_to_number(date_list[idx + offset1])
        elif date_list[idx + offset1].isdigit() and not date_list[idx + offset2].isdigit():
            return date_list[idx + offset1], self.month_convert_to_number(date_list[idx + offset2])
        else:
            print("Date format not handled yet")
        return None, None


    def get_date_indexes(self, date_list):
        """
        
        
        """
        day, month, year = None, None, None
        for idx, elem in enumerate(date_list):
            if elem.isdigit() and len(elem) == 4:
                year_idx = idx
                year = date_list[idx]
                # print(date_list)
                day, month = self.get_day_and_month(year_idx, idx, date_list)
        return [day, month, year]

class TextParser:

    def __init__(self):
        self.year_patterns  =["সালের","সালে", "শতাব্দী", "শতাব্দীর", "শতাব্দীতে"]
        self.year_pattern = r'(?:\b|^\d+)(\d{4})\s*(?:সালে?র?|শতাব্দী(?:র)?|শতাব্দীতে)+'
        self.currency_pattern = r'(?:\$|£|৳|€|¥|₹|₽|₺)?(?:\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)'
        self.npr = NumberParser()

    def collapse_whitespace(self, text):
        return re.sub(_whitespace_re, " ", text)
    
    def expand_symbols(self, text, lang="bn"):
        for regex, replacement in _symbols[lang]:
            # print("regex : ", regex)
            text = re.sub(regex, replacement, text)
            text = text.replace("  ", " ")  # Ensure there are no double spaces
        return text.strip()

    def expand_abbreviations(self, text, lang="bn"):
        for regex, replacement in _abbreviations[lang]:
            text = re.sub(regex, replacement, text)
        return text
    
    def expand_position(self, text, lang="bn"):

        """
        Replace : 
            ("১ম", "প্রথম"),
            ("২য়", "দ্বিতীয়"),
            ("৩য়", "তৃতীয়"),
            ("৪র্থ", "চতুর্থ"),
            ("৫ম","পঞ্চম"),
            ("৬ষ্ঠ", "ষষ্ঠ"),
            ("৭ম", "সপ্তম"),
            ("৮ম", "অষ্টম"),
            ("৯ম", "নবম"),
            ("১০ম", "দশম")
        রাহিম ক্লাস ওয়ান এ ১ম, ১১তম ২২ তম ৩৩ তম -> রাহিম ক্লাস ওয়ান এ প্রথম, এগারোতম বাইশতম তেত্রিশতম
        
        """
        for regex, replacement in _ordinal_re[lang]:
            text = re.sub(regex, replacement, text)
        if lang=="bn":
            matches = re.findall(r'(\d+)(?:\s*)(?:তম)', text)
            if matches:
                for i in matches:
                    word = self.npr.number_to_words(i)
                    text = text.replace(i+"তম", word+"তম")
                    text = text.replace(i+" তম", word+"তম")
        return text

    def year_formation(self, text):
        matches = re.findall(self.year_pattern, text)

        # print(matches)
        """
        Need to correct year format extraction
        """
        for i in matches:
            text = text.replace(i, self.npr.year_in_number(i))
        return text

    def extract_currency_amounts(self, text):

        matches = re.findall(self.currency_pattern, text)
        pattern = r'[৳$£€¥₹₽₺]'

        for m in matches:
            # print("m : ", m)
            # Use findall to extract matches
            currency = re.findall(pattern, m)

            # print(currency)
            if currency:
                # print("m : ", m)
                n_m = m.replace(currency[0], "")
                if "." in n_m:
                    s_m = n_m.split(".")
                    before_dot_word, after_dot_word = self.npr.number_to_words(s_m[0]), self.npr.digit_number_to_digit_word(s_m[1])

                    word =  before_dot_word+" দশমি "+after_dot_word+ " "+_currency[currency[0]]
                    text = text.replace(m, word)
                    # print(s_m, before_dot_word, after_dot_word)
                else:
                    word = self.npr.number_to_words(n_m)
                    n_word = word + " "+_currency[currency[0]]


                    text = text.replace(m, n_word)
        return text
    

    def processing(self, text):
        text = self.collapse_whitespace(text)
        text = self.expand_symbols(text)
        text = self.expand_abbreviations(text)
        text = self.expand_position(text)
        text = self.extract_currency_amounts(text)
        text = self.year_formation(text)
        text = self.npr.number_processing(text)
        return text
    
if __name__ =="__main__":

    text = "রাহিম ক্লাস ওয়ান এ ১ম, ১১তম ২২ তম ৩৩ তম, ১২৩৪ শতাব্দীতে ¥২০৩০.১২৩৪ বিবিধ  বাকেরগঞ্জ উপজেলার প্রায় 40 ভাগের পেশাই চাষাবাদ 80 and 40 ২২"
    tp = TextParser()
    text = tp.processing(text)
    print(text)

    





