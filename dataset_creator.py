from tkinter import *
from tkinter import ttk
from PIL import ImageGrab
import PIL.Image
import os


# noinspection PyAttributeOutsideInit
class DatasetCreator:
    def __init__(self, master):
        self.classes = {}
        self.targetImageHeight = 28
        self.targetImageWidth = 28
        self.datasetLocation = "./dataset/"
        self.datasetTypes = ["train", "test"]
        self.datasetType = StringVar()

        self.master = master
        self.parseConfigurationFile()
        self.createFilesIfNeeded()
        self.color_fg = 'white'
        self.color_bg = 'black'
        self.old_x = None
        self.old_y = None
        self.penWidth = 20
        self.drawWidgets()
        self.canvas.bind('<B1-Motion>', self.paint)  # drwaing the line
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        self.imageIndex = self.checkLastSavedIndex() + 1

    # noinspection PyBroadException
    def checkLastSavedIndex(self):
        try:
            with open('{}/dataset.csv'.format(self.datasetLocation + self.datasetType.get()), 'rb') as f:
                try:  # catch OSError in case of a one line file
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                last_line = f.readline().decode()
                try:
                    imageFullName = last_line.split(",")[0]
                    imageName = imageFullName.split(".")[0]
                    imageIndex = int(imageName[5:])
                    return imageIndex
                except Exception:
                    return -1
        except FileNotFoundError:
            with open('{}/dataset.csv'.format(self.datasetLocation + self.datasetType.get()), 'w'):
                return -1

    def parseConfigurationFile(self):
        try:
            with open('config.txt', 'r') as f:
                lines = f.readlines()
                classesKeys = lines[0].split(":")[1].strip().split(",")
                classesKeys = [x.strip() for x in classesKeys]
                for i in range(len(classesKeys)):
                    self.classes[classesKeys[i]] = i
                targetSize = lines[1].split(":")[1].split("x")
                targetSize = [x.strip() for x in targetSize]
                self.targetImageWidth = int(targetSize[0])
                self.targetImageHeight = int(targetSize[1])
        except Exception as exc:
            print("Invalid config file: {}".format(exc))
            exit(-1)

    def paint(self, e):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, e.x, e.y, width=self.penWidth, fill=self.color_fg,
                                    capstyle=ROUND, smooth=True)

        self.old_x = e.x
        self.old_y = e.y

    def reset(self, event=None):  # resetting or cleaning the canvas
        self.old_x = None
        self.old_y = None

    def clear(self):
        self.canvas.delete(ALL)

    def saveCommand(self):
        x = self.master.winfo_rootx() + self.canvas.winfo_x()
        y = self.master.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        image = ImageGrab.grab().crop((x + 10, y + 10, x1 - 10, y1 - 10))
        imageResized = image.resize((28, 28), PIL.Image.LINEAR)
        self.saveAsImage(imageResized)
        self.saveToCSV()
        self.clear()
        self.imageIndex += 1

    def saveAsImage(self, image):
        image.save(
            "{}/created_images/image{:0>4}.jpg".format(self.datasetLocation + self.datasetType.get(), self.imageIndex))

    def saveToCSV(self):
        selectedClass = self.classes.get(self.classString.get())
        with open("{}/dataset.csv".format(self.datasetLocation + self.datasetType.get()), "a") as csvFile:
            csvFile.write("image{:0>4}.jpg,{}\n".format(self.imageIndex, selectedClass))

    def drawWidgets(self):
        self.controls = Frame(self.master, padx=0, pady=0)

        Label(self.controls, text='Set', font='arial 10').pack()
        self.setCombo = ttk.Combobox(self.controls, width=10,
                                     textvariable=self.datasetType, state="readonly")
        self.setCombo["values"] = self.datasetTypes
        self.setCombo.set(self.datasetTypes[0])
        self.setCombo.pack(padx=5, pady=5)

        Label(self.controls, text='Class', font='arial 10').pack()
        self.classString = StringVar()

        self.classCombo = ttk.Combobox(self.controls, width=15,
                                       textvariable=self.classString, state="readonly")
        self.classCombo["values"] = list(self.classes.keys())
        self.classCombo.set(list(self.classes.keys())[0])
        self.classCombo.pack(padx=5, pady=5)

        self.saveButton = Button(self.controls, text="Save", command=self.saveCommand)
        self.saveButton.pack()
        self.controls.pack(side=LEFT)

        self.canvas = Canvas(self.master, width=224, height=224, bg=self.color_bg, borderwidth=0)
        self.canvas.pack()

        menu = Menu(self.master)
        self.master.config(menu=menu)
        self.optionMenu = Menu(menu)
        menu.add_cascade(label='Options', menu=self.optionMenu)
        self.optionMenu.add_command(label='Clear Canvas', command=self.clear)
        self.optionMenu.add_command(label='Exit', command=self.master.destroy)

    def createFilesIfNeeded(self):
        # create folders if they don't exist
        try:
            os.makedirs(self.datasetLocation + self.datasetTypes[0] + "/created_images")
            os.makedirs(self.datasetLocation + self.datasetTypes[1] + "/created_images")
        except OSError:
            pass
        # create csv files if they don't exist
        try:
            open('{}/dataset.csv'.format(self.datasetLocation + self.datasetTypes[0]), 'rb').close()
        except FileNotFoundError:
            open('{}/dataset.csv'.format(self.datasetLocation + self.datasetTypes[0]), 'w+').close()
        try:
            open('{}/dataset.csv'.format(self.datasetLocation + self.datasetTypes[1]), 'rb').close()
        except FileNotFoundError:
            open('{}/dataset.csv'.format(self.datasetLocation + self.datasetTypes[1]), 'w+').close()


if __name__ == '__main__':
    root = Tk()
    DatasetCreator(root)
    root.title('Application')
    root.mainloop()
