from llama_cpp import Llama
import os
import sys

class LlamaEngine:
    def __init__(self, model_path="models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"):
        """
        Initializes the TinyLlama model on CPU.
        """
        # 1. Validation: Check if model exists
        if not os.path.exists(model_path):
            print(f"[Error] Model file '{model_path}' not found!")
            print("Please run 'download_tinyllama.py' first.")
            sys.exit(1)
            
        print("[Brain] Loading TinyLlama 1.1B (Quantized)...")
        
        # 2. Load Model
        # n_ctx=2048: Allows for decent conversation history
        # verbose=False: Keeps your terminal clean
        self.llm = Llama(
            model_path=model_path, 
            n_ctx=2048, 
            verbose=False,
            n_threads=4 # Uses 4 CPU cores for speed
        )
        print("[Brain] Model Loaded. Ready to think.")

    def _format_prompt(self, user_input, system_prompt="You are a helpful rural assistant."):
        """
        TinyLlama specific prompt formatting.
        Structure: <|system|>...</s><|user|>...</s><|assistant|>
        """
        return f"<|system|>\n{system_prompt}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"

    def generate_response(self, user_input, context=""):
        """
        Generates a natural language response.
        """
        # Inject context if provided (e.g., from RAG)
        full_input = user_input
        if context:
            full_input = f"Context info: {context}\n\nUser Question: {user_input}"

        prompt = self._format_prompt(full_input)
        
        output = self.llm(
            prompt, 
            max_tokens=200, 
            stop=["</s>", "<|user|>"], # Stop generating when done
            echo=False,
            temperature=0.7 # Creativity balance
        )
        return output['choices'][0]['text'].strip()

    def classify_intent(self, user_input):
        """
        Determines the USER INTENT.
        """
        system_instruction = (
            "You are a router. Classify the user query into EXACTLY one of these categories: "
            "[DIAGNOSE_MACHINERY, CHECK_SCHEMES, MARKET_PRICE, GENERAL_CHAT]. "
            "Do not explain. Reply ONLY with the category name."
        )
        
        # Few-shot examples to help the small model understand
        examples = (
            "Examples:\n"
            "User: My tractor engine is making a knocking sound.\nAssistant: DIAGNOSE_MACHINERY\n"
            "User: Is there a subsidy for solar pumps?\nAssistant: CHECK_SCHEMES\n"
            "User: What is the price of tomatoes today?\nAssistant: MARKET_PRICE\n"
            "User: How are you?\nAssistant: GENERAL_CHAT\n"
        )
        
        # Combine instructions + examples + current query
        final_query = f"{examples}\nUser: {user_input}"
        prompt = self._format_prompt(final_query, system_instruction)
        
        output = self.llm(
            prompt, 
            max_tokens=15, # We only need a short label
            stop=["\n", "</s>"],
            temperature=0.1 # Low temp = High precision
        )
        
        intent = output['choices'][0]['text'].strip()
        
        # Validation/Fallback
        valid_intents = ["DIAGNOSE_MACHINERY", "CHECK_SCHEMES", "MARKET_PRICE", "GENERAL_CHAT"]
        
        # Simple cleanup in case model adds punctuation
        for v in valid_intents:
            if v in intent:
                return v
                
        return "GENERAL_CHAT"

# --- Test Block ---
if __name__ == "__main__":
    # Ensure you have the model downloaded first!
    try:
        brain = LlamaEngine()
        
        # Test 1: Intent Classification
        print("\n--- Testing Intent ---")
        q1 = "My water pump is making a weird noise."
        print(f"Q: {q1}")
        print(f"Intent: {brain.classify_intent(q1)}")
        
        # Test 2: General Conversation
        print("\n--- Testing Response ---")
        q2 = "Why should I use organic fertilizer?"
        print(f"Q: {q2}")
        print(f"A: {brain.generate_response(q2)}")
        
    except Exception as e:
        print(f"Error: {e}")