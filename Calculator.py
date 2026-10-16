import tkinter as tk
from tkinter import messagebox
import ast
import operator


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()
window.title("Calculator")
window.geometry("400x600")
window.resizable(False, False)
window.configure(bg="#202124")


# ============================================================
# VARIABLES
# ============================================================

expression = ""


# ============================================================
# SAFE CALCULATION SYSTEM
# ============================================================

# Allowed mathematical operators
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
        Negative numbers
    """

    try:
        tree = ast.parse(expression, mode="eval")
        return evaluate_node(tree.body)

    except ZeroDivisionError:
        raise ZeroDivisionError

    except Exception:
        raise ValueError("Invalid calculation")


def evaluate_node(node):

    # Number
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
# DISPLAY UPDATE
# ============================================================

def update_display():
    display.delete(0, tk.END)
    display.insert(0, expression)


# ============================================================
# BUTTON INPUT
# ============================================================

def press(value):
    global expression

    expression += str(value)

    update_display()


# ============================================================
# CALCULATE
# ============================================================

def calculate():
    global expression

    if not expression:
        return

    try:
        result = safe_calculate(expression)

        # Remove unnecessary .0
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        expression = str(result)

        update_display()

    except ZeroDivisionError:

        messagebox.showerror(
            "Error",
            "Division by zero is not allowed."
        )

        expression = ""
        update_display()

    except ValueError:

        messagebox.showerror(
            "Error",
            "Invalid calculation."
        )

        expression = ""
        update_display()


# ============================================================
# CLEAR
# ============================================================

def clear():
    global expression

    expression = ""

    update_display()


# ============================================================
# BACKSPACE
# ============================================================

def backspace():
    global expression

    expression = expression[:-1]

    update_display()


# ============================================================
# EXIT
# ============================================================

def exit_calculator():
    window.destroy()


# ============================================================
# KEYBOARD INPUT
# ============================================================

def keyboard_input(event):

    key = event.keysym
    char = event.char

    # Number keys
    if char in "0123456789":
        press(char)

    # Decimal
    elif char == ".":
        press(".")

    # Operators
    elif char in "+-*/":
        press(char)

    # Enter
    elif key in ("Return", "KP_Enter"):
        calculate()

    # Backspace
    elif key == "BackSpace":
        backspace()

    # Delete / Escape
    elif key in ("Delete", "Escape"):
        clear()


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    window,
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
    window,
    bg="#303134",
    height=80
)

display_frame.pack(
    padx=20,
    pady=(0, 20),
    fill="x"
)

display_frame.pack_propagate(False)


display = tk.Entry(
    display_frame,
    font=("Arial", 28),
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
# BUTTON FRAME
# ============================================================

button_frame = tk.Frame(
    window,
    bg="#202124"
)

button_frame.pack(
    padx=20,
    fill="both",
    expand=True
)


# Make all four columns equal
for column in range(4):
    button_frame.columnconfigure(
        column,
        weight=1
    )


# Make rows equal
for row in range(5):
    button_frame.rowconfigure(
        row,
        weight=1
    )


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
        bg = "#8AB4F8"

    elif button_type == "equal":
        bg = "#81C995"

    elif button_type == "clear":
        bg = "#F28B82"

    elif button_type == "backspace":
        bg = "#5F6368"

    else:
        bg = "#3C4043"

    button = tk.Button(
        button_frame,
        text=text,
        font=("Arial", 18, "bold"),
        bg=bg,
        fg="white",
        activebackground="#70757A",
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
        padx=5,
        pady=5,
        sticky="nsew"
    )

    return button


# ============================================================
# NUMBER / OPERATOR BUTTONS
# ============================================================

create_button("7", 0, 0, lambda: press("7"))
create_button("8", 0, 1, lambda: press("8"))
create_button("9", 0, 2, lambda: press("9"))
create_button("/", 0, 3, lambda: press("/"), "operator")

create_button("4", 1, 0, lambda: press("4"))
create_button("5", 1, 1, lambda: press("5"))
create_button("6", 1, 2, lambda: press("6"))
create_button("*", 1, 3, lambda: press("*"), "operator")

create_button("1", 2, 0, lambda: press("1"))
create_button("2", 2, 1, lambda: press("2"))
create_button("3", 2, 2, lambda: press("3"))
create_button("-", 2, 3, lambda: press("-"), "operator")

create_button("0", 3, 0, lambda: press("0"))
create_button(".", 3, 1, lambda: press("."))
create_button("+", 3, 2, lambda: press("+"), "operator")
create_button("⌫", 3, 3, backspace, "backspace")


# ============================================================
# EQUAL BUTTON
# ============================================================

create_button(
    "=",
    4,
    0,
    calculate,
    "equal",
    columnspan=2
)


# ============================================================
# CLEAR BUTTON
# ============================================================

create_button(
    "CLEAR",
    4,
    2,
    clear,
    "clear",
    columnspan=2
)


# ============================================================
# EXIT BUTTON
# ============================================================

exit_button = tk.Button(
    window,
    text="EXIT",
    font=("Arial", 12, "bold"),
    width=12,
    height=2,
    bg="#303134",
    fg="white",
    activebackground="#5F6368",
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=exit_calculator
)

exit_button.pack(
    pady=15
)


# ============================================================
# KEYBOARD SUPPORT
# ============================================================

window.bind("<Key>", keyboard_input)

display.focus_set()


# ============================================================
# START APPLICATION
# ============================================================

window.mainloop()