import subprocess
import shutil
import sys

class LLMInterface:
    """
    A lightweight interface for local LLMs using Ollama, with streaming output.
    """

    def __init__(self, model: str = "llama3:8b"):
        self.model = model
        self.ollama_path = shutil.which("ollama") or "/usr/local/bin/ollama"

    def chat(self, prompt: str, stream: bool = False) -> str:
        """
        Sends a prompt to Ollama. If stream=True, prints the output as it comes in.
        Returns the full text response.
        """
        try:
            if stream:
                # Live-streaming mode
                process = subprocess.Popen(
                    [self.ollama_path, "run", self.model],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1  # line-buffered
                )

                # Send the prompt
                process.stdin.write(prompt)
                process.stdin.close()

                output = ""
                for line in process.stdout:
                    # Print as it arrives (without extra newline)
                    print(line, end="", flush=True)
                    output += line

                process.wait()
                return output.strip()

            else:
                # Normal blocking mode
                result = subprocess.run(
                    [self.ollama_path, "run", self.model],
                    input=prompt.encode("utf-8"),
                    capture_output=True,
                    check=True
                )
                return result.stdout.decode("utf-8").strip()

        except subprocess.CalledProcessError as e:
            print("Ollama error:", e.stderr.decode())
            return "Error: LLM call failed."
        except Exception as e:
            print("Unexpected error:", e)
            return f"Error: {e}"
