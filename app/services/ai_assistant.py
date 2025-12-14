from openai import OpenAI

class AIAssistant:
    def __init__(self, system_prompt: str, client: OpenAI, history: list[dict[str, str]]):
        self._system_prompt: str = system_prompt
        self._history: list[dict[str, str]] = history
        self._client: OpenAI = client

    def SendMessage(self, user_message: str) :
        self._history.append({"role": "user", "content": user_message})
        gptMsg = [{"role": "system", "content": self._system_prompt}]

        completion = self._client.chat.completions.create(
            messages = gptMsg + self._history, #type: ignore
            model = "gpt-4o-mini",
            stream = True
            ) #type: ignore
        
        return completion 
    
    def clear_history(self):
        self._history.clear()