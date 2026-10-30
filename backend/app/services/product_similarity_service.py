from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
class ProductSimilarityService:
        def __init__(self) -> None:
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        @staticmethod
        def build_product_text(product)->str:
            #Join all parts of the text
            parts = [
                 product.brand or "",
                 product.product_name or "",
                 product.category or "",
                 product.description or "",
            ] 
             
            parts.extend(product.ingredients or [])
            return " ".join(str(part) for part in parts if part).strip()
        
        def calculate_score(self,product_a,product_b)->float:
            
            text_a = self.build_product_text(product_a)
            text_b = self.build_product_text(product_b)
            
            if not text_a or not text_b :
                return 0.0
            
            embeddings = self.model.encode([text_a,text_b],show_progress_bar=True)
            
            score = cosine_similarity([embeddings[0]],[embeddings[1]])[0][0]
            
            return round(float(score),4)
        @staticmethod
        def normalize_text(value)->str:
            if value is None:
                return ""
            return " ".join(str(value).casefold().split())
        @classmethod
        def text_similarity(cls,value_a,value_b)->float:
            
            text_a = cls.normalize_text(value_a)
            text_b = cls.normalize_text(value_b)
            
            if not text_a or not text_b:
                return 0.0
            return SequenceMatcher(None,text_a,text_b).ratio()
        @classmethod
        def compare_similarity_score(cls,product_a,product_b)->dict:
            brand_score = cls.text_similarity(product_a.brand,product_b.brand,)           
            name_score = cls.text_similarity(product_a.product_name,product_b.product_name,)
            category_score = cls.text_similarity(product_a.category,product_b.category,)
            size_a = product_a.pack_size
            size_b = product_b.pack_size
            
            if (
                size_a is not None 
                and size_b is not None
                and size_a.value is not None 
                and size_b.value is not None 
                and size_a.unit and size_b.unit ):
                
                unit_a = cls.normalize_text(size_a.unit)
                unit_b = cls.normalize_text(size_b.unit)
                pack_size_score = (1.0 if size_a.value == size_b.value and unit_a == unit_b else 0.0 )
            else:
                pack_size_score = None
            identifiers_a = product_a.identifiers
            identifiers_b = product_b.identifiers
            barcode_a = (identifiers_a.barcode if identifiers_a else None)
            barcode_b = (identifiers_b.barcode if identifiers_b else None)
            sku_a = identifiers_a.sku if identifiers_a else None
            sku_b = identifiers_b.sku if identifiers_b else None
            
            if barcode_a and barcode_b:
                barcode_match = (cls.normalize_text(barcode_a) == cls.normalize_text(barcode_b))
            else:
                barcode_match = None
            if sku_a and sku_b:
                sku_match = ( cls.normalize_text(sku_a)== cls.normalize_text(sku_b))
            else:
                sku_match = None

            return {
                "brand_similarity": round(brand_score, 4),
                "name_similarity": round(name_score, 4),
                "category_similarity": round(category_score, 4),
                "pack_size_similarity": pack_size_score,
                "barcode_match": barcode_match,
                "sku_match": sku_match,
                   }
            
                       
            
            