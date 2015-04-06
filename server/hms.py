from Tkinter import *
import MySQLdb
from fetcher import update_db


f = open("hms.conf", "r")
for line in f:
    if "IP:" in line:
        dbip = line.split(":")[1].lstrip(" ").rstrip("\n")
    elif "Username:" in line:
        dbuser = line.split(":")[1].lstrip(" ").rstrip("\n")
    elif "Password:" in line:
        dbpass = line.split(":")[1].lstrip(" ").rstrip("\n")
    elif "Database name:" in line:
        dbname = line.split(":")[1].lstrip(" ").rstrip("\n")
        
#db = MySQLdb.connect("localhost","monitoring","mon1toring*pass","monitoringdb" )
db = MySQLdb.connect(dbip,dbuser,dbpass,dbname )


def whichSelected () :
    print "Selected entry No %s" % (select.curselection())
    return int(select.curselection()[0])

def dosql (cmd) :
    cursor = db.cursor()
    cursor.execute(cmd)
    setSelect ()

def addEntry () :
    dosql("insert into nodes values ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (nodeidVar.get(), nodeipVar.get(), nodeportVar.get(), freeramVar.get(), totalramVar.get(), freedVar.get(), totaldVar.get(), cpuVar.get()))
    
def updateEntry() :
    nodeid = nodeslist[whichSelected()][0]
    dosql("update nodes set nodeip='%s', nodeport='%s', freeram='%s', totalram='%s', freed='%s', totald='%s', cpu='%s' where nodeid='%s'" %
          (nodeipVar.get(), nodeportVar.get(),freeramVar.get(), totalramVar.get(), freedVar.get(), totaldVar.get(), cpuVar.get(), nodeid ))

def deleteEntry() :
    nodeid = nodeslist[whichSelected()][0]
    dosql("delete from nodes where nodeid='%s'" % nodeid)

def loadEntry  () :
    nodeid, nodeip, nodeport, freeram, totalram, freed, totald, cpu = nodeslist[whichSelected()]
    nodeidVar.set(nodeid)
    nodeipVar.set(nodeip)
    nodeportVar.set(nodeport)
    freeramVar.set(freeram)
    totalramVar.set(totalram)
    freedVar.set(freed)
    totaldVar.set(totald)
    cpuVar.set(cpu)
    
def makeWindow () :
    global nodeidVar, nodeipVar, nodeportVar, freeramVar, totalramVar, freedVar, totaldVar, cpuVar, select
    win = Tk()
    win.title("Demo NMS")

    frame1 = Frame(win)
    frame1.pack()

    Label(frame1, text="Node ID").grid(row=0, column=0, sticky=W)
    nodeidVar = StringVar()
    nodeid = Entry(frame1, textvariable=nodeidVar)
    nodeid.grid(row=0, column=1, sticky=W)

    Label(frame1, text="Node IP").grid(row=1, column=0, sticky=W)
    nodeipVar = StringVar()
    nodeip = Entry(frame1, textvariable=nodeipVar)
    nodeip.grid(row=1, column=1, sticky=W)

    Label(frame1, text="Node Port").grid(row=2, column=0, sticky=W)
    nodeportVar = StringVar()
    nodeport = Entry(frame1, textvariable=nodeportVar)
    nodeport.grid(row=2, column=1, sticky=W)
    
    Label(frame1, text="Free RAM (kB)").grid(row=3, column=0, sticky=W)
    freeramVar = StringVar()
    freeram = Entry(frame1, textvariable=freeramVar)
    freeram.grid(row=3, column=1, sticky=W)
    
    Label(frame1, text="Total RAM (kB)").grid(row=4, column=0, sticky=W)
    totalramVar = StringVar()
    totalram = Entry(frame1, textvariable=totalramVar)
    totalram.grid(row=4, column=1, sticky=W)
    
    Label(frame1, text="Free Disk").grid(row=5, column=0, sticky=W)
    freedVar = StringVar()
    freedid = Entry(frame1, textvariable=freedVar)
    freedid.grid(row=5, column=1, sticky=W)
    
    Label(frame1, text="Total Disk").grid(row=6, column=0, sticky=W)
    totaldVar = StringVar()
    totald = Entry(frame1, textvariable=totaldVar)#, state=DISABLED)
    totald.grid(row=6, column=1, sticky=W)

    Label(frame1, text="CPU Usage %").grid(row=7, column=0, sticky=W)
    cpuVar= StringVar()
    cpu= Entry(frame1, textvariable=cpuVar)
    cpu.grid(row=7, column=1, sticky=W)

    frame2 = Frame(win)       # Row of buttons
    frame2.pack()
    b1 = Button(frame2,text=" Add  ",command=addEntry)
    b2 = Button(frame2,text="Update",command=updateEntry)
    b3 = Button(frame2,text="Delete",command=deleteEntry)
    b4 = Button(frame2,text="Load  ",command=loadEntry)
    b5 = Button(frame2,text="Refresh",command=setSelect)
    b1.pack(side=LEFT); b2.pack(side=LEFT)
    b3.pack(side=LEFT); b4.pack(side=LEFT); b5.pack(side=LEFT)

    frame3 = Frame(win)       # select of names
    frame3.pack()
    scroll = Scrollbar(frame3, orient=VERTICAL)
    select = Listbox(frame3, yscrollcommand=scroll.set, height=6)
    scroll.config (command=select.yview)
    scroll.pack(side=RIGHT, fill=Y)
    select.pack(side=LEFT,  fill=BOTH, expand=1)
    return win


def setSelect () :
    global nodeslist
    update_db(db)
    cursor = db.cursor()
    sql = "select nodeid, nodeip, nodeport, freeram, totalram, freed, totald, cpu from nodes order by nodeid"
    cursor.execute(sql)
    nodeslist = cursor.fetchall()
    select.delete(0,END)
    for nodeid, nodeip, nodeport, freeram, totalram, freed, totald, cpu in nodeslist :
        select.insert (END, nodeid)


win = makeWindow()
setSelect ()
win.mainloop()