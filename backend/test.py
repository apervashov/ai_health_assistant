import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image

PROJECT_ID = "datahackaton-projekt-8"
REGION = "us-central1"
vertexai.init(project=PROJECT_ID, location=REGION)


generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002")
response = generative_multimodal_model.generate_content(["how are you?"])

print(response)