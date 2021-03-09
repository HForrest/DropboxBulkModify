#
# TO DO
# Needs a progress bar
# Needs to implement a delete workflow
#

#Imports
import tkinter as tk
from tkinter import ttk
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import webbrowser

#Dropbox vars
APP_KEY = "XXX"
APP_SECRET = "XXX"

auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
authorize_url = auth_flow.start()


#Controller, sets up a base frame that you can throw other frames on
class pageContainer(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        #Variables
        self.child = tk.StringVar()
        self.content = tk.StringVar()
        self.selection = []
        self.txtselection = tk.StringVar()
        self.mode = tk.StringVar()
        self.progvar = tk.StringVar()
        
        container = tk.Frame(self)
        tk.Tk.geometry(self, '500x300')
        container.pack(side = 'top', fill = 'both', expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 2)
        
        self.frame = {}
        
        for F in (StartPage, ModePage, ChildPage, ContentPage, SelectionPage, ActionPage):
            
            frame = F(container, self)
            
            self.frame[F] = frame
            
            frame.grid(row = 0,column = 0, sticky = 'nsew')
            
        self.show_frame(StartPage)
        

    #Shows a new frame
    def show_frame(self, cont):
            
        frame = self.frame[cont]
        frame.tkraise()
        frame.event_generate('<<ShowFrame>>')
        
    #Insert Treeview Node
    def insert_node(self, tree, parent, path, treelist):
        if path not in treelist:
            treelist.append(path)
            try:
                x = dbx.files_list_folder(path)
                for entry in x.entries:
                    name = entry.path_display.split('/')[-1]
                    print(name)
                    tree.insert(parent, 'end', text=name, open=True)
                    
            except:
                pass
    
    #Open Treeview Node
    def open_node(self, treelist, tree, var):
        node = tree.selection()
        parent = tree.parent(node)
        parent_text = tree.item(parent,'text')
        path = tree.item(node, 'text')
        
        if path != '':
            while parent != '':
                path = parent_text + '/' + path
                parent = tree.parent(parent)
                parent_text = tree.item(parent,'text')
            else:
                path = '/' + path
        else:
            pass
                
        var.set(path)
        self.insert_node(tree, node, path, treelist)  

    #dropbox Commands
    #Oauth2 bit
    def auth(self, code):
        try:
            global oauth_result
            oauth_result = auth_flow.finish(code)
            global dbx
            dbx = dropbox.Dropbox(oauth2_access_token = oauth_result.access_token)
            self.show_frame(ContentPage)
        except Exception as e:
            print('Error: %s' % (e,))
            tk.messagebox.showwarning('Error','Auth code rejected, try again?')
            
    #Bulk copy/delete function
    def change(self,child, mContent, selection, mode, progvar): 
        '''
        Parameters
        ----------
        child : Child directory as string
        mContent : master Content ditrectory as string
        Spreadsheet: Spreadsheet directory as string
        mode : mode as string

        Bulk copies or deletes dropbox files. Does not use the built in API 
        bulk copy b/c there's no overwrite ability.'

        '''
        with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
            dbx.users_get_current_account()
        mName = mContent.split('/')[-1]
        
        intake = []
        output = []
        
        #tkStringVar selection to selection list
        selection = selection.replace(' ','')
        selection = selection.replace(',','')
        selection = selection.replace("'",'')
        selection = list(selection)[1:-1]
        
        #create a todo list
        for i, entry in enumerate(selection):
            output_name = (child + '/' + entry + '/' + mName)
            output.append(output_name)
            
        for entry in selection:
            intake.append(mContent)
        
        lst = list(zip(intake, output))
        
        #The actual change
        if mode == 'Copy':
            for entry in lst:
                try:
                    dbx.files_delete_v2(entry[1])
                except Exception:
                    pass
                dbx.files_copy_v2(entry[0],entry[1])
        else:
            for entry in lst:
                try:
                    dbx.files_delete_v2(entry[1])

                except Exception:
                    pass
        progvar.set('Done')


#First page, Authorize script called
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        lb1 = tk.Label(self, text = 'Authorization')
        lb2 = tk.Label(self, text = 'Go to the link below and copy-paste the code into the box')
        lb3 = tk.Label(self, text = 'www.dropbox.com', fg='blue', cursor = 'hand2', font = ('Arial 12 underline'))
        lb3.bind('<Button-1>', lambda e: webbrowser.open_new(authorize_url))
        CodeEntry = tk.Entry(self, width = 60)
        button1 = tk.Button(self, text = 'Authorize', 
                            command = lambda: controller.auth(CodeEntry.get()),
                            width = 20, height = 1)
        
        lb1.pack(pady=10)
        lb2.pack()
        lb3.pack()
        CodeEntry.pack(pady=20)
        button1.pack(pady=10)
        
#Currently unimplemented, will let the user select what they're doing then change the flow depending on what they do
class ModePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lb1 = tk.Label(self, text = 'What action do you want to do?')
        
        choices = {'Copy', 'Delete'}
        controller.mode.set('Copy')
        op1 = tk.OptionMenu(self, controller.mode, *choices)
        
        button = tk.Button(self, text = 'Next', 
                           command = lambda: controller.show_frame(ChildPage))
        
        lb1.pack(pady = 20)
        op1.pack(pady = 5)
        button.pack()
        
        #Add a dropdown, then do some logic for the delete workflow 
       
#Treeview selection of Dropbox location of the content folder     
class ContentPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lb1 = tk.Label(self, text = 'Select the Template Directory')
        tree = ttk.Treeview(self)
        tree.column("#0", width=475, stretch=False)
        treelist = []
        ysb = ttk.Scrollbar(self, orient='vertical', command=tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=tree.xview)
        tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        tree.bind('<ButtonRelease-1>', lambda e:controller.open_node(treelist, tree, controller.content))
        button1 = tk.Button(self, text = 'Confirm',
                            command = lambda :controller.show_frame(ChildPage), width = 20, height = 1)
        
        lb1.grid(row = 0, column = 0)
        tree.grid(row = 1, column = 0, columnspan = 2)
        ysb.grid(row=1, column=2, sticky='ns')
        xsb.grid(row=2, column=0, sticky='ew')
        button1.grid(row = 3, column = 0)
        self.bind('<<ShowFrame>>', lambda e:controller.open_node(treelist, tree, controller.content))
        
 
class ChildPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lb1 = tk.Label(self, text = 'Select the Destination Directory')
        tree = ttk.Treeview(self)
        tree.column("#0", width=475, stretch=False)
        treelist = []
        ysb = ttk.Scrollbar(self, orient='vertical', command=tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=tree.xview)
        tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        tree.bind('<ButtonRelease-1>', lambda e:controller.open_node(treelist, tree, controller.child))
        button1 = tk.Button(self, text = 'Confirm',
                            command = lambda :controller.show_frame(SelectionPage), width = 20, height = 1)
        
        lb1.grid(row = 0, column = 0)
        tree.grid(row = 1, column = 0, columnspan = 2)
        ysb.grid(row=1, column=2, sticky='ns')
        xsb.grid(row=2, column=0, sticky='ew')
        button1.grid(row = 3, column = 0)
        self.bind('<<ShowFrame>>', lambda e:controller.open_node(treelist, tree, controller.child))
 
class SelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lb1 = tk.Label(self, text = 'Select which folders to modify')
        childfolders = []
        listvar = tk.StringVar()
        listvar.set(childfolders)
        checklist = tk.Listbox(self, listvar = listvar, selectmode = 'multiple')
        
        selbutton = tk.Button(self, text='select all', command = lambda : checklist.select_set(0, tk.END))
        deselbutton = tk.Button(self, text='deselect all', command = lambda : checklist.selection_clear(0, tk.END))
        
        save = tk.Button(self, text = 'save',
                         command = lambda :[
                             self.getsel(checklist, controller.selection, controller.txtselection, childfolders),
                             controller.show_frame(ActionPage)
                                           ]
                         )
        
        lb1.pack()
        checklist.pack()
        selbutton.pack()
        deselbutton.pack()
        save.pack()
        
        self.bind('<<ShowFrame>>', 
                  lambda e: 
                      [
                          self.update_list(
                              checklist,
                              childfolders,
                              controller.child,
                              listvar
                              )
                      ]
                  )
        
    def update_list(self, lst, childfolders, child, listvar):
        drct = dbx.files_list_folder(child.get()).entries
        
        for index, entry in enumerate(drct):
            childfolders.append(drct[index].path_display.split('/')[-1])
        listvar.set(childfolders)
        

    def getsel(self, lst, var, txtvar, childfolders):
        index = lst.curselection()
        var = []
        for i in index:
            var.append(childfolders[i])
        txtvar.set(var)
        
        
#Reviews selections and commits changes to dropbox. Needs a progress bar.
class ActionPage(tk.Frame):
    def __init__(self,parent,controller):
        
        tk.Frame.__init__(self, parent)
        lb1 = tk.Label(self, text = 'Review Selections')
        lb2 = tk.Label(self, text = 'Template')
        lb2a = tk.Label(self, textvariable = controller.content)
        lb3 = tk.Label(self, text = 'Destination')
        lb3a = tk.Label(self, textvariable = controller.child)
        lb4 = tk.Label(self, text = 'Selection')
        list4 =tk.Listbox(self, listvar = controller.txtselection)
        #lb5 = tk.Label(self, text = 'Mode')
        #lb5a = tk.Label(self, textvariable = controller.mode)
        lb6 = tk.Label(self, textvariable = controller.progvar)
        #progbar = ttk.Progressbar(self, mode = "indeterminate")
        button = tk.Button(self, text = 'Confirm', bg = 'IndianRed1',
                           command = lambda: controller.change(
                               controller.child.get(),
                               controller.content.get(),
                               controller.txtselection.get(),
                               controller.mode.get(),
                               controller.progvar))
        
        
        
        lb1.grid(row = 0, column = 0)
        lb2.grid(row = 1, column = 0)
        lb2a.grid(row = 1, column = 1)
        lb3.grid(row = 2, column = 0)
        lb3a.grid(row = 2, column = 1)
        lb4.grid(row = 3, column = 0)
        list4.grid(row = 3, column = 1)
        #lb5.grid(row = 4, column = 0)
        #lb5a.grid(row = 4, column = 1)
        button.grid(row = 5, column = 1)
        lb6.grid(row = 6, column = 1)
       #progbar.grid(row = 7, column = 0)
        
#class ProgressPage(tk.Frame):
#    def __init__(self, parent):
#        tk.Frame.__init__(self,parent)
#        lb1 = tk.Label(self, text = 'Working...')
#        progbar = ttk.Progressbar(self, orient = tk.HORIZONTAL, mode = 'indeterminate')


app = pageContainer()
app.mainloop()        
