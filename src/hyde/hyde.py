import numpy as np


class HyDE:
    def __init__(self, promptor, generator, encoder, searcher, second_promptor=None):
        self.promptor = promptor
        self.generator = generator
        self.encoder = encoder
        self.searcher = searcher
        self.second_promptor = second_promptor  # Optional second prompter


    def improve_query(self, query):
        prompt = f"Improve the following search query to be more specific, clear, and optimized for retrieving accurate and relevant results. The improved version should maintain the original intent while refining the search for better precision. Output only the improved search query, without adding any context or explanation: {query}"
        # print(f"Original: {query}")
        # print(f"New: {prompt}") #DEBUG
        return self.generator.generate(prompt)
    
    def prompt(self, query):
        output = self.promptor.build_prompt(query)
        if self.second_promptor:
            output += "\n Second Prompt: "
            output += self.second_promptor.build_prompt(query)
        return output

    def generate(self, query, n=8):
        hypothesis_documents = []
        if self.second_promptor:
            n = int(n/2)
            prompt = self.second_promptor.build_prompt(query)
            hypothesis_documents += self.generator.generate(prompt, n)
        prompt = self.promptor.build_prompt(query)
        hypothesis_documents += self.generator.generate(prompt, n)
        return hypothesis_documents
    
    def encode(self, query, hypothesis_documents):
        all_emb_c = []
        for c in [query] + hypothesis_documents:
            c_emb = self.encoder.encode(c)
            all_emb_c.append(np.array(c_emb))
        all_emb_c = np.array(all_emb_c)
        avg_emb_c = np.mean(all_emb_c, axis=0)
        hyde_vector = avg_emb_c.reshape((1, len(avg_emb_c)))
        return hyde_vector
    
    def search(self, hyde_vector, k=10):
        hits = self.searcher.search(hyde_vector, k=k)
        return hits
    

    def e2e_search(self, query, k=10):
        prompt = self.promptor.build_prompt(query)
        hypothesis_documents = self.generator.generate(prompt)
        hyde_vector = self.encode(query, hypothesis_documents)
        hits = self.searcher.search(hyde_vector, k=k)
        return hits