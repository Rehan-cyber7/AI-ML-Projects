import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import google.generativeai as genai

class AIQuizGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumina AI Quiz Generator")
        self.root.geometry("640x580")
        self.root.minsize(580, 485)
        
        # Configure flat tech visual theme using clam style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Elegant Dark Slate Colors Setup
        self.bg_color = "#121214"
        self.text_color = "#e4e4e7"
        self.accent_color = "#4f46e5"
        self.card_bg = "#1a1a1d"
        self.gray_border = "#2a2a32"
        
        self.root.configure(bg=self.bg_color)
        
        # Style Definitions for Dark Palette
        self.style.configure(".", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#ffffff")
        self.style.configure("Heading.TLabel", font=("Helvetica", 12, "bold"), foreground="#ffffff")
        self.style.configure("Sub.TLabel", font=("Helvetica", 9, "normal"), foreground="#a1a1aa")
        
        # Entry / Combobox overrides
        self.style.configure("TEntry", fieldbackground="#26262b", foreground="#ffffff", bordercolor=self.gray_border)
        self.style.configure("TCombobox", fieldbackground="#26262b", foreground="#ffffff", bordercolor=self.gray_border, arrowcolor=self.text_color)
        self.root.option_add("*TCombobox*Listbox.background", "#26262b")
        self.root.option_add("*TCombobox*Listbox.foreground", "#e4e4e7")
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent_color)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        
        self.style.configure("TButton", font=("Helvetica", 10, "bold"), padding=7, background="#26262b", foreground=self.text_color)
        self.style.map("TButton",
                       background=[("active", self.gray_border), ("disabled", "#18181b")],
                       foreground=[("disabled", "#52525b")])
                       
        self.style.configure("Primary.TButton", font=("Helvetica", 10, "bold"), background=self.accent_color, foreground="#ffffff", padding=7)
        self.style.map("Primary.TButton", 
                       background=[("active", "#6366f1"), ("disabled", "#1d1d2b")],
                       foreground=[("disabled", "#5c5c70")])
        
        # Option button (Radio) styling
        self.style.configure("TRadiobutton", background=self.card_bg, foreground=self.text_color, font=("Helvetica", 10), padding=4)
        self.style.map("TRadiobutton",
                       foreground=[("active", "#ffffff")],
                       background=[("active", self.card_bg)])
                       
        self.style.configure("Card.TLabelframe", background=self.card_bg, relief="solid", borderwidth=1, bordercolor=self.gray_border)
        self.style.configure("Card.TLabelframe.Label", font=("Helvetica", 9, "bold"), foreground=self.accent_color, background=self.bg_color)
        
        # Application States
        self.quiz_questions = []
        self.current_question_index = 0
        self.score = 0
        self.selected_option = tk.StringVar()
        
        # Create Core Views
        self.create_widgets()

    def create_widgets(self):
        # 1. Title/Header Region
        header_frame = ttk.Frame(self.root, padding=(20, 15, 20, 10))
        header_frame.pack(fill="x")
        
        title_label = ttk.Label(header_frame, text="AI Quiz Generator", style="Title.TLabel")
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(header_frame, text="Generates interactive multiple-choice drills powered by Gemini API", style="Sub.TLabel")
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # 2. Main Work Area (Panels)
        self.main_content = ttk.Frame(self.root, padding=20)
        self.main_content.pack(fill="both", expand=True)

        self.show_configuration_panel()

    def show_configuration_panel(self):
        # Clear existing visual workspace
        for child in self.main_content.winfo_children():
            child.destroy()

        # Config Panel Frame
        config_frame = ttk.LabelFrame(self.main_content, text=" Configuration Parameters ", style="Card.TLabelframe", padding=20)
        config_frame.pack(fill="both", expand=True)

        # Topic Entry Field
        ttk.Label(config_frame, text="Quiz Topic(s) (comma-separated):").pack(anchor="w", pady=(0, 2))
        self.topic_entry = ttk.Entry(config_frame, font=("Helvetica", 10))
        self.topic_entry.pack(fill="x", pady=(0, 12))
        self.topic_entry.insert(0, "Python Programming, React")

        # Difficulty Selector (ttk.Combobox)
        ttk.Label(config_frame, text="Difficulty Level:").pack(anchor="w", pady=(0, 2))
        self.difficulty_combo = ttk.Combobox(
            config_frame, 
            values=["Easy", "Medium", "Hard"], 
            state="readonly",
            font=("Helvetica", 10)
        )
        self.difficulty_combo.set("Medium")
        self.difficulty_combo.pack(fill="x", pady=(0, 20))

        # Action Button Frame
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill="x", side="bottom")

        self.generate_btn = ttk.Button(btn_frame, text="Generate Quiz", style="Primary.TButton", command=self.start_generation_process)
        self.generate_btn.pack(side="right", padx=(5, 0))

    def start_generation_process(self):
        topic = self.topic_entry.get().strip()
        difficulty = self.difficulty_combo.get()

        if not topic:
            messagebox.showerror("Configuration Error", "Please provide a valid topic to generate the quiz.")
            return

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            messagebox.showerror("Configuration Error", "GEMINI_API_KEY environment variable is not defined.")
            return

        self.generate_btn.configure(state="disabled", text="Generating...")
        self.topic_entry.configure(state="disabled")
        self.difficulty_combo.configure(state="disabled")

        # Spawn a background thread to prevent GUI lockup
        args = (api_key, topic, difficulty)
        threading.Thread(target=self.generate_quiz_thread, args=args, daemon=True).start()

    def generate_quiz_thread(self, api_key, topic, difficulty):
        try:
            # Configure generative AI
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Supports both single and multiple topics via comma separation
            topics = [t.strip() for t in topic.split(",") if t.strip()]
            topics_str = ", ".join(topics) if topics else topic
            
            prompt = f"""
            Generate a multiple choice quiz about the topic(s) "{topics_str}" with difficulty level "{difficulty}".
            Provide exactly 5 multiple choice questions.
            Return a JSON array of objects with the exact structure below.
            Do not wrap the response with any markdown formatting (like triple backtick json), commentary or prose. Return raw clean JSON string.
            
            [
              {{
                "question": "Example Question text remains here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option C"
              }}
            ]
            
            Make sure correct_answer matches the exact literal string of one of the options.
            """

            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            # Clean possible markdown container artifacts which models sometimes output
            for symbol in ["```json", "```", "'''json", "'''"]:
                if raw_text.startswith(symbol):
                    raw_text = raw_text[len(symbol):]
                if raw_text.endswith(symbol):
                    raw_text = raw_text[:-len(symbol)]
            raw_text = raw_text.strip()

            questions_data = json.loads(raw_text)

            # Support nested JSON structure under a "questions" key or direct array
            if isinstance(questions_data, dict) and "questions" in questions_data:
                self.quiz_questions = questions_data["questions"]
            elif isinstance(questions_data, list):
                self.quiz_questions = questions_data
            else:
                raise ValueError("Response structure is unexpected.")

            if not self.quiz_questions or len(self.quiz_questions) == 0:
                raise ValueError("No questions found in generated feedback.")

            # Schedule UI updates back onto Tkinter's main thread gracefully
            self.root.after(0, self.on_generation_success)

        except Exception as e:
            # Handle key invalidation or connection loss
            error_message = f"Failed to generate quiz: {str(e)}"
            self.root.after(0, lambda: self.on_generation_failure(error_message))

    def on_generation_success(self):
        self.current_question_index = 0
        self.score = 0
        self.show_quiz_panel()

    def on_generation_failure(self, error_message):
        messagebox.showerror("API Connection / Generation Error", error_message)
        self.generate_btn.configure(state="normal", text="Generate Quiz")
        self.api_key_entry.configure(state="normal")
        self.topic_entry.configure(state="normal")
        self.difficulty_combo.configure(state="normal")

    def show_quiz_panel(self):
        # Clear workspace
        for child in self.main_content.winfo_children():
            child.destroy()

        self.selected_option.set("") # Reset selection

        question_data = self.quiz_questions[self.current_question_index]
        
        # Card style wrapper for questions
        quiz_card = ttk.LabelFrame(
            self.main_content, 
            text=f" Question {self.current_question_index + 1} of {len(self.quiz_questions)} ", 
            style="Card.TLabelframe", 
            padding=20
        )
        quiz_card.pack(fill="both", expand=True)

        # Question text wrapper configured to handle wrapping elegantly
        q_label = ttk.Label(
            quiz_card, 
            text=question_data["question"], 
            style="Heading.TLabel", 
            wraplength=520, 
            justify="left"
        )
        q_label.pack(anchor="w", fill="x", pady=(5, 15))

        # Display Choice Radio Buttons
        for opt in question_data["options"]:
            rb = ttk.Radiobutton(
                quiz_card, 
                text=opt, 
                variable=self.selected_option, 
                value=opt
            )
            rb.pack(anchor="w", fill="x", pady=6)

        # Navigation Options and commands
        actions_frame = ttk.Frame(quiz_card)
        actions_frame.pack(fill="x", side="bottom", pady=(15, 0))

        submit_btn = ttk.Button(
            actions_frame, 
            text="Submit Answer", 
            style="Primary.TButton", 
            command=self.submit_answer
        )
        submit_btn.pack(side="right")

    def submit_answer(self):
        selected = self.selected_option.get()
        if not selected:
            messagebox.showwarning("Incomplete Selection", "Please make a selection before submitting.")
            return

        correct = self.quiz_questions[self.current_question_index]["correct_answer"]
        if selected == correct:
            self.score += 1
            messagebox.showinfo("Result", "Correct! Excellent job.")
        else:
            messagebox.showinfo("Result", f"Incorrect.\n\nThe correct answer was: {correct}")

        self.current_question_index += 1
        if self.current_question_index < len(self.quiz_questions):
            self.show_quiz_panel()
        else:
            self.show_summary_panel()

    def show_summary_panel(self):
        for child in self.main_content.winfo_children():
            child.destroy()

        summary_frame = ttk.LabelFrame(self.main_content, text=" Quiz Results ", style="Card.TLabelframe", padding=20)
        summary_frame.pack(fill="both", expand=True)

        # Center contents
        center_container = ttk.Frame(summary_frame)
        center_container.pack(expand=True)

        total = len(self.quiz_questions)
        percentage = int((self.score / total) * 100) if total > 0 else 0

        # Output feedback depending on results
        ttk.Label(center_container, text="Quiz Completed!", style="Title.TLabel").pack(pady=(0, 10))
        
        score_text = f"You Scored: {self.score} / {total}"
        ttk.Label(center_container, text=score_text, style="Heading.TLabel").pack(pady=5)
        
        percent_label = ttk.Label(center_container, text=f"{percentage}%", font=("Helvetica", 24, "bold"), foreground=self.accent_color)
        percent_label.pack(pady=8)

        status_text = "Review completed. Try another topic to keep practicing!"
        if percentage >= 80:
            status_text = "Mastery Level! Outstanding understanding of the material."
        elif percentage >= 60:
            status_text = "Good job! Keep reviewing to gain full mastery."
            
        ttk.Label(center_container, text=status_text, style="TLabel", font=("Helvetica", 10)).pack(pady=(5, 15))

        btn = ttk.Button(center_container, text="Create New Quiz", style="Primary.TButton", command=self.show_configuration_panel)
        btn.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIQuizGeneratorApp(root)
    root.mainloop()