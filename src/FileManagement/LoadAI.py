from customtkinter import CTkProgressBar, CTk, CTkLabel
from tkinter.messagebox import askokcancel
from contextlib import redirect_stderr
from FileManagement.IORedirect import IORedirect
from threading import Thread


def load_ai():
    """
    the function that loads the ai
    """
    global pipe

    # imports modules
    try:
        with redirect_stderr(IORedirect(progress_bar)):
            from diffusers import AudioLDM2Pipeline
            progress_bar.set(1 / 3)
            from torch.cuda import is_available
            progress_bar.set(2 / 3)
            from torch import float16
            progress_bar.set(3 / 3)

            # loads ai
            label.configure(text="Loading AI...")
            repo_id = "cvssp/audioldm2"
            pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=float16)
            pipe = pipe.to("cuda" if is_available() else "cpu")

        # remaining loading message
        progress_bar.set(0)
        label.configure(text="Cleaning Up...")
        root.update_idletasks()
        root.quit()

    # handles when user quits while still loading
    except RuntimeError:
        pass


# creates loading menu
root = CTk()
root.title("Orbital Resonance")
root.resizable(False, False)
label = CTkLabel(root, text="Importing Modules...", font=("Arial", 20))
label.pack(padx=50, pady=(50, 0))
progress_bar = CTkProgressBar(root, mode="determinate", width=500)
progress_bar.set(0)
progress_bar.pack(padx=50, pady=(10, 50))

# starts thread
pipe = None
thread = Thread(target=load_ai)
thread.start()
root.protocol("WM_DELETE_WINDOW", lambda: [root.destroy(), exit()] if askokcancel(
    "Exit", "You are are about to exit. Continue?") else None)
root.mainloop()
