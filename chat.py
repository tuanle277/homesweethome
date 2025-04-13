import os
import pandas as pd
from pathlib import Path
import ollama
import google.generativeai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font
from datetime import datetime
import json
import sqlite3
import threading
import queue

# Configure Gemini API key - you'll need to set this in your environment
# Load API key from .env file
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in .env file")
genai.configure(api_key=GOOGLE_API_KEY)

def init_db():
    """Initialize SQLite database for chat history"""
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                 (id INTEGER PRIMARY KEY, name TEXT, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, 
                  session_id INTEGER,
                  content TEXT,
                  is_user BOOLEAN,
                  timestamp TIMESTAMP,
                  FOREIGN KEY (session_id) REFERENCES chat_sessions(id))''')
    conn.commit()
    conn.close()

def load_data_context():
    """Load and combine all Excel files from data/ directory"""
    data_dir = Path("data")
    context = []
    for excel_file in data_dir.glob("*.xlsx"):
        df = pd.read_excel(excel_file)
        context.append(f"Data from {excel_file.name}:\n{df.to_string()}")
    return "\n\n".join(context)

def stream_gemini_response(prompt, context, queue):
    """Stream response from Gemini model"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    full_prompt = f"""Context:
        {context}

        User Question: {prompt}

        Please provide your response in a clear, conversational format. Also allows up to a list of 10 properties. Avoid using markdown syntax or special formatting. Use natural paragraphs and bullet points with simple dashes (-) when needed."""
    
    response = model.generate_content(full_prompt, stream=True)
    for chunk in response:
        if chunk.text:
            queue.put(("chunk", chunk.text))
    queue.put(("done", None))

def stream_ollama_response(prompt, context, queue):
    """Stream response from Ollama model"""
    full_prompt = f"""Context:
        {context}

        User Question: {prompt}

        Please provide your response in a clear, conversational format. Also allows up to a list of 10 properties. Avoid using markdown syntax or special formatting. Use natural paragraphs and bullet points with simple dashes (-) when needed."""
    
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': full_prompt}],
        stream=True
    )
    
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            queue.put(("chunk", chunk['message']['content']))
    queue.put(("done", None))

class ChatMessage:
    def __init__(self, content, is_user=True, timestamp=None, session_id=None):
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.session_id = session_id
    
    def save_to_db(self):
        conn = sqlite3.connect('chats.db')
        c = conn.cursor()
        c.execute('''INSERT INTO messages (session_id, content, is_user, timestamp)
                    VALUES (?, ?, ?, ?)''',
                 (self.session_id, self.content, self.is_user, self.timestamp))
        conn.commit()
        conn.close()

class RealEstateAssistantUI:
    def __init__(self, root):
        init_db()
        self.root = root
        self.root.title("Real Estate Chat Assistant")
        self.root.configure(bg='#f0f0f0')
        self.context = load_data_context()
        self.current_session_id = None
        self.chat_history = []
        self.response_queue = queue.Queue()
        self.current_response_label = None
        self.current_response_text = ""
        
        # Set custom fonts and colors
        self.header_font = Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = Font(family="Helvetica", size=11)
        self.small_font = Font(family="Helvetica", size=9)
        
        # Colors
        self.user_msg_bg = "#DCF8C6"    # Light green for user messages
        self.bot_msg_bg = "#FFFFFF"      # White for bot messages
        self.chat_bg = "#ECE5DD"         # WhatsApp style background
        
        # Create main container with left sidebar and chat area
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for chat sessions
        self.sidebar_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.sidebar_frame, weight=1)
        
        # New chat button
        ttk.Button(self.sidebar_frame, text="New Chat", command=self.create_new_chat).pack(fill=tk.X, padx=5, pady=5)
        
        # Chat sessions list
        self.sessions_frame = ttk.Frame(self.sidebar_frame)
        self.sessions_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        self.load_chat_sessions()
        
        # Main chat area
        self.main_frame = ttk.Frame(self.paned_window, padding="10")
        self.paned_window.add(self.main_frame, weight=3)
        
        # Header frame
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        self.chat_title = ttk.Label(header_frame, text="Real Estate AI Assistant", font=self.header_font)
        self.chat_title.pack(side=tk.LEFT)
        
        # Model selection
        model_frame = ttk.Frame(header_frame)
        model_frame.pack(side=tk.RIGHT)
        self.model_var = tk.StringVar(value="gemini")
        ttk.Radiobutton(model_frame, text="Gemini", variable=self.model_var, value="gemini").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Ollama", variable=self.model_var, value="ollama").pack(side=tk.LEFT)
        
        # Chat display area
        self.setup_chat_area()
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create initial chat session if none exists
        if not self.current_session_id:
            self.create_new_chat()

    def setup_chat_area(self):
        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(self.chat_frame, bg=self.chat_bg)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.chat_bg)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Input area
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10,0))
        
        self.message_input = ttk.Entry(input_frame, font=self.normal_font)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        self.message_input.bind('<Return>', lambda e: self.send_message())
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, font=self.small_font)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5,0))

    def create_new_chat(self):
        """Create a new chat session"""
        conn = sqlite3.connect('chats.db')
        c = conn.cursor()
        c.execute('''INSERT INTO chat_sessions (name, created_at) 
                    VALUES (?, ?)''', (f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}", datetime.now()))
        session_id = c.lastrowid
        conn.commit()
        conn.close()
        
        self.switch_to_session(session_id)
        self.load_chat_sessions()
        
        # Add welcome message
        welcome_msg = ChatMessage("Hello! I'm your Real Estate Assistant. How can I help you today?", False, session_id=session_id)
        welcome_msg.save_to_db()
        self.display_message(welcome_msg)

    def load_chat_sessions(self):
        """Load and display all chat sessions in sidebar"""
        # Clear existing sessions
        for widget in self.sessions_frame.winfo_children():
            widget.destroy()
            
        conn = sqlite3.connect('chats.db')
        c = conn.cursor()
        c.execute('SELECT id, name, created_at FROM chat_sessions ORDER BY created_at DESC')
        sessions = c.fetchall()
        conn.close()
        
        for session in sessions:
            session_id, name, _ = session
            btn = ttk.Button(self.sessions_frame, 
                           text=name,
                           command=lambda sid=session_id: self.switch_to_session(sid))
            btn.pack(fill=tk.X, pady=2)

    def switch_to_session(self, session_id):
        """Switch to a different chat session"""
        self.current_session_id = session_id
        
        # Clear current chat display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Load messages for this session
        conn = sqlite3.connect('chats.db')
        c = conn.cursor()
        c.execute('''SELECT content, is_user, timestamp 
                    FROM messages 
                    WHERE session_id = ? 
                    ORDER BY timestamp''', (session_id,))
        messages = c.fetchall()
        conn.close()
        
        # Display messages
        for msg in messages:
            content, is_user, timestamp = msg
            message = ChatMessage(content, is_user, datetime.fromisoformat(timestamp), session_id)
            self.display_message(message)

    def display_message(self, message):
        """Display a message in the UI"""
        msg_container = tk.Frame(self.scrollable_frame, bg=self.chat_bg)
        msg_container.pack(fill=tk.X, padx=10, pady=5)
        
        bubble = tk.Frame(msg_container, bg=self.user_msg_bg if message.is_user else self.bot_msg_bg)
        bubble.pack(side=tk.RIGHT if message.is_user else tk.LEFT, anchor=tk.E if message.is_user else tk.W, padx=10)
        
        padding_frame = tk.Frame(bubble, bg=self.user_msg_bg if message.is_user else self.bot_msg_bg)
        padding_frame.pack(padx=10, pady=5)
        
        msg_text = tk.Label(
            padding_frame,
            text=message.content,
            wraplength=350,
            justify=tk.LEFT,
            bg=self.user_msg_bg if message.is_user else self.bot_msg_bg,
            font=self.normal_font,
            fg='black'  # Set text color to black
        )
        msg_text.pack()
        
        time_label = tk.Label(
            padding_frame,
            text=message.timestamp.strftime("%H:%M"),
            font=self.small_font,
            bg=self.user_msg_bg if message.is_user else self.bot_msg_bg,
            fg='gray'
        )
        time_label.pack(anchor=tk.E)
        
        bubble.configure(relief="raised", borderwidth=0)
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)
        
        if not message.is_user:
            self.current_response_label = msg_text

    def check_response_queue(self):
        """Check for new response chunks in the queue"""
        try:
            while True:
                msg_type, content = self.response_queue.get_nowait()
                if msg_type == "chunk":
                    self.current_response_text += content
                    if self.current_response_label:
                        self.current_response_label.configure(text=self.current_response_text)
                        self.canvas.update_idletasks()
                        self.canvas.yview_moveto(1)
                elif msg_type == "done":
                    # Save the complete response to database
                    ai_message = ChatMessage(self.current_response_text, False, session_id=self.current_session_id)
                    ai_message.save_to_db()
                    self.current_response_text = ""
                    self.current_response_label = None
                    self.status_var.set("Ready")
                    self.send_button.configure(state='normal')
                    return
        except queue.Empty:
            self.root.after(10, self.check_response_queue)

    def send_message(self):
        if not self.current_session_id:
            return
            
        query = self.message_input.get().strip()
        if not query:
            return
            
        self.message_input.delete(0, tk.END)
        
        # Add and save user message
        user_message = ChatMessage(query, True, session_id=self.current_session_id)
        user_message.save_to_db()
        self.display_message(user_message)
        
        # Create empty AI message for streaming
        ai_message = ChatMessage("", False, session_id=self.current_session_id)
        self.display_message(ai_message)
        
        self.status_var.set("Getting response...")
        self.send_button.configure(state='disabled')
        self.current_response_text = ""
        
        # Start response streaming in a separate thread
        if self.model_var.get() == "gemini":
            threading.Thread(target=stream_gemini_response, args=(query, self.context, self.response_queue)).start()
        else:
            threading.Thread(target=stream_ollama_response, args=(query, self.context, self.response_queue)).start()
        
        # Start checking for response chunks
        self.check_response_queue()

def chat():
    """Main chat application"""
    root = tk.Tk()
    root.geometry("1024x768")
    app = RealEstateAssistantUI(root)
    root.mainloop()

if __name__ == "__main__":
    chat()
