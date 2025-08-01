# init_qdrant.py

from utils.vector_store import init_collection

if __name__ == "__main__":
    try:
        init_collection()
        print("✅ Qdrant collection initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize Qdrant collection: {e}")
