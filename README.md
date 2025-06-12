# ComfyUI-keitNodes

**Languages:** [English](README.md) | [日本語](README.ja.md)

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
- African: Arabic (ar), Swahili (sw), Amharica (am), Hausa (ha), etc.
- And many more...

### 🎯 Pixel Limit Resizer (16×)

An intelligent image resizing node that maintains aspect ratio while constraining pixel count and optimizing for 16-pixel multiple resolutions. Designed for 3D VAE spatiotemporal compression compatibility.

**Key Features:**
- **Pixel Count Limiting**: Calculates optimal resolution within specified pixel count constraints
- **Aspect Ratio Preservation**: Maintains original image aspect ratio as closely as possible
- **16-Pixel Multiple Constraint**: Adjusts width and height to be multiples of 16 (3D VAE compatible)
- **Multiple Upscale Methods**: Supports nearest-exact, bilinear, area, bicubic, lanczos interpolation methods
- **Detailed Output Information**: Provides resized image along with resolution metrics and aspect ratio data

**Technical Specifications:**
- **Default Max Pixels**: 728,320 (equivalent to 1138×640)
- **Minimum Resolution**: 16×16
- **Maximum Resolution**: 2048×2048
- **3D VAE Optimization**: Compatible with spatiotemporal compression (256× compression ready)

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
