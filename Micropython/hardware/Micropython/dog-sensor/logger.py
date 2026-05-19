from _lib.display import Display
class Logger:
    def __init__(self, display: Display, color=0xFFFF, background=0x0000, line_width=10, width_pct=0.5):
        self.display = display
        self.color = color
        self.background = background
        self.line_width = line_width
        
        # Define the "zone" for the logger
        # start_x is the right-most edge, end_x is the limit on the left
        self.start_x = self.display.width - self.line_width
        self.end_x = int(self.display.width * (1 - width_pct))
        
        self.x_pos = self.start_x
        self.clear()

    def clear(self):
        """Clears only the logger's designated side of the screen."""
        # We draw a filled rectangle over the logger area to 'clear' it
        # without touching the rest of the display
        rect_width = self.display.width - self.end_x
        self.display.fill_rectangle(self.end_x, 0, rect_width, self.display.height, self.background)
        self.x_pos = self.start_x

    def log(self, message, color=0xFFFF):
        """
        Writes text within the assigned side. 
        Resets to start_x if it hits the end_x boundary.
        """
        # If the next line exceeds our boundary (the 'middle' or set width)
        if self.x_pos < self.end_x:
            self.clear()

        # Render the text
        self.display.draw_text8x8(
            self.x_pos, 
            0, 
            str(message), 
            color, 
            rotate=90
        )
        
        self.x_pos -= self.line_width

    def info(self, message):
        self.log(f"INFO: {message}", 0x00FF00)

    def error(self, message):
        self.log(f"ERR: {message}", 0xFF0000)
