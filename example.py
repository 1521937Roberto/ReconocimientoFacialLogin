from tkinter import *
from tkinter import messagebox as msg
import os
import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import database as db
import base64

# CONFIG
path = os.getcwd()  # Usar el directorio actual en lugar de una ruta fija
txt_login = "Iniciar Sesión"
txt_register = "Registrarse"

color_white = "#f4f5f4"
color_black = "#101010"

color_black_btn = "#202020"
color_background = "#151515"

font_label = "Century Gothic"
size_screen = "500x300"

# GENERAL
def getEnter(screen):
    ''' Set an enter inside the screen '''
    Label(screen, text="", bg=color_background).pack()

def printAndShow(screen, text, flag):
    ''' Prints and shows text '''
    if flag:
        print(text)
        screen.destroy()
        msg.showinfo(message=text, title="¡Éxito!")
    else:
        print(text)
        Label(screen, text=text, fg="red", bg=color_background, font=(font_label, 12)).pack()

def configure_screen(screen, text):
    ''' Configure global styles '''
    screen.title(text)
    screen.geometry(size_screen)
    screen.configure(bg=color_background)
    Label(screen, text=f"¡{text}!", fg=color_white, bg=color_black, font=(font_label, 18), width="500", height="2").pack()

def credentials(screen, var, flag):
    ''' Configuration of user input '''
    Label(screen, text="Usuario:", fg=color_white, bg=color_background, font=(font_label, 12)).pack()
    entry = Entry(screen, textvariable=var, justify=CENTER, font=(font_label, 12))
    entry.focus_force()
    entry.pack(side=TOP, ipadx=30, ipady=6)

    getEnter(screen)
    if flag:
        Button(screen, text="Capturar rostro", fg=color_white, bg=color_black_btn, activebackground=color_background, borderwidth=0, font=(font_label, 14), height="2", width="40", command=login_capture).pack()
    else:
        Button(screen, text="Capturar rostro", fg=color_white, bg=color_black_btn, activebackground=color_background, borderwidth=0, font=(font_label, 14), height="2", width="40", command=register_capture).pack()
    return entry

def face(img, faces):
    data = plt.imread(img)
    for i in range(len(faces)):
        x1, y1, ancho, alto = faces[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        plt.subplot(1,len(faces), i + 1)
        plt.axis("off")
        face = cv2.resize(data[y1:y2, x1:x2],(150,200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(img, face)
        plt.imshow(data[y1:y2, x1:x2])

# REGISTER #
def register_face_db(img, name_user):
    with open(img, "rb") as image_file:
        # Convertir la imagen a base64
        photo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    res_bd = db.registerUser(name_user, photo_base64)
    
    getEnter(screen1)
    if(res_bd["affected"]):
        printAndShow(screen1, "¡Éxito! Se ha registrado correctamente", 1)
    else:
        printAndShow(screen1, "¡Error! No se ha registrado correctamente", 0)
    os.remove(img)

def register_capture():
    cap = cv2.VideoCapture(0)
    user_reg_img = user1.get()
    img = f"{user_reg_img}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Registro Facial", frame)
        if cv2.waitKey(1) == 27:
            break
    
    cv2.imwrite(img, frame)
    cap.release()
    cv2.destroyAllWindows()

    user_entry1.delete(0, END)
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)
    face(img, faces)
    register_face_db(img, user_reg_img)

def register():
    global user1
    global user_entry1
    global screen1

    screen1 = Toplevel(root)
    user1 = StringVar()

    configure_screen(screen1, txt_register)
    user_entry1 = credentials(screen1, user1, 0)

# LOGIN #
def compatibility(img1, img2):
    orb = cv2.ORB_create()

    kpa, dac1 = orb.detectAndCompute(img1, None)
    kpa, dac2 = orb.detectAndCompute(img2, None)

    comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = comp.match(dac1, dac2)

    similar = [x for x in matches if x.distance < 70]
    if len(matches) == 0:
        return 0
    return len(similar)/len(matches)

def login_capture():
    cap = cv2.VideoCapture(0)
    user_login = user2.get()
    img = f"{user_login}_login.jpg"
    img_user = f"{user_login}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Login Facial", frame)
        if cv2.waitKey(1) == 27:
            break
    
    cv2.imwrite(img, frame)
    cap.release()
    cv2.destroyAllWindows()

    user_entry2.delete(0, END)
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)

    face(img, faces)
    getEnter(screen2)

    res_db = db.getUser(user_login)
    if(res_db["affected"]):
        photo_base64 = res_db["photo"]
        photo_data = base64.b64decode(photo_base64)
        
        with open(img_user, "wb") as f:
            f.write(photo_data)
        
        face_reg = cv2.imread(img_user, 0)
        face_log = cv2.imread(img, 0)

        comp = compatibility(face_reg, face_log)
        
        if comp >= 0.94:
            print(f"Compatibilidad del {comp:.1%}")
            printAndShow(screen2, f"Bienvenido, {user_login}", 1)
        else:
            print(f"Compatibilidad del {comp:.1%}")
            printAndShow(screen2, "¡Error! Incopatibilidad de datos", 0)
        os.remove(img_user)
    else:
        printAndShow(screen2, "¡Error! Usuario no encontrado", 0)
    os.remove(img)

def login():
    global screen2
    global user2
    global user_entry2

    screen2 = Toplevel(root)
    user2 = StringVar()

    configure_screen(screen2, txt_login)
    user_entry2 = credentials(screen2, user2, 1)

root = Tk()
root.geometry(size_screen)
root.title("AVM")
root.configure(bg=color_background)

Button(root, text="Iniciar sesión", bg=color_black_btn, fg=color_white, activebackground=color_background, borderwidth=0, font=(font_label, 14), height="2", width="40", command=login).pack(side=TOP)
Button(root, text="Registrarse", bg=color_black_btn, fg=color_white, activebackground=color_background, borderwidth=0, font=(font_label, 14), height="2", width="40", command=register).pack(side=TOP)

root.mainloop()
