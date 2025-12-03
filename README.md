# WanAnimate for RunPod Serverless
[한국어 README 보기](README_kr.md)

This project provides a Python client for generating animated videos from images using [WanAnimate](https://humanaigc.github.io/wan-animate/) model through RunPod's serverless endpoint. The client supports S3 upload functionality, control points, and batch processing capabilities.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Wan_Animate_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Wan_Animate_Runpod_hub)

**WanAnimate** is an advanced AI model that converts static images into dynamic animated videos with natural motion and realistic animations. It uses pose estimation and advanced control mechanisms for precise animation control.

## 🎨 Engui Studio Integration

[![EnguiStudio](https://raw.githubusercontent.com/wlsdml1114/Engui_Studio/main/assets/banner.png)](https://github.com/wlsdml1114/Engui_Studio)

This WanAnimate client is primarily designed for **Engui Studio**, a comprehensive AI model management platform. While it can be used via API, Engui Studio provides enhanced features and broader model support.

## ✨ Key Features

*   **WanAnimate Model**: Powered by the advanced WanAnimate AI model for high-quality video animation.
*   **Image-to-Video Animation**: Converts static images into dynamic animated videos with natural motion.
*   **S3 Upload Support**: Handles file uploads using RunPod Network Volume S3 automatically.
*   **Control Points**: Supports point-based control for precise animation guidance.
*   **Batch Processing**: Process multiple images in a single operation.
*   **Error Handling**: Comprehensive error handling and logging.
*   **Async Job Management**: Automatic job submission and status monitoring.
*   **ComfyUI Integration**: Built on ComfyUI for flexible workflow management.

## 🚀 RunPod Serverless Template

This template includes all the necessary components to run **WanAnimate** as a RunPod Serverless Worker.

*   **Dockerfile**: Configures the environment and installs all dependencies required for WanAnimate model execution.
*   **handler.py**: Implements the handler function that processes requests for RunPod Serverless.
*   **entrypoint.sh**: Performs initialization tasks when the worker starts.
*   **newWanAnimate_api.json**: Workflow configuration for image-to-video animation with control points.
*   **newWanAnimate_noSAM_api.json**: Workflow configuration for image-to-video animation without SAM.

## 📖 Python Client Usage

### Basic Usage

```python
from wananimate_s3_client import WanAnimateS3Client

# Initialize client
client = WanAnimateS3Client(
    runpod_endpoint_id="your-endpoint-id",
    runpod_api_key="your-runpod-api-key",
    s3_endpoint_url="https://s3api-eu-ro-1.runpod.io/",
    s3_access_key_id="your-s3-access-key",
    s3_secret_access_key="your-s3-secret-key",
    s3_bucket_name="your-bucket-name",
    s3_region="eu-ro-1"
)

# Generate animation from image
result = client.create_animation_from_files(
    image_path="./example_image.jpeg",
    video_path="./example_video.mp4",
    prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
    negative_prompt="blurry, low quality, distorted",  # Optional: omit to use default
    seed=12345,
    width=832,
    height=480,
    fps=16,
    cfg=1.0,
    steps=6
)

# Save result if successful
if result.get('status') == 'COMPLETED':
    client.save_video_result(result, "./output_animation.mp4")
else:
    print(f"Error: {result.get('error')}")
```

### Using Control Points

```python
# Configure control points
positive_points = [
    {"x": 483.34844284815, "y": 333.283583335728},
    {"x": 479.85856239437277, "y": 158.78956064686517}
]
negative_points = [{"x": 0, "y": 0}]

# Generate animation with control points
result = client.create_animation_with_control_points(
    image_path="./example_image.jpeg",
    video_path="./example_video.mp4",
    prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
    negative_prompt="blurry, low quality, distorted",  # Optional: omit to use default
    seed=12345,
    width=832,
    height=480,
    fps=16,
    cfg=1.0,
    steps=6,
    positive_points=positive_points,
    negative_points=negative_points
)
```

### Batch Processing

```python
# Process multiple images
batch_result = client.batch_process_animations(
    image_folder_path="./input_images",
    video_folder_path="./input_videos",
    output_folder_path="./output_animations",
    prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
    negative_prompt="blurry, low quality, distorted",  # Optional: omit to use default
    seed=12345,
    width=832,
    height=480,
    fps=16,
    cfg=1.0,
    steps=6
)

print(f"Batch processing completed: {batch_result['successful']}/{batch_result['total_files']} successful")
```

## 🔧 API Reference

### Input

The `input` object must contain the following fields. Images and videos can be input using **path, URL or Base64** - one method for each.

#### Image Input (use only one)
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `image_path` | `string` | No | `/examples/image.jpg` | Local path to the input image |
| `image_url` | `string` | No | `/examples/image.jpg` | URL of the input image |
| `image_base64` | `string` | No | `/examples/image.jpg` | Base64 encoded string of the input image |

#### Video Input (use only one)
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `video_path` | `string` | No | `/examples/image.jpg` | Local path to the reference video |
| `video_url` | `string` | No | `/examples/image.jpg` | URL of the reference video |
| `video_base64` | `string` | No | `/examples/image.jpg` | Base64 encoded string of the reference video |

#### Control Points (optional)
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `points_store` | `string` | No | - | JSON string containing positive and negative control points |
| `coordinates` | `string` | No | - | JSON string containing positive coordinate points |
| `neg_coordinates` | `string` | No | - | JSON string containing negative coordinate points |

#### Animation Parameters
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **Yes** | - | Description text for the video animation to be generated |
| `negative_prompt` | `string` | No | - | Negative prompt to avoid unwanted elements in the generated video (uses default if omitted) |
| `seed` | `integer` | **Yes** | - | Random seed for video generation |
| `width` | `integer` | **Yes** | - | Width of the output video in pixels |
| `height` | `integer` | **Yes** | - | Height of the output video in pixels |
| `fps` | `integer` | **Yes** | - | Frame rate of the output video |
| `cfg` | `float` | **Yes** | - | Classifier-free guidance scale for generation control |
| `steps` | `integer` | No | `6` | Number of denoising steps |

**Request Examples:**

#### 1. Basic Animation (No Control Points)
```json
{
  "input": {
    "prompt": "A person walking in a natural way, soft 3D render style, night time, moonlight",
    "negative_prompt": "blurry, low quality, distorted",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "video_base64": "data:video/mp4;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "seed": 12345,
    "width": 832,
    "height": 480,
    "fps": 16,
    "cfg": 1.0,
    "steps": 6
  }
}
```

#### 2. With Control Points
```json
{
  "input": {
    "prompt": "A person walking in a natural way, soft 3D render style, night time, moonlight",
    "negative_prompt": "blurry, low quality, distorted",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "video_base64": "data:video/mp4;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "seed": 12345,
    "width": 832,
    "height": 480,
    "fps": 16,
    "cfg": 1.0,
    "steps": 6,
    "points_store": "{\"positive\":[{\"x\":483.34844284815,\"y\":333.283583335728},{\"x\":479.85856239437277,\"y\":158.78956064686517}],\"negative\":[{\"x\":0,\"y\":0}]}",
    "coordinates": "[{\"x\":483.34844284815,\"y\":333.283583335728},{\"x\":479.85856239437277,\"y\":158.78956064686517}]",
    "neg_coordinates": "[{\"x\":0,\"y\":0}]"
  }
}
```

#### 3. Using Network Volume Paths
```json
{
  "input": {
    "prompt": "A person walking in a natural way, soft 3D render style, night time, moonlight",
    "negative_prompt": "blurry, low quality, distorted",
    "image_path": "/runpod-volume/input_image.png",
    "video_path": "/runpod-volume/reference_video.mp4",
    "seed": 12345,
    "width": 832,
    "height": 480,
    "fps": 16,
    "cfg": 1.0,
    "steps": 6
  }
}
```

#### 4. URL Input
```json
{
  "input": {
    "prompt": "A person walking in a natural way, soft 3D render style, night time, moonlight",
    "negative_prompt": "blurry, low quality, distorted",
    "image_url": "https://example.com/image.jpg",
    "video_url": "https://example.com/video.mp4",
    "seed": 12345,
    "width": 832,
    "height": 480,
    "fps": 16,
    "cfg": 1.0,
    "steps": 6
  }
}
```

### Output

#### Success

If the job is successful, it returns a JSON object with the generated video Base64 encoded.

| Parameter | Type | Description |
| --- | --- | --- |
| `video` | `string` | Base64 encoded video file data. |

**Success Response Example:**

```json
{
  "video": "data:video/mp4;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}
```

#### Error

If the job fails, it returns a JSON object containing an error message.

| Parameter | Type | Description |
| --- | --- | --- |
| `error` | `string` | Description of the error that occurred. |

**Error Response Example:**

```json
{
  "error": "비디오를 찾을 수 없습니다."
}
```

## 🛠️ Direct API Usage

1.  Create a Serverless Endpoint on RunPod based on this repository.
2.  Once the build is complete and the endpoint is active, submit jobs via HTTP POST requests according to the API Reference above.

### 📁 Using Network Volumes

Instead of directly transmitting Base64 encoded files, you can use RunPod's Network Volumes to handle large files. This is especially useful when dealing with large image and video files.

1.  **Create and Connect Network Volume**: Create a Network Volume (e.g., S3-based volume) from the RunPod dashboard and connect it to your Serverless Endpoint settings.
2.  **Upload Files**: Upload the image and video files you want to use to the created Network Volume.
3.  **File Organization**: 
    - Place your input images and videos anywhere in the Network Volume
4.  **Specify Paths**: When making an API request, specify the file paths within the Network Volume:
    - For `image_path`: Use the full path to your image file (e.g., `"/runpod-volume/images/portrait.jpg"`)
    - For `video_path`: Use the full path to your video file (e.g., `"/runpod-volume/videos/reference.mp4"`)

## 🔧 Client Methods

### WanAnimateS3Client Class

#### `__init__(runpod_endpoint_id, runpod_api_key, s3_endpoint_url, s3_access_key_id, s3_secret_access_key, s3_bucket_name, s3_region)`
Initialize the client with RunPod endpoint ID, API key, and S3 configuration.

#### `create_animation_from_files(image_path, video_path, prompt, negative_prompt, seed, width, height, fps, cfg, steps, points_store, coordinates, neg_coordinates)`
Generate animation from local files with automatic S3 upload.

**Parameters:**
- `image_path` (str): Path to the input image
- `video_path` (str, optional): Path to the reference video
- `prompt` (str): Text prompt for animation generation
- `negative_prompt` (str, optional): Negative prompt to avoid unwanted elements (default: Chinese negative prompt)
- `seed` (int): Random seed (default: 12345)
- `width` (int): Output video width (default: 832)
- `height` (int): Output video height (default: 480)
- `fps` (int): Frame rate (default: 16)
- `cfg` (float): CFG scale (default: 1.0)
- `steps` (int): Denoising steps (default: 6)
- `points_store` (str, optional): JSON string containing control points
- `coordinates` (str, optional): JSON string containing positive coordinates
- `neg_coordinates` (str, optional): JSON string containing negative coordinates

#### `create_animation_with_control_points(image_path, video_path, prompt, negative_prompt, seed, width, height, fps, cfg, steps, positive_points, negative_points)`
Generate animation with control points from local files.

**Parameters:**
- `image_path` (str): Path to the input image
- `video_path` (str, optional): Path to the reference video
- `prompt` (str): Text prompt for animation generation
- `negative_prompt` (str, optional): Negative prompt to avoid unwanted elements (default: Chinese negative prompt)
- `seed` (int): Random seed (default: 12345)
- `width` (int): Output video width (default: 832)
- `height` (int): Output video height (default: 480)
- `fps` (int): Frame rate (default: 16)
- `cfg` (float): CFG scale (default: 1.0)
- `steps` (int): Denoising steps (default: 6)
- `positive_points` (list, optional): List of positive control points [{"x": float, "y": float}]
- `negative_points` (list, optional): List of negative control points [{"x": float, "y": float}]

#### `batch_process_animations(image_folder_path, video_folder_path, output_folder_path, valid_image_extensions, valid_video_extensions, ...)`
Process multiple images in a folder.

**Parameters:**
- `image_folder_path` (str): Path to folder containing images
- `video_folder_path` (str, optional): Path to folder containing videos
- `output_folder_path` (str): Path to save output animations
- `valid_image_extensions` (tuple): Valid image extensions (default: ('.jpg', '.jpeg', '.png', '.bmp'))
- `valid_video_extensions` (tuple): Valid video extensions (default: ('.mp4', '.avi', '.mov', '.mkv'))
- Other parameters same as `create_animation_from_files`

#### `save_video_result(result, output_path)`
Save animation result to file.

**Parameters:**
- `result` (dict): Job result dictionary
- `output_path` (str): Path to save the video file

## 🔧 WanAnimate Workflow Configuration

This template uses workflow configurations for **WanAnimate**:

*   **newWanAnimate_api.json**: WanAnimate image-to-video animation workflow with control points
*   **newWanAnimate_noSAM_api.json**: WanAnimate image-to-video animation workflow without SAM
*   **newWanAnimate_point_api.json**: WanAnimate image-to-video animation workflow with point control

The workflow is based on ComfyUI and includes all necessary nodes for WanAnimate processing:
- WanVideo model loading and configuration
- Pose estimation and control (DWPose)
- Face detection and masking
- SAM2 segmentation for precise control
- CLIP vision encoding for image understanding
- VAE loading and processing
- Video encoding and output generation

## 🎯 Control Features

WanAnimate provides advanced control mechanisms:

*   **Point-based Control**: Use `points_store` and `coordinates` to specify control points for animation
*   **Negative Control**: Use `neg_coordinates` to specify areas to avoid during animation
*   **Pose Estimation**: Automatic pose detection from reference videos
*   **Face Detection**: Automatic face detection and masking for better results
*   **Mask Editing**: Advanced mask editing capabilities for precise control

## 🙏 About WanAnimate

**WanAnimate** is a state-of-the-art AI model for image-to-video animation that produces high-quality videos with natural motion and realistic animations. This project provides a Python client and RunPod serverless template for easy deployment and usage of the WanAnimate model.

### Key Features of WanAnimate:
- **High-Quality Output**: Generates videos with excellent visual quality and smooth motion
- **Natural Animation**: Creates realistic and natural-looking movements from static images
- **Control Points**: Supports point-based control for precise animation guidance
- **ComfyUI Integration**: Built on ComfyUI for flexible workflow management
- **Customizable Parameters**: Full control over animation generation parameters

## 🙏 Original Project

This project is based on the following original repository. All rights to the model and core logic belong to the original authors.

*   **WanAnimate:** [https://humanaigc.github.io/wan-animate/](https://humanaigc.github.io/wan-animate/)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
*   **ComfyUI-WanVideoWrapper** [https://github.com/kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)

## 📄 License

The original WanAnimate project follows its respective license. This template also adheres to that license.
