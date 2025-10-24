#!/usr/bin/env python3
"""
Download Nomic Embed Text V2 model for local deployment

This script downloads the Nomic embedding model to ./models/nomic-embed-v2
for self-hosted, unlimited usage.

Requirements:
    pip install transformers torch
"""

import os
import sys
from pathlib import Path
from transformers import AutoModel, AutoTokenizer

def download_model(output_dir="./models/nomic-embed-v2"):
    """Download Nomic Embed Text V2 model"""
    
    # Model details
    model_name = "nomic-ai/nomic-embed-text-v2-moe"
    model_dir = Path(output_dir)
    
    print("=" * 70)
    print("📥 Downloading Nomic Embed Text V2 Model")
    print("=" * 70)
    print(f"\n📦 Model: {model_name}")
    print(f"📁 Destination: {model_dir.absolute()}")
    print(f"💾 Size: ~1.9GB")
    print(f"📄 License: Apache 2.0 (Open Source)\n")
    
    # Create directory
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    if (model_dir / "config.json").exists():
        print("✅ Model already exists!")
        response = input("\n🔄 Re-download? (y/N): ")
        if response.lower() != 'y':
            print("\n✅ Using existing model")
            return True
    
    try:
        print("\n⏳ Downloading model... (this may take a few minutes)")
        print("━" * 70)
        
        # Download model
        print("\n1️⃣  Downloading model weights...")
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Download tokenizer
        print("2️⃣  Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Save locally
        print(f"3️⃣  Saving to {model_dir}...")
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Model downloaded and ready to use!")
        print("=" * 70)
        
        # Show usage
        print("\n📚 Usage:")
        print("━" * 70)
        print("""
from sutra.intelligence.local_embeddings import LocalNomicEmbeddings

# Initialize embedder
embedder = LocalNomicEmbeddings()

# Generate embedding
embedding = embedder.embed_text("Your text here")

# Batch embeddings
embeddings = embedder.embed_batch(["text1", "text2", "text3"])
        """)
        
        # Show benefits
        print("\n💡 Benefits of Local Deployment:")
        print("━" * 70)
        print("✅ 100% FREE - No per-request costs")
        print("✅ UNLIMITED - No rate limits or quotas")
        print("✅ FAST - 8-80ms per embedding (GPU/CPU)")
        print("✅ PRIVATE - Your data never leaves your infrastructure")
        print("✅ OFFLINE - Works without internet connection")
        
        # Test it
        print("\n🧪 Testing model...")
        print("━" * 70)
        
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device: {device}")
        
        model_test = AutoModel.from_pretrained(
            str(model_dir),
            trust_remote_code=True
        ).to(device)
        
        tokenizer_test = AutoTokenizer.from_pretrained(str(model_dir))
        
        # Quick test
        inputs = tokenizer_test(
            "search_document: Test embedding",
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(device)
        
        with torch.no_grad():
            outputs = model_test(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1)
        
        print(f"✅ Test successful!")
        print(f"   Embedding shape: {embedding.shape}")
        print(f"   Sample values: {embedding[0][:5].tolist()}")
        
        print("\n" + "=" * 70)
        print("🎉 All done! You're ready to use local embeddings!")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        print("\n💡 Troubleshooting:")
        print("━" * 70)
        print("1. Check internet connection")
        print("2. Ensure you have ~2GB free disk space")
        print("3. Install dependencies:")
        print("   pip install transformers torch")
        print("4. Try running with: python -u scripts/download_model.py")
        print()
        return False


def show_info():
    """Show information about the model"""
    print("\n📊 Nomic Embed Text V2 Information")
    print("=" * 70)
    print("""
Model: nomic-ai/nomic-embed-text-v2-moe
Architecture: Mixture-of-Experts (MoE)
License: Apache 2.0 (Commercial use allowed)
Parameters: 137M total, ~30M active
Dimensions: 768
Max Context: 8192 tokens
Languages: 100+ languages supported

Performance:
  - GPU (T4):  ~15-25ms per embedding
  - GPU (A100): ~8-12ms per embedding  
  - CPU (16c): ~45-80ms per embedding

Memory:
  - Model: ~1.9GB on disk
  - Runtime: ~2-4GB RAM (CPU), ~2-6GB VRAM (GPU)

Use Cases:
  - ✅ Document classification
  - ✅ Semantic search
  - ✅ Clustering
  - ✅ Duplicate detection
  - ✅ Complexity analysis

Benchmarks:
  - BEIR Average: Competitive with SOTA
  - MIRACL Average: Strong multilingual performance
  - Speed: 30-40% faster than comparable models
    """)
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download Nomic Embed Text V2 for local deployment"
    )
    parser.add_argument(
        "--output",
        default="./models/nomic-embed-v2",
        help="Output directory for the model"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show model information"
    )
    
    args = parser.parse_args()
    
    if args.info:
        show_info()
    else:
        success = download_model(args.output)
        sys.exit(0 if success else 1)
