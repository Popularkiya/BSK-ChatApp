from styles.styles import *
from fileupload.fileuploader import *


class ClientChatView:
    OPTIONS = [
        "ECB",
        "CBC"
    ]

    filepath = ""

    def __init__(self, window, clientName, controller):
        self.rootWindow = window
        self.username = clientName

        self.controller = controller

        self.rootWindow.protocol("WM_DELETE_WINDOW", self.controller.stopCommunication)
        self.rootWindow.deiconify()
        self.rootWindow.title("BSK-ChatApp")
        self.rootWindow.resizable(width=False,
                                  height=False)
        self.rootWindow.configure(width=470,
                                  height=550,
                                  bg=black)
        self.headLabel = Header1B(self.rootWindow, darkmode=True,
                                  text=self.username,
                                  pady=5)

        self.headLabel.place(relwidth=1)
        self.line = Label(self.rootWindow,
                          width=450,
                          bg=blue)

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = MessageConsole(self.rootWindow,
                                       width=20,
                                       height=2,
                                       padx=5,
                                       pady=5)

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.bottomLabel = Label(self.rootWindow,
                                 bg=blue,
                                 height=80)

        self.bottomLabel.place(relwidth=1,
                               rely=0.75)

        self.messageEntry = MultiLineTextFiled(self.bottomLabel)

        # place the given widget
        # into the gui window
        self.messageEntry.place(relwidth=0.74,
                                relheight=0.1,
                                rely=0.008,
                                relx=0.011)

        self.messageEntry.focus()

        # Send Button
        self.rootWindow.bind('<Return>', (lambda event: self.sendMessage(self.messageEntry.get())))
        self.sendButton = CustomButton(self.bottomLabel,
                                       text="Send",
                                       width=20,
                                       command=lambda: self.controller.sendMessage(self.messageEntry.get()))

        self.sendButton.place(relx=0.77,
                              rely=0.008,
                              relheight=0.03,
                              relwidth=0.22)
        # Add file Button
        self.addFileButton = CustomButton(self.bottomLabel,
                                          text="Add file",
                                          width=20,
                                          command=lambda: self.addFileButtonOnClick())

        self.addFileButton.place(relx=0.77,
                                 rely=0.040,
                                 relheight=0.03,
                                 relwidth=0.22)

        self.textCons.config(cursor="arrow")

        #cipher drop down menu
        self.cipherPicker = StringVar(self.bottomLabel)
        self.cipherPicker.set(self.OPTIONS[0]) # default value

        w = OptionMenu(self.bottomLabel, self.cipherPicker, *self.OPTIONS)
        w.config(bg=gray, fg=white)
        w["menu"].config(bg=gray, fg=white)
        w.place(relx=0.77,
                 rely=0.072,
                 relheight=0.03,
                 relwidth=0.22)

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def addFileButtonOnClick(self):
        uploader = FileUploader()
        self.filepath = uploader.file.name
        print(self.filepath)
    
    # def addController(self, controller):
    #     self.controller = controller
    
    def displayMessage(self, message):
        # insert messages to text box
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "\n" + message + "\n")

        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def displayAcknowledgement(self, user):
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, user + " ")

        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    
    def sendMessage(self, message):
        self.controller.cipherMode = self.cipherPicker.get()
        # self.cipherPicker.get() # get the dropdown list value
        # print(self.cipherPicker.get()) # debugging
        self.messageEntry.delete(0, 'end')
        if self.filepath:
            self.controller.sendFile(self.filepath)
            self.filepath = ""
        else:
            self.controller.sendMessage(message)
