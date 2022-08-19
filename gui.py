from contextlib import nullcontext
import os
from time import sleep
import wx

from find_dup import check_for_duplicates


class MainWindow(wx.Frame):
    path = ''
    auto_delete_dup = False

    size_hash_progress = None
    small_hash_progress = None
    full_hash_progress = None

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600, 600))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.browse_button = wx.Button(panel, -1, 'Select Folder')
        self.browse_button.Bind(wx.EVT_BUTTON, self.on_browse_clicked)
        self.start_button = wx.Button(panel, -1,
                                      f'Please select a folder before clicking this button or it won\'t do anything!')
        self.start_button.Bind(wx.EVT_BUTTON, self.start_finding_duplicates)

        self.auto_delete_dup_chk = wx.CheckBox(
            panel, label="Auto Delete Files")
        self.auto_delete_dup_chk.Bind(
            wx.EVT_CHECKBOX, self.on_auto_delete_dup_chk)
        vbox.Add(self.browse_button)
        vbox.Add(self.auto_delete_dup_chk)
        vbox.Add(self.start_button)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()
        self.Fit()

    def on_browse_clicked(self, event):
        dialog = wx.DirDialog(
            self, message='Choose a folder', style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.path = dialog.GetPath()
            self.start_button.SetLabel(
                f'Start finding duplicates in {self.path}')
            self.Layout()

    def start_finding_duplicates(self, event):
        self.size_hash_progress = wx.ProgressDialog('Size hashing in progress...', 'Please wait',
                                                    maximum=100, parent=self, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE)
        duplicates = check_for_duplicates(self.path, size_hash_update=self.size_hash_update,
                                          small_hash_update=self.small_hash_update, full_hash_update=self.full_hash_update)
        self.Layout()
        if self.auto_delete_dup:
            delete_duplicates(duplicates)
        else:
            pass

            
    # this is very hacky but this is just for fun mostly here
    def on_auto_delete_dup_chk(self, event):
        self.auto_delete_dup = event.GetEventObject().GetValue()

    def size_hash_update(self, curr_dec):
        self.size_hash_progress.Update(int(curr_dec * 100))
        if curr_dec == 1 and not self.small_hash_progress:
            self.small_hash_progress = wx.ProgressDialog('Small hashing in progress...', 'Please wait',
                                                         maximum=100, parent=self, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE)

    def small_hash_update(self, curr_dec):
        self.small_hash_progress.Update(int(curr_dec * 100))

        if curr_dec == 1 and not self.full_hash_progress:
            self.small_hash_progress.Hide()
            self.full_hash_progress = wx.ProgressDialog('Full hashing in progress...', 'Please wait',
                                                        maximum=100, parent=self, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE)

    def full_hash_update(self, curr_dec):
        if curr_dec >= 1:
            self.full_hash_progress.Update(99)
        self.full_hash_progress.Update(int(curr_dec * 100))


app = wx.App(False)
frame = MainWindow(None, 'Duplicate File Finder')
app.MainLoop()
