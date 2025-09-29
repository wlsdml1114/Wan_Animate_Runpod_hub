# WanAnimate for RunPod Serverless
[한국어 README 보기](README_kr.md)

This project is a template designed to easily deploy and use [WanAnimate](https://humanaigc.github.io/wan-animate/) in the RunPod Serverless environment.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Wan_Animate_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Wan_Animate_Runpod_hub)

WanAnimate is an advanced AI model that generates high-quality animated videos from static images with natural motion and realistic animations, using pose estimation and advanced control mechanisms.


## 🎨 Engui Studio Integration

[![EnguiStudio](https://raw.githubusercontent.com/wlsdml1114/Engui_Studio/main/assets/banner.png)](https://github.com/wlsdml1114/Engui_Studio)

This InfiniteTalk template is primarily designed for **Engui Studio**, a comprehensive AI model management platform. While it can be used via API, Engui Studio provides enhanced features and broader model support.

**Engui Studio Benefits:**
- **Expanded Model Support**: Access to a wider variety of AI models beyond what's available through API
- **Enhanced User Interface**: Intuitive workflow management and model selection
- **Advanced Features**: Additional tools and capabilities for AI model deployment
- **Seamless Integration**: Optimized for Engui Studio's ecosystem

> **Note**: While this template works perfectly with API calls, Engui Studio users will have access to additional models and features that are planned for future releases.


## ✨ Key Features

*   **Image-to-Video Animation**: Converts static images into dynamic animated videos with natural motion.
*   **Pose-Controlled Animation**: Uses pose estimation to control and guide the animation process.
*   **Advanced Control**: Supports point-based control, mask editing, and face detection for precise animation control.
*   **High-Quality Output**: Produces high-resolution videos with realistic animations and smooth motion.
*   **Customizable Parameters**: Control video generation with various parameters like seed, width, height, fps, and prompts.
*   **ComfyUI Integration**: Built on top of ComfyUI for flexible workflow management.

## 🚀 RunPod Serverless Template

This template includes all the necessary components to run WanAnimate as a RunPod Serverless Worker.

*   **Dockerfile**: Configures the environment and installs all dependencies required for model execution.
*   **handler.py**: Implements the handler function that processes requests for RunPod Serverless.
*   **entrypoint.sh**: Performs initialization tasks when the worker starts.
*   **WanAnimate_api.json**: Workflow configuration for image-to-video animation.

### Input

The `input` object must contain the following fields. `image_path`, `image_url`, or `image_base64` supports **URL, file path, or Base64 encoded string**. Similarly, `video_path`, `video_url`, or `video_base64` can be used for reference videos.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **Yes** | `N/A` | Description text for the video animation to be generated. |
| `image_path` | `string` | **No** | `/examples/image.jpg` | Path of the input image to animate. |
| `image_url` | `string` | **No** | `/examples/image.jpg` | URL of the input image to animate. |
| `image_base64` | `string` | **No** | `/examples/image.jpg` | Base64 encoded input image to animate. |
| `video_path` | `string` | **No** | `/examples/image.jpg` | Path of the reference video for pose control. |
| `video_url` | `string` | **No** | `/examples/image.jpg` | URL of the reference video for pose control. |
| `video_base64` | `string` | **No** | `/examples/image.jpg` | Base64 encoded reference video for pose control. |
| `seed` | `integer` | **Yes** | `N/A` | Random seed for video generation (affects the randomness of the output). |
| `width` | `integer` | **Yes** | `N/A` | Width of the output video in pixels. |
| `height` | `integer` | **Yes** | `N/A` | Height of the output video in pixels. |
| `fps` | `integer` | **Yes** | `N/A` | Frame rate of the output video. |
| `cfg` | `float` | **Yes** | `N/A` | Classifier-free guidance scale for generation control. |
| `steps` | `integer` | **No** | `6` | Number of denoising steps. |
| `points_store` | `string` | **Yes** | `N/A` | JSON string containing positive control points for animation. |
| `coordinates` | `string` | **Yes** | `N/A` | JSON string containing coordinate points for control. |
| `neg_coordinates` | `string` | **Yes** | `N/A` | JSON string containing negative coordinate points for control. |

**Request Example:**

```json
{
  "input": {
    "prompt": "A person walking in a natural way, soft 3D render style, night time, moonlight",
    "image_path": "https://path/to/your/image.jpg",
    "video_path": "https://path/to/your/reference_video.mp4",
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

## 🛠️ Usage and API Reference

1.  Create a Serverless Endpoint on RunPod based on this repository.
2.  Once the build is complete and the endpoint is active, submit jobs via HTTP POST requests according to the API Reference below.

### 📁 Using Network Volumes

Instead of directly transmitting Base64 encoded files, you can use RunPod's Network Volumes to handle large files. This is especially useful when dealing with large image and video files.

1.  **Create and Connect Network Volume**: Create a Network Volume (e.g., S3-based volume) from the RunPod dashboard and connect it to your Serverless Endpoint settings.
2.  **Upload Files**: Upload the image and video files you want to use to the created Network Volume.
3.  **Specify Paths**: When making an API request, specify the file paths within the Network Volume for `image_path` and `video_path`. For example, if the volume is mounted at `/my_volume` and you use `image.jpg`, the path would be `"/my_volume/image.jpg"`.

## 🔧 Workflow Configuration

This template includes a workflow configuration:

*   **WanAnimate_api.json**: Image-to-video animation workflow

The workflow is based on ComfyUI and includes all necessary nodes for WanAnimate processing, including:
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

## 🙏 Original Project

This project is based on the following original repository. All rights to the model and core logic belong to the original authors.

*   **Wan22:** [https://github.com/Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
*   **ComfyUI-WanVideoWrapper** [https://github.com/kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)

## 📄 License

The original Wan22 project follows its respective license. This template also adheres to that license.
