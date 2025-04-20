from io import TextIOBase


class IORedirect(TextIOBase):
    def __init__(self, progress_bar):
        super().__init__()
        self.progress_bar = progress_bar
        self.buffer = ""

    def write(self, message):
        self.buffer += message
        if "\r" in message or "\n" in message:
            lines = self.buffer.strip().splitlines()
            if lines:
                last_line = lines[-1]
                last_line = last_line.replace("Loading pipeline components...:", "")
                percent_index = last_line.find('%')
                try:
                    progress_value = int(last_line[:percent_index])/100
                    self.progress_bar.after(0, lambda: self.progress_bar.set(progress_value)) #trim lastline
                except ValueError:
                    pass
            self.buffer = ""

    def flush(self):
        pass
