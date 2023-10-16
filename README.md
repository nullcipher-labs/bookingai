# bookingai
a project that combines a booking.com bot with chatgpt to be able to search and ask questions about bookings.

this is meant as a proof of concept for pipelines that combine chatgpt with APIs or web scraping to produce a prompt GUI, that would allow to ask free questions about distributed data, and get good answers without looking through it manually. in other words, automation of day-to-day actions with the use of ais like chatgpt that are able to automate actions that used to require a human.

in this demo, there's a booking bot that sscrapes through booking.com for several listeings given search parameters (destination, dates, number of adults, minimum stars).
after finding and organizing the data, the user is than allowed to ask a general yes or no question that will be prompted to gpt about each room, for example "does this room have a kettle?".
The results will print a message showing which rooms/listings in the data do in fact have a kettle.

# why is this necessary? 
booking.com provides a lot of hard coded info about each listing, like size, allowance for pets, existence of AC and so on. Lets call that data "dry details".
Some information is not coded like that and cannot be accessed by dry details, but is present, in natural language form, in the listing's description. Let's call these et details.
For example, if the booking.com GUI does not show whether the listing is close to a coffee shop, but the description mentions its "only five minutes walk from a lovely coffee house", then that's a wet detail.

chatgpt has the capability to deduce from free text the answers to such questions, and can be automated. 

# future features
this little demo could be expanded to more general questions (not just yes or no), include a comfortable GUI etc.

# points about the code
1. the bookingai_bot file uses selenium to scrape data from booking.com manually. the nature of html bots is not stable since the site changes its structure every once in a while.
  however, the bot can be completeley replaced with one using the official booking API, and the code will still function as long as the bot has:
  * an init that functions similarly and allows loading external data and search parameters
  * the search_vacation method
  * the save_search_data method
  * the create_prompts method
  
  see inside documentation for details.

2. the booking_cgpt file and the entire project require an openai_api key to function (to access gpt through python).
   if you have one, put it as a string in the openai_key attribute in GPThelper class, in the booking_cgpt file.

# points about prompt design
1. some finicking with chatgpt prompts was required. firstly, to get a prompt that gets the correct answer most of the times, and secondly, that does not add extra superfluous details to the answers.
  the prompt_format.txt file contains the format of the prompt and is used by the program to create the actual prompts, with listing descriptions and user questions.

2. through testing, it proved that asking chatgpt about each room/listing in a separate prompt, instead of all of them together, improves accuracy. that's why it is done like that in the code.

# the input_outputs folder
this folder contains an example of a csv file with results from the booking bot, and an example of a txt file containing seatch parameters for the booking bot.
