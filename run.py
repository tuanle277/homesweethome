import subprocess
import sys
import time
import os
import signal
import platform

def run_commands():
    # Start ollama serve
    print("Starting Ollama server...")
    if platform.system() == "Windows":
        ollama_process = subprocess.Popen(["ollama", "serve"], 
                                        creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        ollama_process = subprocess.Popen(["ollama", "serve"])
    
    # Wait for ollama to start
    time.sleep(3)  # Give ollama some time to initialize
    
    # Start data_call.py
    print("Starting data service...")
    if platform.system() == "Windows":
        data_process = subprocess.Popen([sys.executable, "data_call.py"],
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        data_process = subprocess.Popen([sys.executable, "data_call.py"])
    
    # Start chat.py
    print("Starting chat interface...")
    if platform.system() == "Windows":
        chat_process = subprocess.Popen([sys.executable, "chat.py"],
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        chat_process = subprocess.Popen([sys.executable, "chat.py"])
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all processes...")
        # Terminate all processes
        if platform.system() == "Windows":
            ollama_process.terminate()
            data_process.terminate()
            chat_process.terminate()
        else:
            # On Unix-like systems, send SIGTERM
            os.killpg(os.getpgid(ollama_process.pid), signal.SIGTERM)
            os.killpg(os.getpgid(data_process.pid), signal.SIGTERM)
            os.killpg(os.getpgid(chat_process.pid), signal.SIGTERM)
        
        # Wait for processes to terminate
        ollama_process.wait()
        data_process.wait()
        chat_process.wait()
        print("All processes terminated.")

if __name__ == "__main__":
    run_commands()
