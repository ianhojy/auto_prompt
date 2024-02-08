from self_improving_llm.llm.openai import CompletionEngine

ce = CompletionEngine('hello')
print(ce.message)