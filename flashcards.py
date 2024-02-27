import threading
import asyncio
import random as rd
from tkinter import *
import mysql.connector

number = 0
flashcards = []

db = mysql.connector.connect(
    host="sql11.freesqldatabase.com",
    user="sql11686966",
    password="RBGLkqHdur",
    database="sql11686966"
    )

mycursor = db.cursor()

event_card = threading.Event()  # THREADING EVENTS = SCRATCH MESSAGES
event_card.clear()


def split_string(text, line_length):
    chunks = [text[i:i+line_length] for i in range(0, len(text), line_length)]
    return '\n'.join(chunks)


def addFlashcard():
    display_object.displayed_question.set("INPUT THE QUESTION : ")
    event_card.wait()
    question = entry_card.get()
    event_card.clear()
    display_object.displayed_question.set("INPUT THE ANSWER : ")
    event_card.wait()
    answer = entry_card.get()
    event_card.clear()
    mycursor.execute("INSERT Flashcards_table (question, answer) VALUES (%s, %s)", (question, answer))
    display_object.displayed_question.set("")
    db.commit()


def answerQuestion():
    a_q = rd.randint(0, 1)
    mycursor.execute("SELECT MAX(flashcard_id), MIN(flashcard_id) FROM Flashcards_table")
    result = mycursor.fetchone()
    max_id, min_id = result[0], result[1]
    if a_q == 0:
        chosen_one = rd.randint(min_id, max_id)
        mycursor.execute("SELECT question FROM Flashcards_table WHERE flashcard_id = %s", (chosen_one,))
        question = mycursor.fetchone()[0].lower()
        mycursor.execute("SELECT answer FROM Flashcards_table WHERE flashcard_id = %s", (chosen_one,))
        correct = mycursor.fetchone()[0].lower()
    elif a_q == 1:
        chosen_one = rd.randint(min_id, max_id)
        mycursor.execute("SELECT answer FROM Flashcards_table WHERE flashcard_id = %s", (chosen_one,))
        question = mycursor.fetchone()[0].lower()
        mycursor.execute("SELECT question FROM Flashcards_table WHERE flashcard_id = %s", (chosen_one,))
        correct = mycursor.fetchone()[0].lower()
    display_object.displayed_question.set(split_string(str(question), 60))
    event_card.wait()
    user_answer = entry_card.get().lower()
    event_card.clear()
    if user_answer == correct:
        display_object.displayed_question.set("CONGRATS !")
        asyncio.run(asyncio.sleep(2))
        display_object.displayed_question.set("")
    else:
        display_object.displayed_question.set(split_string(f"Wrong. Correct Answer : ({correct})", 60))
        asyncio.run(asyncio.sleep(2))
        display_object.displayed_question.set("")


def deleteFlashcard(request):
    num = int(request.replace("deleteFlashcard", ''))
    mycursor.execute("DELETE FROM Flashcards_table WHERE flashcard_id = %s", (num, ))
    db.commit()
    display_object.displayed_question.set(f"The {num}'th flashcard has been deleted")
    asyncio.run(asyncio.sleep(2))
    display_object.displayed_question.set("")


def viewFlashcards():
    mycursor.execute("SELECT * FROM Flashcards_table")
    list_flashcards = ''
    for x in mycursor:
        list_flashcards += str(x)
    display_object.displayed_question.set(split_string(list_flashcards, 60))


def deleteAll():
    mycursor.execute("DELETE FROM Flashcards_table WHERE flashcard_id > 0")
    db.commit()
    display_object.displayed_question.set("All flashcards have been deleted")
    asyncio.run(asyncio.sleep(2))
    display_object.displayed_question.set("")


def commands(request):
    if "addFlashcard" in request:
        new_thread_add_flashcard = threading.Thread(target=addFlashcard)
        new_thread_add_flashcard.start()
    elif "answerQuestion" in request:
        new_thread_answer_question = threading.Thread(target=answerQuestion)
        new_thread_answer_question.start()
    elif "deleteFlashcard" in request:
        deleteFlashcard(request)
    elif "viewFlashcards" in request:
        viewFlashcards()
    elif "deleteAll" in request:
        deleteAll()


def submit_request():
    user_answer_window = entry_request.get()
    commands(user_answer_window)


def submit_card():
    event_card.set()


window = Tk()
WIDTH = 1366
HEIGHT = 768


class Display:
    def __init__(self, x_value, y_value):
        self.displayed_question = StringVar()
        self.X = x_value
        self.Y = y_value


display_object = Display(0, 0)


window.geometry(f"{WIDTH}x{HEIGHT}")  # SIZE
window.title("Flashcards by Sak_Am")  # TITLE
window.config(background="#387FC8")  # BACKGROUND_COLOR

label1 = Label(window, text="WELCOME BACK AMINE !", font=('Helvetica', 21, 'bold'), fg='#F3B552', bg="#387FC8")  # LABELS = BOXES
label2 = Label(window, text="YOUR FLASHCARDS ARE HERE : ", font=('Helvetica', 21, 'bold'), fg='#F3B552', bg="#387FC8")
label1.place(x=(WIDTH - label1.winfo_reqwidth()) / 2, y=15)  # PLACEMENT OF LABELS
label2.place(x=(WIDTH - label2.winfo_reqwidth()) / 2, y=115)

entry_request = Entry(window, font=("Helvetica", 14))  # INPUT
entry_request_width = entry_request.winfo_reqwidth()
entry_request.place(x=(WIDTH - entry_request.winfo_reqwidth()) / 2 - 40, y=600)

entry_card = Entry(window, font=("Helvetica", 14))  # INPUT
entry_card_width = entry_card.winfo_reqwidth()
entry_card.place(x=(WIDTH - entry_card.winfo_reqwidth()) / 2 - 40, y=650)

submit_request_button = Button(window, text='Submit Request', command=submit_request)  # BUTTON = SUBMIT + COMMAND
submit_request_button.place(x=(WIDTH - entry_request_width) / 2 - 40 + entry_request_width + 20, y=607)

submit_card_button = Button(window, text='Submit Card', command=submit_card)  # BUTTON = SUBMIT + COMMAND
submit_card_button.place(x=(WIDTH - entry_request_width) / 2 - 40 + entry_request_width + 20, y=657)

WIDTH_CANVAS = 711
HEIGHT_CANVAS = 355

canvas = Canvas(window, height=HEIGHT_CANVAS, width=WIDTH_CANVAS, borderwidth=0, highlightthickness=0)
canvas.create_rectangle(0, 0, WIDTH_CANVAS, HEIGHT_CANVAS, fill="darkorange")  # SHAPES <-- WITHIN THE CANVA
label3 = Label(canvas, textvariable=display_object.displayed_question, font=('Helvetica', 20, 'bold'), fg="black", bg="darkorange")
label3.place(x=display_object.X, y=display_object.Y)
canvas.place(x=(WIDTH - WIDTH_CANVAS) / 2, y=200)

window.mainloop()
