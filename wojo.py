import select
import socket
import time
import sys
import math
import tkinter as tk
from tkinter import messagebox

import rsa
from choice import choice


bg = "#fff59d"
msg_box_color_yours = "#017ced"
msg_box_color_other = "#f50057"
msg_box_txt_color_yours = "#ffffff"
msg_box_txt_color_other = "#ffffff"
bufsize = 36

print()

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



destip = input("Dest ip: ")
choice = bool(choice(["Start new connection", "Join open connection"]))

def listen(socket, port):
	socket.bind(("127.0.0.1", port))
	socket.listen(1)
	print("Listening for a new connection...")

	clientip, addr = socket.accept()
	print(f"Connection established at {addr}...")

	return clientip


def connect(socket, ip, port):
	while True:
		try:
			print("Trying to connect...")
			socket.connect((ip if ip else "127.0.0.1", port))
		except ConnectionRefusedError:
			continue
		print("Connected")
		break


if choice:
	n, e, d = rsa.generate()	
	connect(sock1, destip, 1234)
	recv_sock = listen(sock2, 5555)
	send_sock = sock1
else:
	recv_sock = listen(sock1, 1234)
	connect(sock2, destip, 5555)
	send_sock = sock2



win = tk.Tk()
win.configure(background=bg)
win.iconbitmap("./favicon.ico")
win.geometry("400x525")
win.pack_propagate(0)
win.title("WoJo Messenger Extreme")

msg_frame = tk.Frame(win, bg=bg, padx=8, pady=4)
msg_frame.pack(fill=tk.BOTH, side=tk.TOP)


msg_send_frame = tk.Frame(win)
msg_send_frame.pack(fill=tk.X, side=tk.BOTTOM)
msg_input = tk.Entry(msg_send_frame)
msg_input.pack(fill=tk.X, side=tk.BOTTOM)
msg_send_btn_img = tk.PhotoImage(file="send.png")


def clear(_=None):
	for old_msg in msg_frame.winfo_children():
		old_msg.destroy()

def close():
	# win.destroy()
	send_sock.close()
	recv_sock.close()
	sys.exit(0)

def send(_=None):
	msg = msg_input.get()
	if msg == "/clear":
		clear()
		return
	msg_input.delete(0, tk.END)
	recv(msg, True)
	send_sock.send(msg.encode("utf-8"))


def recv(recv_msg, you):
	# Shit to ensure that own messages wil be recieved in bufsize
	for index in range(math.ceil(len(recv_msg)/bufsize)):
		recv_part = recv_msg[index*bufsize:index*bufsize+bufsize]
		msg_box = tk.Label(msg_frame, text=recv_part, bg=msg_box_color_yours if you else msg_box_color_other,
		                   borderwidth=1, fg=msg_box_txt_color_yours if you else msg_box_txt_color_other, font=("Roboto", 11, "normal"), padx=4, relief="raised")
		msg_box.pack(anchor=tk.E if you else tk.W)



msg_send_btn = tk.Button(msg_send_frame, image=msg_send_btn_img, relief="flat", cursor="hand2", command=send)
msg_send_btn.pack(side=tk.RIGHT, in_=msg_input)
msg_input.bind("<Return>", send)
msg_input.bind("<Escape>", clear)
msg_frame.bind("")

while True:
	win.protocol("WM_DELETE_WINDOW", close)
	win.update()
	try: ready = select.select([recv_sock], [], [], 0)
	except ValueError:
		messagebox.showerror("Disconnection error", "An error occurred, the other probbably diconnected.")
		close()

	if ready[0]:
		recv_data = recv_sock.recv(bufsize)
		if not recv_data: close()
		recv_msg = recv_data.decode("utf-8")
		recv(recv_msg, False)
		print(recv_msg, "<-- recvd")
