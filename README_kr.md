# WanAnimate for RunPod Serverless

이 프로젝트는 RunPod의 서버리스 엔드포인트를 통해 **WanAnimate** 모델을 사용하여 이미지에서 애니메이션 비디오를 생성하는 Python 클라이언트를 제공합니다. 클라이언트는 S3 업로드 기능, 제어점, 배치 처리 기능을 지원합니다.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Wan_Animate_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Wan_Animate_Runpod_hub)

**WanAnimate**은 정적 이미지를 자연스러운 움직임과 현실적인 애니메이션을 가진 동적 애니메이션 비디오로 변환하는 고급 AI 모델입니다. 포즈 추정과 고급 제어 메커니즘을 사용하여 정밀한 애니메이션 제어를 제공합니다.

## 🎨 Engui Studio 통합

[![EnguiStudio](https://raw.githubusercontent.com/wlsdml1114/Engui_Studio/main/assets/banner.png)](https://github.com/wlsdml1114/Engui_Studio)

이 WanAnimate 클라이언트는 포괄적인 AI 모델 관리 플랫폼인 **Engui Studio**를 위해 주로 설계되었습니다. API를 통해 사용할 수 있지만, Engui Studio는 향상된 기능과 더 넓은 모델 지원을 제공합니다.

## ✨ 주요 기능

*   **WanAnimate 모델**: 고품질 비디오 애니메이션을 위한 고급 WanAnimate AI 모델을 사용합니다.
*   **이미지-비디오 애니메이션**: 정적 이미지를 자연스러운 움직임을 가진 동적 애니메이션 비디오로 변환합니다.
*   **S3 업로드 지원**: RunPod Network Volume S3를 사용한 자동 파일 업로드를 처리합니다.
*   **제어점**: 정밀한 애니메이션 가이드를 위한 포인트 기반 제어를 지원합니다.
*   **배치 처리**: 단일 작업에서 여러 이미지를 처리합니다.
*   **오류 처리**: 포괄적인 오류 처리 및 로깅을 제공합니다.
*   **비동기 작업 관리**: 자동 작업 제출 및 상태 모니터링을 제공합니다.
*   **ComfyUI 통합**: 유연한 워크플로우 관리를 위해 ComfyUI 위에 구축되었습니다.

## 🚀 RunPod Serverless 템플릿

이 템플릿에는 **WanAnimate**을 RunPod Serverless Worker로 실행하는 데 필요한 모든 구성 요소가 포함되어 있습니다.

*   **Dockerfile**: WanAnimate 모델 실행에 필요한 모든 종속성을 설치하고 환경을 구성합니다.
*   **handler.py**: RunPod Serverless용 요청을 처리하는 핸들러 함수를 구현합니다.
*   **entrypoint.sh**: 워커가 시작될 때 초기화 작업을 수행합니다.
*   **newWanAnimate_api.json**: 제어점이 있는 이미지-비디오 애니메이션을 위한 워크플로우 구성입니다.
*   **newWanAnimate_noSAM_api.json**: SAM이 없는 이미지-비디오 애니메이션을 위한 워크플로우 구성입니다.

## 📖 Python 클라이언트 사용법

### 기본 사용법

```python
from wananimate_s3_client import WanAnimateS3Client

# 클라이언트 초기화
client = WanAnimateS3Client(
    runpod_endpoint_id="your-endpoint-id",
    runpod_api_key="your-runpod-api-key",
    s3_endpoint_url="https://s3api-eu-ro-1.runpod.io/",
    s3_access_key_id="your-s3-access-key",
    s3_secret_access_key="your-s3-secret-key",
    s3_bucket_name="your-bucket-name",
    s3_region="eu-ro-1"
)

# 이미지에서 애니메이션 생성
result = client.create_animation_from_files(
    image_path="./example_image.jpeg",
    video_path="./example_video.mp4",
    prompt="자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
    negative_prompt="blurry, low quality, distorted",  # 선택사항: 생략 시 기본값 사용
    seed=12345,
    width=832,
    height=480,
    fps=16,
    cfg=1.0,
    steps=6
)

# 성공 시 결과 저장
if result.get('status') == 'COMPLETED':
    client.save_video_result(result, "./output_animation.mp4")
else:
    print(f"오류: {result.get('error')}")
```

### 제어점 사용

```python
# 제어점 구성
positive_points = [
    {"x": 483.34844284815, "y": 333.283583335728},
    {"x": 479.85856239437277, "y": 158.78956064686517}
]
negative_points = [{"x": 0, "y": 0}]

# 제어점을 사용한 애니메이션 생성
result = client.create_animation_with_control_points(
    image_path="./example_image.jpeg",
    video_path="./example_video.mp4",
    prompt="자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
    negative_prompt="blurry, low quality, distorted",  # 선택사항: 생략 시 기본값 사용
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

### 배치 처리

```python
# 여러 이미지 처리
batch_result = client.batch_process_animations(
    image_folder_path="./input_images",
    video_folder_path="./input_videos",
    output_folder_path="./output_animations",
    prompt="자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
    negative_prompt="blurry, low quality, distorted",  # 선택사항: 생략 시 기본값 사용
    seed=12345,
    width=832,
    height=480,
    fps=16,
    cfg=1.0,
    steps=6
)

print(f"배치 처리 완료: {batch_result['successful']}/{batch_result['total_files']} 성공")
```

## 🔧 API 참조

### 입력

`input` 객체는 다음 필드를 포함해야 합니다. 이미지와 비디오는 **경로, URL 또는 Base64** 중 하나의 방법으로 입력할 수 있습니다.

#### 이미지 입력 (하나만 사용)
| 매개변수 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `image_path` | `string` | 아니오 | `/examples/image.jpg` | 입력 이미지의 로컬 경로 |
| `image_url` | `string` | 아니오 | `/examples/image.jpg` | 입력 이미지의 URL |
| `image_base64` | `string` | 아니오 | `/examples/image.jpg` | 입력 이미지의 Base64 인코딩된 문자열 |

#### 비디오 입력 (하나만 사용)
| 매개변수 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `video_path` | `string` | 아니오 | `/examples/image.jpg` | 참조 비디오의 로컬 경로 |
| `video_url` | `string` | 아니오 | `/examples/image.jpg` | 참조 비디오의 URL |
| `video_base64` | `string` | 아니오 | `/examples/image.jpg` | 참조 비디오의 Base64 인코딩된 문자열 |

#### 제어점 (선택사항)
| 매개변수 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `points_store` | `string` | 아니오 | - | 양수 및 음수 제어점을 포함하는 JSON 문자열 |
| `coordinates` | `string` | 아니오 | - | 양수 좌표점을 포함하는 JSON 문자열 |
| `neg_coordinates` | `string` | 아니오 | - | 음수 좌표점을 포함하는 JSON 문자열 |

#### 애니메이션 매개변수
| 매개변수 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **예** | - | 생성할 비디오 애니메이션에 대한 설명 텍스트 |
| `negative_prompt` | `string` | 아니오 | - | 생성된 비디오에서 원하지 않는 요소를 피하기 위한 네거티브 프롬프트 (생략 시 기본값 사용) |
| `seed` | `integer` | **예** | - | 비디오 생성을 위한 랜덤 시드 |
| `width` | `integer` | **예** | - | 출력 비디오의 픽셀 단위 너비 |
| `height` | `integer` | **예** | - | 출력 비디오의 픽셀 단위 높이 |
| `fps` | `integer` | **예** | - | 출력 비디오의 프레임 속도 |
| `cfg` | `float` | **예** | - | 생성 제어를 위한 분류기 없는 가이던스 스케일 |
| `steps` | `integer` | 아니오 | `6` | 노이즈 제거 단계 수 |

**요청 예시:**

#### 1. 기본 애니메이션 (제어점 없음)
```json
{
  "input": {
    "prompt": "자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
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

#### 2. 제어점 사용
```json
{
  "input": {
    "prompt": "자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
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

#### 3. 네트워크 볼륨 경로 사용
```json
{
  "input": {
    "prompt": "자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
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

#### 4. URL 입력
```json
{
  "input": {
    "prompt": "자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
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

### 출력

#### 성공

작업이 성공하면 생성된 비디오가 Base64로 인코딩된 JSON 객체를 반환합니다.

| 매개변수 | 타입 | 설명 |
| --- | --- | --- |
| `video` | `string` | Base64 인코딩된 비디오 파일 데이터입니다. |

**성공 응답 예시:**

```json
{
  "video": "data:video/mp4;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}
```

#### 오류

작업이 실패하면 오류 메시지를 포함한 JSON 객체를 반환합니다.

| 매개변수 | 타입 | 설명 |
| --- | --- | --- |
| `error` | `string` | 발생한 오류에 대한 설명입니다. |

**오류 응답 예시:**

```json
{
  "error": "비디오를 찾을 수 없습니다."
}
```

## 🛠️ 직접 API 사용법

1.  이 저장소를 기반으로 RunPod에서 Serverless Endpoint를 생성합니다.
2.  빌드가 완료되고 엔드포인트가 활성화되면 위의 API 참조에 따라 HTTP POST 요청을 통해 작업을 제출합니다.

### 📁 네트워크 볼륨 사용

Base64 인코딩된 파일을 직접 전송하는 대신 RunPod의 네트워크 볼륨을 사용하여 대용량 파일을 처리할 수 있습니다. 이는 특히 대용량 이미지 및 비디오 파일을 다룰 때 유용합니다.

1.  **네트워크 볼륨 생성 및 연결**: RunPod 대시보드에서 네트워크 볼륨(예: S3 기반 볼륨)을 생성하고 Serverless Endpoint 설정에 연결합니다.
2.  **파일 업로드**: 사용하려는 이미지 및 비디오 파일을 생성된 네트워크 볼륨에 업로드합니다.
3.  **파일 구성**: 
    - 입력 이미지와 비디오를 네트워크 볼륨의 어디든 배치합니다
4.  **경로 지정**: API 요청을 할 때 네트워크 볼륨 내의 파일 경로를 지정합니다:
    - `image_path`의 경우: 이미지 파일의 전체 경로 사용 (예: `"/runpod-volume/images/portrait.jpg"`)
    - `video_path`의 경우: 비디오 파일의 전체 경로 사용 (예: `"/runpod-volume/videos/reference.mp4"`)

## 🔧 클라이언트 메서드

### WanAnimateS3Client 클래스

#### `__init__(runpod_endpoint_id, runpod_api_key, s3_endpoint_url, s3_access_key_id, s3_secret_access_key, s3_bucket_name, s3_region)`
RunPod 엔드포인트 ID, API 키, S3 구성을 사용하여 클라이언트를 초기화합니다.

#### `create_animation_from_files(image_path, video_path, prompt, negative_prompt, seed, width, height, fps, cfg, steps, points_store, coordinates, neg_coordinates)`
자동 S3 업로드와 함께 로컬 파일에서 애니메이션을 생성합니다.

**매개변수:**
- `image_path` (str): 입력 이미지의 경로
- `video_path` (str, 선택사항): 참조 비디오의 경로
- `prompt` (str): 애니메이션 생성을 위한 텍스트 프롬프트
- `negative_prompt` (str, 선택사항): 원하지 않는 요소를 피하기 위한 네거티브 프롬프트 (생략 시 기본값 사용)
- `seed` (int): 랜덤 시드 (기본값: 12345)
- `width` (int): 출력 비디오 너비 (기본값: 832)
- `height` (int): 출력 비디오 높이 (기본값: 480)
- `fps` (int): 프레임 속도 (기본값: 16)
- `cfg` (float): CFG 스케일 (기본값: 1.0)
- `steps` (int): 노이즈 제거 단계 (기본값: 6)
- `points_store` (str, 선택사항): 제어점을 포함하는 JSON 문자열
- `coordinates` (str, 선택사항): 양수 좌표를 포함하는 JSON 문자열
- `neg_coordinates` (str, 선택사항): 음수 좌표를 포함하는 JSON 문자열

#### `create_animation_with_control_points(image_path, video_path, prompt, negative_prompt, seed, width, height, fps, cfg, steps, positive_points, negative_points)`
로컬 파일에서 제어점을 사용하여 애니메이션을 생성합니다.

**매개변수:**
- `image_path` (str): 입력 이미지의 경로
- `video_path` (str, 선택사항): 참조 비디오의 경로
- `prompt` (str): 애니메이션 생성을 위한 텍스트 프롬프트
- `negative_prompt` (str, 선택사항): 원하지 않는 요소를 피하기 위한 네거티브 프롬프트 (생략 시 기본값 사용)
- `seed` (int): 랜덤 시드 (기본값: 12345)
- `width` (int): 출력 비디오 너비 (기본값: 832)
- `height` (int): 출력 비디오 높이 (기본값: 480)
- `fps` (int): 프레임 속도 (기본값: 16)
- `cfg` (float): CFG 스케일 (기본값: 1.0)
- `steps` (int): 노이즈 제거 단계 (기본값: 6)
- `positive_points` (list, 선택사항): 양수 제어점 목록 [{"x": float, "y": float}]
- `negative_points` (list, 선택사항): 음수 제어점 목록 [{"x": float, "y": float}]

#### `batch_process_animations(image_folder_path, video_folder_path, output_folder_path, valid_image_extensions, valid_video_extensions, ...)`
폴더의 여러 이미지를 처리합니다.

**매개변수:**
- `image_folder_path` (str): 이미지를 포함하는 폴더의 경로
- `video_folder_path` (str, 선택사항): 비디오를 포함하는 폴더의 경로
- `output_folder_path` (str): 출력 애니메이션을 저장할 경로
- `valid_image_extensions` (tuple): 유효한 이미지 확장자 (기본값: ('.jpg', '.jpeg', '.png', '.bmp'))
- `valid_video_extensions` (tuple): 유효한 비디오 확장자 (기본값: ('.mp4', '.avi', '.mov', '.mkv'))
- 기타 매개변수는 `create_animation_from_files`와 동일

#### `save_video_result(result, output_path)`
애니메이션 결과를 파일로 저장합니다.

**매개변수:**
- `result` (dict): 작업 결과 딕셔너리
- `output_path` (str): 비디오 파일을 저장할 경로

## 🔧 WanAnimate 워크플로우 구성

이 템플릿은 **WanAnimate**을 위한 워크플로우 구성을 사용합니다:

*   **newWanAnimate_api.json**: 제어점이 있는 WanAnimate 이미지-비디오 애니메이션 워크플로우
*   **newWanAnimate_noSAM_api.json**: SAM이 없는 WanAnimate 이미지-비디오 애니메이션 워크플로우
*   **newWanAnimate_point_api.json**: 포인트 제어가 있는 WanAnimate 이미지-비디오 애니메이션 워크플로우

워크플로우는 ComfyUI를 기반으로 하며 WanAnimate 처리에 필요한 모든 노드를 포함합니다:
- WanVideo 모델 로딩 및 구성
- 포즈 추정 및 제어 (DWPose)
- 얼굴 감지 및 마스킹
- 정밀한 제어를 위한 SAM2 분할
- 이미지 이해를 위한 CLIP 비전 인코딩
- VAE 로딩 및 처리
- 비디오 인코딩 및 출력 생성

## 🎯 제어 기능

WanAnimate은 고급 제어 메커니즘을 제공합니다:

*   **포인트 기반 제어**: `points_store`와 `coordinates`를 사용하여 애니메이션을 위한 제어 포인트를 지정합니다
*   **음수 제어**: `neg_coordinates`를 사용하여 애니메이션 중 피할 영역을 지정합니다
*   **포즈 추정**: 참조 비디오에서 자동 포즈 감지
*   **얼굴 감지**: 더 나은 결과를 위한 자동 얼굴 감지 및 마스킹
*   **마스크 편집**: 정밀한 제어를 위한 고급 마스크 편집 기능

## 🙏 WanAnimate 소개

**WanAnimate**은 자연스러운 움직임과 현실적인 애니메이션을 가진 고품질 비디오를 생성하는 최첨단 AI 모델입니다. 이 프로젝트는 WanAnimate 모델의 쉬운 배포 및 사용을 위한 Python 클라이언트와 RunPod 서버리스 템플릿을 제공합니다.

### WanAnimate의 주요 기능:
- **고품질 출력**: 우수한 시각적 품질과 부드러운 움직임을 가진 비디오 생성
- **자연스러운 애니메이션**: 정적 이미지에서 현실적이고 자연스러운 움직임 생성
- **제어점**: 정밀한 애니메이션 가이드를 위한 포인트 기반 제어 지원
- **ComfyUI 통합**: 유연한 워크플로우 관리를 위해 ComfyUI 위에 구축
- **사용자 정의 가능한 매개변수**: 애니메이션 생성 매개변수의 완전한 제어

## 🙏 원본 프로젝트

이 프로젝트는 다음 원본 저장소를 기반으로 합니다. 모델 및 핵심 로직에 대한 모든 권리는 원본 작성자에게 있습니다.

*   **WanAnimate:** [https://humanaigc.github.io/wan-animate/](https://humanaigc.github.io/wan-animate/)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
*   **ComfyUI-WanVideoWrapper** [https://github.com/kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)

## 📄 라이선스

원본 WanAnimate 프로젝트는 해당 라이선스를 따릅니다. 이 템플릿도 해당 라이선스를 준수합니다.
