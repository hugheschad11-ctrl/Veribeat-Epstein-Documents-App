import os
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.metrics import dp

import sqlite3

APP_NAME = "Epstein JPT"

def get_db_path():
    # On Android, shipped inside app; copy to app storage if needed
    return os.path.join(os.path.dirname(__file__), "epstein_index.sqlite")

def search(db_path: str, query: str, top: int = 25):
    if not query.strip():
        return []
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        sql = """
        SELECT file, page,
               snippet(docs_fts, 2, '⟦', '⟧', ' … ', 16) AS snippet,
               bm25(docs_fts) AS score
        FROM docs_fts
        WHERE docs_fts MATCH ?
        ORDER BY score
        LIMIT ?;
        """
        rows = con.execute(sql, (query, top)).fetchall()
    except Exception:
        sql = """
        SELECT file, page, substr(text, 1, 280) AS snippet, 0.0 AS score
        FROM docs_fts
        WHERE docs_fts MATCH ?
        LIMIT ?;
        """
        rows = con.execute(sql, (query, top)).fetchall()
    finally:
        con.close()
    out=[]
    for r in rows:
        f=os.path.basename(str(r["file"]))
        p=r["page"]
        cite=f + (f" p.{p}" if p is not None and str(p).isdigit() else "")
        out.append({"cite": cite, "snippet": str(r["snippet"]).replace("\n"," ")})
    return out

class ResultRow(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=(dp(10), dp(8)), spacing=dp(4), **kwargs)
        self.cite = Label(text="", size_hint_y=None, height=dp(18))
        self.cite.bold = True
        self.cite.color = (1,1,1,1)
        self.snip = Label(text="", size_hint_y=None, height=dp(44))
        self.snip.color = (.75,.75,.75,1)
        self.snip.text_size = (0, None)
        self.add_widget(self.cite)
        self.add_widget(self.snip)

    def refresh_view_attrs(self, rv, index, data):
        self.cite.text = data.get("cite","")
        self.snip.text = data.get("snippet","")
        return super().refresh_view_attrs(rv, index, data)

class ResultsView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "ResultRow"
        layout = RecycleBoxLayout(default_size=(None, dp(72)), default_size_hint=(1, None),
                                  size_hint=(1, None), orientation="vertical", spacing=dp(6))
        layout.bind(minimum_height=layout.setter("height"))
        self.layout_manager = layout

class Root(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(14), spacing=dp(10), **kwargs)
        self.db_path = get_db_path()

        title = Label(text="EPSTEIN JPT", size_hint_y=None, height=dp(26))
        title.color=(1,1,1,1)
        self.add_widget(title)

        self.q = TextInput(hint_text="Search (examples: \"little saint james\", maxwell, flight*)",
                           multiline=False, size_hint_y=None, height=dp(44))
        self.q.bind(on_text_validate=lambda *_: self.do_search())
        self.add_widget(self.q)

        bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        self.btn = Button(text="Search")
        self.btn.bind(on_release=lambda *_: self.do_search())
        self.copy = Button(text="Copy top cite")
        self.copy.bind(on_release=lambda *_: self.copy_top())
        bar.add_widget(self.btn)
        bar.add_widget(self.copy)
        self.add_widget(bar)

        self.status = Label(text="", size_hint_y=None, height=dp(18))
        self.status.color=(.7,.7,.7,1)
        self.add_widget(self.status)

        self.rv = ResultsView()
        self.add_widget(self.rv)

        self.results=[]

    def do_search(self):
        query = self.q.text.strip()
        self.results = search(self.db_path, query, top=50)
        self.rv.data = self.results
        self.status.text = f"{len(self.results)} result(s)"

    def copy_top(self):
        if not self.results:
            return
        Clipboard.copy(self.results[0].get("cite",""))

class EpsteinJPTApp(App):
    def build(self):
        self.title = APP_NAME
        return Root()

if __name__ == "__main__":
    EpsteinJPTApp().run()
