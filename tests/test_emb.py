import os
# Suppress heavy backends to avoid environment conflicts
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_JAX"] = "1"

try:
    print("Testing explicit import with backend suppression...")
    from transformers.models.bert.modeling_bert import BertModel
    from transformers import AutoTokenizer
    import torch
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)
    print("Model loaded successfully!")
    
    text = ["Hello world"]
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    print(f"Output shape: {outputs.last_hidden_state.shape}")

except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
