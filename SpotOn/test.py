from openai import AzureOpenAI

# Azure OpenAI credentials
endpoint = "https://sharm-meolv79i-eastus2.cognitiveservices.azure.com/"
deployment = "gpt-5-mini"  # Your deployment name
subscription_key = "8CkxOIueKqlW6n9ZTElFnlGpoMi0P5aYZAA9pY4fHlPh0J0xx275JQQJ99BHACHYHv6XJ3w3AAAAACOGsUmj"
api_version = "2024-12-01-preview"

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

def test_summarization():
    prompt = [
        {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
        {"role": "user", "content": "Please summarize this news article: 'AI technology is rapidly advancing in healthcare, finance, and education sectors, making life easier and more efficient for everyone.'"}
    ]

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=prompt,
            max_completion_tokens=500  # removed temperature to avoid error
        )
        print("✅ Summary Result:\n")
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_summarization()
