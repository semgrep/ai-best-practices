import cohere

client = cohere.Client("api-key")

# ruleid: cohere-no-error-handling
response = client.chat(message="Hello")

# ruleid: cohere-no-error-handling
response = client.generate(prompt="Hello")

# ruleid: cohere-no-error-handling
response = client.chat_stream(message="Hello")

def no_try():
    # ruleid: cohere-no-error-handling
    response = client.chat(message="Hello")
    return response

# ok: cohere-no-error-handling
try:
    response = client.chat(message="Hello")
except Exception as e:
    handle_error(e)

# ok: cohere-no-error-handling
try:
    response = client.generate(prompt="Hello")
except Exception as e:
    handle_error(e)

# ok: cohere-no-error-handling
try:
    response = client.chat_stream(message="Hello")
except Exception as e:
    handle_error(e)

def with_try():
    try:
        # ok: cohere-no-error-handling
        response = client.chat(message="Hello")
    except Exception as e:
        handle_error(e)
