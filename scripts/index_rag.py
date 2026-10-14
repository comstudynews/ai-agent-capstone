from dotenv import load_dotenv
from app.rag import index_demo_documents

load_dotenv()
print("Indexed documents:", index_demo_documents())
