import random

#Dictionary 
DIFFICULTY_LEVELS = {
    "Easy":   {"ops": ["+", "-"],           "range": (1, 10)},
    "Medium": {"ops": ["+", "-", "*"],      "range": (2, 12)},
    "Hard":   {"ops": ["+", "-", "*", "/"], "range": (3, 15)},
}

#Functions
def _compute(a: int, b: int, op: str) -> int:
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/": return a // b  
    return 0

def generate_question(level: str = "Easy"):
    cfg = DIFFICULTY_LEVELS.get(level, DIFFICULTY_LEVELS["Easy"])
    a = random.randint(*cfg["range"])
    b = random.randint(*cfg["range"])
    op = random.choice(cfg["ops"])

    # Make division clean: ensure a is a multiple of b
    if op == "/":
        b = random.randint(*cfg["range"])
        a = a * b  # guarantees integer result

    expr = f"{a} {op} {b}"
    ans = _compute(a, b, op)
    return expr, ans

REWARD_OUTCOMES = [1, 3, 5]
REWARD_WEIGHTS  = [0.50, 0.40, 0.10]  

def draw_reward():
    reward = random.choices(REWARD_OUTCOMES, weights=REWARD_WEIGHTS, k=1)[0]
    return reward


import tkinter as tk
from tkinter import ttk, messagebox
from core import DIFFICULTY_LEVELS, generate_question, draw_reward

    
BIG_FONT = ("Segoe UI", 14)
TITLE_FONT = ("Segoe UI", 18, "bold")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aura Maths — Uncertain Rewards")
        self.geometry("720x480")
        self.resizable(False, False)

        # Game state (dictionary)
        self.state = {
            "attempts": 0,
            "correct": 0,
            "coins": 0,
            "history": []  # each item: {"q": str, "given": str, "ok": bool, "coins": int}
        }

        # UI state
        self.current_level = tk.StringVar(value="Easy")
        self.current_q = None
        self.current_ans = None

        # Layout containers
        self.header = tk.Frame(self, pady=8)
        self.header.pack(fill="x")
        self.body = tk.Frame(self, padx=16, pady=10)
        self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self, pady=8)
        self.footer.pack(fill="x")

        # Header contents
        tk.Label(self.header, text="Aura Maths", font=TITLE_FONT).pack(anchor="center", padx=0,)
        self.stats_lbl = tk.Label(self.header, text=self._stats_text(), font=BIG_FONT)
        self.stats_lbl.pack(side="right", padx=10)

        # Screens
        self.screens = {}
        for name in ("home", "difficulty", "practice", "results"):
            self.screens[name] = tk.Frame(self.body)

        self._build_home()
        self._build_difficulty()
        self._build_practice()
        self._build_results()

        # Footer buttons
        tk.Button(self.footer, text="Reset Session", font=BIG_FONT, command=self._reset_session).pack(side="left", padx=6)
        tk.Button(self.footer, text="Quit", font=BIG_FONT, command=self.destroy).pack(side="right", padx=6)

        self._show("home")

    # ---------- Builders ----------
    def _build_home(self):
        f = self.screens["home"]
        
        tk.Button(f, text="Choose Difficulty", font=BIG_FONT,
          command=lambda: self._show("difficulty")).pack(pady=6)

        self.home_info = tk.Label(f, text=self._stats_text(long=True), font=("Segoe UI", 16), justify="left")
        self.home_info.pack(pady=6)

    def _build_difficulty(self):
        f = self.screens["difficulty"]
        tk.Label(f, text="Choose difficulty and start practice.", font=BIG_FONT).pack(pady=10)

        dd = tk.OptionMenu(f, self.current_level, *DIFFICULTY_LEVELS.keys())
        dd.config(font=BIG_FONT)
        dd.pack(pady=8)

        self.message_text = tk.StringVar()
        self.message_text.set("Easy only inculdes + & - \n Medium only inculdes +, - & x \n Hard inculdes +, -, x & ÷.")

        ttk.Label(f, textvariable=self.message_text, justify = "left", wraplength = 500).pack(pady=4, anchor="center")

        ttk.Button(f, text="Start Practice",
                   command=self._start_practice).pack(pady=10)
        ttk.Button(f, text="Back",
                   command=lambda: self._show("home")).pack()

    def _build_practice(self):

        f = self.screens["practice"]
    
        self.q_lbl = tk.Label(f, text="Solve: —", font=TITLE_FONT)
        self.q_lbl.pack(pady=8)

        # Answer entry
        self.answer_var = tk.StringVar()
        entry = tk.Entry(f, textvariable=self.answer_var, font=BIG_FONT, width=14, justify="center")
        entry.pack(pady=10)
        entry.bind("<Return>", lambda _e: self._submit_answer())

        # Buttons row
        row = tk.Frame(f)
        row.pack(pady=6)
        tk.Button(row, text="Submit", font=BIG_FONT, command=self._submit_answer).pack(side="left", padx=6)
        tk.Button(row, text="Skip", font=BIG_FONT, command=self._next_question).pack(side="left", padx=6)
        tk.Button(row, text="Finish", font=BIG_FONT, command=lambda: self._show("results")).pack(side="left", padx=6)

        self.feedback_lbl = tk.Label(f, text="", font=BIG_FONT)
        self.feedback_lbl.pack(pady=8)

    def _build_results(self):
        f = self.screens["results"]
        tk.Label(f, text="Session Summary", font=TITLE_FONT).pack(pady=10)

        self.results_text = tk.Text(f, height=12, width=80, font=("Consolas", 12))
        self.results_text.pack(pady=4)

        tk.Button(f, text="Back to Home", font=BIG_FONT, command=lambda: self._show("home")).pack(pady=8)

    # ---------- Navigation ----------
    def _show(self, name):
        for n, frame in self.screens.items():
            frame.pack_forget()
        self.screens[name].pack(fill="both", expand=True)
        self._refresh()

    # ---------- Stats helpers ----------
    def _stats_text(self, long=False):
        
        s = self.state
        acc = (s["correct"]/s["attempts"]*100) if s["attempts"] else 0
        base = f"Coins: {s['coins']}  |  Attempts: {s['attempts']}  |  Correct: {s['correct']}  |  Accuracy: {acc:.0f}%"
        if not long:
            return base
       

    def _refresh(self):
        self.stats_lbl.config(text=self._stats_text())

        if self.screens.get("home") and self.screens["home"].winfo_ismapped():
            self.home_info.config(text=self._stats_text(long=True))

        if self.screens.get("results") and self.screens["results"].winfo_ismapped():
            self._render_results()

    # ---------- Flow ----------
    def _start_practice(self):
        self._show("practice")
        self._next_question()

    def _next_question(self):
        level = self.current_level.get()
        q, a = generate_question(level)
        print("DEBUG:", level, "->", q, a)   # <-- should print something like: Easy -> 3 + 4 7
        self.current_q, self.current_ans = q, a
        self.current_q, self.current_ans = generate_question(level)
        self.q_lbl.config(text=f"Solve:  {self.current_q}")
        self.answer_var.set("")
        self.feedback_lbl.config(text="", fg="#006400")

    def _submit_answer(self):
        if self.current_q is None:
            return

        raw = self.answer_var.get().strip()
        if raw == "":
            messagebox.showinfo("Enter an answer", "Please type your answer.")
            return

        # Update attempts
        self.state["attempts"] += 1

        # Validate number
        try:
            given = int(raw)
        except ValueError:
            self.feedback_lbl.config(text="Please enter a whole number.", fg="#8B0000")
            return

        # Check correctness
        if given == self.current_ans:
            self.state["correct"] += 1
            reward = draw_reward()
            self.state["coins"] += reward
            self.feedback_lbl.config(text=f"Correct! +{reward} coin(s) YAY! 🎉", fg="#006400")
        else:
            self.feedback_lbl.config(text=f"Not quite. Correct answer: {self.current_ans}", fg="#8B0000")

        # Record history
        self.state["history"].append({
            "q": self.current_q,
            "given": raw,
            "ok": (given == self.current_ans),
            "coins": reward if (given == self.current_ans) else 0
        })

        self._refresh()
        # brief pause then next question
        self.after(500, self._next_question)

    def _render_results(self):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        s = self.state
        acc = (s["correct"]/s["attempts"]*100) if s["attempts"] else 0
        summary = [
            f"Coins: {s['coins']}",
            f"Attempts: {s['attempts']}",
            f"Correct: {s['correct']}",
            f"Accuracy: {acc:.1f}%",
            "",
            "Recent Answers:"
        ]
        self.results_text.insert("end", "\n".join(summary) + "\n")
        for h in self.state["history"][-15:]:
            self.results_text.insert("end", f"{h['q']} → {h['given']} | {'✓' if h['ok'] else '✗'} | +{h['coins']}c\n")
        self.results_text.config(state="disabled")

    def _reset_session(self):
        if messagebox.askyesno("Confirm", "Reset current session stats?"):
            self.state = {"attempts": 0, "correct": 0, "coins": 0, "history": []}
            self._refresh()
            if self.screens["practice"].winfo_ismapped():
                self._next_question()

if __name__ == "__main__":
    app = App()
    app.mainloop()
