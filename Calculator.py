import tkinter as tk
import ast
import operator
import re


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
just_calculated = False


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
        +  Addition
        -  Subtraction
        *  Multiplication
        /  Division
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
# STATUS / ERROR MESSAGE
# ============================================================

def show_status(message):
    status_label.config(text=message)


def clear_status():
    status_label.config(text="")


# ============================================================
# GET CURRENT NUMBER
# ============================================================

def get_current_number_match():

    return re.search(r"(-?\d*\.?\d+)$", expression)


# ============================================================
# NUMBER / OPERATOR INPUT
# ============================================================

def press(value):

    global expression
    global just_calculated

    clear_status()

    # If a calculation was just completed and a number is pressed,
    # start a new calculation.
    if just_calculated:

        if value.isdigit() or value == ".":

            expression = ""

        just_calculated = False

    # --------------------------------------------------------
    # DECIMAL POINT
    # --------------------------------------------------------

    if value == ".":

        match = get_current_number_match()

        if match and "." in match.group():

            return

        if not expression or expression[-1] in "+-*/":

            expression += "0."

        else:

            expression += "."

    # --------------------------------------------------------
    # OPERATORS
    # --------------------------------------------------------

    elif value in "+-*/":

        if not expression:

            # Allow negative numbers at the beginning
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

                # Replace the previous operator
                expression = expression[:-1] + value

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

    if expression[-1] in "+-*/":

        show_status("Calculation is incomplete.")

        return

    try:

        result = safe_calculate(expression)

        # Remove unnecessary .0
        if isinstance(result, float) and result.is_integer():

            result = int(result)

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

        # Remove only the current number
        expression = expression[:match.start()]

    else:

        # If there is no current number, clear everything
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

    # Remove negative sign
    if number.startswith("-"):

        number = number[1:]

    # Add negative sign
    else:

        number = "-" + number

    expression = expression[:start] + number

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
        r"^(.+)([+\-*/])(-?\d*\.?\d+)$",
        expression
    )

    try:

        # Example:
        # 200 + 10%
        # becomes:
        # 200 + 20

        if match:

            left_side = match.group(1)
            operation = match.group(2)
            number = float(match.group(3))

            if operation in "+-":

                base = safe_calculate(left_side)

                percentage_value = base * number / 100

            else:

                percentage_value = number / 100

            if percentage_value.is_integer():

                percentage_value = int(percentage_value)

            expression = (
                left_side
                + operation
                + str(percentage_value)
            )

        else:

            # Simple percentage
            # 50 -> 0.5

            number = float(expression)

            result = number / 100

            if result.is_integer():

                result = int(result)

            expression = str(result)

        just_calculated = False

        update_display()

    except ZeroDivisionError:

        show_status("Cannot divide by zero.")

    except Exception:

        show_status("Invalid percentage.")


# ============================================================
# BUTTON ANIMATION
# ============================================================

def add_button_effect(button, normal_color, hover_color):

    def on_enter(event):

        button.config(
            bg=hover_color
        )

    def on_leave(event):

        button.config(
            bg=normal_color
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

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    button.bind("<ButtonPress-1>", on_press)
    button.bind("<ButtonRelease-1>", on_release)


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
        font=("Arial", 18, "bold"),
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
        padx=5,
        pady=5,
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
    pady=(0, 5),
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
# STATUS MESSAGE
# ============================================================

status_label = tk.Label(
    window,
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
    window,
    bg="#202124"
)

button_frame.pack(
    padx=20,
    pady=5,
    fill="both",
    expand=True
)


# Equal column sizes
for column in range(4):

    button_frame.columnconfigure(
        column,
        weight=1
    )


# Equal row sizes
for row in range(5):

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


# ============================================================
# EQUAL BUTTON
# ============================================================

# Separate equal button below the number pad
equal_button = tk.Button(
    window,
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
# KEYBOARD HIGHLIGHTING
# ============================================================

def flash_button(button):

    if not button:
        return

    original = button.cget("bg")

    button.config(
        bg="#FFFFFF",
        fg="#202124"
    )

    window.after(
        100,
        lambda: restore_button(button, original)
    )


def restore_button(button, original):

    button.config(
        bg=original,
        fg="white"
    )


# ============================================================
# KEYBOARD INPUT
# ============================================================

def keyboard_input(event):

    key = event.keysym
    char = event.char

    # Normal number keys
    if char in "0123456789":

        press(char)

        if char in button_map:
            flash_button(button_map[char])

        return

    # Number pad keys
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

        return

    # Decimal
    if char == "." or key == "KP_Decimal":

        press(".")

        flash_button(
            button_map["."]
        )

        return

    # Operators
    if char in "+-*/":

        press(char)

        if char in button_map:
            flash_button(
                button_map[char]
            )

        return

    # Number pad operators
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

        return

    # Enter
    if key in ("Return", "KP_Enter"):

        calculate()

        flash_button(
            button_map["="]
        )

        return

    # Backspace
    if key == "BackSpace":

        backspace()

        flash_button(
            button_map["⌫"]
        )

        return

    # Escape / Delete
    if key in ("Escape", "Delete"):

        all_clear()

        flash_button(
            button_map["AC"]
        )

        return


# ============================================================
# KEYBOARD BINDING
# ============================================================

window.bind("<Key>", keyboard_input)


# ============================================================
# START APPLICATION
# ============================================================

display.focus_set()

window.mainloop()
