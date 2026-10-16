from paddleocr import PaddleOCR
class OCRService:
    def __init__(self) -> None:
        self.ocr = PaddleOCR(lang="en", enable_mkldnn=False)
    def extract_text(self,image_path:str):
        print(f"Running OCR on: {image_path}")
        result = self.ocr.predict(image_path)
        
        extracted_text = []
        
        for page in result:
            texts  = page["rec_texts"]
            scores = page["rec_scores"]
            boxes = page["rec_boxes"]
            for text,score,box in zip(texts,scores,boxes):
                extracted_text.append({
                    "text":text,
                    "score":float(score),
                    "box":box.tolist(),
                })
        print(f"The OCR detected {len(extracted_text)} text regions")
        return extracted_text
    
        