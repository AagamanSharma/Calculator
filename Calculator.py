import tkinter as tk
import ast
import operator
import re
# ============================================================
# MAIN WINDOW
# ============================================================
window = tk.Tk()
window.title("Calculator")
window.geometry("720x600")
window.resizable(False, False)
window.configure(bg="#202124")
# ============================================================
# VARIABLES
# ============================================================
expression = ""
just_calculated = False
history = []
# ============================================================
# SAFE CALCULATION SYSTEM
# ============================================================
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}
def safe_calculate(expression):
    """
    Safely calculate a mathematical expression.
    Supported:
        +   Addition
        -   Subtraction
        *   Multiplication
        /   Division
        ()  Parentheses
        Decimal numbers
        Positive/negative numbers
    """
    tree = ast.parse(expression, mode="eval")
    return evaluate_node(tree.body)
def evaluate_node(node):
    # Numbers
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid number")
    # Binary operations
    if isinstance(node, ast.BinOp):
        if type(node.op) not in OPERATORS:
            raise ValueError("Operator not allowed")
        left = evaluate_node(node.left)
        right = evaluate_node(node.right)
        return OPERATORS[type(node.op)](left, right)
    # Positive / negative numbers
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in OPERATORS:
            raise ValueError("Operator not allowed")
        value = evaluate_node(node.operand)
        return OPERATORS[type(node.op)](value)
    raise ValueError("Invalid calculation")
# ============================================================
# DISPLAY
# ============================================================
def update_display():
    display.delete(0, tk.END)
    display.insert(0, expression)
# ============================================================
# STATUS MESSAGE
# ============================================================
def show_status(message):
    status_label.config(text=message)
def clear_status():
    status_label.config(text="")
# ============================================================
# CURRENT NUMBER
# ============================================================
def get_current_number_match():
    return re.search(
        r"(-?\d*\.?\d+)$",
        expression
    )
# ============================================================
# NUMBER / OPERATOR INPUT
# ============================================================
def press(value):
    global expression
    global just_calculated
    clear_status()
    # Start a new calculation after a result
    if just_calculated:
        if value.isdigit() or value == ".":
            expression = ""
        just_calculated = False
    # --------------------------------------------------------
    # DECIMAL
    # --------------------------------------------------------
    if value == ".":
        match = get_current_number_match()
        if match and "." in match.group():
            return
        if not expression or expression[-1] in "+-*/(":
            expression += "0."
        else:
            expression += "."
    # --------------------------------------------------------
    # PARENTHESES
    # --------------------------------------------------------
    elif value == "(":
        # Start a new calculation after result
        if just_calculated:
            expression = ""
            just_calculated = False
        # Add multiplication automatically when needed
        if expression:
            if expression[-1].isdigit() or expression[-1] == ")":
                expression += "*"
        expression += "("
    elif value == ")":
        # Do not allow closing parenthesis at the beginning
        if not expression:
            show_status("No opening parenthesis.")
            return
        # Do not allow ) immediately after an operator or (
        if expression[-1] in "+-*/(":
            show_status("Invalid parenthesis placement.")
            return
        # Make sure there is an unmatched opening parenthesis
        if expression.count("(") <= expression.count(")"):
            show_status("No matching opening parenthesis.")
            return
        expression += ")"
    # --------------------------------------------------------
    # OPERATORS
    # --------------------------------------------------------
    elif value in "+-*/":
        if not expression:
            if value == "-":
                expression = "-"
            else:
                show_status("Enter a number first.")
                return
        elif expression[-1] in "+-*/":
            # Allow negative numbers after an operator
            if value == "-" and expression[-1] != "-":
                expression += "-"
            else:
                expression = expression[:-1] + value
        elif expression[-1] == "(":
            if value == "-":
                expression += "-"
            else:
                show_status("Invalid operator placement.")
                return
        else:
            expression += value
    # --------------------------------------------------------
    # NUMBERS
    # --------------------------------------------------------
    else:
        expression += str(value)
    update_display()
# ============================================================
# CALCULATE
# ============================================================
def calculate():
    global expression
    global just_calculated
    clear_status()
    if not expression:
        show_status("Nothing to calculate.")
        return
    if expression[-1] in "+-*/(":
        show_status("Calculation is incomplete.")
        return
    if expression.count("(") != expression.count(")"):
        show_status("Missing closing parenthesis.")
        return
    original_expression = expression
    try:
        result = safe_calculate(expression)
        # Remove unnecessary .0
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        # Add to history
        add_to_history(
            original_expression,
            result
        )
        expression = str(result)
        just_calculated = True
        update_display()
    except ZeroDivisionError:
        show_status("Cannot divide by zero.")
    except (ValueError, SyntaxError):
        show_status("Invalid calculation.")
    except Exception:
        show_status("Unable to calculate.")
# ============================================================
# ALL CLEAR
# ============================================================
def all_clear():
    global expression
    global just_calculated
    expression = ""
    just_calculated = False
    update_display()
    clear_status()
# ============================================================
# CLEAR ENTRY
# ============================================================
def clear_entry():
    global expression
    global just_calculated
    clear_status()
    if not expression:
        return
    just_calculated = False
    match = get_current_number_match()
    if match:
        expression = expression[:match.start()]
    else:
        expression = ""
    update_display()
# ============================================================
# BACKSPACE
# ============================================================
def backspace():
    global expression
    global just_calculated
    clear_status()
    if expression:
        expression = expression[:-1]
    just_calculated = False
    update_display()
# ============================================================
# PLUS / MINUS
# ============================================================
def toggle_sign():
    global expression
    global just_calculated
    clear_status()
    if not expression:
        expression = "-"
        update_display()
        return
    just_calculated = False
    match = get_current_number_match()
    if not match:
        show_status("Enter a number first.")
        return
    number = match.group()
    start = match.start()
    if number.startswith("-"):
        number = number[1:]
    else:
        number = "-" + number
    expression = (
        expression[:start]
        + number
    )
    update_display()
# ============================================================
# PERCENTAGE
# ============================================================
def percentage():
    global expression
    global just_calculated
    clear_status()
    if not expression:
        show_status("Enter a number first.")
        return
    match = re.match(
        r"^(.+)([+\-/])(-?\d\.?\d+)$",
        expression
    )
    try:
        if match:
            left_side = match.group(1)
            operation = match.group(2)
            number = float(match.group(3))
            if operation in "+-":
                base = safe_calculate(left_side)
                percentage_value = (
                    base * number / 100
                )
            else:
                percentage_value = number / 100
            if percentage_value.is_integer():
                percentage_value = int(
                    percentage_value
                )
            expression = (
                left_side
                + operation
                + str(percentage_value)
            )
        else:
            number = float(expression)
            result = number / 100
            if result.is_integer():
                result = int(result)
            expression = str(result)
        just_calculated = False
        update_display()
    except Exception:
        show_status("Invalid percentage.")
# ============================================================
# HISTORY
# ============================================================
def add_to_history(calculation, result):
    history.append(
        {
            "expression": calculation,
            "result": result
        }
    )
    # Keep the most recent 50 calculations
    if len(history) > 50:
        history.pop(0)
    update_history_panel()
def update_history_panel():
    history_listbox.delete(
        0,
        tk.END
    )
    # Show newest first
    for item in reversed(history):
        history_listbox.insert(
            tk.END,
            f"{item['expression']} = {item['result']}"
        )
def clear_history():
    history.clear()
    update_history_panel()
    show_status("History cleared.")
def use_history(event=None):
    global expression
    global just_calculated
    selection = history_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    reversed_history = list(
        reversed(history)
    )
    item = reversed_history[index]
    expression = str(
        item["result"]
    )
    just_calculated = True
    update_display()
    clear_status()
# ============================================================
# COPY RESULT
# ============================================================
def copy_result():
    if not expression:
        show_status("Nothing to copy.")
        return
    try:
        window.clipboard_clear()
        window.clipboard_append(
            expression
        )
        window.update()
        show_status("Result copied to clipboard.")
    except Exception:
        show_status("Unable to copy result.")
# ============================================================
# PASTE NUMBER
# ============================================================
def paste_number():
    global expression
    global just_calculated
    try:
        clipboard_text = (
            window.clipboard_get()
            .strip()
        )
    except tk.TclError:
        show_status("Clipboard is empty.")
        return
    # Only allow a number
    if not re.fullmatch(
        r"-?\d*\.?\d+",
        clipboard_text
    ):
        show_status(
            "Clipboard does not contain a valid number."
        )
        return
    clear_status()
    if just_calculated:
        expression = ""
        just_calculated = False
    expression += clipboard_text
    update_display()
# ============================================================
# HISTORY PANEL TOGGLE
# ============================================================
history_visible = False
def toggle_history():
    global history_visible
    if history_visible:
        history_frame.pack_forget()
        history_visible = False
        history_toggle_button.config(text="HISTORY")
    else:
        history_frame.pack(
            side="right",
            fill="both",
            padx=(10, 20),
            pady=(20, 15)
        )
        history_visible = True
        history_toggle_button.config(text="HIDE HISTORY")
        update_history_panel()
def add_button_effect(
    button,
    normal_color,
    hover_color
):
    def on_enter(event):
        button.config(
            bg=hover_color
        )
    def on_leave(event):
        button.config(
            bg=normal_color,
            relief="flat"
        )
    def on_press(event):
        button.config(
            bg="#70757A",
            relief="sunken"
        )
    def on_release(event):
        button.config(
            bg=hover_color,
            relief="flat"
        )
    button.bind(
        "<Enter>",
        on_enter
    )
    button.bind(
        "<Leave>",
        on_leave
    )
    button.bind(
        "<ButtonPress-1>",
        on_press
    )
    button.bind(
        "<ButtonRelease-1>",
        on_release
    )
# ============================================================
# BUTTON STORAGE
# ============================================================
button_map = {}
# ============================================================
# BUTTON CREATOR
# ============================================================
def create_button(
    text,
    row,
    column,
    command,
    button_type="number",
    columnspan=1
):
    if button_type == "operator":
        normal_color = "#8AB4F8"
        hover_color = "#A8C7FA"
    elif button_type == "equal":
        normal_color = "#81C995"
        hover_color = "#9BD8AD"
    elif button_type == "clear":
        normal_color = "#F28B82"
        hover_color = "#F6A29B"
    elif button_type == "function":
        normal_color = "#5F6368"
        hover_color = "#73777B"
    else:
        normal_color = "#3C4043"
        hover_color = "#505458"
    button = tk.Button(
        button_frame,
        text=text,
        font=("Arial", 16, "bold"),
        bg=normal_color,
        fg="white",
        activebackground=hover_color,
        activeforeground="white",
        bd=0,
        relief="flat",
        cursor="hand2",
        command=command
    )
    button.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        padx=4,
        pady=4,
        sticky="nsew"
    )
    add_button_effect(
        button,
        normal_color,
        hover_color
    )
    button_map[text] = button
    return button
# ============================================================
# CALCULATOR FRAME
# ============================================================
calculator_frame = tk.Frame(
    window,
    bg="#202124",
    width=420
)
calculator_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(20, 0),
    pady=20
)
calculator_frame.pack_propagate(False)
# ============================================================
# TITLE
# ============================================================
title_label = tk.Label(
    calculator_frame,
    text="CALCULATOR",
    font=("Arial", 22, "bold"),
    bg="#202124",
    fg="white"
)
title_label.pack(
    pady=(20, 15)
)
# ============================================================
# DISPLAY
# ============================================================
display_frame = tk.Frame(
    calculator_frame,
    bg="#303134",
    height=80
)
display_frame.pack(
    padx=20,
    pady=(0, 5),
    fill="x"
)
display_frame.pack_propagate(False)
display = tk.Entry(
    display_frame,
    font=("Arial", 26),
    justify="right",
    bg="#303134",
    fg="white",
    insertbackground="white",
    bd=0
)
display.pack(
    padx=15,
    pady=15,
    fill="both",
    expand=True
)
# ============================================================
# STATUS MESSAGE
# ============================================================
status_label = tk.Label(
    calculator_frame,
    text="",
    font=("Arial", 10),
    bg="#202124",
    fg="#F28B82",
    height=2
)
status_label.pack(
    padx=20,
    fill="x"
)
# ============================================================
# BUTTON FRAME
# ============================================================
button_frame = tk.Frame(
    calculator_frame,
    bg="#202124"
)
button_frame.pack(
    padx=20,
    pady=5,
    fill="both",
    expand=True
)
for column in range(4):
    button_frame.columnconfigure(
        column,
        weight=1
    )
for row in range(6):
    button_frame.rowconfigure(
        row,
        weight=1
    )
# ============================================================
# BUTTON LAYOUT
# ============================================================
# Row 0
create_button(
    "AC",
    0,
    0,
    all_clear,
    "clear"
)
create_button(
    "CE",
    0,
    1,
    clear_entry,
    "function"
)
create_button(
    "%",
    0,
    2,
    percentage,
    "function"
)
create_button(
    "/",
    0,
    3,
    lambda: press("/"),
    "operator"
)
# Row 1
create_button(
    "7",
    1,
    0,
    lambda: press("7")
)
create_button(
    "8",
    1,
    1,
    lambda: press("8")
)
create_button(
    "9",
    1,
    2,
    lambda: press("9")
)
create_button(
    "*",
    1,
    3,
    lambda: press("*"),
    "operator"
)
# Row 2
create_button(
    "4",
    2,
    0,
    lambda: press("4")
)
create_button(
    "5",
    2,
    1,
    lambda: press("5")
)
create_button(
    "6",
    2,
    2,
    lambda: press("6")
)
create_button(
    "-",
    2,
    3,
    lambda: press("-"),
    "operator"
)
# Row 3
create_button(
    "1",
    3,
    0,
    lambda: press("1")
)
create_button(
    "2",
    3,
    1,
    lambda: press("2")
)
create_button(
    "3",
    3,
    2,
    lambda: press("3")
)
create_button(
    "+",
    3,
    3,
    lambda: press("+"),
    "operator"
)
# Row 4
create_button(
    "±",
    4,
    0,
    toggle_sign,
   "function"
)
create_button(
    "0",
    4,
    1,
    lambda: press("0")
)
create_button(
    ".",
    4,
    2,
    lambda: press(".")
)
create_button(
    "⌫",
    4,
    3,
    backspace,
    "function"
)
# Row 5
create_button(
    "(",
    5,
    0,
    lambda: press("("),
    "function"
)
create_button(
    ")",
    5,
    1,
    lambda: press(")"),
    "function"
)
history_toggle_button = create_button(
    "HISTORY",
    5,
    2,
    toggle_history,
    "function",
    columnspan=2
)
# EQUAL BUTTON
# ============================================================
equal_button = tk.Button(
    calculator_frame,
    text="=",
    font=("Arial", 20, "bold"),
    bg="#81C995",
    fg="white",
    activebackground="#9BD8AD",
    activeforeground="white",
    bd=0,
    relief="flat",
    cursor="hand2",
    command=calculate
)
equal_button.pack(
    padx=20,
    pady=(5, 15),
    fill="x",
    ipady=8
)
add_button_effect(
    equal_button,
    "#81C995",
    "#9BD8AD"
)
button_map["="] = equal_button
# ============================================================
# HISTORY PANEL
# ============================================================
history_frame = tk.Frame(
    window,
    bg="#303134",
    width=260
)
history_frame.pack_propagate(False)
history_title = tk.Label(
    history_frame,
    text="HISTORY",
    font=("Arial", 16, "bold"),
    bg="#303134",
    fg="white"
)
history_title.pack(
    pady=(15, 10)
)
history_listbox = tk.Listbox(
    history_frame,
    font=("Arial", 11),
    bg="#202124",
    fg="white",
    selectbackground="#8AB4F8",
    selectforeground="#202124",
    bd=0,
    highlightthickness=0,
    activestyle="none"
)
history_listbox.pack(
    padx=10,
    pady=5,
    fill="both",
    expand=True
)
history_listbox.bind(
    "<Double-Button-1>",
    use_history
)
clear_history_button = tk.Button(
    history_frame,
    text="CLEAR HISTORY",
    font=("Arial", 10, "bold"),
    bg="#5F6368",
    fg="white",
    activebackground="#73777B",
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=clear_history
)
clear_history_button.pack(
    padx=10,
    pady=10,
    fill="x",
    ipady=6
)
# ============================================================
# KEYBOARD HIGHLIGHTING
# ============================================================
def flash_button(button):
    if not button:
        return
    original_bg = button.cget("bg")
    original_fg = button.cget("fg")
    button.config(
        bg="#FFFFFF",
        fg="#202124"
    )
    window.after(
        100,
        lambda: restore_button(
            button,
            original_bg,
            original_fg
        )
    )
def restore_button(
    button,
    original_bg,
    original_fg
):
    button.config(
        bg=original_bg,
        fg=original_fg
    )
# ============================================================
# KEYBOARD INPUT
# ============================================================
def keyboard_input(event):
    key = event.keysym
    char = event.char
    # --------------------------------------------------------
    # KEYBOARD SHORTCUTS
    # --------------------------------------------------------
    if event.state & 0x4:
        if key.lower() == "c":
            copy_result()
            return "break"
        if key.lower() == "v":
            paste_number()
            return "break"
        if key.lower() == "h":
            toggle_history()
            return "break"
        if key.lower() == "l":
            all_clear()
            return "break"
        # Ignore every other Ctrl combination.
        return "break"
    # --------------------------------------------------------
    # NUMBERS
    # --------------------------------------------------------
    if char in "0123456789":
        press(char)
        flash_button(
            button_map[char]
        )
        return "break"
    keypad_numbers = {
        "KP_0": "0",
        "KP_1": "1",
        "KP_2": "2",
        "KP_3": "3",
        "KP_4": "4",
        "KP_5": "5",
        "KP_6": "6",
        "KP_7": "7",
        "KP_8": "8",
        "KP_9": "9"
    }
    if key in keypad_numbers:
        number = keypad_numbers[key]
        press(number)
        flash_button(
            button_map[number]
        )
        return "break"
    # --------------------------------------------------------
    # DECIMAL
    # --------------------------------------------------------
    if char == "." or key == "KP_Decimal":
        press(".")
        flash_button(
            button_map["."]
        )
        return "break"
    # --------------------------------------------------------
    # PERCENTAGE
    # --------------------------------------------------------
    if char == "%":
        percentage()
        flash_button(
            button_map["%"]
        )
        return "break"
    # --------------------------------------------------------
    # OPERATORS
    # --------------------------------------------------------
    if char in "+-*/":
        press(char)
        flash_button(
            button_map[char]
        )
        return "break"
    keypad_operators = {
        "KP_Add": "+",
        "KP_Subtract": "-",
        "KP_Multiply": "*",
        "KP_Divide": "/"
    }
    if key in keypad_operators:
        operation = keypad_operators[key]
        press(operation)
        flash_button(
            button_map[operation]
        )
        return "break"
    # --------------------------------------------------------
    # PARENTHESES
    # --------------------------------------------------------
    if char == "(":
        press("(")
        flash_button(
            button_map["("]
        )
        return "break"
    if char == ")":
        press(")")
        flash_button(
            button_map[")"]
        )
        return "break"
    # --------------------------------------------------------
    # ENTER
    # --------------------------------------------------------
    if key in ("Return", "KP_Enter"):
        calculate()
        flash_button(
            button_map["="]
        )
        return "break"
    # --------------------------------------------------------
    # BACKSPACE
    # --------------------------------------------------------
    if key == "BackSpace":
        backspace()
        flash_button(
            button_map["⌫"]
        )
        return "break"
    # --------------------------------------------------------
    # ESCAPE / DELETE
    # --------------------------------------------------------
    if key in ("Escape", "Delete"):
        all_clear()
        flash_button(
            button_map["AC"]
        )
        return "break"
    # --------------------------------------------------------
    # EVERYTHING ELSE IS IGNORED
    # --------------------------------------------------------
    # This prevents Tkinter's Entry widget from inserting
    # unsupported characters.
    return "break"
# KEYBOARD BINDING
# ============================================================
display.bind(
    "<Key>",
    keyboard_input
)
# ============================================================
# START APPLICATION
# ============================================================
display.focus_set()
window.mainloop()