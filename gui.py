from contextlib import nullcontext
import os
from time import sleep
import time
import wx

from find_dup import check_for_duplicates
from delete_dup import delete_duplicate, delete_duplicates, delete_file


class MainWindow(wx.Frame):
    path = ''
    auto_delete_dup = False

    size_hash_progress = None
    small_hash_progress = None
    full_hash_progress = None

    delete_duplicate_progress = None

    num_deletion_windows = 0
    num_closed_deletion_windows = 0

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

        if self.auto_delete_dup:
            self.delete_duplicate_progress = wx.ProgressDialog('Deleting duplicaates in progress...', 'Please wait',
                                                               maximum=100, parent=self, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE)
            delete_duplicates(
                duplicates, delete_duplicate_update=self.delete_duplicate_update)
        else:
            self.dups = [dups for _, dups in duplicates.items()]
            self.prompt_for_deletion()
            # for _, dups in duplicates.items():
            #     windows = list()
            #     for dup in dups:
            #         windows.append(PromptForDeletionWindow(
            #             None, 'Delete Photo?', dup))

    def prompt_for_deletion(self):
        if len(self.dups) == 0:
            return
        curr_dups = self.dups.pop()
        self.num_deletion_windows = len(curr_dups)
        self.num_closed_deletion_windows = 0
        for dup_path in curr_dups:
            window = PromptForDeletionWindow(None, 'Delete Photo?', dup_path)
            window.Bind(wx.EVT_CLOSE, self.on_deletion_window_closed)
            window.Show()

    def on_deletion_window_closed(self, evt):
        self.num_closed_deletion_windows += 1
        evt.Skip()

        if self.num_closed_deletion_windows == self.num_deletion_windows:
            self.prompt_for_deletion()

    def all_windows_closed(self, windows):
        for window in windows:
            if window.IsShown():
                return False
        return True

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
            self.full_hash_progress = wx.ProgressDialog('Full hashing in progress...', 'Please wait',
                                                        maximum=100, parent=self, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE)

    def full_hash_update(self, curr_dec):
        self.full_hash_progress.Update(int(curr_dec * 100))

    def delete_duplicate_update(self, curr_dec):
        self.delete_duplicate_progress.Update(int(curr_dec * 100))


def scale_bitmap(bitmap, width, height):
    image = bitmap.ConvertToImage()
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result


class PromptForDeletionWindow(wx.Frame):
    def __init__(self, parent, title, img_file):
        wx.Frame.__init__(self, parent, title=title, size=(600, 600))
        panel = wx.Panel(self)
        self.img_file = img_file
        bitmap = wx.Bitmap(img_file)
        bitmap = scale_bitmap(bitmap, 300, 200)
        vbox = wx.BoxSizer(wx.VERTICAL)
        control = wx.StaticBitmap(panel, -1, bitmap)
        control.SetPosition((0, 0))

        delete_button = wx.Button(panel, -1, "Delete")
        delete_button.Bind(wx.EVT_BUTTON, self.delete_file)

        vbox.Add(control)
        vbox.Add(delete_button)

        panel.SetSizer(vbox)

    def delete_file(self, evt):
        print(f"USER CHOSE TO DELETE: {self.img_file}")
        delete_file(self.img_file)
        self.Close()


app = wx.App(False)
frame = MainWindow(None, 'Duplicate File Finder')
app.MainLoop()
