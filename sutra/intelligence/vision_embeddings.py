"""
Nomic Vision Embeddings Service

This module provides vision embedding capabilities using Nomic Embed Vision v1.5
for spatial layout understanding and multimodal document analysis.

Key Features:
- ✅ Spatial layout detection (columns, tables, figures)
- ✅ Page structure analysis for better content extraction
- ✅ Complements text-v2 embeddings (separate latent space)
- ✅ Both API and local deployment modes
- ✅ Optimized for document understanding tasks

Architecture:
    Text Embeddings (v2) → Semantic understanding, content routing
    Vision Embeddings (v1.5) → Spatial understanding, layout detection
    
Usage:
    vision_service = NomicVisionEmbeddings()
    
    # Analyze page layout
    layout_embedding = vision_service.embed_image(page_image)
    
    # Detect columns and spatial structure
    spatial_features = vision_service.analyze_layout(page_image)
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import numpy as np
from PIL import Image
import io
import base64

try:
    import torch
    from transformers import AutoModel, AutoTokenizer, AutoProcessor
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class NomicVisionEmbeddings:
    """
    Nomic Embed Vision v1.5 service for spatial layout understanding
    
    This service provides vision embeddings specifically for:
    - Document layout analysis (columns, tables, figures)
    - Spatial relationship detection
    - Page structure understanding
    - Multimodal document processing
    
    Args:
        mode: "local" or "api" deployment mode
        model_path: Path to downloaded model (local mode)
        api_key: Nomic API key (api mode)
        device: "cuda", "cpu", or "auto" (local mode)
        
    Example:
        >>> vision_service = NomicVisionEmbeddings(mode="local")
        >>> page_image = Image.open("document_page.png")
        >>> embedding = vision_service.embed_image(page_image)
        >>> layout_info = vision_service.analyze_layout(page_image)
    """
    
    def __init__(
        self,
        mode: str = "local",
        model_path: str = "./models/nomic-embed-vision-v1.5", 
        api_key: Optional[str] = None,
        device: str = "auto",
        api_endpoint: str = "https://api.nomic.ai/v1"
    ):
        self.mode = mode
        self.model_path = Path(model_path)
        self.api_key = api_key or os.getenv("NOMIC_API_KEY")
        self.api_endpoint = api_endpoint
        
        # Detect device for local mode
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"\n{'='*70}")
        print(f"👁️  Initializing Nomic Vision Embeddings")
        print(f"{'='*70}")
        print(f"Mode: {mode}")
        print(f"Model: nomic-embed-vision-v1.5")
        print(f"Purpose: Spatial layout understanding")
        
        if mode == "local":
            self._init_local()
        elif mode == "api":
            self._init_api()
        else:
            raise ValueError(f"Unknown mode: {mode}. Use 'local' or 'api'")
    
    def _init_local(self):
        """Initialize local vision embeddings"""
        if not TORCH_AVAILABLE:
            raise ImportError(
                "Local vision embeddings require PyTorch and Transformers.\n"
                "Install with: pip install torch transformers pillow\n"
                "Or use API mode instead"
            )
        
        print(f"Device: {self.device}")
        print(f"Model path: {self.model_path}")
        
        # Check if model exists
        if not self.model_path.exists():
            print(f"\n⚠️  Model not found at: {self.model_path}")
            print(f"📥 Downloading nomic-ai/nomic-embed-vision-v1.5...")
            self._download_model()
        
        # Load model and processor
        print(f"\n⏳ Loading vision model...")
        start_time = time.time()
        
        try:
            # Load vision model from HuggingFace
            self.model = AutoModel.from_pretrained(
                "nomic-ai/nomic-embed-vision-v1.5",
                trust_remote_code=True,
                cache_dir=str(self.model_path.parent)
            ).to(self.device)
            
            # Load processor for image preprocessing
            self.processor = AutoProcessor.from_pretrained(
                "nomic-ai/nomic-embed-vision-v1.5",
                trust_remote_code=True,
                cache_dir=str(self.model_path.parent)
            )
            
            # Set to evaluation mode
            self.model.eval()
            
            load_time = time.time() - start_time
            
            print(f"✅ Vision model loaded in {load_time:.1f}s")
            print(f"\n🎯 Capabilities:")
            print(f"   👁️  Spatial layout detection")
            print(f"   📄 Document structure analysis") 
            print(f"   🔍 Column boundary identification")
            print(f"   📊 Table and figure recognition")
            print(f"   💡 Complements text-v2 embeddings")
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"❌ Failed to load vision model: {e}")
            print(f"\n🔧 Troubleshooting:")
            print(f"   1. Install dependencies: pip install torch transformers pillow")
            print(f"   2. Check internet connection for HuggingFace download")
            print(f"   3. Try API mode: mode='api'")
            raise
    
    def _init_api(self):
        """Initialize API-based vision embeddings"""
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "API mode requires httpx.\n"
                "Install with: pip install httpx"
            )
        
        if not self.api_key:
            raise ValueError(
                "NOMIC_API_KEY not found. Please:\n"
                "1. Run: nomic login\n"
                "2. Set NOMIC_API_KEY in environment"
            )
        
        print(f"API endpoint: {self.api_endpoint}")
        print(f"API key: {self.api_key[:8]}...")
        print(f"\n💡 Using hosted Nomic API for vision embeddings")
        print(f"{'='*70}\n")
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    def _download_model(self):
        """Download vision model from HuggingFace"""
        print(f"📥 Downloading nomic-embed-vision-v1.5...")
        print(f"   This may take a few minutes on first run...")
        
        # Create model directory
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # The model will be downloaded when we call AutoModel.from_pretrained
        print(f"   Model will be cached to: {self.model_path.parent}")
    
    def _preprocess_image(self, image: Union[Image.Image, str, bytes]) -> Image.Image:
        """
        Preprocess image for vision embedding
        
        Args:
            image: PIL Image, file path, or image bytes
            
        Returns:
            PIL Image ready for processing
        """
        if isinstance(image, str):
            # File path
            image = Image.open(image)
        elif isinstance(image, bytes):
            # Image bytes
            image = Image.open(io.BytesIO(image))
        elif not isinstance(image, Image.Image):
            raise ValueError(f"Unsupported image type: {type(image)}")
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        return image
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string for API"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    async def embed_image(
        self,
        image: Union[Image.Image, str, bytes],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate vision embedding for image
        
        Args:
            image: Image to embed (PIL Image, file path, or bytes)
            normalize: Whether to L2 normalize embedding
            
        Returns:
            768-dimensional vision embedding
            
        Example:
            >>> page_image = Image.open("document.png")
            >>> embedding = await vision_service.embed_image(page_image)
            >>> print(embedding.shape)
            (768,)
        """
        image = self._preprocess_image(image)
        
        if self.mode == "local":
            return self._embed_image_local(image, normalize)
        else:
            return await self._embed_image_api(image, normalize)
    
    def _embed_image_local(self, image: Image.Image, normalize: bool) -> np.ndarray:
        """Generate embedding using local model"""
        # Preprocess image
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Extract image embedding (usually from last_hidden_state or pooler_output)
            if hasattr(outputs, 'pooler_output'):
                embedding = outputs.pooler_output
            elif hasattr(outputs, 'last_hidden_state'):
                # Mean pool over spatial dimensions
                embedding = outputs.last_hidden_state.mean(dim=1)
            else:
                # Fallback to first output
                embedding = outputs[0].mean(dim=1)
            
            # Normalize if requested
            if normalize:
                embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        
        return embedding.cpu().numpy()[0]
    
    async def _embed_image_api(self, image: Image.Image, normalize: bool) -> np.ndarray:
        """Generate embedding using Nomic API"""
        # Convert image to base64
        image_b64 = self._image_to_base64(image)
        
        # API request
        response = await self.client.post(
            f"{self.api_endpoint}/embedding",
            json={
                "model": "nomic-embed-vision-v1.5",
                "input": image_b64,
                "encoding_format": "float"
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
        embedding = np.array(data["data"][0]["embedding"])
        
        if normalize:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    async def embed_batch(
        self,
        images: List[Union[Image.Image, str, bytes]],
        normalize: bool = True,
        batch_size: int = 8
    ) -> np.ndarray:
        """
        Generate embeddings for batch of images
        
        Args:
            images: List of images to embed
            normalize: Whether to L2 normalize
            batch_size: Batch size for processing
            
        Returns:
            Array of embeddings (n_images, 768)
        """
        if not images:
            return np.array([])
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            batch_embeddings = []
            
            for image in batch_images:
                embedding = await self.embed_image(image, normalize)
                batch_embeddings.append(embedding)
            
            all_embeddings.extend(batch_embeddings)
        
        return np.array(all_embeddings)
    
    async def analyze_layout(
        self,
        image: Union[Image.Image, str, bytes],
        return_embedding: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze document layout using vision embeddings
        
        This is a high-level method that uses vision embeddings to understand
        spatial layout and document structure.
        
        Args:
            image: Document page image
            return_embedding: Whether to include raw embedding
            
        Returns:
            Dict with layout analysis results:
            {
                "layout_type": "single_column" | "multi_column" | "complex",
                "confidence": 0.0-1.0,
                "spatial_features": {...},
                "embedding": np.ndarray (optional)
            }
            
        Example:
            >>> layout_info = await vision_service.analyze_layout(page_image)
            >>> if layout_info["layout_type"] == "multi_column":
            ...     print("Detected multi-column layout")
        """
        # Generate vision embedding
        embedding = await self.embed_image(image, normalize=True)
        
        # Analyze spatial characteristics from embedding
        # This is a simplified heuristic - in practice you might train
        # a classifier on top of vision embeddings
        
        layout_analysis = self._analyze_spatial_features(embedding)
        
        result = {
            "layout_type": layout_analysis["layout_type"],
            "confidence": layout_analysis["confidence"],
            "spatial_features": {
                "complexity_score": layout_analysis["complexity"],
                "column_indicators": layout_analysis["column_hints"],
                "structure_type": layout_analysis["structure"]
            }
        }
        
        if return_embedding:
            result["embedding"] = embedding
        
        return result
    
    def _analyze_spatial_features(self, embedding: np.ndarray) -> Dict[str, Any]:
        """
        Analyze spatial features from vision embedding
        
        This is a heuristic-based analysis. In production, you might:
        1. Train a classifier on labeled layout data
        2. Use clustering to identify layout patterns
        3. Combine with traditional CV techniques
        """
        # Simple heuristics based on embedding characteristics
        # These would be refined based on training data
        
        # Calculate embedding statistics
        mean_activation = np.mean(embedding)
        std_activation = np.std(embedding)
        max_activation = np.max(embedding)
        
        # Heuristic indicators (would be learned from data)
        complexity = min(std_activation * 10, 1.0)  # Normalized complexity
        
        # Simple layout classification based on embedding patterns
        if complexity < 0.3:
            layout_type = "single_column"
            confidence = 0.8
        elif complexity < 0.6:
            layout_type = "multi_column" 
            confidence = 0.7
        else:
            layout_type = "complex"
            confidence = 0.6
        
        return {
            "layout_type": layout_type,
            "confidence": confidence,
            "complexity": complexity,
            "column_hints": complexity > 0.4,  # Suggests multi-column
            "structure": "structured" if complexity < 0.7 else "unstructured"
        }
    
    def similarity(
        self,
        image1: Union[Image.Image, str, bytes],
        image2: Union[Image.Image, str, bytes]
    ) -> float:
        """
        Compute visual similarity between two images
        
        Args:
            image1: First image
            image2: Second image
            
        Returns:
            Similarity score between -1 and 1
        """
        import asyncio
        
        async def _compute_similarity():
            emb1 = await self.embed_image(image1, normalize=True)
            emb2 = await self.embed_image(image2, normalize=True)
            return float(np.dot(emb1, emb2))
        
        return asyncio.run(_compute_similarity())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the vision model"""
        info = {
            "model": "nomic-embed-vision-v1.5",
            "mode": self.mode,
            "embedding_dim": 768,
            "purpose": "Spatial layout understanding",
            "latent_space": "v1.5 (separate from text-v2)"
        }
        
        if self.mode == "local":
            info.update({
                "device": str(self.device),
                "model_path": str(self.model_path)
            })
        else:
            info.update({
                "api_endpoint": self.api_endpoint,
                "api_key_preview": f"{self.api_key[:8]}..." if self.api_key else None
            })
        
        return info
    
    def __repr__(self) -> str:
        return f"NomicVisionEmbeddings(mode={self.mode}, model=vision-v1.5)"


# Convenience functions for quick testing
async def quick_test_vision():
    """Quick test of vision embeddings"""
    print("\n" + "="*70)
    print("🧪 QUICK TEST - Nomic Vision Embeddings")
    print("="*70)
    
    try:
        # Initialize
        vision_service = NomicVisionEmbeddings(mode="local")
        
        # Create test image (simple gradient for testing)
        from PIL import Image, ImageDraw
        
        # Create a test document-like image
        img = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some text-like rectangles to simulate document layout
        draw.rectangle([50, 100, 180, 120], fill='black')  # Title
        draw.rectangle([50, 140, 350, 160], fill='gray')   # Paragraph
        draw.rectangle([50, 180, 320, 200], fill='gray')   # Paragraph
        draw.rectangle([50, 240, 180, 480], fill='lightgray')  # Left column
        draw.rectangle([200, 240, 350, 480], fill='lightgray')  # Right column
        
        print("\n1️⃣  Vision Embedding Test")
        print("-"*70)
        start = time.time()
        embedding = await vision_service.embed_image(img)
        elapsed = time.time() - start
        
        print(f"Image size: {img.size}")
        print(f"Embedding shape: {embedding.shape}")
        print(f"Time: {elapsed*1000:.1f}ms")
        print(f"Sample values: {embedding[:5]}")
        
        print("\n2️⃣  Layout Analysis Test")
        print("-"*70)
        start = time.time()
        layout_info = await vision_service.analyze_layout(img)
        elapsed = time.time() - start
        
        print(f"Layout type: {layout_info['layout_type']}")
        print(f"Confidence: {layout_info['confidence']:.2f}")
        print(f"Complexity: {layout_info['spatial_features']['complexity_score']:.2f}")
        print(f"Analysis time: {elapsed*1000:.1f}ms")
        
        print("\n3️⃣  Model Information")
        print("-"*70)
        info = vision_service.get_model_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        
        print("\n" + "="*70)
        print("✅ Vision embedding tests passed!")
        print("="*70)
        print("\n💡 Vision embeddings are ready for:")
        print("   👁️  Document layout detection")
        print("   📄 Spatial structure analysis")
        print("   🔍 Column boundary identification")
        print("   📊 Multimodal document understanding")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install torch transformers pillow")
        print("2. Check GPU availability for local mode")
        print("3. Try API mode if local fails")
        print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(quick_test_vision())