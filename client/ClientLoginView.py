from styles.styles import *


class ClientLoginView:
    def __init__(self, client, rootWindow):
        self.client = client
        self.rootWindow = rootWindow

        self.rootWindow.withdraw()
        
        self.loginWindow = Toplevel()
        self.loginWindow.protocol("WM_DELETE_WINDOW", self.rootWindow.destroy)
        self.loginWindow.title("Login")
        self.loginWindow.resizable(width = False, height = False)
        self.loginWindow.configure(width = 400, height = 300, background=dark_blue)
        
        self.description = Header1(self.loginWindow, darkmode=True,
                                    text = "Please log in to continue",
                                    justify = CENTER)
         
        self.description.place(relheight = 0.15,
                       relx = 0.2,
                       rely = 0.07)
        # Username
        self.usernameLabel = Header2(self.loginWindow, darkmode=True, text = "Username: ", justify=LEFT)
        self.usernameLabel.place(relheight = 0.2,
                                    relx = 0.15,
                                    rely = 0.2)
        
        self.usernameField = TextField(self.loginWindow)
         
        self.usernameField.place(relwidth = 0.4,
                             relheight = 0.12,
                             relx = 0.4,
                             rely = 0.25)
        # Password
        self.pswdLabel = Header2(self.loginWindow, darkmode=True, text = "Password: ", justify=LEFT)
        self.pswdLabel.place(relheight = 0.2,
                                    relx = 0.15,
                                    rely = 0.35)
        
        self.pswdField = TextField(self.loginWindow, show="*")
         
        self.pswdField.place(relwidth = 0.4,
                             relheight = 0.12,
                             relx = 0.4,
                             rely = 0.4)
        
        self.usernameField.focus()
        self.pswdField.focus()

        self.loginWindow.bind('<Return>', (lambda event: self.saveUserInput(self.usernameField.get(), self.pswdField.get())))
        self.loginButton = CustomButton(self.loginWindow,
                         text = "Log in",
                         width = 25,
                         command = lambda: self.saveUserInput(self.usernameField.get(), self.pswdField.get()))
         
        self.loginButton.place(relx = 0.15, rely = 0.60)

    def saveUserInput(self, name, password):
        # add some user validation
        self.loginWindow.destroy()
        
        self.client.startMainApp(name, password)
