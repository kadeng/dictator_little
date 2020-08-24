# ----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
# ----------------------------------------------------------------------

import wx
import wx.richtext as rt
import winsound

import base64

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(350, 250))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

        self.CreateStatusBar()
        self.dictating = False

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)
        toolbar = wx.Panel(panel)

        # richtext control

        rtext: rt.RichTextCtrl = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.TE_WORDWRAP | wx.NO_BORDER);
        rtext.SetSizeHints((600, 200))

        btn = wx.Button(toolbar, -1, "Diktat beginnen")

        funbtn = wx.Button(toolbar, -1, "Diktat beenden")
        self.startbutton = btn
        self.endbutton = funbtn

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnStartDictation, btn)
        self.Bind(wx.EVT_BUTTON, self.OnEndDictation, funbtn)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.Add(btn, 0, wx.ALL, 10)
        tsizer.Add(funbtn, 0, wx.ALL, 10)

        toolbar.SetSizer(tsizer)
        toolbar.Layout()
        sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar.SetSizeHints(600, 50)
        rtext.AcceptsFocus()
        rtext.AcceptsFocusFromKeyboard()
        sizer.Add(toolbar, 0, wx.ALL, 10)
        sizer.Add(rtext, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Layout()
        panel.CanAcceptFocus()
        panel.AcceptsFocus()
        rtext.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        rtext.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseDown)
        rtext.Bind(wx.EVT_CHAR, self.OnKeyUp)
        rtext.SetFontScale(1.8)
        self.dictation_text = """Im Sommer machten wir an einem Strand im schönen Italien Urlaub. Das Land ist bekannt für seine tausend verschiedenen Pizzen, daher hatte ich mich besonders darauf gefreut. Nachdem der Flug endlich vorbei war, hoffte ich auf ein paar aufregende Erlebnisse. Auf einer Landkarte hatte ich mir vorher schon angeschaut, wie man an den Strand kommt. Auf dem Weg dorthin lag eine verschlossene Geldkassette im Staub. Ich nahm sie mit zu meinen Eltern, die versuchten, sie aufzumachen. Nachdem ihnen das gelungen war, entdeckten wir einen Zettel mit einem besonders schönen Lied darauf. Seitdem singen wir unser Lied aus dem Land des Stiefels immer dann, wenn wir gerne wieder eine Urlaubsreise machen möchten."""
        self.endbutton.Enable(False)
        rtext.SetValue(self.dictation_text)
        # And also use a sizer to manage the size of the panel such
        # that it fills the frame
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.Layout()
        self.rtext: rt.RichTextCtrl = rtext
        wx.CallAfter(self.rtext.SetFocus)

    def OnMouseDown(self, evt: wx.MouseEvent):
        if not self.dictating:
            evt.Skip(True)
            return
        if evt.ButtonDown(1):
            self.rtext.SetInsertionPointEnd()
            evt.Skip(False)

    def OnKeyDown(self, evt):
        if not self.dictating:
            evt.Skip(True)
            return
        keycode = evt.GetKeyCode()
        # self.rtext.SetInsertionPointEnd()
        if keycode not in [314, 315, 316, 317]:
            evt.Skip(True)
        return True

    def OnKeyUp(self, evt: wx.KeyEvent):
        if not self.dictating:
            evt.Skip(True)
            return
        if evt.GetKeyCode() in [8]:
            evt.Skip(True)
        else:
            evt.Skip(False)
            text = self.rtext.GetValue()
            actual_char = chr(evt.GetUnicodeKey())
            expected_char = self.dictation_text[len(text)]
            if actual_char == expected_char:
                self.rtext.EndUnderline()
                self.rtext.WriteText(actual_char)
                try:
                    expected_char = self.dictation_text[len(text)+1]
                    if expected_char in ';.,:!?" ':
                        self.say_next_word()
                except:
                    pass
            else:
                self.rtext.BeginUnderline()
                self.rtext.BeginTextColour(wx.Colour(255, 0, 0, 255))
                self.rtext.WriteText(actual_char)
                self.rtext.EndTextColour()
                self.rtext.EndUnderline()
                winsound.MessageBeep(500)

    def play_and_stop(self, sound):
        from threading import Timer
        player = sound.play()
        t = Timer(player.source.duration, player.next_source)
        t.start()


    def OnStartDictation(self, evt):
        """Event handler for the button click."""
        self.dictating = True
        self.dictation_text = self.rtext.GetValue()
        dtext = self.dictation_text.replace(".", " Punkt").replace(",", " Komma").replace(":", "Doppelpunkt")\
            .replace("?", " Fragezeichen").replace("!", " Ausrufezeichen").replace(";", " Semikolon").replace("\"", " Anführungszeichen")
        words = dtext.strip().split(" ")
        import os
        from gtts import gTTS
        import re
        import pyglet
        os.makedirs("tts_mp3", exist_ok=True)
        medias = []
        for word in words:
            fname = "tts_mp3/%s.mp3" % (base64.b64encode(word.encode("utf-8")).decode("utf-8"))
            if not os.path.exists(fname):
                tts = gTTS(text=word, lang='de')
                tts.save(fname)
            medias.append(pyglet.media.load(fname, streaming=False))
        self.dwords = words
        self.dmedias = medias
        self.rtext.SetValue("")
        self.rtext.SetInsertionPointEnd()
        self.rtext.SetFocus()
        self.startbutton.Enable(False)
        self.endbutton.Enable(True)
        self.say_next_word()

    def say_next_word(self):
        text = self.rtext.GetValue()
        import re
        word_idx = 0
        for c in self.dictation_text[:len(text)+1]:
            if c in ';.,:!?" ':
                word_idx += 1
        word = self.dmedias[word_idx]
        self.play_and_stop(word)

    def OnEndDictation(self, evt):
        """Event handler for the button click."""
        self.dictating = False
        self.rtext.SetValue(self.dictation_text)
        self.endbutton.Enable(False)
        self.startbutton.Enable(True)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Dictator Little")
        self.SetTopWindow(frame)

        print("Print statements go to this stdout window by default.")

        frame.Show(True)
        return True


app = MyApp(redirect=True)
app.MainLoop()

