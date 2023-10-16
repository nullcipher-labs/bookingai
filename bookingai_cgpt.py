import openai


class GPThelper:
    """
    a class used to send prompts and get back answers from gpt's api, requires an openai key

    Attributes
    ----------
    openai_key : str
        a string with your own api key for accessing chatgpt

    model_params : dict
        a dictionary used for the openai module

    Methods
    -------
    query_chatgpt(prompt)
        sends a single prompt (str) to chatgpt and returns the answer

    query_list(queries)
        iterates over a list of prompts and sends them one by one to chatgpt, returning a list of answers

    response_to_bool(lst)
        takes a list of answers from gpt (only 'yes' or 'no') and converts is to a list of bools (True for yes)

    string_results()
        returns the results well worded within a string, format example: "entries 5,8,9 match your question."
    """
    def __init__(self):
        self.answers = None
        self.openai_key = ''
        openai.api_key = self.openai_key

        # model setup
        self.model_params = dict(
            model="gpt-3.5-turbo-0613",
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    def query_chatgpt(self, prompt):
        """sends a query to chatgpt and returns an answer

        Parameters
        ----------
        prompt : str
           a prompt to send to chatgpt

        Returns
        -------
        str
           answer from chatgpt
        """

        messages = [
            {
                "role": "system",
                "content": prompt
            },
        ]
        response = openai.ChatCompletion.create(
            messages=messages,
            **self.model_params
        )
        return response['choices'][0]['message'].content

    def query_list(self, prompts):
        """iterates over a list of queries, sending them one by one to chatgpt and populate the answers attribute with
        a list of answers
        in this project the prompts are designed in a way that the answer is only either yes or no

        Parameters
        ----------
        prompts : list
           a list of prompts to send to chatgpt
        """
        self.answers = self.response_to_bool([self.query_chatgpt(p) for p in prompts])

    def response_to_bool(self, responses):
        """takes in a list of yes and no answers and populates the attribute answers a list of bools (yes becomes True)

        Parameters
        ----------
        responses : list
           a list of yes and no answers from chatgpt, by order of questions asked
        """
        bools = []
        for ans in responses:
            ans = ''.join(x for x in ans if x.isalpha()).lower()
            bools.append(ans == 'yes')

        self.answers = bools

    def string_results(self):
        """returns a string describing which entries got a yes answer from chatgpt
        in practice - takes the attribute answers, a list of booleans, a string describing which ones are True

        Returns
        -------
        str
           a string describing which entries got the answer yes to the prompt,
           format example: "entries 5,8,9 match your question."
        """
        if self.answers is not None:
            s = 'entries '

            for i in range(len(self.answers)):
                if self.answers[i]:
                    s += f'{i}, '

            return s[:-2] + ' match your question.'
