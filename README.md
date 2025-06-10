# ComfyUI-keitNodes

Custom nodes for ComfyUI by keit.

## Features

### 🌍 M2M-100 Translator

A powerful multilingual translation node powered by Meta's M2M-100 (Many-to-Many 100) model, supporting translation between 100+ languages.

**Key Features:**
- **Automatic Language Detection**: Automatically detects the source language when set to "auto_detect"
- **100+ Language Support**: Supports major world languages including Asian, European, African, and more
- **Multiple Model Sizes**: Choose between 418M and 1.2B parameter models based on your needs
- **GPU Acceleration**: Automatically utilizes CUDA if available for faster translation
- **Beam Search**: Configurable beam search for improved translation quality
- **Memory Efficient**: Models are shared across multiple node instances

**Supported Languages Include:**
- Asian: Japanese (ja), Chinese (zh), Korean (ko), Thai (th), Vietnamese (vi), Hindi (hi), etc.
- European: English (en), French (fr), German (de), Spanish (es), Russian (ru), Italian (it), etc.
- African: Arabic (ar), Swahili (sw), Amharic (am), Hausa (ha), etc.
- And many more...

### 🎬 WanVideo Optimal Resizer

A specialized image resizing node optimized for WanVideo, which intelligently resizes images to the most suitable resolution based on aspect ratio matching.

**Key Features:**
- **Smart Resolution Selection**: Automatically selects the best resolution from supported WanVideo formats
- **Aspect Ratio Optimization**: Finds the closest aspect ratio match to minimize distortion
- **Multiple Upscale Methods**: Supports various interpolation methods (nearest-exact, bilinear, area, bicubic, lanczos)
- **Detailed Output Information**: Returns resized image along with resolution metrics and aspect ratio data

**Supported Resolutions:**
- **1:1 Square**: 640×640 (perfect for square content)
- **2:3 Portrait**: 512×768 (ideal for vertical content)
- **3:2 Landscape**: 768×512 (great for horizontal content)
- **16:9 Landscape**: 854×480 (standard widescreen format)
- **9:16 Portrait**: 480×854 (mobile-friendly vertical format)

## Installation

### Prerequisites
- ComfyUI installed and working

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "ComfyUI-keitNodes"
3. Click Install

### Method 2: Manual Installation
1. Clone this repository into your ComfyUI custom_nodes directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/ComfyUI-keitNodes.git
```

2. Install required dependencies:
```bash
cd ComfyUI-keitNodes
pip install -r requirements.txt
```

3. Restart ComfyUI
