from tkinter import *
from PIL import Image, ImageTk
import socket
import qrcode
from resizeimage import resizeimage
import numpy as np
import pyautogui
import _thread
import select
import time


class Server:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x700+200+50")  # Width, Height, Distance from side and top
        self.root.title("GUI Development | Developed by Avinash")  # Setting the Title
        self.root.resizable(False, False)  # Resize width and height false

        title = Label(self.root,
                      text="GUI Development",
                      font=("times new roman", 40),
                      bg="#053246", fg="white",    # background and foreround
                      ).place(x=0, y=0, relwidth=1)    # relwidth is for center

        # ------------ Instruction Windows ---------------

        instruction_Frame = Frame(self.root, bd=2,  # border pixels
                          relief=RIDGE,  # border style
                          bg='white')
        instruction_Frame.place(x=50, y=100, width=680, height=580)

        instruction_title = Label(instruction_Frame,
                          text="To use this app on your computer:",
                          font=("goudy old style", 20),
                          bg="white"
                          # bg="#043246", fg="white",  # background and foreround
                          ).place(x=0, y=10, relwidth=1)

        instruction_connect = Label(instruction_Frame, text="1. Connect your Phone and Computer to the same wifi.", font=("times new roman", 15), bg="white") \
            .place(x=20, y=60)
        instruction_pair = Label(instruction_Frame, text="2. Click on Start Wave AI. Scan the QR Code to pair your devices.", font=("times new roman", 15), bg="white") \
            .place(x=20, y=100)
        instruction_gestures = Label(instruction_Frame,
                                 text="3. Here are the gestures to use Wave AI",
                                 font=("times new roman", 15), bg="white") \
            .place(x=20, y=140)
        # Images can be placed on buttons or labels
        instruction_photo = Image.open("unsplash.jpg")
        test = ImageTk.PhotoImage(instruction_photo)
        # Using self because We can change it later
        sign_code = Label(instruction_Frame, image=test, font=("times new roman", 15), bg="#3f51b5", fg="white",
                             bd=1, relief=RIDGE)
        sign_code.image = test
        sign_code.place(x=20, y=200, width=640, height=360)

        # ----------------- QR Scan Window ----------------------------

        qr_code = Label(self.root, text="QR Scan Here", font=("times new roman", 15), bg="#3f51b5", fg="white",
                             bd=1, relief=RIDGE)
        qr_code.place(x=800, y=100, width=250, height=250)
        IP = self.getIP()
        qr_data = qrcode.make(IP)
        qr_data = resizeimage.resize_cover(qr_data, [250, 250])
        self.im = ImageTk.PhotoImage(qr_data)
        qr_code.config(image=self.im)

        # We will use the attributes to create the chat server here

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    # ALl the functions in the mouse_Server.py will be methods here



root = Tk()
obj = Server(root)

# IP = getIP()
IP = obj.getIP()

HEADER_SIZE = 100
PORT = 1234
SOCKET_LIST = []
l_ctr = 0
coords = np.array([[96, 54]] * 10)
pyautogui.FAILSAFE = False
print(f'IP and PORT at {IP} and {PORT}')


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    SOCKET_LIST.append(server_socket)

    print(f'Chat server started at {IP} and {PORT}')
    ptime = time.time()

    while True:
        # 4th arg, time_out = 0: poll and never block
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:
            if sock == server_socket:
                clientsocket, address = server_socket.accept()
                SOCKET_LIST.append(clientsocket)
                print(f'Connection from {address} has been established. \n')
                broadcast(server_socket, clientsocket, "Welcome to the server \n")
            # A message from client. Not a new connection
            else:
                data = receive_message(sock)
                # data = sock.recv(HEADER_SIZE)
                if data:
                    broadcast(server_socket, sock, data)
                    ctime = time.time()
                    fps = 1 / (ctime - ptime)
                    ptime = ctime
                    print(f"FPS: {int(fps)}")
                else:
                    if sock in SOCKET_LIST:
                        SOCKET_LIST.remove(sock)

                    broadcast(server_socket, sock, "Did not receive message: Client is offline \n")


def receive_message(sock):
    try:
        message = sock.recv(HEADER_SIZE)
        if not len(message):
            return False

        return message
    except:
        return False


def calcXY(message):
    x = (1.0 - float(message.split(' ')[2])) * 200
    y = float(message.split(' ')[1]) * 100
    z = float(message.split(' ')[1])
    return x, y, z


def broadcast(server_socket, sock, message):
    for socket in SOCKET_LIST:

        if socket != server_socket:
            try:
                if type(message) == bytes:
                    message = message.decode()

                global l_ctr
                global coords
                if message.split(' ')[0] == "MOUSE":

                    x, y, z = calcXY(message)
                    coords = np.append(coords, [[x, y]], axis=0)
                    coords = coords[-10:]

                    # This is old technique
                    # current = coords[-5:].mean(axis=0)
                    # pyautogui.moveTo(current[0], current[1])   # Average Technique

                    # print(f"MOUSE: {x}, {y}, {z}")
                    if abs(x - coords[0][0]) < 50 and abs(y - coords[0][1]) < 25: # and z > 0.5:  # This is 25% of total scope
                        pyautogui.move((x - coords[0][0]) * 1.25, (y - coords[0][1]) * 1.25)    # Relative Technique
                    else:
                        coords = np.append(coords, [[x, y]], axis=0)
                        coords = coords[-10:]

                    if l_ctr > 0:
                        l_ctr = 0
                        pyautogui.mouseUp(button='left')

                elif message == "RIGHT ":
                    # print("RIGHT")
                    pyautogui.click(button='right')
                elif message == "SCROLL UP ":
                    # print("SCROLL UP")
                    pyautogui.scroll(1)
                elif message == "SCROLL DOWN ":
                    # print("SCROLL DOWN")
                    pyautogui.scroll(-1)
                elif message.split(' ')[0] == "LEFT":
                    x, y, z = calcXY(message)
                    l_ctr = l_ctr + 1
                    coords = np.append(coords, [[x, y]], axis=0)
                    coords = coords[-10:]
                    # print(f"LEFT : {l_ctr}, {x}, {y}, {z}")
                    if l_ctr == 2:
                        pyautogui.click(button='left')
                    elif l_ctr > 5:

                        # Average techniques used earlier
                        # pyautogui.mouseDown(coords[-5:].mean(axis=0)[0], coords[-5:].mean(axis=0)[1], button='left')

                        pyautogui.mouseDown(button='left')

                        if abs(x - coords[0][0]) < 50 and abs(y - coords[0][1]) < 25:
                            pyautogui.move((x - coords[0][0]) * 1.25, (y - coords[0][1]) * 1.25)
                        else:  # If the distance is too large, append the new position
                            coords = np.append(coords, [[x, y]], axis=0)
                            coords = coords[-10:]

            except:
                # broken socket connection
                socket.close()
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)


_thread.start_new_thread(chat_server, () )   # Replace socket creation with chat_server
root.mainloop()
