from customtkinter import CTkProgressBar, CTk
from contextlib import redirect_stderr
from FileManagement.IORedirect import IORedirect
from threading import Thread


def load_ai():
    """
    the function that loads the ai
    """
    global pipe

    # imports modules
    with redirect_stderr(IORedirect(progress_bar)):
        from diffusers import AudioLDM2Pipeline
        from torch.cuda import is_available
        from torch import float16

        # loads ai
        repo_id = "cvssp/audioldm2"
        pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=float16)
        pipe = pipe.to("cuda" if is_available() else "cpu")

    print("done")


# creates progress bar for loading AI
pipe = None
progress_bar = CTkProgressBar(CTk(), mode="determinate")
progress_bar.set(0)
progress_bar.pack()
Thread(target=load_ai).start()
progress_bar.master.mainloop()
