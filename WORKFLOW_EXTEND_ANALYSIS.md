# Workflow Extend 동적 확장 분석

## 📋 개요

`onetoall_0extend.json`과 `onetoall_3extend.json` 두 워크플로우를 분석하여, 비디오 길이에 따라 동적으로 Extend 블록을 추가하는 방법을 제시합니다.

## 🔍 두 Workflow의 차이점 분석

### 1. 기본 구조

**`onetoall_0extend.json` (기본 워크플로우)**
- 최종 출력: 노드 `"28"` (WanVideoDecode)
- Extend 블록 없음
- 총 노드 수: 약 20개

**`onetoall_3extend.json` (3번 Extend)**
- 기본 워크플로우 + 3개의 Extend 블록
- 각 Extend 블록은 동일한 구조를 가짐
- 총 노드 수: 약 44개 (기본 20개 + Extend 블록 24개)

### 2. Extend 블록 구조

각 Extend 블록은 다음 8개 노드로 구성됩니다:

```
Extend 블록 노드 패턴 (예: "263:xxx")
├── 260: GetImageSizeAndCount          # 이전 출력에서 이미지 정보 가져오기
├── 243: ImageBatchExtendWithOverlap   # 이전 이미지와 오버랩 (첫 번째)
├── 258: WanVideoEncode                 # 이미지를 latent로 인코딩
├── 261: WanVideoAddOneToAllExtendEmbeds # Extend embeds 추가
├── 251: WanVideoAddOneToAllPoseEmbeds  # Pose embeds 추가
├── 248: WanVideoSampler                # 샘플링
├── 247: WanVideoDecode                 # 디코딩
└── 249: ImageBatchExtendWithOverlap    # 최종 이미지 병합
```

### 3. 노드 ID 패턴

각 Extend 블록은 고유한 base ID를 가집니다:
- 첫 번째 Extend: `263` (263:260, 263:243, 263:258, ...)
- 두 번째 Extend: `297` (297:260, 297:243, 297:258, ...)
- 세 번째 Extend: `311` (311:260, 311:243, 311:258, ...)

**패턴**: `base_id = 263 + (extend_index * 34)`

### 4. 연결 구조

```
기본 워크플로우
  └─ "28" (WanVideoDecode) ──┐
                              │
첫 번째 Extend 블록           │
  └─ "263:260" ←──────────────┘
      └─ ... → "263:249" ──┐
                           │
두 번째 Extend 블록         │
  └─ "297:260" ←────────────┘
      └─ ... → "297:249" ──┐
                           │
세 번째 Extend 블록         │
  └─ "311:260" ←────────────┘
      └─ ... → "311:249" ──┐
                           │
최종 출력                   │
  └─ "139" (VHS_VideoCombine) ←┘
```

## 🛠️ 동적 Extend 구현 방안

### 1. 필요한 계산

#### 비디오 프레임 수 계산
```python
import cv2

def get_video_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count
```

#### Extend 횟수 계산
```python
def calculate_extend_count(total_frames, window_size=81, overlap=5):
    """
    Args:
        total_frames: 비디오의 총 프레임 수
        window_size: 한 번에 처리할 프레임 수 (기본값: 81)
        overlap: 각 Extend 블록 간 오버랩 프레임 수 (기본값: 5)
    
    Returns:
        필요한 Extend 횟수
    """
    if total_frames <= window_size:
        return 0
    
    # 첫 번째 window_size 프레임은 기본 워크플로우에서 처리
    remaining_frames = total_frames - window_size
    
    # 각 Extend는 (window_size - overlap)만큼의 새로운 프레임을 생성
    frames_per_extend = window_size - overlap
    
    # 필요한 Extend 횟수 계산
    extend_count = (remaining_frames + frames_per_extend - 1) // frames_per_extend
    
    return max(0, extend_count)
```

### 2. Extend 블록 생성 함수

각 Extend 블록은 다음 함수로 생성할 수 있습니다:

```python
def create_extend_block(base_id, prev_output_node, ...):
    """
    하나의 Extend 블록을 생성합니다.
    
    Returns:
        Extend 블록의 노드 딕셔너리
    """
    nodes = {}
    
    # 1. GetImageSizeAndCount
    nodes[f"{base_id}:260"] = {...}
    
    # 2. ImageBatchExtendWithOverlap (첫 번째)
    nodes[f"{base_id}:243"] = {...}
    
    # 3. WanVideoEncode
    nodes[f"{base_id}:258"] = {...}
    
    # 4. WanVideoAddOneToAllExtendEmbeds
    nodes[f"{base_id}:261"] = {...}
    
    # 5. WanVideoAddOneToAllPoseEmbeds
    nodes[f"{base_id}:251"] = {...}
    
    # 6. WanVideoSampler
    nodes[f"{base_id}:248"] = {...}
    
    # 7. WanVideoDecode
    nodes[f"{base_id}:247"] = {...}
    
    # 8. ImageBatchExtendWithOverlap (최종 병합)
    nodes[f"{base_id}:249"] = {...}
    
    return nodes
```

### 3. 동적 워크플로우 빌더

전체 워크플로우를 동적으로 생성하는 함수:

```python
def build_dynamic_workflow(base_workflow_path, video_path):
    """
    1. 기본 워크플로우 로드
    2. 비디오 프레임 수 계산
    3. 필요한 Extend 횟수 계산
    4. 각 Extend 블록 생성 및 연결
    5. 최종 출력 노드 업데이트
    """
    # 기본 워크플로우 로드
    workflow = load_workflow(base_workflow_path)
    
    # 비디오 프레임 수 계산
    total_frames = get_video_frame_count(video_path)
    
    # 필요한 Extend 횟수 계산
    extend_count = calculate_extend_count(total_frames)
    
    # 각 Extend 블록 생성 및 연결
    prev_output_node = "28"  # 기본 워크플로우의 출력 노드
    
    for i in range(extend_count):
        base_id = get_extend_base_id(i)
        extend_nodes = create_extend_block(base_id, prev_output_node, ...)
        workflow.update(extend_nodes)
        prev_output_node = f"{base_id}:249"
    
    # 최종 출력 노드 업데이트
    workflow["139"]["inputs"]["images"] = [prev_output_node, 0]
    
    return workflow
```

## 📝 구현 예시

### `workflow_builder.py` 사용법

```python
from workflow_builder import build_dynamic_workflow, save_workflow

# 동적 워크플로우 생성
workflow = build_dynamic_workflow(
    base_workflow_path="workflow/onetoall_0extend.json",
    video_path="input_video.mp4"
)

# 워크플로우 저장
save_workflow(workflow, "dynamic_workflow.json")
```

### `handler.py`에서 사용

```python
from workflow_builder import build_dynamic_workflow

def handler(job):
    job_input = job.get("input", {})
    
    # ... 입력 처리 ...
    
    # 동적 워크플로우 생성
    if job_input.get("use_onetoall", False):
        prompt = build_dynamic_workflow(
            base_workflow_path="/workflow/onetoall_0extend.json",
            video_path=video_path
        )
        
        # 워크플로우 파라미터 설정
        prompt["16"]["inputs"]["positive_prompt"] = job_input["prompt"]
        # ... 기타 설정 ...
    
    # ... 워크플로우 실행 ...
```

## 🎯 주요 고려사항

### 1. 노드 ID 충돌 방지
- 각 Extend 블록은 고유한 base_id를 가져야 합니다
- 패턴: `base_id = 263 + (extend_index * 34)`

### 2. 연결 관계 유지
- 각 Extend 블록은 이전 블록의 출력을 입력으로 받아야 합니다
- 마지막 Extend 블록의 출력을 최종 출력 노드에 연결해야 합니다

### 3. 비디오 길이 제한
- 너무 긴 비디오의 경우 메모리 문제가 발생할 수 있습니다
- 적절한 최대 Extend 횟수를 설정하는 것을 권장합니다

### 4. 성능 최적화
- Extend 횟수가 많을수록 처리 시간이 길어집니다
- 비디오 길이에 따라 적절한 Extend 횟수를 계산하는 것이 중요합니다

## 📊 Extend 횟수 계산 예시

| 총 프레임 수 | window_size | overlap | 필요한 Extend 횟수 |
|------------|-------------|---------|------------------|
| 81 이하    | 81          | 5       | 0                |
| 100        | 81          | 5       | 1                |
| 150        | 81          | 5       | 1                |
| 200        | 81          | 5       | 2                |
| 300        | 81          | 5       | 3                |

**계산 공식**: 
```
extend_count = ceil((total_frames - window_size) / (window_size - overlap))
```

## 🔗 관련 파일

- `workflow/onetoall_0extend.json`: 기본 워크플로우
- `workflow/onetoall_3extend.json`: 3번 Extend 예시
- `workflow_builder.py`: 동적 워크플로우 빌더 구현
- `handler.py`: 워크플로우 실행 핸들러

## ✅ 다음 단계

1. `workflow_builder.py`를 `handler.py`에 통합
2. 비디오 길이에 따른 Extend 횟수 자동 계산
3. 워크플로우 실행 및 테스트
4. 성능 최적화 및 에러 처리 개선

