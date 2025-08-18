# ───── Standard-library imports ─────────────────────────────────────────────
import time, platform, webbrowser, urllib.parse, json, os, subprocess
import pyperclip
from pynput.mouse     import Controller as Mouse, Button
from pynput.keyboard  import Controller as Kbd, Key

# ───── Files ───────────────────────────────────────────────────────────────
HISTORY_FILE = "convo.json"
MAX_CONTEXT_TURNS = 50   # only last 50 turns are sent to ChatGPT

# ───── Controllers ─────────────────────────────────────────────────────────
MOD   = Key.cmd if platform.system() == "Darwin" else Key.ctrl
mouse = Mouse(); kbd = Kbd()

# ───── Helpers ─────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def focus_back_to_pycharm():
    system = platform.system()
    if system == "Darwin":  # macOS
        subprocess.run(["osascript", "-e", 'tell application "PyCharm" to activate'])
    elif system == "Windows":
        try:
            import pygetwindow as gw
            for w in gw.getWindowsWithTitle("PyCharm"):
                w.activate()
                break
        except Exception:
            with kbd.pressed(Key.alt): kbd.press(Key.tab); kbd.release(Key.tab)
    elif system == "Linux":
        subprocess.run(["wmctrl", "-a", "PyCharm"])

# ───── Main function ───────────────────────────────────────────────────────
def run(system_prompt: str, user_prompt: str) -> str:
    history = load_history()

    # build context with limited history
    conversation_lines = [system_prompt.strip(), ""]
    if history:
        recent_history = history[-MAX_CONTEXT_TURNS:]
        conversation_lines.append("Here is the most recent conversation history:")
        for turn in recent_history:
            role = "User" if turn["role"] == "user" else "Assistant"
            conversation_lines.append(f"{role}: {turn['content']}")
        conversation_lines.append("")
    conversation_lines.append("Now the user asks:")
    conversation_lines.append(user_prompt.strip())

    combined = "\n".join(conversation_lines)
    encoded  = urllib.parse.quote(combined, safe="")
    URL      = f"https://chatgpt.com/?q={encoded}&temporary-chat=true"

    # open ChatGPT
    webbrowser.open(URL)
    time.sleep(5)
    mouse.position = (700, 450)
    time.sleep(0.25)
    mouse.click(Button.left, 1)

    # clipboard loop
    start, prev, stable = time.time(), "", 0
    GENERATING_MARKERS = (
        "chatgpt is generating",
        "chatgpt is still generating",
        "generating a response",
    )
    while True:
        with kbd.pressed(MOD): kbd.press('a'); kbd.release('a')
        time.sleep(0.15)
        with kbd.pressed(MOD): kbd.press('c'); kbd.release('c')
        time.sleep(0.25)
        clip_now = pyperclip.paste() or ""
        stable   = stable + 1 if clip_now == prev else 0
        prev     = clip_now
        if stable >= 2 and not any(m in clip_now.lower() for m in GENERATING_MARKERS):
            break
        if time.time() - start > 90:
            raise TimeoutError("Timed out waiting for ChatGPT to finish")
        time.sleep(0.8)

    # close tab + refocus
    with kbd.pressed(MOD): kbd.press('w'); kbd.release('w')
    time.sleep(0.5)
    focus_back_to_pycharm()

    # clean response
    lines = clip_now.splitlines()
    answer_lines, capture = [], False
    UNWANTED_PREFIXES = (
        "Skip to content", "ChatGPT can make mistakes",
        "No file chosen", "Cookie Preferences",
        "ChatGPT is generating", "ChatGPT is still generating",
        "Generating a response",
    )
    for ln in lines:
        stripped, lower = ln.strip(), ln.strip().lower()
        if lower.startswith("chatgpt said:") or lower.startswith("chatgpt says:"):
            after = ln.split(":", 1)[1].strip()
            if after: answer_lines.append(after)
            capture = True
            continue
        if capture and any(lower.startswith(pfx.lower()) for pfx in UNWANTED_PREFIXES):
            break
        if capture:
            answer_lines.append(ln)

    clean_answer = "\n".join(answer_lines).strip()

    # save history
    history.append({"role": "user", "content": user_prompt})
    history.append({"role": "assistant", "content": clean_answer})
    save_history(history)

    return clean_answer

# ───── Alias ───────────────────────────────────────────────────────────────
query = run
