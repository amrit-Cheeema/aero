from PIL import Image, ImageFile
import ollama
from vram import get_vram
import asyncio

class image:
    """
    A class for handling images, opening, describing and saving them
    """
    def __init__(self):
        im: ImageFile.ImageFile | None = None
        fileName: str = ""
        pass
    
    def open(self, fileName: str) -> image:
        """Opens image from file and stores it in self.im and the file name in self.fileName, returns self for chaining"""
        try:
            im = Image.open(fileName)
            self.im, self.fileName = im, fileName
        except OSError:
            print(f"Failed opening {fileName}")
        return self
    def describe(self) -> image:
        """
        Describes the image and prints to stdout
        """
        print(f"Image format: {self.im.format}\nImage Size (x,y)(px): {self.im.size}\nMode: {self.im.mode}")
        return self
    
    def save(self, outFile) -> None:
        """Saves image to path given by outfile handeling conversions by using extension
            - ie (obj.save("out.png"))
        """
        if self.fileName != outFile:
            try:
                with Image.open(self.fileName) as im:
                    im.save(outFile)
            except OSError:
                print(f"Cannot convert {self.fileName} to {outFile}")

class LLM:
    """
    A class for handling LLMs, discovering them and chatting with them
    
    Attributes
    ----------
    - models: dict[str, int]
        A dictionary of model names and their sizes in GB
    - vram_used: float
        The amount of VRAM currently being used in GB
    - total_vram: 
        The total amount of VRAM available in GB
    
    Methods
    -------
    chat(name='qwen2.5-coder', content='Say "Hello World!"')
        Send content to specified LLM

    """
    vram_used: float
    total_vram: float
    def __init__(self):

        self.models: dict[str, int] = {}
        self.__discover()
        self.vram_used, self.total_vram = get_vram()
    
    async def chat(self, name: str, content: str, stream:bool=False) -> None|str:
        """Takes in a model name and message and sends it to the models, returns the output and logs LLM message to stdout"""
        if name not in self.models:
            print("Model does not exists/not downloaded.")
            print("Models available:")
            for name in self.models.keys():
                print(f" - {name}")
            return None
        client = ollama.AsyncClient()
        res = await client.chat(model=name, messages=[
            {
                'role': 'user',
                'content': content,
            },
        ], stream=stream)
        if stream:
            async for chunk in res:
                print(chunk['message']['content'], end='', flush=True)
            print("")
        else:
            print(res["message"]["content"])
        return res
        

    def __discover(self):
        """Discovers all models with ollama and stores the name and size attributes self.models"""
        models = ollama.list()
        for model in models['models']:
            name: str = str(model['model'])
            size_gb: int = float(model['size']) / 1e9
            
            # storing inside self.models
            self.models[name] = round(size_gb, 2)

"should be able to take a photo and classify it"
def main():
    llm=LLM()
    asyncio.run(llm.chat("gemma4:e2b", "hello", True))
    print(llm.vram_used / llm.total_vram)
    print(llm.models)
    

    im = image()
    i = im.open("hello.png").describe()
    
    
    return

main()



