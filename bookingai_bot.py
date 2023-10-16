import bookingai_utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time


class BookingBot(webdriver.Chrome):
    """
    a class used to surf through booking.com, search accommodations by given parameters, scrape and save the results
    inherits from selenium.webdriver.Chrome to enable use of builtin scraping funcs

    Parameters
    ----------
    imp_wait_time : int
        time for implicit wait by selenium

    data_csv_path : str
        if not None, loads data from a previously created csv and skips need to scrape again

    stats_dict : dict
        if not None, loads search params from an existing dict instead of from a txt file, skips need to parse txt

    Attributes
    ----------
    TXT_PATH : str
        path to txt file with the phrasing of the chatgpt prompt

    BASE_URL : str
        booking homepage url

    imp_time : int
        implicit time as described above

    data : dataframe
        results of search, organized as a dataframe with the columns: name,price,score,link,text

        name - name of accommodation
        price - price as seen in the site
        score - score by reviews
        link - url leading to the accommodation page
        text - str of the description of the accommodations in its page

    stats_dict : dict
        dictionary with search parameters for booking.com

    Methods
    -------
    go_to_home_page()
        opens up a Chrome window and goes to BASE_URL (booking homepage)
        closes a popup window that tends to appear

    query_list(queries)
        iterates over a list of prompts and sends them one by one to chatgpt, returning a list of answers

    change_currency(currency)
        changing the current display currency on booking, currently unused

    search_vacation()
        searches for accommodations by the parameters given in stats_dict
        stops at search page after applying filters

    click_stars_above(star_dict, star_choice)
        static method
        takes in a dict of stars (2,3,4,5) and their html counterparts created by scraping (buttons), and a
        star choice (e.g. 4)
        iterates over the dict and clicks all the star buttons of stars equal or above the choice (e.g. 4, 5)

    save_search_data(amount=10, save_csv=False, csv_path=None)
        saves the first "amount" entries from the search results into the attribute data (dataframe)
        can save an external csv file of the data if needed

    load_data_from_csv(csv_path)
        loads a dataframe from an external csv file and populate the attribute data

    create_prompt(description, question)
        takes in a room/accommodation description and a yes or no question, and returns a prompt around them
        to send to chatgpt

    create_prompts(self, question)
        takes in a question about an accommodation, iterates over the data attribute and creates a list of prompts using
        room descriptions and that question
    """

    def __init__(self, imp_wait_time=10, data_csv_path=None, stats_dict=None):
        """
        Parameters
        ----------
        imp_wait_time : int
            time for implicit wait by selenium

        data_csv_path : str
            if not None, loads data from a previously created csv and skips need to scrape again

        stats_dict : dict
            if not None, loads search params from an existing dict instead of from a txt file, skips need to parse txt
        """

        self.TXT_PATH = r'prompt_format.txt'
        self.BASE_URL = r"https://www.booking.com"
        self.imp_time = imp_wait_time

        self.data = None
        if data_csv_path is not None:
            self.load_data_from_csv(data_csv_path)

        self.stats_dict = {}
        if stats_dict is not None:
            self.stats_dict = stats_dict

        super().__init__()

    def go_to_home_page(self):
        """goes to booking home page and closes a common popup"""

        self.get(self.BASE_URL)
        self.implicitly_wait(self.imp_time)
        self.maximize_window()

        # get rid of popup at homepage
        try:
            x_button = self.find_element(By.XPATH, "//button[@aria-label='Dismiss sign-in info.']")
            x_button.click()
        except:
            pass

        actions = ActionChains(self)
        actions.send_keys(Keys.END).perform()

    def change_currency(self, currency):
        """changes the currency displayed on the booking page

        Parameters
        ----------
        currency : str
          the wanted currency, needs to be called as it would show on booking's html
        """
        currency_button = self.find_element(By.XPATH, "//button[@data-testid='header-currency-picker-trigger']")
        currency_button.click()

        my_cur_button = self.find_element(By.XPATH, f"//span[text()='{currency}']").find_element(By.XPATH, "../../..")
        my_cur_button.click()

    def search_vacation(self):
        """searches for a vacation by a given set of parameters from the attribute stats_data
        stops on search page after filters have been applied

        the parameters are currently:
        destination - name of destination city or area
        starting_date - starting date of booking
        ending_date - ending date of booking
        adults - number of adults to book, no support of children yet
        min_stars - number of stars to show listings from (e.g. 3 would min showing listings with 3,4,5), min is 2
        """

        self.go_to_home_page()
        time.sleep(2)

        # get params from stats_dict
        destination = self.stats_dict['destination']
        starting_date = bookingai_utils.parse_and_format_date(self.stats_dict['start_date'])
        ending_date = bookingai_utils.parse_and_format_date(self.stats_dict['end_date'])
        adults = int(self.stats_dict['n_adults'])
        min_stars = int(self.stats_dict['min_stars'])

        # write destination in search bar
        search_bar = self.find_element(By.XPATH, "//input[@id=':re:']")
        search_bar.clear()
        search_bar.send_keys(destination)

        # click the first result
        time.sleep(1)
        options = self.find_element(By.XPATH, "//ul[@data-testid='autocomplete-results-options']")
        choice = options.find_element(By.CLASS_NAME, "be14df8bfb")
        choice.click()

        # click dates
        start_cell = self.find_element(By.XPATH, f"//span[@data-date='{starting_date}']").find_element(By.XPATH, '..')
        start_cell.click()

        end_cell = self.find_element(By.XPATH, f"//span[@data-date='{ending_date}']").find_element(By.XPATH, '..')
        end_cell.click()

        # input number of adults
        occupancy_button = self.find_element(By.XPATH, "//button[@data-testid='occupancy-config']")
        occupancy_button.click()

        current_adults = self.find_element(By.XPATH, "//span[@class='d723d73d5f']")
        current_adults = int(current_adults.get_attribute('innerHTML'))

        clicks = adults - current_adults

        if clicks > 0:
            adult_button = self.find_element(By.XPATH, "//button[@class='a83ed08757 c21c56c305 f38b6daa18 d691166b09 "
                                                       "ab98298258 deab83296e bb803d8689 f4d78af12a']")
        else:
            adult_button = self.find_element(By.XPATH, "//button[@class='a83ed08757 c21c56c305 f38b6daa18 d691166b09 "
                                                       "ab98298258 deab83296e bb803d8689 e91c91fa93']")

        clicks = abs(clicks)
        for i in range(clicks):
            adult_button.click()

        # click the search button
        search_button = self.find_element(By.XPATH, "//button[@class='a83ed08757 c21c56c305 a4c1805887 f671049264 "
                                                    "d2529514af c082d89982 cceeb8986b']")
        time.sleep(0.5)
        search_button.click()

        # find and click on all stars above the given int
        time.sleep(3)
        stars = {}

        for i in range(2, 6):
            star = self.find_element(By.XPATH, f"//div[@data-filters-item='class:class={i}']")

            if 'stars' in star.text:
                star_button = star.find_element(By.XPATH, ".//span[@class='fcd9eec8fb b27b51da7f bf9a32efa5']")
                stars[i] = star_button

        self.click_stars_above(stars, min_stars)

    @staticmethod
    def click_stars_above(star_dict, star_choice):
        """clicks on all star filter buttons given a min star value

        Parameters
        ----------
        star_dict : dict
            a dictionary where the keys are star values (2,3,4,5) and the values are html buttons to click to filter
            by that star value

        star_choice : int
            a choice of star to filter by itself and above (e.g. choosing 3 would filter by 3,4,5)
        """
        for star_rating, star_button in star_dict.items():
            if star_rating >= star_choice:
                star_button.click()
                time.sleep(1)

    def save_search_data(self, amount=10, csv_path=None):
        """when the search page is open, scrapes all the listings and saves them into a dataframe in the data
        attribute
        if save_csv and csv_path are not None, saves the results as an external csv for later use

        Parameters
        ----------
        amount : int
            amount of listings to save in the dataframe (by order shown int he page)

        csv_path : str
            if not None, saves external results as a csv
        """

        # creating dict to populate and convert to dataframe
        d = {'name': [], 'price': [], 'score': [], 'link': [], 'text': []}

        # getting all listings in page
        properties = self.find_elements(By.XPATH, "//div[@data-testid='property-card']")[:amount]

        for prop in properties:
            # scraping data from each listing
            title_and_link = prop.find_element(By.XPATH, './/a[@data-testid="title-link"]')
            title = title_and_link.text.splitlines()[0].strip()
            link = title_and_link.get_attribute('href')

            price = prop.find_element(By.XPATH, ".//span[@data-testid='price-and-discounted-price']").text
            new_price = ''
            for c in price:
                if c.isdigit():
                    new_price += c
            price = int(new_price)

            score = float(prop.find_element(By.XPATH, ".//div[@class='a3b8729ab1 d86cee9b25']").text)

            d['name'].append(title)
            d['price'].append(price)
            d['score'].append(score)
            d['link'].append(link)

        # going into each listing's link to scrape the full description
        for link in d['link']:
            self.get(link)
            time.sleep(1)

            p_container = self.find_element(By.XPATH, "//div[@class='hp-description k2-hp_main_desc--collapsed']")
            p = p_container.find_element(By.XPATH, ".//p[@class='a53cbfa6de b3efd73f69']").text
            d['text'].append(p)

        self.data = pd.DataFrame(d)

        if csv_path is not None:
            self.data.to_csv(csv_path, index=False)

    def load_data_from_csv(self, csv_path):
        """loads data from an external csv to the data attribute

        Parameters
        ----------
        csv_path : str
            path to the csv to load the data from
        """
        self.data = pd.read_csv(csv_path)

    def create_prompt(self, description, question):
        """returns a prompt containing a room description and a question for chatgpt
        prompt format comes from a txt file, the path of which is saved in the attribute TXT_PATH

        Parameters
        ----------
        description : str
            description of a room or listing

        question : str
            question about the room
        """
        with open(self.TXT_PATH, 'r') as f:
            s = f.read()

        return s.replace('@@@@@', description).replace('&&&&&', question)

    def create_prompts(self, question):
        """returns a list of prompts containing a room description and the same question, for chatgpt

        Parameters
        ----------
        question : str
            question about the rooms (asked about each room separately

        Raises
        ------
        ValueError
            if the data attribute is empty (no data has been scraped or loaded)
        """
        if self.data is not None:
            return [self.create_prompt(des, question) for des in self.data['text']]
        else:
            raise ValueError('no data')
