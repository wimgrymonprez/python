# expanded on the original work of adam jagosz who created a python script to be able to reorder a listbox
# I altered the code to be able to link multiple listbox and keep them synchronized. This way you can have key value pairs.

import tkinter as tk

class MultiListbox(tk.Listbox):
    def __init__(self,parent,lists):
        super().__init__(parent)
        self._selection = None
        self.lists = []
        self.ctrlClicked = False
        self.left = False
        self.selectionClicked = False
        self.unlockShifting()
        a=1
        b=0
        sb = tk.Scrollbar(self, orient=tk.VERTICAL,command=self._scroll)
        sb.grid(row=1,column=10,sticky="ns")
        for value,width in lists:
            self.columnName = tk.Label(self,text=f"{value}")
            self.columnName.grid(row=0,column=b,sticky="news")
            self.lb = tk.Listbox(self, width=width, borderwidth=0, selectborderwidth=0, relief=tk.FLAT, exportselection=tk.FALSE)
            self.lb.grid(row=a,column=b)
            self.lists.append(self.lb)
            self.lb.bind("<MouseWheel>", self._on_mouse_wheel)
            self.lb.bind("<Control-1>", self.toggleSelection)
            self.lb.bind('<B1-Motion>', self.shiftselection)
            self.lb.bind('<Button-1>', self.setCurrent) #lambda e, s=self: s._select(e.y)
            self.lb.bind('<Leave>', self.onLeave)
            self.lb.bind('<Enter>', self.onEnter)
            self.lb.bind('<Button-2>', self.printlistbox)
            b+=1
            self.lb['yscrollcommand'] = sb.set
            self.lb['selectmode'] = tk.EXTENDED

    def orderChangedEventHandler(self):
        pass

    def printlistbox(self,event):
        for l in self.lists:
            for value in l.get(0,tk.END):
                print(value)

    def lockShifting(self):
        # prevent moving processes from disturbing each other
        # and prevent scrolling too fast
        # when dragged to the top/bottom of visible area
        self.shifting = True

    def unlockShifting(self):
        self.shifting = False

    def toggleSelection(self, event):
        # variable to simulate ctrlpress to select multiple values
        self.ctrlClicked = True

    def onLeave(self,event):
        if self.selectionClicked:
            self.left = True
            return "break"

    def onEnter(self,event):
        self.left = False

    def _donothing(self,event):
        return "break"

    def insert(self,index,*elements):
        print(type(elements))
        #insert values in every column
        for e in elements:
            print(e)
            i=0 #column counter
            for l in self.lists:
                l.insert(index,e[i])
                i=i+1

    def _scroll(self,*args):
        for l in self.lists:
            l.yview(*args)

    def _on_mouse_wheel(self,event):
        for l in self.lists:
            l.yview("scroll",(int(-1*event.delta/120)),"units")
        return "break"

    def moveElement(self, source, target):
        if not self.ctrlClicked:
            for l in self.lists:
                element = l.get(source)
                l.delete(source)
                l.insert(target,element)

    def shiftselection(self, event):
        if self.ctrlClicked:
            return
        selection = self.curselection()
        if not self.selectionClicked or len(selection) == 0:
            self.selection_clear(0, tk.END)
            self.selection_set(min(selection),max(selection))
            return

        selectionRange = range(min(selection), max(selection))
        currentIndex = self.lists[0].nearest(event.y)

        if self.shifting:
            return 'break'

        lineHeight = 13
        bottomY = self.winfo_height()
        if event.y >= bottomY - lineHeight:
            self.lockShifting()
            for l in self.lists:
                l.see(l.nearest(bottomY - lineHeight)+1)
            self.after(500, self.unlockShifting)
        if event.y <= lineHeight:
            self.lockShifting()
            for l in self.lists:
                l.see(l.nearest(lineHeight) - 1)
            self.after(500, self.unlockShifting)

        if currentIndex < min(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange[::-1]:
                if not self.lists[0].selection_includes(i):
                    self.moveElement(i, max(selection)-notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = min(selection)-1
            self.moveElement(currentIndex, currentIndex + len(selection))
            self.orderChangedEventHandler()
        elif currentIndex > max(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange:
                if not self.lists[0].selection_includes(i):
                    self.moveElement(i, min(selection)+notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = max(selection)+1
            self.moveElement(currentIndex, currentIndex - len(selection))
            self.orderChangedEventHandler()
        self.unlockShifting()
        return 'break'

    def curselection(self):
        return self.lists[0].curselection()

    def setCurrent(self, event):
        self.ctrlClicked = False
        i = self.lists[0].nearest(event.y)
        self.selectionClicked = self.lists[0].selection_includes(i)#self.selection_includes(i)
        if (self.selectionClicked):
            return 'break'
        self.selection_clear(0,tk.END)
        self.selection_set(i)

    def selection_clear(self,first,last=None):
        #clear selection
        for l in self.lists:
            l.selection_clear(first,last)

    def selection_set(self,first,last=None):
        #select all column at selected index
        for l in self.lists:
            l.selection_set(first,last)

if __name__ == '__main__':
    root = tk.Tk()
    label = tk.Label(root, text="multicolumn listbox")
    label.grid(row=0,column=0)
    mclb = MultiListbox(root,(('Productnaam',15),('sku',15)))
    for i in range(1000):
        mclb.insert(tk.END,(f"Product{i}",f"sku{i}"))
    mclb.grid(row=1,column=0)
    tk.mainloop()