import subprocess

def ask_ollama(prompt: str, model="llama3"):
    """
        Sends a prompt to a local Ollama and returns the response text.
        Requires Ollama to be running locally.
    """

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            check=True
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print("Ollama error: ", e.stderr.decode())
        return None
    
if __name__ == "__main__":
    response = ask_ollama("Nexcai, tell me a quote about discipline.")
    print("Nexcai:", response)