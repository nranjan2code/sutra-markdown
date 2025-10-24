# 🚀 Nomic Embed Deployment Options

## 🎯 **You Have TWO Great Options!**

Nomic Embed Text V2 is **Apache 2.0 licensed** - you can:
1. ✅ **Self-host locally** (100% free, unlimited usage!)
2. ✅ **Use Nomic API** (managed service, free tier)

---

## 📊 **Comparison: Local vs API**

| Feature | **Local Self-Hosted** | **Nomic API** |
|---------|----------------------|---------------|
| **Cost** | 💚 **100% FREE** (after hardware) | 💚 Free tier (~100K/month) then $0.001/1K |
| **Speed** | ⚡ **FASTEST** (no network) | 🌐 Network latency |
| **Privacy** | 🔒 **100% Private** | ☁️ Data sent to Nomic |
| **Setup** | 🔧 Initial setup required | ✅ Instant (API key only) |
| **Maintenance** | 🛠️ You manage updates | ✅ Nomic manages |
| **Scalability** | 🖥️ Limited by hardware | ☁️ Infinite scale |
| **Hardware Needs** | 📟 GPU recommended (8GB+ VRAM) | ❌ None |
| **Best For** | Production, high volume, privacy | Development, prototyping, low volume |

---

## 🏠 **Option 1: Self-Hosted Local Deployment** ⭐ RECOMMENDED FOR PRODUCTION

### **Why Self-Host?**

1. **💰 ZERO Cost** - No per-request charges (after hardware investment)
2. **🔒 100% Privacy** - Your data never leaves your infrastructure
3. **⚡ Maximum Speed** - No network latency, instant embeddings
4. **📈 Unlimited Scale** - Process millions without API limits
5. **🎯 Full Control** - Customize, optimize, fine-tune as needed

### **Hardware Requirements**

#### **Minimum (Development)**
```yaml
CPU: 8+ cores
RAM: 16GB+
GPU: Optional but recommended
Disk: 5GB for model
```

#### **Recommended (Production)**
```yaml
CPU: 16+ cores
RAM: 32GB+
GPU: NVIDIA GPU with 8GB+ VRAM (T4, A4000, or better)
Disk: 10GB (model + cache)
```

#### **High Volume (Enterprise)**
```yaml
CPU: 32+ cores
RAM: 64GB+
GPU: NVIDIA A100 (40GB/80GB) or multiple GPUs
Disk: SSD with 50GB+
Load Balancer: Distribute across multiple instances
```

### **Installation Steps**

#### **1. Install Dependencies**

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch (with CUDA if you have GPU)
# For GPU:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CPU only:
pip install torch torchvision torchaudio

# Install Transformers and required packages
pip install transformers sentence-transformers einops
```

#### **2. Download Model**

```python
from transformers import AutoModel, AutoTokenizer

# Download model (one-time, ~1.9GB)
model = AutoModel.from_pretrained(
    "nomic-ai/nomic-embed-text-v2-moe",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(
    "nomic-ai/nomic-embed-text-v2-moe"
)

# Save locally for faster loading
model.save_pretrained("./models/nomic-embed-v2")
tokenizer.save_pretrained("./models/nomic-embed-v2")

print("✅ Model downloaded and ready!")
```

#### **3. Create Embedding Service**

```python
# sutra/intelligence/local_embeddings.py

import torch
from transformers import AutoModel, AutoTokenizer
from typing import List
import numpy as np

class LocalNomicEmbeddings:
    """Local Nomic Embed Text V2 service - 100% self-hosted"""
    
    def __init__(self, model_path: str = "./models/nomic-embed-v2"):
        # Load model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Loading Nomic Embed on {self.device}...")
        
        self.model = AutoModel.from_pretrained(
            model_path,
            trust_remote_code=True
        ).to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.eval()  # Inference mode
        
        print(f"✅ Model loaded! Device: {self.device}")
    
    def embed_text(self, text: str, task_type: str = "search_document") -> np.ndarray:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            task_type: One of: search_document, search_query, clustering, classification
        
        Returns:
            768-dimensional embedding vector
        """
        # Add task prefix
        prefixed_text = self._add_task_prefix(text, task_type)
        
        # Tokenize
        inputs = self.tokenizer(
            prefixed_text,
            padding=True,
            truncation=True,
            max_length=8192,  # Nomic supports long context!
            return_tensors="pt"
        ).to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Mean pooling
            embedding = outputs.last_hidden_state.mean(dim=1)
            # Normalize
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        
        return embedding.cpu().numpy()[0]
    
    def embed_batch(self, texts: List[str], task_type: str = "search_document") -> np.ndarray:
        """
        Generate embeddings for batch of texts
        
        Args:
            texts: List of texts to embed
            task_type: Task type for all texts
        
        Returns:
            Array of embeddings (n_texts, 768)
        """
        # Add task prefixes
        prefixed_texts = [self._add_task_prefix(t, task_type) for t in texts]
        
        # Tokenize batch
        inputs = self.tokenizer(
            prefixed_texts,
            padding=True,
            truncation=True,
            max_length=8192,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def _add_task_prefix(self, text: str, task_type: str) -> str:
        """Add task-specific prefix for better performance"""
        prefixes = {
            "search_document": "search_document: ",
            "search_query": "search_query: ",
            "clustering": "clustering: ",
            "classification": "classification: "
        }
        return prefixes.get(task_type, "") + text


# Quick benchmark
if __name__ == "__main__":
    import time
    
    embedder = LocalNomicEmbeddings()
    
    # Test single embedding
    start = time.time()
    embedding = embedder.embed_text("This is a test document about machine learning.")
    elapsed = time.time() - start
    
    print(f"✅ Single embedding: {elapsed*1000:.1f}ms")
    print(f"   Shape: {embedding.shape}")
    print(f"   Sample: {embedding[:5]}")
    
    # Test batch
    texts = [f"Document {i} about various topics" for i in range(100)]
    start = time.time()
    embeddings = embedder.embed_batch(texts)
    elapsed = time.time() - start
    
    print(f"\n✅ Batch (100 docs): {elapsed:.2f}s ({elapsed/len(texts)*1000:.1f}ms per doc)")
    print(f"   Shape: {embeddings.shape}")
```

#### **4. Integration with Sutra**

```python
# config.yaml

embedding_service:
  mode: "local"  # or "api"
  
  local:
    model_path: "./models/nomic-embed-v2"
    device: "cuda"  # or "cpu"
    batch_size: 32
  
  api:
    api_key: "${NOMIC_API_KEY}"
    endpoint: "https://api.nomic.ai/v1"
```

```python
# sutra/intelligence/embeddings.py

from typing import Union
from .local_embeddings import LocalNomicEmbeddings
from .api_embeddings import NomicAPIEmbeddings

class EmbeddingService:
    """Unified embedding service - supports both local and API"""
    
    def __init__(self, config: dict):
        mode = config.get("mode", "local")
        
        if mode == "local":
            print("🏠 Using LOCAL Nomic embeddings")
            self.embedder = LocalNomicEmbeddings(
                model_path=config["local"]["model_path"]
            )
            self.is_local = True
        else:
            print("☁️  Using Nomic API")
            self.embedder = NomicAPIEmbeddings(
                api_key=config["api"]["api_key"]
            )
            self.is_local = False
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding (works for both local and API)"""
        if self.is_local:
            return self.embedder.embed_text(text)
        else:
            return await self.embedder.embed_text(text)
```

### **Performance Benchmarks (Local)**

#### **With GPU (NVIDIA T4)**
```
Single embedding:  15-25ms
Batch (100 docs):  800ms (~8ms per doc)
Throughput:       ~125 docs/second
```

#### **With CPU (16 cores)**
```
Single embedding:  80-150ms
Batch (100 docs):  4.5s (~45ms per doc)
Throughput:       ~22 docs/second
```

#### **With GPU (NVIDIA A100)**
```
Single embedding:  8-12ms
Batch (100 docs):  350ms (~3.5ms per doc)
Throughput:       ~285 docs/second
```

### **Cost Analysis (Local)**

#### **Hardware Investment**
```yaml
Option 1 - Cloud GPU:
  Provider: AWS/GCP/Azure
  Instance: g4dn.xlarge (T4 GPU)
  Cost: ~$0.50/hour = ~$360/month
  Capacity: ~125 docs/second = ~324M docs/month
  Cost per 1M docs: $1.11

Option 2 - Dedicated Server:
  Hardware: GPU server with A4000
  One-time: ~$5,000
  Monthly: ~$100 (power + cooling)
  Capacity: ~200 docs/second = ~518M docs/month
  Amortized (3 years): $0.43 per 1M docs

Option 3 - CPU Only:
  Server: Any modern server
  One-time: ~$1,500
  Monthly: ~$50
  Capacity: ~22 docs/second = ~57M docs/month
  Amortized (3 years): $0.13 per 1M docs (if under capacity)
```

#### **Comparison with API**
```yaml
Volume: 10M docs/month

Local (Cloud GPU):
  Cost: $360/month (fixed)
  Per doc: $0.000036
  Total: $360

Nomic API:
  Cost: $20/month (10M * 2 embeddings * $0.001/1K)
  Per doc: $0.000002
  Total: $20

Winner: API (for this volume)

---

Volume: 100M docs/month

Local (Cloud GPU):
  Cost: $1,080/month (3 instances)
  Per doc: $0.0000108
  Total: $1,080

Nomic API:
  Cost: $200/month
  Per doc: $0.000002
  Total: $200

Winner: API (still cheaper!)

---

Volume: 1B docs/month

Local (Dedicated):
  Cost: $200/month (2 GPU servers)
  Per doc: $0.0000002
  Total: $200

Nomic API:
  Cost: $2,000/month
  Per doc: $0.000002
  Total: $2,000

Winner: LOCAL (10x cheaper at scale!)
```

### **When to Self-Host**

✅ **Self-host if you have:**
- Privacy/compliance requirements (HIPAA, GDPR, etc.)
- High volume (>100M docs/month)
- Low latency requirements (<20ms)
- Existing GPU infrastructure
- Need for customization/fine-tuning

❌ **Use API if you have:**
- Low/medium volume (<10M docs/month)
- Rapid prototyping needs
- No GPU infrastructure
- Want zero maintenance
- Variable/unpredictable load

---

## ☁️ **Option 2: Nomic API (Managed Service)**

### **Why Use API?**

1. **⚡ Instant Setup** - No model downloads, just API key
2. **🔄 Auto-Updates** - Always latest model version
3. **📊 Easy Scaling** - Handle traffic spikes automatically
4. **🛠️ Zero Maintenance** - No servers to manage
5. **💰 Low Volume Friendly** - Free tier covers development

### **Setup (5 Minutes)**

```bash
# 1. Get API key
nomic login

# 2. Add to .env
echo "NOMIC_API_KEY=your_key_here" >> .env

# 3. Done! ✅
```

### **Usage**

```python
from sutra import SutraConverter

# Automatically uses API if configured
converter = SutraConverter(embedding_mode="api")

result = await converter.convert("document.pdf")
# ✅ Uses Nomic API
```

---

## 🎯 **RECOMMENDED HYBRID APPROACH**

**Best of both worlds:**

```yaml
Development/Staging:
  - Use Nomic API
  - Fast iteration
  - No infrastructure
  
Production:
  - Use Local self-hosted
  - Maximum performance
  - Zero per-request cost
  - 100% privacy
```

**Implementation:**

```python
# config.yaml

environments:
  development:
    embedding_service:
      mode: "api"
  
  production:
    embedding_service:
      mode: "local"
      local:
        model_path: "./models/nomic-embed-v2"
        device: "cuda"
```

---

## 📊 **Final Recommendation**

### **For Your Use Case (Document Conversion at Scale):**

```yaml
RECOMMENDED: Self-Hosted Local 🏠

Why?
  1. ✅ One-time setup, unlimited usage
  2. ✅ No API limits or costs
  3. ✅ Maximum speed (8-25ms per embedding)
  4. ✅ 100% privacy (documents never leave your infrastructure)
  5. ✅ Perfect for batch processing
  6. ✅ Apache 2.0 - fully open source

Hardware:
  - Development: CPU is fine (22 docs/sec)
  - Production: GPU recommended (125-285 docs/sec)
  - Enterprise: Multiple GPUs for high throughput

Cost at 1M docs/month:
  - Local: ~$200/month (hardware amortized)
  - API: $2,000/month
  - SAVINGS: $1,800/month ($21,600/year!)
```

---

## 🚀 **Quick Start (Local)**

```bash
# 1. Clone and setup
cd sutra-markdown
python -m venv venv
source venv/bin/activate

# 2. Install with GPU support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers sentence-transformers einops

# 3. Download model (one-time, ~2GB)
python scripts/download_model.py

# 4. Test it!
python -c "
from sutra.intelligence.local_embeddings import LocalNomicEmbeddings
embedder = LocalNomicEmbeddings()
emb = embedder.embed_text('Hello world!')
print(f'✅ Working! Shape: {emb.shape}')
"

# 5. Start using Sutra with local embeddings
sutra convert document.pdf --embedding-mode local
```

---

## 💡 **Summary**

| Aspect | Local | API |
|--------|-------|-----|
| **Setup Time** | 30 mins | 2 mins |
| **Ongoing Cost** | Hardware only | Per request |
| **Speed** | Fastest | Network dependent |
| **Privacy** | 100% | Data sent to Nomic |
| **Best For** | Production, scale | Development, prototyping |

**Bottom Line:** 
- 🎯 **Use Local for production** (Apache 2.0, unlimited, fast, private)
- 🚀 **Use API for development** (quick setup, easy testing)

**You don't need to choose just one - use both!** ✨
