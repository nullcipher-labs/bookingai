import bookingai_bot
import bookingai_cgpt
from dateutil import parser
import ast


def parse_and_format_date(date_string):
    """takes in a date in any format and returns a fromatted str of the form yyyy-mm-dd

    Parameters
    ----------
    date_string : str
       original date

    Raises
    ------
    ValueError
        if the parsing fails

    Returns
    -------
    str
       date formatted as yyyy-mm-dd
    """
    try:
        parsed_date = parser.parse(date_string, dayfirst=True)
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        return formatted_date
    except ValueError:
        return


def dict_from_text(txt_filepath):
    """takes a txt file with a dictionary plainly written in it, and returns a dict made out of it
    dict used to specify search parameters for booking.com
    see txt example in inputs_outputs folder

    Parameters
    ----------
    txt_filepath : str
        path to txt file

    Raises
    ------
    ValueError
        if the text file is not written as a dict

    Returns
    -------
    dict
        dictionary made out of the contents of the file
    """
    with open(txt_filepath, 'r') as txt_file:
        dict_string = txt_file.read()
        data = ast.literal_eval(dict_string)
        if isinstance(data, dict):
            return data
        else:
            raise ValueError("File does not contain a valid dictionary")


def get_user_choices():
    """text inputs to take in user's choices and perform the right actions

    right now the menu performs as such:

    data portion:
        * ask if the user already has a csv with listings data - if so loads from it and skips to questions portion
        * asks if the user has a txt with parameters for web scarping, if so skips manually entering parameters
        * manually entering parameters
    questions portion:
        * asks if the user has a question about the rooms, sends the questions through gpt and shows the answers

    Returns
    -------
    bot
        the booking bot created in the process
    bool
        a bool indicating whether an external csv was used for data
    """
    choice = input('do you have a csv file with booking data already? y/n\n')

    if choice.lower() == 'y':
        csv_path = input('please enter your csv path:\n')
        bot = create_bot(csv_path=csv_path)
        return bot, True
    else:
        choice = input('do you have a txt file with your search data? y/n\n')

        if choice.lower() == 'n':
            d = {}
            d['destination'] = input('please enter your destination: ')
            d['n_adults'] = int(input('please enter number of adults: '))
            d['start_date'] = input('please enter a starting date (yyyy-mm-dd): ')
            d['end_date'] = input('please enter an ending date (yyyy-mm-dd): ')
            d['min_stars'] = int(input('please enter a minimum number of stars (starting from 2): '))
            bot = create_bot(search_data=d)
        else:
            txt_path = input('please enter your txt path:\n')
            bot = create_bot(txt_path=txt_path)

    bot.search_vacation()
    return bot, False


def create_bot(search_data=None, txt_path=None, csv_path=None):
    """creates a booking bot by given parameters, external csv for data (if exists),
    txt file for search parameters (if exists)

    Parameters
    ----------
    search_data : dict
        dictionary with search parameters

    txt_path : str
        if not None, loads search parameters from txt in this path

    csv_path: str
        if not None, loads data from external csv in this path


    Raises
    ------
    ValueError
        if all arguments are None
    """
    if csv_path is not None:
        return bookingai_bot.BookingBot(data_csv_path=csv_path)
    elif txt_path is not None:
        search_data = dict_from_text(txt_path)
        return bookingai_bot.BookingBot(stats_dict=search_data)
    elif search_data is not None:
        return bookingai_bot.BookingBot(stats_dict=search_data)
    else:
        raise ValueError('one of the arguments must be not None')


def query_gpt(prompts):
    """creates a chatgpt helper instance, sends a list of prompts and returns the string representing the results

    Parameters
    ----------
    prompts : list
        a list of prompts to ask gpt
    """
    gpt_helper = bookingai_cgpt.GPThelper()
    gpt_helper.query_list(prompts)
    return gpt_helper.string_results()
