#!/usr/bin/env python3
"""
Download Nomic Vision v1.5 model for local deployment

This script downloads the Nomic Vision embedding model for spatial layout analysis.
"""

import os
import sys
from pathlib import Path
from transformers import AutoModel, AutoProcessor, AutoImageProcessor

def download_vision_model(output_dir="./models/nomic-embed-vision-v1.5"):
    """Download Nomic Vision v1.5 model"""
    
    # Model details
    model_name = "nomic-ai/nomic-embed-vision-v1.5"
    model_dir = Path(output_dir)
    
    print("=" * 70)
    print("📥 Downloading Nomic Vision v1.5 Model")
    print("=" * 70)
    print(f"\n📦 Model: {model_name}")
    print(f"📁 Destination: {model_dir.absolute()}")
    print(f"💾 Size: ~1.5GB")
    print(f"📄 License: Apache 2.0 (Open Source)\n")
    
    # Create directory
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    if (model_dir / "config.json").exists():
        print("✅ Vision model already exists!")
        print(f"✅ Using existing model at {model_dir}")
        return True
    
    try:
        print("\n⏳ Downloading vision model... (this may take a few minutes)")
        print("━" * 70)
        
        # Download model
        print("\n1️⃣  Downloading vision model weights...")
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Download processor/tokenizer  
        print("2️⃣  Downloading image processor...")
        try:
            processor = AutoProcessor.from_pretrained(model_name)
        except:
            # Fallback to AutoImageProcessor if AutoProcessor fails
            processor = AutoImageProcessor.from_pretrained(model_name)
        
        # Save locally
        print(f"3️⃣  Saving to {model_dir}...")
        model.save_pretrained(model_dir)
        processor.save_pretrained(model_dir)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Vision model downloaded and ready to use!")
        print("=" * 70)
        
        # Test the model
        print("\n🧪 Testing vision model...")
        print("━" * 70)
        
        import torch
        from PIL import Image
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device: {device}")
        
        # Load model for testing
        test_model = AutoModel.from_pretrained(
            str(model_dir),
            trust_remote_code=True
        ).to(device)
        
        # Create a simple test image
        test_image = Image.new('RGB', (224, 224), color='white')
        
        # Test encoding
        try:
            if hasattr(processor, 'preprocess'):
                inputs = processor.preprocess(test_image, return_tensors="pt").to(device)
            else:
                inputs = processor(test_image, return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = test_model(**inputs)
                if hasattr(outputs, 'last_hidden_state'):
                    embedding = outputs.last_hidden_state.mean(dim=1)
                elif hasattr(outputs, 'pooler_output'):
                    embedding = outputs.pooler_output
                else:
                    # Get the first output if structure is different
                    embedding = outputs[0].mean(dim=1) if len(outputs[0].shape) > 2 else outputs[0]
            
            print(f"✅ Vision test successful!")
            print(f"   Embedding shape: {embedding.shape}")
            print(f"   Sample values: {embedding[0][:5].tolist()}")
            
        except Exception as test_e:
            print(f"⚠️  Vision test had issues but model downloaded: {test_e}")
            # Don't fail the download if test fails
        
        print("\n" + "=" * 70)
        print("🎉 Vision model ready for spatial layout analysis!")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR downloading vision model: {e}")
        print("=" * 70)
        print("\n💡 Troubleshooting:")
        print("━" * 70)
        print("1. Check internet connection")
        print("2. Ensure you have ~2GB free disk space")
        print("3. Install dependencies:")
        print("   pip install transformers torch pillow")
        print("4. Try running with: python -u scripts/download_vision_model.py")
        print()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download Nomic Vision v1.5 for local deployment"
    )
    parser.add_argument(
        "--output",
        default="./models/nomic-embed-vision-v1.5",
        help="Output directory for the model"
    )
    
    args = parser.parse_args()
    
    success = download_vision_model(args.output)
    sys.exit(0 if success else 1)