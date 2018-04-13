from exe import get_info
from exe import csv_parser
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

#define the action of the single record submit button
def singleSubmit(*args):
    writeToSingleOutput("You pressed the button!")

def writeToSingleOutput(msg):
    singleOutput['state'] = 'normal'
    singleOutput.insert('end', msg + "\n")
    singleOutput['state'] = 'disabled'

def selectFile(*args):
    filepath.set(filedialog.askopenfilename())

def multipleSubmit(*args):
    writeToMultipleOutput("You pressed the button!")

def writeToMultipleOutput(msg):
    multipleOutput['state'] = 'normal'
    multipleOutput.insert('end', msg + "\n")
    multipleOutput['state'] = 'disabled'

#create the root window
root = Tk()
root.title("IMDb to MARC")

#put a base frame into the root window
mainframe = ttk.Frame(root, padding=(12,12,12,12))
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#put tabs in the base frame
tabs = ttk.Notebook(mainframe)
singleRecord = ttk.Frame(tabs)
multipleRecords = ttk.Frame(tabs)
tabs.add(singleRecord, text = "Single")
tabs.add(multipleRecords, text = "Multiple")
tabs.grid(column=0, row=0, sticky=(N,S))
tabs.columnconfigure(0, weight=1)
tabs.rowconfigure(0, weight=1)

#create oclc number entry box
oclcNum = StringVar()
oclcNumLabel = ttk.Label(singleRecord, text="OCLC Number")
oclcNumEntry = ttk.Entry(singleRecord, textvariable=oclcNum)
oclcNumLabel.grid(column=0, row=0, sticky=(N,S))
oclcNumEntry.grid(column=0, row=1, sticky=(N,S))

#create imdb id entry box
imdbID = StringVar()
imdbIDLabel = ttk.Label(singleRecord, text="3rd Party ID (IMDB ID)")
imdbIDEntry = ttk.Entry(singleRecord, textvariable=imdbID)
imdbIDLabel.grid(column=0, row=2, sticky=(N,S))
imdbIDEntry.grid(column=0, row=3, sticky=(N,S))

#create upc number entry box
upcNum = StringVar()
upcNumLabel = ttk.Label(singleRecord, text="UPC")
upcNumEntry = ttk.Entry(singleRecord, textvariable=upcNum)
upcNumLabel.grid(column=0, row=4, sticky=(N,S))
upcNumEntry.grid(column=0, row=5, sticky=(N,S))

#create price entry box
price = StringVar()
priceLabel = ttk.Label(singleRecord, text="Price")
priceEntry = ttk.Entry(singleRecord, textvariable=price)
priceLabel.grid(column=0, row=6, sticky=(N,S))
priceEntry.grid(column=0, row=7, sticky=(N,S))

#create edition entry box
edition = StringVar()
editionLabel = ttk.Label(singleRecord, text="Edition/Season Number")
editionEntry = ttk.Entry(singleRecord, textvariable=edition)
editionLabel.grid(column=0, row=8, sticky=(N,S))
editionEntry.grid(column=0, row=9, sticky=(N,S))

#create single file submit button
singleButton = ttk.Button(singleRecord, text="Submit", command=singleSubmit)
singleButton.grid(column=0, row=10, sticky=(N,S))

#create single file output window
singleOutput = Text(singleRecord, wrap=WORD, state=DISABLED, width=30)
writeToSingleOutput("IMDb ID and UPC are required to generate a MARC record.")
singleOutput.grid(column=0, row=11, sticky=(N,S,E,W))
singleOutputScroll = ttk.Scrollbar(singleRecord, orient=VERTICAL, command=singleOutput.yview)
singleOutput['yscrollcommand'] = singleOutputScroll.set
singleOutputScroll.grid(column=1, row=11, sticky=(N,S,W))

#create file selection
filepath = StringVar()
fileLabel = ttk.Label(multipleRecords, text="File")
fileEntry = ttk.Entry(multipleRecords, textvariable=filepath)
fileButton = ttk.Button(multipleRecords, text="Browse...", command=selectFile)
fileLabel.grid(column=0, row=0, sticky=(N,S))
fileEntry.grid(column=0, row=1, sticky=(N,S,W))
fileButton.grid(column=1, row=1, sticky=(N,S,W))

#create multipe files submit button
multipleButton = ttk.Button(multipleRecords, text="Submit", command=multipleSubmit)
multipleButton.grid(column=1, row=2, sticky=(N,S,W))

#create multiple files output window
multipleOutput = Text(multipleRecords, wrap=WORD, state=DISABLED, width=30, height=33)
writeToMultipleOutput("Select a CSV file to process batches of records.")
multipleOutput.grid(column=0, row=3, sticky=(N,S,E,W), columnspan=3)
multipleOutputScroll = ttk.Scrollbar(multipleRecords, orient=VERTICAL, command=multipleOutput.yview)
multipleOutput['yscrollcommand'] = multipleOutputScroll.set
multipleOutputScroll.grid(column=4, row=3, sticky=(N,S,W))

#run the gui
root.mainloop()