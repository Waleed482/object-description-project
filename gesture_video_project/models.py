# from transformers import AutoProcessor, BlipForConditionalGeneration
# import torch
# import logging
# from config import logger

# def load_caption_models():
#     try:
#         processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
#         model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
#         device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         if device == 'cuda':
#             model = model.half().to(device)
#         return processor, model, device
#     except Exception as e:
#         logger.error(f"Model load failed: {e}")
#         return None, None, None