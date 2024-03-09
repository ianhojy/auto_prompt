from ..llm.openai import OpenAICompletionEngine
import streamlit as st



@st.cache_data(show_spinner=False)
def get_response(msg):
    ce = OpenAICompletionEngine()
    ce.insert_message('user', msg)
    return ce.get_response()


prompt_writer_role = """
You are an expert at writing prompts for prompting the OpenAI Large Language Model.
Your job is to improve a given prompt based on feedback for examples that were generated using that prompt.
"""

prompt_improvement_prompt = """

# Context # 

You are given an original prompt.

Your task is to improve the prompt to make it better at generating responses when prompted against the GPT language model.

The original prompt was used to generate some example responses. For each response, feedback was provided on how to improve the desired response.

Your task is to review all the feedback and then return an improved prompt that addresses the feedback.

# Guidelines # 

- The original prompt will contain placeholders within double curly brackets. These are values for input that you will see in the examples.
- The improved prompt should not exceed 200 words
- Just return the improved prompt and nothing else before and after. Remember to include the same placeholders with double curly brackets.
- When generating the improved prompt, refrain from writing the entire prompt as one paragraph. Instead, you should use a combination of task descriptions, guidelines (in point form), and other sections to the prompt as appropriate.
- The guidelines should be in point form, and should not be a repetition of the task. The guidelines shouild also be distinct from one another.
- The improved prompt should be written in normal English that is best understood by the language model.
- Based on the feedback provided, you must rephrase the desired behavior of the response into `must`, imperative statements, instead of `should` suggestive statements.
- Improvements made to the prompt should not be overly specific to one single example.

# Details # 

The original prompt is:
```
{original_prompt}
```

These are the examples that were provided and the feedback for each:
```
{examples}
```

The improved prompt is:
```
"""

def format_prompt_with_examples(prompt_template, original_prompt, list_of_examples):
    examples_string = ""
    for eg in list_of_examples:
        num = list(eg.keys())[0]
        vals = list(eg.values())[0]
        inner_string = ""
        inner_string += f"Example {num}:\n"
        for keyword, keyval in vals['keyword_dict'].items():
            inner_string += f"- {keyword}: {keyval}\n"
        inner_string += f"<RESPONSE_START>\n{vals['response']}<RESPONSE_END>\n"
        inner_string += f"Feedback:\n{vals['feedback']}"
        inner_string += '-' * 20
        examples_string += inner_string


    formatted_prompt =  prompt_template.format(
        original_prompt=original_prompt, examples=examples_string
    )

    return formatted_prompt

@st.cache_data(show_spinner=False)
def get_better_prompt(original_prompt, list_of_examples):
    ce = OpenAICompletionEngine()
    ce.insert_message('system', prompt_writer_role)
    ce.insert_message('user', format_prompt_with_examples(
        prompt_improvement_prompt, original_prompt, list_of_examples)
        )
    return ce.get_response().strip("`")
