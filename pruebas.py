import wx
import wx.grid
import time
 
app = wx.App()
window = wx.Frame(None, -1, title='Test', size=(960, 850), pos = (-5, 0))
background = wx.Panel(window)
background.SetBackgroundColour("Blue")
 
grid = wx.grid.Grid(background, size=(800,400), pos=(0,0))
grid.CreateGrid(6,6)
for c in range(6): grid.SetColSize(c,120)
for r in range(6):
    grid.SetRowLabelValue(r,time.strftime('%H:%M:%S'))
    for c in range(6):
        grid.SetCellValue(r, c, "Before Insert: R"+str(r)+"/C"+str(c))
grid.InsertRows(1,1,False)
grid.SetRowLabelValue(1,'Inserted Row')
 
window.Show()
app.MainLoop()