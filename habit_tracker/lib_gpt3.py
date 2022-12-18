from django.conf import settings
import openai
openai.api_key = settings.OPENAI_API_KEY

# chat_log: previous chat history
def gpt3_get_ai_chat_response(chat_input, chat_log=''):
    starting_prompt = 'The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. '
    prompt = f'{starting_prompt} {chat_log}Human: {chat_input}\nAI:'
    return gpt3_generate_base_completion(prompt)

# get GPT3 completion via API
#
# temperature: 0 to 1. Higher value means model will take more risk. 0 means deterministic answer. (openAI default: 1)
# frequency_penalty: between -2.0 and 2.0. Positive values decrease likelihood to repeat same line verbatim for new tokens. (openAI default: 0)
# presence_penalty: between -2.0 and 2.0. Positive values increase likelihood to talk about new topics for new tokens. (openAI default: 0)
def gpt3_generate_base_completion(prompt, max_tokens=100, temperature=0.9, frequency_penalty=1, presence_penalty=0.6):
    results = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    answer = results['choices'][0]['text'].strip()
    return answer