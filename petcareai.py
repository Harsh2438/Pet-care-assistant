import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import random
from datetime import datetime
import google.generativeai as genai
from PIL import Image, ImageTk
import io

class ModernPetCareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PawTalk - AI Pet Care Companion")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)  # Set minimum window size
        
        # Set dark theme colors
        self.bg_dark = "#1e1e2e"
        self.bg_medium = "#313244"
        self.bg_light = "#45475a"
        self.accent_color = "#f38ba8"  # Pink
        self.text_color = "#cdd6f4"
        self.highlight_color = "#89b4fa"  # Blue
        self.success_color = "#a6e3a1"  # Green
        self.warning_color = "#f9e2af"  # Yellow
        self.error_color = "#f38ba8"  # Red
        
        # Configure root window
        self.root.configure(bg=self.bg_dark)
        
        # API key for Google Gemini
        self.api_key = "AIzaSyDawJ7lh8kfC0SIhJDQ5CC1j_2HXkdsDM0"  # Replace with your actual API key
        self.model_name = "gemini-1.5-pro-latest"  # Using Gemini Pro model
        
        # Initialize Gemini
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
        # User preferences
        self.user_name = "Pet Owner"
        self.pet_type = "General"
        self.pet_age = "Adult"
        self.pet_breed = "Mixed/Unknown"
        
        # Pet care data
        self.care_history = []
        self.uploaded_image = None
        
        # Setup UI components
        self.setup_ui()
        
        # Add resize binding with delay to prevent too many updates
        self.resize_id = None
        self.root.bind("<Configure>", self.on_resize)

        # Initialize conversation
        self.messages = []
        self.add_system_message("You are a specialized Pet Care Assistant with expertise in: 1) Identifying pet health issues based on symptoms, 2) Providing nutritional advice for different pets, 3) Suggesting first aid or emergency help steps, 4) Offering training and behavior guidance, 5) Recommending fun activities or games for pets, 6) Providing grooming tips and schedules, 7) Recommending pet products or services, 8) Answering questions about pet laws and regulations, 9) Sharing general information about different pets. Always prioritize pet safety and well-being in your advice. If a situation sounds serious, recommend consulting a veterinarian.")
        
        # Welcome message
        self.root.after(500, self.display_bot_message, f"👋 Hello {self.user_name}! I'm your PawTalk AI assistant. I can help you with pet health issues, nutrition advice, first aid guidance, training tips, and more. What type of pet do you have?")
    def clear_chat_history(self):
    # Ask for confirmation
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the chat history?"):
        # Clear the chat display
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
        
        # Keep only system message and reset others
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        self.messages = system_messages
        
        # Clear uploaded image
        self.uploaded_image = None
        self.image_label.config(image="", text="No image uploaded")
        if hasattr(self.image_label, 'image'):
            del self.image_label.image
        
        # Display a system message
        self.display_system_message("Chat history has been cleared")
        
        # Display welcome message again
        self.root.after(500, self.display_bot_message, f"👋 Hello {self.user_name}! I'm your PawTalk AI assistant. I can help you with pet health issues, nutrition advice, first aid guidance, training tips, and more. What type of pet do you have?")
        
        # Display welcome message again
        self.root.after(500, self.display_bot_message, f"👋 Hello {self.user_name}! I'm your PawTalk AI assistant. I can help you with pet health issues, nutrition advice, first aid guidance, training tips, and more. What type of pet do you have?")
    def setup_ui(self):
        # Create style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure ttk styles
        self.style.configure('TNotebook', background=self.bg_dark, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.bg_medium, foreground=self.text_color, 
                            padding=[20, 10], font=('Helvetica', 12))
        self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)], 
                      foreground=[('selected', self.bg_dark)])
        
        self.style.configure('TFrame', background=self.bg_dark)
        self.style.configure('TButton', background=self.accent_color, foreground=self.bg_dark, 
                            font=('Helvetica', 11, 'bold'), padding=10)
        self.style.map('TButton', background=[('active', self.highlight_color)])
        
        self.style.configure('TLabel', background=self.bg_dark, foreground=self.text_color, 
                            font=('Helvetica', 12))
        self.style.configure('TEntry', fieldbackground=self.bg_light, foreground=self.text_color, 
                            font=('Helvetica', 12))
        self.style.configure('TCombobox', fieldbackground=self.bg_light, foreground=self.bg_dark, 
                            font=('Helvetica', 12))
        
        # Create main container with padding that adjusts based on window size
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Make the main frame responsive
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Header
        self.main_frame.rowconfigure(1, weight=1)  # Notebook
        
        # Create header with logo
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)  # Middle space expands
        
        # App title/logo
        title_label = tk.Label(header_frame, text="🐾 PawTalk", 
                              font=('Helvetica', 24, 'bold'), 
                              bg=self.bg_dark, fg=self.accent_color)
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = tk.Label(header_frame, text="AI Pet Care Companion", 
                                 font=('Helvetica', 14), 
                                 bg=self.bg_dark, fg=self.text_color)
        subtitle_label.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(10, 0))
        
        # Settings button
        settings_button = ttk.Button(header_frame, text="⚙️ Settings", 
                                    command=self.open_settings)
        settings_button.grid(row=0, column=2, sticky="e")
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Create Chat tab
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="💬 Chat")
        
        # Create Pet Types tab
        self.pet_types_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pet_types_tab, text="🐶 Pet Types")
        
        # Create Care Categories tab
        self.categories_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_tab, text="🩺 Care Categories")
        
        # Setup each tab
        self.setup_chat_tab()
        self.setup_pet_types_tab()
        self.setup_categories_tab()
        
    def on_resize(self, event):
        # Cancel the previous resize event if it exists
        if self.resize_id:
            self.root.after_cancel(self.resize_id)
        
        # Schedule a new resize event with a delay
        self.resize_id = self.root.after(100, lambda: self.update_layout(event.width, event.height))
    
    def update_layout(self, width, height):
        # Reset the resize ID
        self.resize_id = None
        
        # Print dimensions for debugging
        print(f"Window resized to {width}x{height}")
        
        # Adjust font sizes based on window width
        if width < 900:
            font_size = 10
            header_size = 18
        else:
            font_size = 12
            header_size = 24
            
        # Update fonts
        self.style.configure('TNotebook.Tab', font=('Helvetica', font_size))
        self.style.configure('TButton', font=('Helvetica', font_size - 1, 'bold'))
        self.style.configure('TLabel', font=('Helvetica', font_size))
    
    def setup_chat_tab(self):
        # Create chat container with grid layout for better responsiveness
        self.chat_tab.columnconfigure(0, weight=1)
        self.chat_tab.rowconfigure(0, weight=1)  # Chat display
        self.chat_tab.rowconfigure(1, weight=0)  # Image upload area
        self.chat_tab.rowconfigure(2, weight=0)  # Input area
        self.chat_tab.rowconfigure(3, weight=0)  # Status bar
        
        # Chat display area
        chat_display_frame = ttk.Frame(self.chat_tab)
        chat_display_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        chat_display_frame.columnconfigure(0, weight=1)
        chat_display_frame.rowconfigure(0, weight=1)
        
        # Chat display with custom colors
        self.chat_display = scrolledtext.ScrolledText(
            chat_display_frame, 
            wrap=tk.WORD,
            bg=self.bg_medium,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            selectforeground=self.bg_dark,
            font=('Helvetica', 12),
            padx=15,
            pady=15
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for text styling
        self.chat_display.tag_configure("user_tag", foreground=self.highlight_color, font=('Helvetica', 12, 'bold'))
        self.chat_display.tag_configure("user_message", foreground=self.text_color, font=('Helvetica', 12))
        self.chat_display.tag_configure("bot_tag", foreground=self.accent_color, font=('Helvetica', 12, 'bold'))
        self.chat_display.tag_configure("bot_message", foreground=self.text_color, font=('Helvetica', 12))
        self.chat_display.tag_configure("system", foreground=self.warning_color, font=('Helvetica', 10, 'italic'))
        self.chat_display.tag_configure("emergency", foreground=self.error_color, font=('Helvetica', 12, 'bold'))
        # Add Clear History button
        clear_history_button = ttk.Button(
        chat_display_frame, 
        text="🗑️ Clear History",
        command=self.clear_chat_history
        )
        clear_history_button.grid(row=0, column=0, sticky="ne", padx=5, pady=5)
        # Image upload area with modern styling
        image_frame = ttk.Frame(self.chat_tab)
        image_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        image_frame.columnconfigure(1, weight=1)  # Make the label expandable
        
        upload_button = ttk.Button(
            image_frame, 
            text="📷 Upload Pet Image",
            command=self.upload_image
        )
        upload_button.grid(row=0, column=0, sticky="w")
        
        self.image_label = ttk.Label(image_frame, text="No image uploaded")
        self.image_label.grid(row=0, column=1, sticky="ew", padx=10)
        
        # Input area with modern styling - using grid for better control
        input_frame = ttk.Frame(self.chat_tab)
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)  # Make input field expandable
        
        # Message input field with custom colors - ENSURE MINIMUM HEIGHT
        self.message_input = tk.Text(
            input_frame, 
            height=3,  # Set a fixed minimum height
            bg=self.bg_light,
            fg=self.text_color,
            insertbackground=self.text_color,
            font=('Helvetica', 12),
            wrap=tk.WORD,
            padx=15,
            pady=15,
            relief=tk.FLAT
        )
        self.message_input.grid(row=0, column=0, sticky="ew")
        self.message_input.bind("<Return>", self.send_on_enter)
        
        # Placeholder text
        self.message_input.insert("1.0", "Ask about your pet's care...")
        self.message_input.bind("<FocusIn>", self.clear_placeholder)
        self.message_input.bind("<FocusOut>", self.add_placeholder)
        
        # Send button
        send_button = ttk.Button(
            input_frame, 
            text="Send",
            command=self.send_message
        )
        send_button.grid(row=0, column=1, sticky="ns")
        
        # Status bar with modern styling
        self.status_bar = tk.Label(
            self.chat_tab, 
            text="Ready to help with pet care",
            bg=self.bg_light,
            fg=self.text_color,
            font=('Helvetica', 10),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
    
    def setup_pet_types_tab(self):
        # Create a responsive frame with grid layout for pet type cards
        pet_types_frame = ttk.Frame(self.pet_types_tab)
        pet_types_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid with weights
        for i in range(3):  # 3 columns
            pet_types_frame.columnconfigure(i, weight=1)
        for i in range(2):  # number of rows, update if more
            pet_types_frame.rowconfigure(i, weight=1)
        
        # Pet types with emojis and descriptions
        pet_types = [
            ("🐕 Dogs", "Man's best friend", "Dogs"),
            ("🐈 Cats", "Independent companions", "Cats"),
            ("🐦 Birds", "Feathered friends", "Birds"),
            ("🐠 Fish", "Aquatic pets", "Fish"),
            ("🐹 Small Pets", "Pocket-sized companions", "Small Pets"),
            ("🦎 Reptiles", "Cold-blooded friends", "Reptiles")
        ]
        
        # Create a card for each pet type
        for i, (title, desc, pet_type) in enumerate(pet_types):
            row = i // 3
            col = i % 3
            
            # Create card frame
            card = tk.Frame(pet_types_frame, bg=self.bg_medium, padx=15, pady=15, relief=tk.FLAT)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Add title
            title_label = tk.Label(card, text=title, font=('Helvetica', 16, 'bold'), 
                                  bg=self.bg_medium, fg=self.accent_color)
            title_label.pack(anchor="w", pady=(0, 5))
            
            # Add description
            desc_label = tk.Label(card, text=desc, font=('Helvetica', 12), 
                                 bg=self.bg_medium, fg=self.text_color)
            desc_label.pack(anchor="w", pady=(0, 15))
            
            # Add select button
            select_btn = tk.Button(card, text="Select", font=('Helvetica', 11), 
                                  bg=self.accent_color, fg=self.bg_dark, 
                                  command=lambda p=pet_type: self.change_pet_type(p),
                                  padx=10, pady=5, relief=tk.FLAT)
            select_btn.pack(anchor="w")
    
    def setup_categories_tab(self):
        # Create a more responsive frame with grid layout for category cards
        categories_frame = ttk.Frame(self.categories_tab)
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid with weights
        for i in range(2):  # 2 columns
            categories_frame.columnconfigure(i, weight=1)
        for i in range(4):  # 4 rows
            categories_frame.rowconfigure(i, weight=1)
        
        # Care categories with icons and descriptions
        categories = [
            ("🩺 Health Issues", "Common problems & symptoms", self.health_issues),
            ("🍖 Nutrition", "Diet & feeding advice", self.nutrition_advice),
            ("🚑 First Aid", "Emergency care guidance", self.first_aid),
            ("🦮 Training", "Behavior & training tips", self.training_tips),
            ("🎮 Activities", "Fun games & exercises", self.fun_activities),
            ("✂️ Grooming", "Coat, nail & dental care", self.grooming_tips),
            ("🛒 Products", "Recommended pet supplies", self.product_recommendations)
        ]
        
        # Create a card for each category
        for i, (title, desc, command) in enumerate(categories):
            row = i // 2
            col = i % 2
            
            # Create card frame
            card = tk.Frame(categories_frame, bg=self.bg_medium, padx=15, pady=15, relief=tk.FLAT)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Add title
            title_label = tk.Label(card, text=title, font=('Helvetica', 16, 'bold'), 
                                  bg=self.bg_medium, fg=self.highlight_color)
            title_label.pack(anchor="w", pady=(0, 5))
            
            # Add description
            desc_label = tk.Label(card, text=desc, font=('Helvetica', 12), 
                                 bg=self.bg_medium, fg=self.text_color)
            desc_label.pack(anchor="w", pady=(0, 15))
            
            # Add select button
            select_btn = tk.Button(card, text="Get Advice", font=('Helvetica', 11), 
                                  bg=self.highlight_color, fg=self.bg_dark, 
                                  command=command,
                                  padx=10, pady=5, relief=tk.FLAT)
            select_btn.pack(anchor="w")
    
    def clear_placeholder(self, event):
        if self.message_input.get("1.0", "end-1c") == "Ask about your pet's care...":
            self.message_input.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        if not self.message_input.get("1.0", "end-1c").strip():
            self.message_input.insert("1.0", "Ask about your pet's care...")
    
    def send_on_enter(self, event):
        if not event.state & 0x1:  # Check if Shift key is not pressed
            self.send_message()
            return "break"
    
    def send_message(self):
        user_message = self.message_input.get("1.0", tk.END).strip()
        if not user_message or user_message == "Ask about your pet's care...":
            return
        
        # Clear input field
        self.message_input.delete("1.0", tk.END)
        
        # Switch to chat tab if not already there
        self.notebook.select(0)
        
        # Display user message
        self.display_user_message(user_message)
        
        # Add to messages
        self.add_user_message(user_message)
        
        # Update status
        self.status_bar.config(text="Thinking...")
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})
    
    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
    
    def get_ai_response(self):
        try:
            if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
                response_text = "Please set your Google Gemini API key in the settings to enable AI responses."
            else:
                # Prepare context with pet information
                context = f"Pet type: {self.pet_type}. Pet age: {self.pet_age}. Pet breed: {self.pet_breed}."
                
                # Add context to the last user message
                if len(self.messages) > 0 and self.messages[-1]["role"] == "user":
                    self.messages[-1]["content"] += f"\n\n[Context: {context}]"
                
                # Convert messages to Gemini format
                chat = self.model.start_chat(history=[])
                
                # Combine all previous messages into a single prompt for Gemini
                prompt = ""
                for msg in self.messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n"
                    elif msg["role"] == "user":
                        prompt += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        prompt += f"Assistant: {msg['content']}\n"
                
                # Include image if available
                if self.uploaded_image:
                    response = chat.send_message([prompt, self.uploaded_image])
                    # Clear the image after using it
                    self.uploaded_image = None
                    self.root.after(0, lambda: self.image_label.config(text="No image uploaded"))
                else:
                    response = chat.send_message(prompt)
                
                response_text = response.text
                
                # Add the response to messages
                self.add_assistant_message(response_text)
                
                # Log the interaction for care history
                self.care_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pet_type": self.pet_type,
                    "interaction": {
                        "user": self.messages[-2]["content"],
                        "assistant": response_text
                    }
                })
            
            # Update status and display response
            self.root.after(0, lambda: self.status_bar.config(text=f"Pet type: {self.pet_type} | Age: {self.pet_age}"))
            self.root.after(0, self.display_bot_message, response_text)
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.root.after(0, lambda: self.status_bar.config(text="Error occurred"))
            self.root.after(0, self.display_bot_message, error_message)
    
    def display_user_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{self.user_name}: ", "user_tag")
        self.chat_display.insert(tk.END, f"{message}\n\n", "user_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_bot_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "PawTalk: ", "bot_tag")
        
        # Check for emergency keywords to highlight
        emergency_keywords = ["emergency", "urgent", "immediately", "vet", "veterinarian", "danger", "toxic", "poisonous"]
        
        # Split message by lines to check each line for emergency content
        lines = message.split('\n')
        for i, line in enumerate(lines):
            has_emergency = any(keyword in line.lower() for keyword in emergency_keywords)
            
            if has_emergency:
                self.chat_display.insert(tk.END, f"{line}\n", "emergency")
            else:
                self.chat_display.insert(tk.END, f"{line}\n", "bot_message")
            
            # Add an extra newline after the last line
            if i == len(lines) - 1:
                self.chat_display.insert(tk.END, "\n", "bot_message")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_system_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"System: {message}\n\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def change_pet_type(self, pet_type):
        self.pet_type = pet_type
        self.status_bar.config(text=f"Pet type: {pet_type} | Age: {self.pet_age}")
        
        # Switch to chat tab
        self.notebook.select(0)
        
        self.display_system_message(f"Pet type changed to {pet_type}")
        
        # Inform the AI about the pet type change
        prompt = f"The user has a {pet_type} pet. Please provide a brief introduction to {pet_type} care and suggest some key aspects of {pet_type} care that owners should be aware of."
        self.add_user_message(prompt)
        
        # Process in a separate thread
        threading.Thread(target=self.get_ai_response, daemon=True).start()
    
    def open_settings(self):
        # Create settings popup with modern styling - now more responsive
        settings_window = tk.Toplevel(self.root)
        settings_window.title("PawTalk Settings")
        settings_window.geometry("450x550")
        settings_window.minsize(350, 500)  # Set minimum size
        settings_window.configure(bg=self.bg_dark)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings container
        settings_frame = tk.Frame(settings_window, bg=self.bg_dark, padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Make the settings frame responsive
        settings_frame.columnconfigure(0, weight=1)
        
        # Settings title
        title_label = tk.Label(settings_frame, text="Settings", 
                              font=('Helvetica', 20, 'bold'), 
                              bg=self.bg_dark, fg=self.accent_color)
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # API Key
        api_label = tk.Label(settings_frame, text="Google Gemini API Key:", 
                            font=('Helvetica', 12, 'bold'), 
                            bg=self.bg_dark, fg=self.text_color, anchor="w")
        api_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        api_entry = tk.Entry(settings_frame, font=('Helvetica', 12), show="*",
                            bg=self.bg_light, fg=self.text_color, insertbackground=self.text_color,
                            relief=tk.FLAT, bd=0, highlightthickness=1, 
                            highlightcolor=self.accent_color, highlightbackground=self.bg_light)
        api_entry.grid(row=2, column=0, sticky="ew", ipady=8, pady=(0, 20))
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
            api_entry.insert(0, self.api_key)
        
        # User Name
        name_label = tk.Label(settings_frame, text="Your Name:", 
                             font=('Helvetica', 12, 'bold'), 
                             bg=self.bg_dark, fg=self.text_color, anchor="w")
        name_label.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        name_entry = tk.Entry(settings_frame, font=('Helvetica', 12),
                             bg=self.bg_light, fg=self.text_color, insertbackground=self.text_color,
                             relief=tk.FLAT, bd=0, highlightthickness=1, 
                             highlightcolor=self.accent_color, highlightbackground=self.bg_light)
        name_entry.grid(row=4, column=0, sticky="ew", ipady=8, pady=(0, 20))
        name_entry.insert(0, self.user_name)
        
        # Pet Age
        age_label = tk.Label(settings_frame, text="Pet Age:", 
                            font=('Helvetica', 12, 'bold'), 
                            bg=self.bg_dark, fg=self.text_color, anchor="w")
        age_label.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        
        age_var = tk.StringVar(value=self.pet_age)
        age_options = ["Puppy/Kitten", "Young", "Adult", "Senior"]
        
        age_frame = tk.Frame(settings_frame, bg=self.bg_dark)
        age_frame.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        
        for i, age in enumerate(age_options):
            rb = tk.Radiobutton(age_frame, text=age, variable=age_var, value=age,
                               font=('Helvetica', 12), 
                               bg=self.bg_dark, fg=self.text_color, 
                               selectcolor=self.bg_medium, 
                               activebackground=self.bg_dark, activeforeground=self.accent_color)
            rb.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0))
        
        # Pet Breed
        breed_label = tk.Label(settings_frame, text="Pet Breed (optional):", 
                             font=('Helvetica', 12, 'bold'), 
                             bg=self.bg_dark, fg=self.text_color, anchor="w")
        breed_label.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        
        breed_entry = tk.Entry(settings_frame, font=('Helvetica', 12),
                             bg=self.bg_light, fg=self.text_color, insertbackground=self.text_color,
                             relief=tk.FLAT, bd=0, highlightthickness=1, 
                             highlightcolor=self.accent_color, highlightbackground=self.bg_light)
        breed_entry.grid(row=8, column=0, sticky="ew", ipady=8, pady=(0, 20))
        breed_entry.insert(0, self.pet_breed)
        
        # Theme Mode
        theme_label = tk.Label(settings_frame, text="Theme:", 
                             font=('Helvetica', 12, 'bold'), 
                             bg=self.bg_dark, fg=self.text_color, anchor="w")
        theme_label.grid(row=9, column=0, sticky="ew", pady=(0, 5))
        
        theme_var = tk.StringVar(value="Dark")
        theme_options = ["Dark", "Light"]
        
        theme_frame = tk.Frame(settings_frame, bg=self.bg_dark)
        theme_frame.grid(row=10, column=0, sticky="ew", pady=(0, 20))
        
        for i, theme in enumerate(theme_options):
            rb = tk.Radiobutton(theme_frame, text=theme, variable=theme_var, value=theme,
                               font=('Helvetica', 12), 
                               bg=self.bg_dark, fg=self.text_color, 
                               selectcolor=self.bg_medium, 
                               activebackground=self.bg_dark, activeforeground=self.accent_color)
            rb.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0))
        
        # Save button - Bottom of form with some space
        save_button = tk.Button(settings_frame, text="Save Settings", 
                                font=('Helvetica', 12, 'bold'),
                                bg=self.accent_color, fg=self.bg_dark,  
                                relief=tk.FLAT, padx=20, pady=10,
                                command=lambda: self.save_settings(
                                    api_entry.get(), 
                                    name_entry.get(), 
                                    age_var.get(), 
                                    breed_entry.get(),
                                    theme_var.get(),
                                    settings_window))
        save_button.grid(row=11, column=0, sticky="w", pady=(20, 0))
    
    def save_settings(self, api_key, user_name, pet_age, pet_breed, theme, window):
        # Update instance variables
        if api_key and api_key != self.api_key:
            self.api_key = api_key
            # Reinitialize Gemini with new API key
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
        self.user_name = user_name if user_name else "Pet Owner"
        self.pet_age = pet_age
        self.pet_breed = pet_breed if pet_breed else "Mixed/Unknown"
        
        # Update theme (placeholder for future expansion)
        # Would need to implement theme switching logic
        
        # Update status bar with new pet information
        self.status_bar.config(text=f"Pet type: {self.pet_type} | Age: {self.pet_age}")
        
        # Save settings to file for persistence
        self.save_settings_to_file()
        
        # Close settings window
        window.destroy()
        
        # Confirmation message
        self.display_system_message("Settings updated successfully")
    
    def save_settings_to_file(self):
        """Save settings to JSON file for persistence"""
        settings = {
            "api_key": self.api_key,
            "user_name": self.user_name,
            "pet_type": self.pet_type,
            "pet_age": self.pet_age,
            "pet_breed": self.pet_breed,
            "care_history": self.care_history
        }
        
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/settings.json', 'w') as file:
                json.dump(settings, file)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings_from_file(self):
        """Load settings from JSON file if available"""
        try:
            if os.path.exists('data/settings.json'):
                with open('data/settings.json', 'r') as file:
                    settings = json.load(file)
                
                self.api_key = settings.get("api_key", self.api_key)
                self.user_name = settings.get("user_name", self.user_name)
                self.pet_type = settings.get("pet_type", self.pet_type)
                self.pet_age = settings.get("pet_age", self.pet_age)
                self.pet_breed = settings.get("pet_breed", self.pet_breed)
                self.care_history = settings.get("care_history", self.care_history)
                
                # Reinitialize Gemini with loaded API key
                if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
                    genai.configure(api_key=self.api_key)
                    self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def upload_image(self):
        """Handle pet image upload for AI analysis"""
        file_path = filedialog.askopenfilename(
            title="Select Pet Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        
        if file_path:
            try:
                # Open and resize image
                img = Image.open(file_path)
                img.thumbnail((300, 300))  # Resize for display
                
                # Display thumbnail
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep reference
                
                # Store original image for AI processing
                self.uploaded_image = img
                
                # Notify user
                self.display_system_message(f"Image uploaded. Ask a question about your pet with this image.")
                
                # Switch to chat tab
                self.notebook.select(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    # Care category functions for category tab buttons
    def health_issues(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What are common health issues for {self.pet_type.lower()}?")
        self.send_message()
    
    def nutrition_advice(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What should I feed my {self.pet_age.lower()} {self.pet_type.lower()}? What's a healthy diet?")
        self.send_message()
    
    def first_aid(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What basic first aid supplies should I have for my {self.pet_type.lower()}? How do I handle common emergencies?")
        self.send_message()
    
    def training_tips(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What are some effective training techniques for {self.pet_type.lower()}?")
        self.send_message()
    
    def fun_activities(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What are some fun activities or games I can do with my {self.pet_type.lower()}?")
        self.send_message()
    
    def grooming_tips(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What's a good grooming routine for a {self.pet_breed} {self.pet_type.lower()}?")
        self.send_message()
    
    def product_recommendations(self):
        self.notebook.select(0)  # Switch to chat tab
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", f"What are essential products and supplies I should have for my {self.pet_type.lower()}?")
        self.send_message()

# Main function to run the application
def main():
    root = tk.Tk()
    app = ModernPetCareApp(root)
    
    # Load settings if available
    app.load_settings_from_file()
    
    # Set window icon (commented out as icon file not provided)
    # root.iconphoto(True, tk.PhotoImage(file="icon.png"))
    
    root.mainloop()

if __name__ == "__main__":
    main()
