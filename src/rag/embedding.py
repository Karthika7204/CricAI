import os
# Suppress heavy backends to avoid environment conflicts
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_JAX"] = "1"

from transformers.models.bert.modeling_bert import BertModel
from transformers import AutoTokenizer
import torch
import numpy as np

class EmbeddingEngine:
    """
    V5 Stabilized Embedding Engine:
    Direct implementation using Transformers & PyTorch.
    Bypasses unstable AutoModel registry and heavy backends.
    Model: all-MiniLM-L6-v2 (BERT-based)
    """
    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            device = "cpu"
            print(f"Loading local weights (all-MiniLM-L6-v2) on {device}...")
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            # Explicitly load tokenizer and model
            cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._model = BertModel.from_pretrained(model_name)
            cls._model.to(device)
            cls._model.eval()
        return cls._instance

    def _mean_pooling(self, model_output, attention_mask):
        """Perform mean pooling on token embeddings."""
        token_embeddings = model_output[0] 
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, text_list):
        """Encodes text using mean pooling of hidden states."""
        if isinstance(text_list, str):
            text_list = [text_list]
        
        # Internal tokenization
        encoded_input = self._tokenizer(text_list, padding=True, truncation=True, return_tensors='pt')
        
        with torch.no_grad():
            model_output = self._model(**encoded_input)
        
        # Mean pooling
        sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        
        # Normalize (required for all-MiniLM-L6-v2 to work with L2 or cosine)
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        
        return sentence_embeddings.numpy()

    def get_dimension(self):
        return 384
