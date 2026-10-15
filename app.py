
"""Máy tính cầm tay bằng Python + tkinter.
 
Tính năng: số, + − × ÷, %, ±, 1/x, lũy thừa, căn, lượng giác (DEG/RAD),
log/ln, giai thừa, π/e, lịch sử phép tính, bộ nhớ MC/MR/M+/M-/MS.
"""
import math
import re
import tkinter as tk
 
# ---------- Bảng màu ----------
BG = "#1e1f26"
DISPLAY_BG = "#14151a"
BTN_NUM = "#2e303a"
BTN_OP = "#ff9f1c"
BTN_FUNC = "#3f4252"
BTN_MEM = "#26283a"
BTN_EQ = "#2ec4b6"
BTN_CLR = "#e63946"
FG = "#f1f1f1"
FG_DIM = "#9aa0b4"
 
 
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Máy tính cầm tay")
        self.configure(bg=BG)
        self.resizable(False, False)
 
        self.expr = ""              # biểu thức đang nhập
        self.just_evaluated = False  # vừa bấm "=" xong?
        self.deg_mode = True         # True = độ, False = radian
        self.memory = 0.0            # giá trị bộ nhớ
        self.history = []            # danh sách (biểu thức, kết quả)
 
        self._build_display()
        self._build_buttons()
        self._build_history()
        self._bind_keys()
        self._refresh()
 
    # ====================== GIAO DIỆN ======================
    def _build_display(self):
        frame = tk.Frame(self, bg=DISPLAY_BG)
        frame.grid(row=0, column=0, padx=10, pady=(10, 4), sticky="ew")
 
        top = tk.Frame(frame, bg=DISPLAY_BG)
        top.pack(fill="x")
        self.lbl_mem = tk.Label(top, text="", font=("Arial", 10, "bold"),
                                fg=BTN_OP, bg=DISPLAY_BG)
        self.lbl_mem.pack(side="left", padx=8)
        self.lbl_mode = tk.Label(top, text="DEG", font=("Arial", 10, "bold"),
                                 fg=BTN_EQ, bg=DISPLAY_BG)
        self.lbl_mode.pack(side="right", padx=8)
 
        self.var_prev = tk.StringVar()
        tk.Label(frame, textvariable=self.var_prev, font=("Arial", 12),
                 fg=FG_DIM, bg=DISPLAY_BG, anchor="e").pack(fill="x", padx=8)
 
        self.var_main = tk.StringVar(value="0")
        tk.Label(frame, textvariable=self.var_main, font=("Arial", 28, "bold"),
                 fg=FG, bg=DISPLAY_BG, anchor="e").pack(fill="x", padx=8, pady=(0, 8))
 
    def _build_buttons(self):
        pad = tk.Frame(self, bg=BG)
        pad.grid(row=1, column=0, padx=10, pady=(4, 10))
 
        # (nhãn, màu, hàm xử lý)
        layout = [
            [("MC", BTN_MEM, self.mem_clear), ("MR", BTN_MEM, self.mem_recall),
             ("M+", BTN_MEM, self.mem_add), ("M-", BTN_MEM, self.mem_sub),
             ("MS", BTN_MEM, self.mem_store)],
            [("DEG", BTN_FUNC, self.toggle_mode), ("sin", BTN_FUNC, lambda: self.add("sin(")),
             ("cos", BTN_FUNC, lambda: self.add("cos(")), ("tan", BTN_FUNC, lambda: self.add("tan(")),
             ("ln", BTN_FUNC, lambda: self.add("ln("))],
            [("x²", BTN_FUNC, lambda: self.add("^2")), ("xʸ", BTN_FUNC, lambda: self.add("^")),
             ("√", BTN_FUNC, lambda: self.add("√(")), ("log", BTN_FUNC, lambda: self.add("log(")),
             ("n!", BTN_FUNC, lambda: self.add("!"))],
            [("π", BTN_FUNC, lambda: self.add("π")), ("e", BTN_FUNC, lambda: self.add("e")),
             ("(", BTN_FUNC, lambda: self.add("(")), (")", BTN_FUNC, lambda: self.add(")")),
             ("⌫", BTN_CLR, self.backspace)],
            [("7", BTN_NUM, lambda: self.add("7")), ("8", BTN_NUM, lambda: self.add("8")),
             ("9", BTN_NUM, lambda: self.add("9")), ("÷", BTN_OP, lambda: self.add("÷")),
             ("AC", BTN_CLR, self.clear)],
            [("4", BTN_NUM, lambda: self.add("4")), ("5", BTN_NUM, lambda: self.add("5")),
             ("6", BTN_NUM, lambda: self.add("6")), ("×", BTN_OP, lambda: self.add("×")),
             ("±", BTN_FUNC, self.negate)],
            [("1", BTN_NUM, lambda: self.add("1")), ("2", BTN_NUM, lambda: self.add("2")),
             ("3", BTN_NUM, lambda: self.add("3")), ("−", BTN_OP, lambda: self.add("−")),
             ("1/x", BTN_FUNC, self.reciprocal)],
            [("0", BTN_NUM, lambda: self.add("0")), (".", BTN_NUM, lambda: self.add(".")),
             ("%", BTN_FUNC, lambda: self.add("%")), ("+", BTN_OP, lambda: self.add("+")),
             ("=", BTN_EQ, self.equals)],
        ]
        self.buttons = {}
        for r, row in enumerate(layout):
            for c, (text, color, cmd) in enumerate(row):
                b = tk.Button(pad, text=text, command=cmd, width=5, height=2,
                              font=("Arial", 13, "bold"), bg=color, fg=FG,
                              activebackground=color, activeforeground="white",
                              relief="flat", bd=0, cursor="hand2")
                b.grid(row=r, column=c, padx=3, pady=3)
                b.bind("<Enter>", lambda e, w=b: w.config(relief="raised"))
                b.bind("<Leave>", lambda e, w=b: w.config(relief="flat"))
                self.buttons[text] = b
 
    def _build_history(self):
        frame = tk.Frame(self, bg=BG)
        frame.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=10, sticky="ns")
        tk.Label(frame, text="Lịch sử", font=("Arial", 12, "bold"),
                 fg=FG, bg=BG).pack(anchor="w")
 
        box = tk.Frame(frame, bg=BG)
        box.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(box)
        scroll.pack(side="right", fill="y")
        self.lst = tk.Listbox(box, width=26, height=18, bg=DISPLAY_BG, fg=FG,
                              font=("Consolas", 10), bd=0, highlightthickness=0,
                              selectbackground=BTN_OP, yscrollcommand=scroll.set)
        self.lst.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.lst.yview)
        self.lst.bind("<Double-Button-1>", self.recall_history)
 
        tk.Button(frame, text="Xóa lịch sử", command=self.clear_history,
                  bg=BTN_FUNC, fg=FG, relief="flat", cursor="hand2").pack(fill="x", pady=(6, 0))
 
    def _bind_keys(self):
        for ch in "0123456789.()+":
            self.bind(ch, lambda e, c=ch: self.add(c))
        self.bind("-", lambda e: self.add("−"))
        self.bind("*", lambda e: self.add("×"))
        self.bind("/", lambda e: self.add("÷"))
        self.bind("^", lambda e: self.add("^"))
        self.bind("%", lambda e: self.add("%"))
        self.bind("<Return>", lambda e: self.equals())
        self.bind("<KP_Enter>", lambda e: self.equals())
        self.bind("=", lambda e: self.equals())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.clear())
 
    # ====================== NHẬP LIỆU ======================
    def add(self, text):
        # Sau khi bấm "=": gõ số/hàm -> bắt đầu mới; gõ toán tử -> tính tiếp
        if self.just_evaluated:
            if text[0].isdigit() or text in (".", "(", "π", "e") or text[0].isalpha() or text == "√(":
                self.expr = ""
            self.just_evaluated = False
        self.expr += text
        self._refresh()
 
    def clear(self):
        self.expr = ""
        self.var_prev.set("")
        self.just_evaluated = False
        self._refresh()
 
    def backspace(self):
        if self.just_evaluated:
            return self.clear()
        # Xóa cả tên hàm nếu đang đứng sau "sin(" ...
        m = re.search(r"(sin\(|cos\(|tan\(|log\(|ln\(|√\()$", self.expr)
        self.expr = self.expr[:-len(m.group(0))] if m else self.expr[:-1]
        self._refresh()
 
    def negate(self):
        if not self.expr:
            return
        if self.expr.startswith("−(") and self.expr.endswith(")"):
            self.expr = self.expr[2:-1]
        else:
            self.expr = f"−({self.expr})"
        self._refresh()
 
    def reciprocal(self):
        if self.expr:
            self.expr = f"1÷({self.expr})"
            self._refresh()
 
    def toggle_mode(self):
        self.deg_mode = not self.deg_mode
        label = "DEG" if self.deg_mode else "RAD"
        self.lbl_mode.config(text=label)
        self.buttons["DEG"].config(text=label)
 
    def _refresh(self):
        self.var_main.set(self.expr if self.expr else "0")
        self.lbl_mem.config(text="M" if self.memory != 0 else "")
 
    # ====================== TÍNH TOÁN ======================
    def _trig(self, fn):
        if self.deg_mode:
            return lambda x: fn(math.radians(x))
        return fn
 
    @staticmethod
    def _fact(x):
        if x < 0 or x != int(x):
            raise ValueError("giai thừa chỉ cho số nguyên không âm")
        return math.factorial(int(x))
 
    def evaluate(self, expr):
        """Chuyển biểu thức hiển thị -> biểu thức Python rồi tính."""
        e = (expr.replace("×", "*").replace("÷", "/").replace("−", "-")
                 .replace("^", "**").replace("√", "sqrt").replace("π", "pi")
                 .replace("%", "/100"))
        # Tự đóng ngoặc còn thiếu
        e += ")" * (e.count("(") - e.count(")"))
        # Nhân ngầm: 2π, 3(4+1), 2sin(30), (1+2)(3+4)
        e = re.sub(r"(\d|\)|pi)\s*(pi|e\b|sqrt|sin|cos|tan|log|ln|\()", r"\1*\2", e)
        e = re.sub(r"(\))\s*(\d)", r"\1*\2", e)
        # Giai thừa: 5! hoặc (2+3)!
        e = re.sub(r"(\d+(?:\.\d+)?)!", r"fact(\1)", e)
        e = re.sub(r"(\([^()]*\))!", r"fact\1", e)
 
        names = {
            "sin": self._trig(math.sin), "cos": self._trig(math.cos),
            "tan": self._trig(math.tan), "log": math.log10, "ln": math.log,
            "sqrt": math.sqrt, "fact": self._fact, "pi": math.pi, "e": math.e,
        }
        result = eval(e, {"__builtins__": {}}, names)
        if abs(result) < 1e-12:
            result = 0
        return result
 
    @staticmethod
    def fmt(value):
        if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"
 
    def equals(self):
        if not self.expr:
            return
        try:
            res = self.fmt(self.evaluate(self.expr))
        except ZeroDivisionError:
            return self._error("Không thể chia cho 0")
        except Exception:
            return self._error("Biểu thức không hợp lệ")
        self.var_prev.set(self.expr + " =")
        self.history.append((self.expr, res))
        self.lst.insert(tk.END, f"{self.expr} = {res}")
        self.lst.yview_moveto(1)
        self.expr = res
        self.just_evaluated = True
        self._refresh()
 
    def _error(self, msg):
        self.var_prev.set(self.expr)
        self.var_main.set(msg)
        self.expr = ""
        self.just_evaluated = False
 
    # ====================== LỊCH SỬ ======================
    def recall_history(self, _event=None):
        sel = self.lst.curselection()
        if sel:
            self.expr = self.history[sel[0]][1]
            self.just_evaluated = True
            self._refresh()
 
    def clear_history(self):
        self.history.clear()
        self.lst.delete(0, tk.END)
 
    # ====================== BỘ NHỚ ======================
    def _current_value(self):
        try:
            return float(self.evaluate(self.expr)) if self.expr else 0.0
        except Exception:
            self._error("Biểu thức không hợp lệ")
            return None
 
    def mem_clear(self):
        self.memory = 0.0
        self._refresh()
 
    def mem_recall(self):
        if self.just_evaluated:
            self.expr = ""
            self.just_evaluated = False
        self.expr += self.fmt(self.memory)
        self._refresh()
 
    def mem_add(self):
        v = self._current_value()
        if v is not None:
            self.memory += v
            self._refresh()
 
    def mem_sub(self):
        v = self._current_value()
        if v is not None:
            self.memory -= v
            self._refresh()
 
    def mem_store(self):
        v = self._current_value()
        if v is not None:
            self.memory = v
            self._refresh()
 
 
if __name__ == "__main__":
    Calculator().mainloop()
 