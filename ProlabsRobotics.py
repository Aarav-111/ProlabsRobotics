import os, json, urllib.parse, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineScript
from PySide6.QtCore import QUrl, QTimer, QEventLoop

__all__ = ["AI"]

class _SilentPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        return

class AI:
    def __init__(self, system_prompt="", history_path="convo.json", poll_ms=800, stability_hits=2, hidden=True):
        self.system_prompt = system_prompt.strip()
        self.history_path = history_path
        self.poll_ms = int(poll_ms)
        self.stability_hits = max(1, int(stability_hits))
        self.hidden = bool(hidden)
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._browser = QWebEngineView()
        self._browser.setPage(_SilentPage(self._browser))
        self._inject_suppress()
        self._history = self._load_history()
        self._state = {"mode":"idle","last_saved":"","last_scraped":"","stable":0,"scraping_enabled":False}
        self._timer = QTimer()
        self._timer.timeout.connect(self._scrape)
        self._browser.loadStarted.connect(self._on_load_started)
        self._browser.loadFinished.connect(self._on_load_finished)
        if self.hidden:
            self._browser.resize(1,1)
            self._browser.showMinimized()
        else:
            self._browser.resize(900,700)
            self._browser.show()

    def _inject_suppress(self):
        s = QWebEngineScript()
        s.setInjectionPoint(QWebEngineScript.DocumentCreation)
        s.setRunsOnSubFrames(True)
        s.setWorldId(QWebEngineScript.MainWorld)
        s.setSourceCode("console.warn=function(){};console.error=function(){};")
        self._browser.page().scripts().insert(s)

    def _load_history(self):
        if not os.path.exists(self.history_path):
            return []
        try:
            return json.load(open(self.history_path))
        except Exception:
            return []

    def _save_history(self):
        json.dump(self._history, open(self.history_path,"w"), indent=2)

    def _compose(self, prompt):
        b = []
        if self.system_prompt:
            b.append(self.system_prompt)
        b.extend(f"{h['role']}: {h['content']}" for h in self._history[-20:])
        b.append(f"User: {prompt}")
        return "\n".join(b)

    def _nav(self, prompt):
        self._history.append({"role":"user","content":prompt})
        combined = self._compose(prompt)
        encoded = urllib.parse.quote(combined, safe="")
        url = f"https://chatgpt.com/?q={encoded}"
        self._state["last_scraped"] = ""
        self._state["stable"] = 0
        self._state["scraping_enabled"] = False
        self._state["mode"] = "waiting"
        self._browser.setUrl(QUrl(url))

    def _auto_accept(self):
        js = """
        let a=[...document.querySelectorAll("button")].find(b=>b.innerText&&b.innerText.toLowerCase().includes("accept"));if(a)a.click();
        let c=document.querySelector('[aria-label="Close"]');if(c)c.click();
        """
        self._browser.page().runJavaScript(js)

    def _scrape(self):
        if not self._state["scraping_enabled"] or self._state["mode"]!="waiting":
            return
        js = "var m=document.querySelectorAll('[data-message-author-role=\"assistant\"]');m.length?m[m.length-1].innerText:'';"
        self._browser.page().runJavaScript(js, self._on_scrape)

    def _on_scrape(self, text):
        if self._state["mode"]!="waiting":
            return
        t = (text or "").strip()
        if not t:
            self._state["stable"]=0
            self._state["last_scraped"]=""
            return
        if t==self._state["last_scraped"]:
            self._state["stable"]+=1
        else:
            self._state["last_scraped"]=t
            self._state["stable"]=1
        if self._state["stable"]>=self.stability_hits and t!=self._state["last_saved"]:
            self._state["last_saved"]=t
            self._history.append({"role":"assistant","content":t})
            self._save_history()
            self._state["mode"]="idle"
            if hasattr(self,"_wait_loop") and isinstance(self._wait_loop,QEventLoop):
                self._wait_loop.quit()

    def _on_load_started(self):
        self._state["scraping_enabled"]=False

    def _on_load_finished(self, ok):
        self._state["scraping_enabled"]=True
        QTimer.singleShot(1200, self._auto_accept)

    def ask(self, prompt):
        self._timer.start(self.poll_ms)
        self._nav(prompt)
        self._wait_loop = QEventLoop()
        self._wait_loop.exec()
        self._timer.stop()
        return self._state["last_saved"]

    def close(self):
        self._timer.stop()
        self._browser.close()
