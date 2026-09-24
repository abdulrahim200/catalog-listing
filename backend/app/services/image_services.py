from pathlib import Path
import pillow_avif
from PIL import Image

class ImageService:
    @staticmethod
    def normalize_image(input_path:str,output_path:str)->str:
        
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        print(f"Opening image: {input_path}")
        
        image = Image.open(input_path)
        
        print(f"Original format:{image.format}")
        print(f"Original size:{image.size}")
        print(f"Original mode:{image.mode}")
        
        if image.mode != "RGB":
            image = image.convert("RGB")    
        
        image.save(output_path,format="jpeg",quality=95)
        
        print(f"Normalized image saved to: {output_path}")
        
        return str(output_path)