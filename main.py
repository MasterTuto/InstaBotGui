from InstaBot.main import InstaBot, browser_gen_funcs, process_preselected_users
import InstaBotThread
import wx

class meuPrograma(wx.Frame):
    primaryColor = wx.Colour(2,119,189)
    currentThread = None
    canRepeat = False

    def __setColorWhite(self, widget: wx.Control) -> None:
        widget.SetForegroundColour( wx.Colour(255, 255, 255) )
    
    def __setFontSize(self, widget: wx.Control) -> None:
        widget.SetFont( wx.Font( wx.FontInfo(11).Bold() ) )

    def __styleButton(self, button: wx.Button):
        button.SetBackgroundColour( wx.Colour(255, 255, 255) )
        button.SetForegroundColour( self.primaryColor )
    
    def __bindPlaceholder(self, widget: wx.TextCtrl, placeholder: str) -> None:
        widget.SetForegroundColour( wx.Colour(158, 211, 255) )

        def onKillFocus(event: wx.FocusEvent):
            if widget.GetValue() == "":
                widget.SetValue(placeholder)
                widget.SetForegroundColour( wx.Colour(158, 211, 255) )
            event.Skip()
        
        def onSetFocus(event: wx.FocusEvent):
            if widget.GetValue() == placeholder:
                widget.SetValue("")
                widget.SetForegroundColour( wx.Colour(0, 76, 140, 200) )
            event.Skip()
            

        widget.Bind( wx.EVT_KILL_FOCUS, onKillFocus)
        widget.Bind( wx.EVT_SET_FOCUS,  onSetFocus)
    
    def areInformationValid(self):
        if self.browserChoice.GetSelection() == 0 or self.usernameInput.GetValue() == "" or \
           self.passwordInput.GetValue() == ""    or self.linkInput.GetValue() == "" or \
           self.numberInput.GetValue() == ""      or self.intervalInput.GetValue() == "":
           
           return False

        try:
            int(self.numberInput.GetValue())
            int(self.intervalInput.GetValue())
        except TypeError:
            return False
        
        return True
    
    def startProcess(self, event: wx.CommandEvent):
        if not self.areInformationValid():
            self.progressLabel.SetLabel("DADOS INVALIDOS!")
            event.Skip()
            return

        self.progressLabel.SetLabel("Instanciando bot...")

        choiceIndex = self.browserChoice.GetSelection()-1
        self.bot = InstaBot( choiceIndex+1, browser_gen_funcs[choiceIndex](), self.canRepeat )

        self.progressLabel.SetLabel("Fazendo login...")
        
        username = self.usernameInput.GetValue()
        password = self.passwordInput.GetValue()        
        if self.facebookLogCheckBox.GetValue() is True:
            self.bot.log_in_via_facebook(username, password)
        else:
            self.bot.log_in_native(username, password)

        self.progressLabel.SetLabel("Enviando mensagens...")
        
        promo_url         = self.linkInput.GetValue()
        text_to_send      = self.textInput.GetValue() if self.textInput.GetValue() != "Mensagem que acompanha a marcação..." else ""
        preselected_users = process_preselected_users( self.usersListCtrl.GetValue().split("\n") )
        number_of_people  = int(self.numberInput.GetValue())
        interval          = int(self.intervalInput.GetValue())


        self.bot.send_messages(promo_url, text_to_send, preselected_users, number_of_people, interval)
    
    def createThreadAndStartProcess(self, event : wx.CommandEvent):
        if self.currentThread == None:
            self.currentThread = InstaBotThread.InstaBotThread(target=self.startProcess, args=[event])

        if self.startStopButton.GetLabel() == "Iniciar":
            self.startStopButton.SetLabel("Parar")
            self.currentThread.start()

        elif self.startStopButton.GetLabel() == "Parar":
            self.bot.close_browser()
            self.currentThread.stop()
            
            self.startStopButton.SetLabel("Iniciar")
            self.progressLabel.SetLabel("")
            
            self.currentThread = None


    def __init__(self, parent, title, *args, **kwargs):
        wx.Frame.__init__(self,
            parent=parent,
            title=title,
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX,
            size=(500, 500),
            *args, **kwargs
        )

        self.SetBackgroundColour(self.primaryColor)

        leftSizer = self.getLeftSizer()
        rightSizer = self.getRightSizer()

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.SetMinSize(500, 500)

        mainSizer.Add(leftSizer, 1, wx.EXPAND | (wx.ALL ^ wx.RIGHT), 12)
        mainSizer.Add(rightSizer, 1, wx.EXPAND | wx.ALL, 12)

        self.SetSizer(mainSizer)
        self.SetAutoLayout(1)
        mainSizer.Fit(self)
        self.Show(True)
    
    def getLeftSizer(self):
        leftSizer = wx.BoxSizer(wx.VERTICAL)

        leftSizer.Add( self.getLoginWithFacebookSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getLoginDataSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getBrowserSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getLinkToPubSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getTextThatGoesAlongSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getNumberOfPeopleSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getIntervalSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getStartStopButton(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )
        leftSizer.Add( self.getProgressLabelSizer(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10 )

        return leftSizer

    def getLoginWithFacebookSizer(self):
        loginWithFacebookSizer = wx.BoxSizer(wx.HORIZONTAL)

        facebookLogIcon     = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/facebook.png"))
        facebookLogLabel    = wx.StaticText(self, label="Logar com Facebook?")
        self.facebookLogCheckBox = wx.CheckBox(self)

        self.__setColorWhite(facebookLogLabel)
        self.__setFontSize(facebookLogLabel)

        loginWithFacebookSizer.Add( facebookLogIcon, 0, wx.EXPAND | wx.RIGHT, 4 )
        loginWithFacebookSizer.Add( facebookLogLabel, 1, wx.EXPAND | (wx.ALL ^ wx.LEFT), 10)
        loginWithFacebookSizer.Add( self.facebookLogCheckBox, 0, wx.EXPAND | wx.ALL, 10)

        return loginWithFacebookSizer
    
    def getLoginDataSizer(self):
        loginDataSizer = wx.BoxSizer(wx.HORIZONTAL)

        usernameIcon  = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/account.png"))
        self.usernameInput = wx.TextCtrl(self, value="Usuário, email ou telefone")

        passwordIcon  = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/lock.png"))
        self.passwordInput = wx.TextCtrl(self, value="Senha")

        self.__setFontSize(self.usernameInput)
        self.__bindPlaceholder(self.usernameInput, "Usuário, email ou telefone")
        self.__setFontSize(self.passwordInput)
        self.__bindPlaceholder(self.passwordInput, "Senha")


        loginDataSizer.Add( usernameIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        loginDataSizer.Add( self.usernameInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        loginDataSizer.Add( passwordIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        loginDataSizer.Add( self.passwordInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return loginDataSizer

    def getBrowserSizer(self):
        browserSizer = wx.BoxSizer(wx.HORIZONTAL)

        browsers = [
            'Selecionar navegador',
            'Chrome',
            'Chromium',
            'FireFox',
            'Internet Explorer',
            'Microsoft Edge'
        ]

        browserIcon   = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/web.png"))
        self.browserChoice = wx.Choice(self, choices=browsers)

        self.browserChoice.SetSelection(0)

        browserSizer.Add(browserIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        browserSizer.Add(self.browserChoice, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return browserSizer

    def getLinkToPubSizer(self):
        linkToPubSizer = wx.BoxSizer(wx.HORIZONTAL)

        linkIcon  = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/link-box-variant-outline.png"))
        self.linkInput = wx.TextCtrl(self, value="Digite o link da publicação...")

        self.__setFontSize(self.linkInput)
        self.__bindPlaceholder(self.linkInput, "Digite o link da publicação...")

        linkToPubSizer.Add(linkIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        linkToPubSizer.Add(self.linkInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return linkToPubSizer
    
    def getTextThatGoesAlongSizer(self):
        textThatGoesAlongSizer = wx.BoxSizer(wx.HORIZONTAL)

        textIcon   = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/format-color-text.png"))
        self.textInput = wx.TextCtrl(self, value="Mensagem que acompanha a marcação...")

        self.__setFontSize(self.textInput)
        self.__bindPlaceholder(self.textInput, "Mensagem que acompanha a marcação...")

        textThatGoesAlongSizer.Add(textIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        textThatGoesAlongSizer.Add(self.textInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return textThatGoesAlongSizer
    
    def getNumberOfPeopleSizer(self):
        numberOfPeopleSizer = wx.BoxSizer(wx.HORIZONTAL)

        numberIcon  = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/tag-faces.png"))
        self.numberInput = wx.TextCtrl(self, value="Quantidade de pessoas para marcar...")

        self.__setFontSize(self.numberInput)
        self.__bindPlaceholder(self.numberInput, "Quantidade de pessoas para marcar...")

        numberOfPeopleSizer.Add(numberIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        numberOfPeopleSizer.Add(self.numberInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return numberOfPeopleSizer
    
    def getIntervalSizer(self):
        intervalSizer = wx.BoxSizer(wx.HORIZONTAL)

        intervalIcon   = wx.StaticBitmap(self, bitmap=wx.Bitmap("./assets/clock.png"))
        self.intervalInput = wx.TextCtrl(self, size=(-1, 30), value="Intervalo entre os comentários...")

        self.__setFontSize(self.intervalInput)
        self.__bindPlaceholder(self.intervalInput, "Intervalo entre os comentários...")

        intervalSizer.Add(intervalIcon, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 4)
        intervalSizer.Add(self.intervalInput, 1, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)

        return intervalSizer
    
    def getStartStopButton(self):

        self.startStopButton = wx.Button(self, label="Iniciar", size=(-1, 40))

        self.startStopButton.Bind(wx.EVT_BUTTON, self.createThreadAndStartProcess)

        self.__styleButton(self.startStopButton)

        return self.startStopButton
    
    def getProgressLabelSizer(self):
        progressLabelSizer = wx.BoxSizer(wx.HORIZONTAL)

        progressStatic = wx.StaticText(self, label="PROGRESSO: ")
        self.progressLabel  = wx.StaticText(self, label="")

        self.__setColorWhite(progressStatic)
        self.__setFontSize(progressStatic)

        self.__setColorWhite(self.progressLabel)
        self.__setFontSize(self.progressLabel)

        progressLabelSizer.Add(progressStatic, 0, wx.EXPAND, 0)
        progressLabelSizer.Add(self.progressLabel, 0, wx.EXPAND | wx.LEFT, 10)

        return progressLabelSizer
    
    def getRightSizer(self):
        rightSizer = wx.BoxSizer(wx.VERTICAL)

        self.usersListCtrl =  wx.TextCtrl( self, style=wx.TE_MULTILINE )

        rightSizer.Add( self.getUsersLabel() )
        rightSizer.Add( self.getOpenFileBtnSizer(), 0, wx.CENTER, 0)
        rightSizer.Add( self.usersListCtrl, 1, wx.EXPAND )

        return rightSizer

    def getUsersLabel(self) -> wx.StaticText:
        usersLabel    =  wx.StaticText(self, label="Lista de usuários para marcar: @")

        self.__setColorWhite(usersLabel)
        self.__setFontSize(usersLabel)

        return usersLabel

    def onRadioButtonClick(self, event: wx.CommandEvent):
        radioButton = event.GetEventObject()
        self.canRepeat = radioButton.GetLabel() == "Sim"


    def getOpenFileBtnSizer(self):
        openFileBtnSizer = wx.BoxSizer(wx.HORIZONTAL)

        openFileBtn = wx.Button(self, label="Abrir arquivo")
        repeatLabel = wx.StaticText(self, label="Pode repetir usuário? ")
        canRepeatRadio   = wx.RadioButton(self, label="Sim", style=wx.RB_GROUP)
        cantRepeatRadio  = wx.RadioButton(self, label="Não")
        
        self.__styleButton(openFileBtn)
        self.__setColorWhite(repeatLabel)
        self.__setColorWhite(canRepeatRadio)
        self.__setColorWhite(cantRepeatRadio)

        canRepeatRadio.SetValue(True)

        openFileBtn.Bind(wx.EVT_BUTTON, lambda e: self.usersListCtrl.LoadFile( wx.FileSelector("Abrir arquivo") ))
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButtonClick)

        openFileBtnSizer.Add(openFileBtn)      
        openFileBtnSizer.Add(repeatLabel, 0, wx.LEFT, 20)     
        openFileBtnSizer.Add(canRepeatRadio)     
        openFileBtnSizer.Add(cantRepeatRadio)

        return openFileBtnSizer

if __name__ == "__main__":
    prog = wx.App()
    meuPrograma(None, "InstaBot GUI v0.2")
    prog.MainLoop()