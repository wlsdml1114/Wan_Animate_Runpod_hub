"""
동적 Extend 워크플로우 빌더
비디오 길이에 따라 필요한 만큼 Extend 블록을 추가합니다.
"""
import json
import cv2
import logging

logger = logging.getLogger(__name__)

# Extend 블록의 노드 ID 패턴
# 각 Extend 블록은 고유한 base_id를 가집니다
# 첫 번째: 263, 두 번째: 297, 세 번째: 311, ...
# 패턴: base_id = 263 + (extend_index * 34)

EXTEND_BASE_IDS = [263, 297, 311]  # 기존 3extend에서 사용된 ID들
# 더 많은 extend가 필요하면: [263, 297, 311, 345, 379, ...] (34씩 증가)

# 각 Extend 블록의 노드 타입
EXTEND_NODE_TYPES = {
    "260": "GetImageSizeAndCount",
    "243": "ImageBatchExtendWithOverlap",
    "258": "WanVideoEncode",
    "261": "WanVideoAddOneToAllExtendEmbeds",
    "251": "WanVideoAddOneToAllPoseEmbeds",
    "248": "WanVideoSampler",
    "247": "WanVideoDecode",
    "249": "ImageBatchExtendWithOverlap"
}


def get_video_frame_count(video_path):
    """비디오의 총 프레임 수를 반환합니다."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"비디오를 열 수 없습니다: {video_path}")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return frame_count
    except Exception as e:
        logger.error(f"비디오 프레임 수 측정 실패: {e}")
        raise


def get_video_fps(video_path):
    """비디오의 FPS를 반환합니다. (읽기 실패 시 None)"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"비디오를 열 수 없습니다: {video_path}")
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        # 일부 컨테이너/코덱에서 0.0이 나올 수 있음
        if not fps or fps <= 0:
            return None
        return fps
    except Exception as e:
        logger.warning(f"비디오 FPS 측정 실패(무시): {e}")
        return None


def calculate_extend_count(total_frames, window_size=81, overlap=5):
    """
    필요한 Extend 횟수를 계산합니다.
    
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
    
    logger.info(f"Extend 계산: 총 {total_frames}프레임, 기본 {window_size}프레임 처리 후 남은 {remaining_frames}프레임, Extend당 {frames_per_extend}프레임 추가, 필요 Extend: {extend_count}개")
    
    return max(0, extend_count)


def get_extend_base_id(extend_index):
    """
    Extend 블록의 base ID를 반환합니다.
    
    Args:
        extend_index: Extend 블록의 인덱스 (0부터 시작)
    
    Returns:
        base ID (예: 263, 297, 311, ...)
    """
    if extend_index < len(EXTEND_BASE_IDS):
        return EXTEND_BASE_IDS[extend_index]
    else:
        # 패턴: 263 + (extend_index * 34)
        return 263 + (extend_index * 34)


def create_extend_block(base_id, prev_output_node, overlap_node, scheduler_node, 
                       cfg_node, vae_node, model_node, text_embeds_node, 
                       pose_images_node, pose_prefix_node, ref_embeds_node):
    """
    하나의 Extend 블록을 생성합니다.
    
    Args:
        base_id: 이 Extend 블록의 base ID
        prev_output_node: 이전 블록의 출력 노드 ID
        overlap_node: overlap 값을 가진 노드 ID (예: "169")
        scheduler_node: scheduler 노드 ID (예: "231")
        cfg_node: CFG 노드 ID (예: "238")
        vae_node: VAE 노드 ID (예: "38")
        model_node: 모델 노드 ID (예: "80")
        text_embeds_node: 텍스트 embeds 노드 ID (예: "16")
        pose_images_node: 포즈 이미지 노드 ID (예: "141")
        pose_prefix_node: 포즈 prefix 이미지 노드 ID (예: "141", output 1)
        ref_embeds_node: 참조 embeds 노드 ID (예: "105")
    
    Returns:
        Extend 블록의 노드 딕셔너리
    """
    nodes = {}
    
    # 1. GetImageSizeAndCount (260)
    # 이전 Extend 블록의 output 2를 사용 (확장된 이미지 배치)
    # 첫 번째 Extend 블록이면 기본 워크플로우의 output 0 사용
    prev_output_index = 2 if ":" in prev_output_node else 0
    nodes[f"{base_id}:260"] = {
        "inputs": {
            "image": [prev_output_node, prev_output_index]
        },
        "class_type": "GetImageSizeAndCount",
        "_meta": {
            "title": "Get Image Size & Count"
        }
    }
    
    # 2. ImageBatchExtendWithOverlap (243) - 첫 번째
    # 첫 번째 Extend 블록(base_id=263)인 경우 overlap을 직접 값 5로 설정
    # 다른 Extend 블록은 노드 참조 사용
    if base_id == 263:
        overlap_value = 5  # 첫 번째 Extend는 직접 값 사용
    else:
        overlap_value = [overlap_node, 0]  # 나머지는 노드 참조 사용
    
    nodes[f"{base_id}:243"] = {
        "inputs": {
            "overlap": overlap_value,
            "overlap_side": "source",
            "overlap_mode": "linear_blend",
            "source_images": [f"{base_id}:260", 0]
        },
        "class_type": "ImageBatchExtendWithOverlap",
        "_meta": {
            "title": "Image Batch Extend With Overlap"
        }
    }
    
    # 3. WanVideoEncode (258)
    nodes[f"{base_id}:258"] = {
        "inputs": {
            "enable_vae_tiling": False,
            "tile_x": 272,
            "tile_y": 272,
            "tile_stride_x": 144,
            "tile_stride_y": 128,
            "noise_aug_strength": 0,
            "latent_strength": 1,
            "vae": [vae_node, 0],
            "image": [f"{base_id}:243", 1]
        },
        "class_type": "WanVideoEncode",
        "_meta": {
            "title": "WanVideo Encode"
        }
    }
    
    # 4. WanVideoAddOneToAllExtendEmbeds (261)
    nodes[f"{base_id}:261"] = {
        "inputs": {
            "window_size": 81,
            "overlap": [overlap_node, 0],
            "frames_processed": [f"{base_id}:260", 3],
            "if_not_enough_frames": "pad_with_last",
            "embeds": [ref_embeds_node, 0],
            "prev_latents": [f"{base_id}:258", 0],
            "pose_images": [pose_images_node, 0]
        },
        "class_type": "WanVideoAddOneToAllExtendEmbeds",
        "_meta": {
            "title": "WanVideo Add OneToAll Extend Embeds"
        }
    }
    
    # 5. WanVideoAddOneToAllPoseEmbeds (251)
    nodes[f"{base_id}:251"] = {
        "inputs": {
            "strength": 1,
            "start_percent": 0,
            "end_percent": 1,
            "embeds": [f"{base_id}:261", 0],
            "pose_images": [f"{base_id}:261", 1],
            "pose_prefix_image": [pose_prefix_node, 1]
        },
        "class_type": "WanVideoAddOneToAllPoseEmbeds",
        "_meta": {
            "title": "WanVideo Add OneToAll Pose Embeds"
        }
    }
    
    # 6. WanVideoSampler (248)
    nodes[f"{base_id}:248"] = {
        "inputs": {
            "steps": 6,
            "cfg": [cfg_node, 0],
            "shift": 7,
            "seed": 0,
            "force_offload": True,
            "scheduler": [scheduler_node, 3],
            "riflex_freq_index": 0,
            "denoise_strength": 1,
            "batched_cfg": False,
            "rope_function": "comfy",
            "start_step": 0,
            "end_step": -1,
            "add_noise_to_samples": "",
            "model": [model_node, 0],
            "image_embeds": [f"{base_id}:251", 0],
            "text_embeds": [text_embeds_node, 0]
        },
        "class_type": "WanVideoSampler",
        "_meta": {
            "title": "WanVideo Sampler"
        }
    }
    
    # 7. WanVideoDecode (247)
    nodes[f"{base_id}:247"] = {
        "inputs": {
            "enable_vae_tiling": False,
            "tile_x": 272,
            "tile_y": 272,
            "tile_stride_x": 144,
            "tile_stride_y": 128,
            "normalization": "default",
            "vae": [vae_node, 0],
            "samples": [f"{base_id}:248", 0]
        },
        "class_type": "WanVideoDecode",
        "_meta": {
            "title": "WanVideo Decode"
        }
    }
    
    # 8. ImageBatchExtendWithOverlap (249) - 최종 병합
    # 첫 번째 Extend 블록(base_id=263)인 경우 overlap을 직접 값 5로 설정
    # 다른 Extend 블록은 노드 참조 사용
    if base_id == 263:
        overlap_value_249 = 5  # 첫 번째 Extend는 직접 값 사용
    else:
        overlap_value_249 = [overlap_node, 0]  # 나머지는 노드 참조 사용
    
    nodes[f"{base_id}:249"] = {
        "inputs": {
            "overlap": overlap_value_249,
            "overlap_side": "source",
            "overlap_mode": "linear_blend",
            "source_images": [f"{base_id}:243", 0],
            "new_images": [f"{base_id}:247", 0]
        },
        "class_type": "ImageBatchExtendWithOverlap",
        "_meta": {
            "title": "Image Batch Extend With Overlap"
        }
    }
    
    return nodes


def build_dynamic_workflow(base_workflow_path, video_path, output_node_id="139"):
    """
    비디오 길이에 따라 동적으로 Extend 블록을 추가한 워크플로우를 생성합니다.
    
    Args:
        base_workflow_path: 기본 워크플로우 파일 경로
        video_path: 비디오 파일 경로
        output_node_id: 최종 출력 노드 ID (기본값: "139")
    
    Returns:
        동적으로 생성된 워크플로우 딕셔너리
    """
    # 기본 워크플로우 로드
    with open(base_workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 비디오 프레임 수 계산 (원본 파일 기준)
    total_frames = get_video_frame_count(video_path)
    logger.info(f"비디오 총 프레임 수: {total_frames}")
    source_fps = get_video_fps(video_path)
    if source_fps is not None:
        logger.info(f"비디오 FPS: {source_fps}")
    else:
        logger.info("비디오 FPS를 읽지 못해, VideoCombine의 기존 frame_rate 값을 유지합니다.")

    # 비디오 로드 노드 설정 수정
    # IMPORTANT:
    # - VHS_LoadVideo의 frame_load_cap=0이 "무제한"이 아니라 "기본값/0"으로 해석되는 환경이 있어,
    #   긴 비디오에서 pose 배치가 짤리면서 extend가 앞부분을 다시 참조(반복)하는 문제가 발생할 수 있습니다.
    # - 따라서 동적 워크플로우에서는 frame_load_cap을 명시적으로 충분히 크게 설정합니다.
    if "130" in workflow:
        if "frame_load_cap" in workflow["130"]["inputs"]:
            workflow["130"]["inputs"]["frame_load_cap"] = max(int(total_frames), 1)
        # force_rate는 강제하지 않습니다. (원본 FPS 사용)
        # base workflow 기본값(대개 0)을 유지하거나, 존재하면 0으로 설정합니다.
        if "force_rate" in workflow["130"]["inputs"]:
            workflow["130"]["inputs"]["force_rate"] = 0
    
    # 기본 워크플로우의 num_frames 설정
    # 노드 "99" (WanVideoEmptyEmbeds)와 "195" (GetImageRangeFromBatch)의 num_frames 설정
    # window_size는 81로 유지하되, 실제 비디오 길이에 맞게 조정
    window_size = 81
    if total_frames <= window_size:
        # 비디오가 81프레임 이하면 전체 프레임 수 사용
        workflow["99"]["inputs"]["num_frames"] = total_frames
        workflow["195"]["inputs"]["num_frames"] = total_frames
    else:
        # 비디오가 81프레임보다 길면 window_size 사용 (Extend로 처리)
        workflow["99"]["inputs"]["num_frames"] = window_size
        workflow["195"]["inputs"]["num_frames"] = window_size
    
    # 필요한 Extend 횟수 계산
    extend_count = calculate_extend_count(total_frames)
    logger.info(f"필요한 Extend 횟수: {extend_count}")
    
    # 기본 출력 노드 설정
    if extend_count == 0:
        # Extend가 필요 없으면 기본 워크플로우의 출력 노드 사용
        prev_output_node = "28"
    else:
        prev_output_node = None  # 나중에 설정됨
    
    # Extend 블록이 있는 경우에만 생성
    if extend_count > 0:
        # 기본 워크플로우의 주요 노드 ID 추출
        # (onetoall_0extend.json 기준)
        base_output_node = "28"  # 기본 워크플로우의 출력 노드
        overlap_node = "169"
        scheduler_node = "231"
        cfg_node = "238"
        vae_node = "38"
        model_node = "80"
        text_embeds_node = "16"
        pose_images_node = "141"
        pose_prefix_node = "141"  # output 1
        ref_embeds_node = "105"
        
        # 각 Extend 블록 생성 및 연결
        prev_output_node = base_output_node
        
        for i in range(extend_count):
            base_id = get_extend_base_id(i)
            logger.info(f"Extend 블록 {i+1}/{extend_count} 생성 중 (base_id: {base_id})...")
            
            # Extend 블록 생성
            extend_nodes = create_extend_block(
                base_id=base_id,
                prev_output_node=prev_output_node,
                overlap_node=overlap_node,
                scheduler_node=scheduler_node,
                cfg_node=cfg_node,
                vae_node=vae_node,
                model_node=model_node,
                text_embeds_node=text_embeds_node,
                pose_images_node=pose_images_node,
                pose_prefix_node=pose_prefix_node,
                ref_embeds_node=ref_embeds_node
            )
        
            # 워크플로우에 노드 추가
            workflow.update(extend_nodes)
            
            # 다음 Extend 블록을 위한 이전 출력 노드 업데이트
            # ImageBatchExtendWithOverlap의 output 2가 확장된 이미지 배치
            prev_output_node = f"{base_id}:249"
    
    # 최종 출력 노드 업데이트
    # output_node_id가 "139"인 경우 (VHS_VideoCombine)
    # - Extend가 있으면 ImageBatchExtendWithOverlap의 output 2(확장된 이미지 배치)를 연결
    # - Extend가 없으면 기본 WanVideoDecode의 output 0을 연결
    output_index = 2 if extend_count > 0 else 0

    # 최종 프레임 수를 입력 비디오 프레임 수에 맞게 슬라이스
    # (extend 과정에서 pad_with_last 등으로 출력 배치가 더 길어질 수 있어, VideoCombine 직전에 잘라줍니다.)
    slice_node_id = "900"
    workflow[slice_node_id] = {
        "inputs": {
            "start_index": 0,
            "num_frames": int(total_frames),
            "images": [prev_output_node, output_index],
        },
        "class_type": "GetImageRangeFromBatch",
        "_meta": {"title": "Get Image or Mask Range From Batch"},
    }

    if output_node_id in workflow:
        workflow[output_node_id]["inputs"]["images"] = [slice_node_id, 0]
        if source_fps is not None:
            workflow[output_node_id]["inputs"]["frame_rate"] = source_fps
        logger.info(
            f"최종 출력 노드 '{output_node_id}'를 '{slice_node_id}'[0] (slice {total_frames} frames) 에 연결했습니다"
            + (f" (fps={source_fps})" if source_fps is not None else "")
        )
    else:
        # 출력 노드가 없으면 새로 생성
        workflow[output_node_id] = {
            "inputs": {
                "frame_rate": source_fps if source_fps is not None else 0,
                "loop_count": 0,
                "filename_prefix": "WanVideo_OneToAllAnimation",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_metadata": True,
                "trim_to_audio": False,
                "pingpong": False,
                "save_output": False,
                "images": [slice_node_id, 0]
            },
            "class_type": "VHS_VideoCombine",
            "_meta": {
                "title": "Video Combine 🎥🅥🅗🅢"
            }
        }
        logger.info(f"새로운 출력 노드 '{output_node_id}'를 생성하고 '{slice_node_id}'[0] (slice {total_frames} frames) 에 연결했습니다.")
    
    return workflow


def save_workflow(workflow, output_path):
    """워크플로우를 JSON 파일로 저장합니다."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    logger.info(f"워크플로우를 '{output_path}'에 저장했습니다.")


# 사용 예시
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("사용법: python workflow_builder.py <base_workflow.json> <video_path> [output_workflow.json]")
        sys.exit(1)
    
    base_workflow_path = sys.argv[1]
    video_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "dynamic_workflow.json"
    
    workflow = build_dynamic_workflow(base_workflow_path, video_path)
    save_workflow(workflow, output_path)
    print(f"✅ 동적 워크플로우 생성 완료: {output_path}")

