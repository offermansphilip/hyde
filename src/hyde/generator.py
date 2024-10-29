import time
import cohere
import ollama

class Generator:
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.api_key = api_key
    
    def generate(self):
        return ""

class CohereGenerator(Generator):
    def __init__(self, model_name, api_key, max_tokens=512, temperature=0.7, p=1, frequency_penalty=0.0, presence_penalty=0.0, stop=['\n\n\n'], wait_till_success=False):
        super().__init__(model_name, api_key)
        self.cohere = cohere.Cohere(self.api_key)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.p = p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.wait_till_success = wait_till_success

    
    @staticmethod
    def parse_response(response):
        text = response.generations[0].text
        return text
    
    def generate(self, prompt, n=8):
        texts = []
        for _ in range(n):
            get_result = False
            while not get_result:
                try:
                    result = self.cohere.generate(
                        prompt=prompt,
                        model=self.model_name,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        frequency_penalty=self.frequency_penalty,
                        presence_penalty=self.presence_penalty,
                        p=self.p,
                        k=0,
                        stop=self.stop,
                    )
                    get_result = True
                except Exception as e:
                    if self.wait_till_success:
                        time.sleep(1)
                    else:
                        raise e
            text = self.parse_response(result)
            texts.append(text)
        return texts

class OllamaGenerator(Generator):
    def __init__(self, model_name, max_tokens=512, temperature=0.7, top_p=1, stop=None, wait_till_success=False):
        super().__init__(model_name, None)  
        self.max_tokens = max_tokens
        self.temperature=temperature
        self.top_p = top_p
        self.stop = stop
        self.wait_till_success = wait_till_success

    @staticmethod
    def parse_response(response):
        return response.get('response')

    def generate(self, prompt, n=8):
        texts = []
        for _ in range(n):
            get_result = False
            while not get_result:
                try:
                    # Assuming the correct method is something like `complete`
                    result = ollama.generate(  # Use the correct method from the Ollama library
                        model=self.model_name,
                        prompt=prompt,
                        options={"temperature": self.temperature}
                    )
                    get_result = True
                except Exception as e:
                    if self.wait_till_success:
                        time.sleep(1)
                    else:
                        raise e
            text = self.parse_response(result)
            texts.append(text)
        return texts
    
    def get_temperature(self):
        return self.temperature