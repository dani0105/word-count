import csv
from random import choices
import re
from collections import Counter
import pathlib
from turtle import update

import PyPDF2
import docx2txt
import wx
import wx.grid
import wx.xrc

import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords


class MainFrame(wx.Frame):

    filePath = "./import/"

    # Ignore stopwords from the text. Default language is Spanish for now.
    emptyWord = set(stopwords.words('spanish'))

    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(710, 300),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )
        self.__iniComponents()
        self.dictionary = {}
        self.sortedReverse = True

    def __iniComponents(self):
        """
        Create UI
        """
        Container = wx.GridSizer(1, 2, 0, 0)

        self.dataView = wx.grid.Grid(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0
        )

        # Grid
        self.dataView.CreateGrid(0, 3)
        self.dataView.EnableEditing(False)
        self.dataView.EnableGridLines(True)
        self.dataView.EnableDragGridSize(False)
        self.dataView.SetMargins(0, 0)

        # Columns
        self.dataView.EnableDragColMove(False)
        self.dataView.EnableDragColSize(True)
        self.dataView.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.dataView.SetColLabelSize(50)
        self.dataView.SetColLabelValue(0, "Palabra")
        self.dataView.SetColLabelValue(1, "Longitud\nde la\npalabra")
        self.dataView.SetColLabelValue(2, "Cantidad")

        # Rows
        self.dataView.EnableDragRowSize(False)
        self.dataView.SetRowLabelSize(80)
        self.dataView.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Cell Defaults
        self.dataView.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        Container.Add(self.dataView, 1, wx.ALL | wx.EXPAND, 5)

        ContainerRight = wx.BoxSizer(wx.VERTICAL)

        self.lblTitle = wx.StaticText(
            self, wx.ID_ANY, "WordCount", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.lblTitle.Wrap(-1)
        ContainerRight.Add(self.lblTitle, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.lblFilePiker = wx.StaticText(
            self,
            wx.ID_ANY,
            "Seleccione el archivo",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.lblFilePiker.Wrap(-1)
        ContainerRight.Add(self.lblFilePiker, 0, wx.ALL, 5)

        self.filePiker = wx.FilePickerCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            "Seleccione el archivo",
            "*.pdf;*.doc*;*.txt",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.FLP_DEFAULT_STYLE,
        )
        ContainerRight.Add(self.filePiker, 0, wx.ALL | wx.EXPAND, 5)

        # Dropdown for language selection
        self.lblDropdown = wx.StaticText(
            self,
            wx.ID_ANY,
            "Seleccione el idioma",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.lblDropdown.Wrap(-1)
        ContainerRight.Add(self.lblDropdown, 0, wx.ALL, 5)

        languages = ['Spanish', 'English']
        self.languageCombo = wx.ComboBox(self,  wx.ID_ANY, size=(340, 30), choices = languages, style=wx.CB_READONLY)

        ContainerRight.Add(self.languageCombo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        Container.Add(ContainerRight, 1, wx.EXPAND, 5)

        self.SetSizer(Container)
        self.Layout()

        self.Centre(wx.BOTH)

        self.languageCombo.SetValue('Spanish')

        self.gauge = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, (340, 15), wx.GA_HORIZONTAL
        )
        self.gauge.SetValue(0)
        ContainerRight.Add(self.gauge, 0, wx.ALL, 5)

        ##ContainerRight.AddSpacer( ( 0, 40), 0, wx.EXPAND, 5 )

        self.btnStart = wx.Button(
            self, wx.ID_ANY, "Contar", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.btnStart.Enable(False)

        ContainerRight.Add(self.btnStart, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # ContainerRight.AddSpacer( ( 0, 10), 0, wx.EXPAND, 5 )

        self.btnImport = wx.Button(
            self, wx.ID_ANY, "Importar", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.btnImport.Enable(False)

        ContainerRight.Add(self.btnImport, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Connect Events
        self.filePiker.Bind(wx.EVT_FILEPICKER_CHANGED, self.__enableButton)
        self.btnStart.Bind(wx.EVT_BUTTON, self.__countWords)

        self.btnImport.Bind(wx.EVT_BUTTON, self.__importData)
        self.languageCombo.Bind(wx.EVT_COMBOBOX, self.__change_language)

        self.dataView.Bind(wx.grid.EVT_GRID_COL_SORT, self.__sortData)

    def __sortData(self, event):
        col = event.GetCol()
        print(self.dictionary)
        self.sortedReverse = False if self.sortedReverse else True
        self.dictionary.sort(key = lambda a: a[col], reverse = self.sortedReverse)

        self.dataView.ClearGrid()
        if self.dataView.GetNumberRows() > 0:
            self.dataView.DeleteRows(numRows=self.dataView.GetNumberRows())

        for i, value in enumerate(self.dictionary):
            self.dataView.InsertRows(pos=i)
            self.dataView.SetCellValue(i, 0, value[1])
            self.dataView.SetCellValue(i, 1, str(value[2]))
            self.dataView.SetCellValue(i, 2, str(value[0]))

    def __enableButton(self, event):
        self.btnStart.Enabled = True

    def __importData(self, event):
        """
        Read csv with words and load it to table
        """
        self.__resetgauge(len(self.dictionary))
        with open(self.filePath + "words.csv", "w", newline="") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for i, value in enumerate(self.dictionary):
                self.gauge.SetValue(i)
                spamwriter.writerow([value[0], value[2], value[1]])

    def __resetgauge(self, max):
        """
        reset loading bar
        """
        self.gauge.SetValue(0)
        self.gauge.SetRange(max)

    def __update_stopwords(self, language):
        self.emptyWord = set(stopwords.words(language))

    def __change_language(self, event):
        """
        Change language
        """
        self.dataView.InsertRows(pos=0)
        self.dataView.DeleteRows(pos=0)
        currentLang = self.languageCombo.GetValue()
        currentLang = currentLang.lower()
        self.__update_stopwords(currentLang)
        if currentLang == 'english':
            self.btnStart.SetLabel('Count')
            self.btnImport.SetLabel('To import')
            self.dataView.SetColLabelValue(0, "Word")
            self.dataView.SetColLabelValue(1, "Length\nof\nword")
            self.dataView.SetColLabelValue(2, "Quantity")
            self.lblDropdown.SetLabel("Select the Language")
            self.lblFilePiker.SetLabel("Select the file")
        elif currentLang == 'spanish':
            self.btnStart.SetLabel('Contar')
            self.btnImport.SetLabel('Importar')
            self.dataView.SetColLabelValue(0, "Palabra")
            self.dataView.SetColLabelValue(1, "Longitud\nde la\npalabra")
            self.dataView.SetColLabelValue(2, "Cantidad")
            self.lblDropdown.SetLabel("Seleccione el idioma")
            self.lblFilePiker.SetLabel("Seleccione el archivo")
        else:
            pass


    def __countWords(self, event):
        """
        Load the pdf file and start counting words
        """

        self.dataView.ClearGrid()

        rawTxt = self.__getTextFromFile(self.filePiker.GetPath())
        words = []

        txt = self.normalizeText(rawTxt)
        words = self.deleteEmptyWords(txt)
        
        self.dictionary = dict(Counter(words))
        self.dictionary = self.sortDictionary(self.dictionary)

        if self.dataView.GetNumberRows() > 0:
            self.dataView.DeleteRows(numRows=self.dataView.GetNumberRows())

        self.gauge.SetRange(len(self.dictionary))
        for i, value in enumerate(self.dictionary):
            self.dataView.InsertRows(pos=i)
            self.dataView.SetCellValue(i, 0, value[1])
            self.dataView.SetCellValue(i, 1, str(value[2]))
            self.dataView.SetCellValue(i, 2, str(value[0]))
            self.gauge.SetValue(i)

        self.gauge.SetValue(len(self.dictionary)+1)
        self.btnImport.Enable(True)

    def normalizeText(self, txt):
        return re.compile(r"\W+", re.UNICODE).split(txt)

    def deleteEmptyWords(self, txt):
        """
        Remove invalid words
        """
        return [w for w in txt if w.lower() not in self.emptyWord]

    def sortDictionary(self, dictionary):
        """
        Sort the dictionary of words descending
        """
        aux = [(dictionary[key], key, len(key)) for key in dictionary]
        aux.sort()
        aux.reverse()
        return aux

    def __getTextFromFile(self, path):
        """
        Check file type
        """
        fileExtension = pathlib.Path(path).suffix
        text = ""
        
        if fileExtension == ".pdf":
            """
            Load the pdf files
            """
            try:
                binaryPDF = open(path, "rb")  # 'rb' for read binary mode
                pdf = PyPDF2.PdfFileReader(binaryPDF)
                self.gauge.SetRange(pdf.getNumPages())
                for num in range(pdf.getNumPages()):
                    self.gauge.SetValue(num)
                    page = pdf.getPage(num)
                    text += page.extractText()
            except (OSError, IOError) as error:
                text = None
        elif fileExtension == ".txt":
            """
            Load text files
            """
            try:
                with open(path, 'r') as f:
                    text = f.read()
            except (OSError, IOError) as error:
                text = None
        elif fileExtension == ".doc" or fileExtension == ".docx":
            """
            Load Microsoft Word files
            """
            try:
                text = docx2txt.process(path)
            except (OSError, IOError) as error:
                text = None
        else:
            """
            File is unsupported file format
            """
            text = None
       
        return text

    def __del__(self):
        pass
app = wx.App()
frame = MainFrame(None)
frame.Show()
app.MainLoop()
