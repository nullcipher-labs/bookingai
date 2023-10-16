import bookingai_utils as utils
import pprint


if __name__ == "__main__":
    # creates bot, checks if it has loaded external data or needs to scrape its own
    bot, has_data = utils.get_user_choices()

    # if the bot needs to scrape, asks for where to save the data
    if not has_data:
        csv_path = input('please enter a csv path to save the data:\n')
        bot.save_search_data(csv_path=csv_path)

    # shows the results
    print('these are the rooms I found for you:\n\n')
    pprint.pprint(bot.data)
    print('\n\n')

    # asks for a question about the rooms - question must be worded as if for a single listing
    # e.g. "does this room have a kettle?"
    choice = input('do you have any questions about the rooms? y/n ')

    if choice.lower() == 'y':
        q = input('please enter a question about each room: ')
        prompts = bot.create_prompts(q)

        # shows which rooms have a "yes" answer to the question
        s = utils.query_gpt(prompts)
        print(f'\n{s}')

    print('\nthank you for using bookingai!')
