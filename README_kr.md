# WanAnimate for RunPod Serverless

이 프로젝트는 RunPod Serverless 환경에서 [WanAnimate](https://humanaigc.github.io/wan-animate/)를 쉽게 배포하고 사용할 수 있도록 설계된 템플릿입니다.

[![Runpod](https://api.runpod.io/badge/wlsdml1114/Wan_Animate_Runpod_hub)](https://console.runpod.io/hub/wlsdml1114/Wan_Animate_Runpod_hub)

WanAnimate은 포즈 추정과 고급 제어 메커니즘을 사용하여 정적 이미지에서 자연스러운 움직임과 현실적인 애니메이션을 가진 고품질 애니메이션 비디오를 생성하는 고급 AI 모델입니다.


## 🎨 Engui Studio 통합

[![EnguiStudio](https://raw.githubusercontent.com/wlsdml1114/Engui_Studio/main/assets/banner.png)](https://github.com/wlsdml1114/Engui_Studio)

이 InfiniteTalk 템플릿은 포괄적인 AI 모델 관리 플랫폼인 **Engui Studio**를 위해 주로 설계되었습니다. API를 통해 사용할 수 있지만, Engui Studio는 향상된 기능과 더 넓은 모델 지원을 제공합니다.

**Engui Studio의 장점:**
- **확장된 모델 지원**: API를 통해 사용할 수 있는 것보다 더 다양한 AI 모델에 액세스
- **향상된 사용자 인터페이스**: 직관적인 워크플로우 관리 및 모델 선택
- **고급 기능**: AI 모델 배포를 위한 추가 도구 및 기능
- **원활한 통합**: Engui Studio의 생태계에 최적화

> **참고**: 이 템플릿은 API 호출로 완벽하게 작동하지만, Engui Studio 사용자는 향후 릴리스에서 계획된 추가 모델 및 기능에 액세스할 수 있습니다.


## ✨ 주요 기능

*   **이미지-비디오 애니메이션**: 정적 이미지를 자연스러운 움직임을 가진 동적 애니메이션 비디오로 변환합니다.
*   **포즈 제어 애니메이션**: 포즈 추정을 사용하여 애니메이션 프로세스를 제어하고 안내합니다.
*   **고급 제어**: 정밀한 애니메이션 제어를 위한 포인트 기반 제어, 마스크 편집 및 얼굴 감지를 지원합니다.
*   **고품질 출력**: 현실적인 애니메이션과 부드러운 움직임을 가진 고해상도 비디오를 생성합니다.
*   **사용자 정의 가능한 매개변수**: 시드, 너비, 높이, fps, 프롬프트 등 다양한 매개변수로 비디오 생성을 제어합니다.
*   **ComfyUI 통합**: 유연한 워크플로우 관리를 위해 ComfyUI 위에 구축되었습니다.

## 🚀 RunPod Serverless 템플릿

이 템플릿에는 WanAnimate을 RunPod Serverless Worker로 실행하는 데 필요한 모든 구성 요소가 포함되어 있습니다.

*   **Dockerfile**: 모델 실행에 필요한 모든 종속성을 설치하고 환경을 구성합니다.
*   **handler.py**: RunPod Serverless용 요청을 처리하는 핸들러 함수를 구현합니다.
*   **entrypoint.sh**: 워커가 시작될 때 초기화 작업을 수행합니다.
*   **WanAnimate_api.json**: 이미지-비디오 애니메이션을 위한 워크플로우 구성입니다.

### 입력

`input` 객체는 다음 필드를 포함해야 합니다. `image_path`, `image_url`, 또는 `image_base64`는 **URL, 파일 경로 또는 Base64 인코딩된 문자열**을 지원합니다. 마찬가지로 `video_path`, `video_url`, 또는 `video_base64`는 참조 비디오에 사용할 수 있습니다.

| 매개변수 | 타입 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | **예** | `N/A` | 생성할 비디오 애니메이션에 대한 설명 텍스트입니다. |
| `image_path` | `string` | **아니오** | `/examples/image.jpg` | 애니메이션할 입력 이미지의 경로입니다. |
| `image_url` | `string` | **아니오** | `/examples/image.jpg` | 애니메이션할 입력 이미지의 URL입니다. |
| `image_base64` | `string` | **아니오** | `/examples/image.jpg` | 애니메이션할 Base64 인코딩된 입력 이미지입니다. |
| `video_path` | `string` | **아니오** | `/examples/image.jpg` | 포즈 제어를 위한 참조 비디오의 경로입니다. |
| `video_url` | `string` | **아니오** | `/examples/image.jpg` | 포즈 제어를 위한 참조 비디오의 URL입니다. |
| `video_base64` | `string` | **아니오** | `/examples/image.jpg` | 포즈 제어를 위한 Base64 인코딩된 참조 비디오입니다. |
| `seed` | `integer` | **예** | `N/A` | 비디오 생성을 위한 랜덤 시드(출력의 무작위성에 영향을 줍니다). |
| `width` | `integer` | **예** | `N/A` | 출력 비디오의 픽셀 단위 너비입니다. |
| `height` | `integer` | **예** | `N/A` | 출력 비디오의 픽셀 단위 높이입니다. |
| `fps` | `integer` | **예** | `N/A` | 출력 비디오의 프레임 속도입니다. |
| `cfg` | `float` | **예** | `N/A` | 생성 제어를 위한 분류기 없는 가이던스 스케일입니다. |
| `steps` | `integer` | **아니오** | `6` | 노이즈 제거 단계 수입니다. |
| `points_store` | `string` | **예** | `N/A` | 애니메이션을 위한 양수 제어 포인트를 포함하는 JSON 문자열입니다. |
| `coordinates` | `string` | **예** | `N/A` | 제어를 위한 좌표 포인트를 포함하는 JSON 문자열입니다. |
| `neg_coordinates` | `string` | **예** | `N/A` | 제어를 위한 음수 좌표 포인트를 포함하는 JSON 문자열입니다. |

**요청 예시:**

```json
{
  "input": {
    "prompt": "자연스럽게 걷는 사람, 부드러운 3D 렌더 스타일, 밤 시간, 달빛",
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

## 🛠️ 사용법 및 API 참조

1.  이 저장소를 기반으로 RunPod에서 Serverless Endpoint를 생성합니다.
2.  빌드가 완료되고 엔드포인트가 활성화되면 아래 API 참조에 따라 HTTP POST 요청을 통해 작업을 제출합니다.

### 📁 네트워크 볼륨 사용

Base64 인코딩된 파일을 직접 전송하는 대신 RunPod의 네트워크 볼륨을 사용하여 대용량 파일을 처리할 수 있습니다. 이는 특히 대용량 이미지 및 비디오 파일을 다룰 때 유용합니다.

1.  **네트워크 볼륨 생성 및 연결**: RunPod 대시보드에서 네트워크 볼륨(예: S3 기반 볼륨)을 생성하고 Serverless Endpoint 설정에 연결합니다.
2.  **파일 업로드**: 사용하려는 이미지 및 비디오 파일을 생성된 네트워크 볼륨에 업로드합니다.
3.  **경로 지정**: API 요청을 할 때 `image_path`와 `video_path`에 대해 네트워크 볼륨 내의 파일 경로를 지정합니다. 예를 들어, 볼륨이 `/my_volume`에 마운트되고 `image.jpg`를 사용하는 경우 경로는 `"/my_volume/image.jpg"`가 됩니다.

## 🔧 워크플로우 구성

이 템플릿에는 워크플로우 구성이 포함되어 있습니다:

*   **WanAnimate_api.json**: 이미지-비디오 애니메이션 워크플로우

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

## 🙏 원본 프로젝트

이 프로젝트는 다음 원본 저장소를 기반으로 합니다. 모델 및 핵심 로직에 대한 모든 권리는 원본 작성자에게 있습니다.

*   **Wan22:** [https://github.com/Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
*   **ComfyUI-WanVideoWrapper** [https://github.com/kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)

## 📄 라이선스

원본 Wan22 프로젝트는 해당 라이선스를 따릅니다. 이 템플릿도 해당 라이선스를 준수합니다.
