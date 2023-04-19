import tkinter as tk


class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return


b_songs_list = ['Bollywood song 1', 'Bollywood song 2', 'Bollywood song 3']
i_songs_list = ['International song 1', 'International song 2',
                'International song 3']

root = tk.Tk()
S = tk.Scrollbar(root)
T = tk.Text(root, height=20, width=30, cursor="hand2")
hyperlink = HyperlinkManager(T)
S.pack(side=tk.RIGHT, fill=tk.Y)
T.pack(side=tk.LEFT, fill=tk.Y)
S.config(command=T.yview)
T.config(yscrollcommand=S.set)


def click1():
    print('click1')


def callback_a():   # Bollywood songs WITH hyperlinks
    T.delete(1.0, tk.END)
    for songs in b_songs_list:
        T.insert(tk.END, songs, hyperlink.add(click1))
        T.insert(tk.END, '\n')


def callback_b():
    T.delete(1.0, tk.END)
    for songs in i_songs_list:
        T.insert(tk.END, songs + '\n')


bollywood_button = tk.Button(root, text="Bollywood-Top-50", command=callback_a)
bollywood_button.pack()

international_button = tk.Button(root, text="International-Top-50",
                                 command=callback_b)
international_button.pack() 
root.mainloop()
