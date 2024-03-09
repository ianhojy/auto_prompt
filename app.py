import re

import streamlit as st
from src.auto_prompt.tools.tools import get_response, get_better_prompt
from src.auto_prompt.llm.openai import OpenAICompletionEngine

st.subheader('📝 Auto Prompt Improver', divider='blue')

def extract_keywords(s):
    # Regular expression to find all occurrences of text within double curly braces
    pattern = r"\{\{(.*?)\}\}"
    matches = re.findall(pattern, s)
    matches = list(set(matches))
    return matches

def replace_keywords(s, replacements):
    # Replace each placeholder with its corresponding value in the replacements dictionary
    for key, value in replacements.items():
        s = s.replace(f"{{{{{key}}}}}", value)
    return s

if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'already_rerun' not in st.session_state:
    st.session_state.already_rerun = False
if 'examples' not in st.session_state:
    st.session_state.examples = list()
if 'archive_examples' not in st.session_state:
    st.session_state.archive_examples = list()
if 'prompt' not in st.session_state:
    st.session_state.prompt = "write me a 100-word fake but realistic news article about the issue of `{{issue}}` in `{{country}}`"

st.session_state.prompt = st.text_area("Input Prompt:", value=st.session_state.prompt)

keywords = extract_keywords(st.session_state.prompt)

num_keywords = len(keywords)

if num_keywords == 0:
    st.error('No input keywords found! 💡 Tip: Encapsulate your keywords like `{{keyword}}`')
    st.stop()

def example_container(num):

    if num in st.session_state.examples:
        return False, False

    with st.expander(f'Example {num}:', expanded=True):

        cols = st.columns(num_keywords)

        keyword_dict = dict()

        for ii in range(num_keywords):
            with cols[ii]:
                keyword_dict[keywords[ii]] = st.text_input(f":red[{keywords[ii]}]", key=keywords[ii]+str(num))

        all_filled = True
        for val in keyword_dict.values():
            if val.strip() == "":
                all_filled = False
                break

        if all_filled:
            filled_prompt = replace_keywords(st.session_state.prompt, keyword_dict)
            st.write(":green[The filled prompt is:]")
            st.success(filled_prompt)

            with st.spinner('Loading Response'):
                response = get_response(filled_prompt)
                col = st.columns(1)[0]
                with col:
                    st.write(":blue[The generated response is:]")
                    st.info(response.replace('$', '\$'))

            feedback = st.text_input('Provide your feedback:').strip()
            if feedback != "":
                gen_next = st.button('Generate Next Example')
                submit = st.button('Stop Generating')
            else:
                gen_next = False
                submit = False

        else:
            gen_next = False
            submit = False
            feedback = ""

        if gen_next or submit:
        
            st.session_state.examples.append({num: {
                'keyword_dict': keyword_dict,
                'response': response,
                'feedback': feedback
                }})

        return gen_next, submit, feedback

def show_all_previous_examples():
    examples = st.session_state.examples
    num_examples = len(examples)
    for ii in range(num_examples):
        with st.expander(f'Example {ii+1}'):
            st.write(examples[ii])

if 'counter' not in st.session_state:
    st.session_state.counter = 1
    st.session_state.submit = False

if st.session_state.counter == 1 or not st.session_state.submit or st.session_state.feedback == "":
    show_all_previous_examples()
    gen_next, st.session_state.submit, st.session_state.feedback = example_container(
        st.session_state.counter
        )
    if gen_next or st.session_state.submit:
        st.session_state.counter += 1

    if gen_next:
        st.session_state.feedback = ""
        st.rerun()
    if st.session_state.submit:
        st.rerun()
else:
    show_all_previous_examples()
    if not st.session_state.already_rerun:
        st.session_state.already_rerun = True
        st.rerun()
    with st.spinner('Generating Improved Prompt'):
        better_prompt = get_better_prompt(st.session_state.prompt, st.session_state.examples)
        st.subheader('Improved Prompt', divider='grey')
        st.write(better_prompt)
    replace = st.button('Replace Original Prompt')
    if replace:
        st.session_state.prompt = better_prompt
        st.session_state.archive_examples.append(st.session_state.examples)
        st.session_state.examples = list()
        st.session_state.submit = False
        st.session_state.feedback = ""
        del st.session_state['counter']
        st.session_state.already_rerun = False
        st.rerun()