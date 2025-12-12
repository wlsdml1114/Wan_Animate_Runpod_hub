"""
20초 비디오용 워크플로우 생성 스크립트
20초 @ 16fps = 320프레임
"""
import json
import sys
import os

# workflow_builder의 함수들을 직접 구현 (cv2 없이)
def calculate_extend_count(total_frames, window_size=81, overlap=5):
    """필요한 Extend 횟수를 계산합니다."""
    if total_frames <= window_size:
        return 0
    remaining_frames = total_frames - window_size
    frames_per_extend = window_size - overlap
    extend_count = (remaining_frames + frames_per_extend - 1) // frames_per_extend
    return max(0, extend_count)

def get_extend_base_id(extend_index):
    """Extend 블록의 base ID를 반환합니다."""
    EXTEND_BASE_IDS = [263, 297, 311]
    if extend_index < len(EXTEND_BASE_IDS):
        return EXTEND_BASE_IDS[extend_index]
    else:
        return 263 + (extend_index * 34)

def create_extend_block(base_id, prev_output_node, overlap_node, scheduler_node, 
                       cfg_node, vae_node, model_node, text_embeds_node, 
                       pose_images_node, pose_prefix_node, ref_embeds_node):
    """하나의 Extend 블록을 생성합니다."""
    nodes = {}
    
    # 1. GetImageSizeAndCount (260)
    # 이전 Extend 블록의 output 2를 사용 (확장된 이미지 배치)
    # 첫 번째 Extend 블록이면 기본 워크플로우의 output 0 사용
    prev_output_index = 2 if ":" in prev_output_node else 0
    nodes[f"{base_id}:260"] = {
        "inputs": {"image": [prev_output_node, prev_output_index]},
        "class_type": "GetImageSizeAndCount",
        "_meta": {"title": "Get Image Size & Count"}
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
        "_meta": {"title": "Image Batch Extend With Overlap"}
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
        "_meta": {"title": "WanVideo Encode"}
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
        "_meta": {"title": "WanVideo Add OneToAll Extend Embeds"}
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
        "_meta": {"title": "WanVideo Add OneToAll Pose Embeds"}
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
        "_meta": {"title": "WanVideo Sampler"}
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
        "_meta": {"title": "WanVideo Decode"}
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
        "_meta": {"title": "Image Batch Extend With Overlap"}
    }
    
    return nodes

def create_20sec_workflow():
    """20초 비디오용 워크플로우 생성"""
    
    # 기본 워크플로우 경로
    base_workflow_path = 'workflow/onetoall_0extend.json'
    
    # 20초 비디오 시뮬레이션 (16fps * 20초 = 320프레임)
    # 실제 비디오 파일이 없으므로, 워크플로우를 직접 수정하여 생성
    
    # 기본 워크플로우 로드
    with open(base_workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 비디오 설정 (20초 @ 16fps = 320프레임)
    total_frames = 320
    window_size = 81
    overlap = 5
    
    print(f"비디오 총 프레임 수: {total_frames} (20초 @ 16fps)")
    
    # 비디오 로드 노드 설정
    # IMPORTANT: frame_load_cap=0이 환경에 따라 "무제한"이 아니라 "기본값/0"으로 해석될 수 있어,
    #            긴 비디오에서 pose 배치가 잘려 extend 단계에서 앞부분이 반복되는 문제가 생길 수 있습니다.
    #            따라서 필요한 프레임 수(20초@16fps=320)를 명시적으로 설정합니다.
    workflow["130"]["inputs"]["frame_load_cap"] = total_frames
    # force_rate는 강제하지 않습니다 (원본 FPS 사용). 샘플 워크플로우에서는 0(미강제)로 둡니다.
    if "force_rate" in workflow["130"]["inputs"]:
        workflow["130"]["inputs"]["force_rate"] = 0
    
    # 기본 워크플로우의 num_frames 설정
    workflow["99"]["inputs"]["num_frames"] = window_size
    workflow["195"]["inputs"]["num_frames"] = window_size
    
    # 필요한 Extend 횟수 계산
    extend_count = calculate_extend_count(total_frames, window_size, overlap)
    print(f"필요한 Extend 횟수: {extend_count}")
    
    # Extend 블록 생성
    if extend_count > 0:
        base_output_node = "28"
        overlap_node = "169"
        scheduler_node = "231"
        cfg_node = "238"
        vae_node = "38"
        model_node = "80"
        text_embeds_node = "16"
        pose_images_node = "141"
        pose_prefix_node = "141"
        ref_embeds_node = "105"
        
        prev_output_node = base_output_node
        
        for i in range(extend_count):
            base_id = get_extend_base_id(i)
            print(f"Extend 블록 {i+1}/{extend_count} 생성 중 (base_id: {base_id})...")
            
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
            
            workflow.update(extend_nodes)
            prev_output_node = f"{base_id}:249"
    
    # 최종 출력 노드 업데이트 (RIFE 없음)
    # 출력 배치를 입력 비디오 프레임 수(total_frames)만큼 잘라서 VideoCombine에 연결합니다.
    output_index = 2 if extend_count > 0 else 0
    slice_node_id = "900"
    workflow[slice_node_id] = {
        "inputs": {
            "start_index": 0,
            "num_frames": total_frames,
            "images": [prev_output_node, output_index],
        },
        "class_type": "GetImageRangeFromBatch",
        "_meta": {"title": "Get Image or Mask Range From Batch"},
    }
    workflow["139"]["inputs"]["images"] = [slice_node_id, 0]
    # 샘플 워크플로우이므로 frame_rate는 기존값(보통 16)을 유지합니다.
    # 실제 서비스 실행에서는 workflow_builder가 입력 비디오 FPS를 읽어 frame_rate에 반영합니다.
    print(f"최종 출력 노드 '139'를 '{slice_node_id}'[0] (slice {total_frames} frames)에 연결했습니다 (RIFE 없음)")
    
    # 워크플로우 저장
    output_path = "workflow/onetoall_20sec_320frames.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 20초 비디오용 워크플로우 생성 완료: {output_path}")
    print(f"   - 총 프레임: {total_frames} (20초 @ 16fps)")
    print(f"   - 기본 처리: {window_size} 프레임")
    print(f"   - Extend 블록: {extend_count}개")
    print(f"   - 최종 출력: RIFE 없음 (VideoCombine frame_rate는 기본값/입력 설정 사용)")
    
    return workflow

if __name__ == "__main__":
    create_20sec_workflow()

