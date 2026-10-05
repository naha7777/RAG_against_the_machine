from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Any


class GetAnswer:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
        self.model: Any = (
            AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B"))

    def augmente(self, query: str, chunks: list[Any],
                 context_limite: int) -> Any:

        tokens_used = 0
        parts = []

        tokens_used += len(self.tokenizer.encode("Context:"))
        parts.append("Context:")
        tokens_used += len(
            self.tokenizer.encode(f"Question: {query}\nAnswer:")
            )
        for c in chunks:
            n = len(self.tokenizer.encode(c["text"]))
            if n + tokens_used < context_limite:
                parts.append(c["text"])
                tokens_used += n
            else:
                break
        parts.append(f"Question: {query}Answer:")

        content = " ".join(parts)
        messages = [{"role": "user", "content": content}]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False)

        prompt_token = self.tokenizer(
            prompt,
            return_tensors="pt").to(self.model.device)

        return prompt_token

    def generate(self, tokens: Any) -> Any:
        result = self.model.generate(**tokens, max_new_tokens=300)
        answer = self.tokenizer.decode(
            result[0][tokens["input_ids"].shape[1]:],
            skip_special_tokens=True)
        return answer
