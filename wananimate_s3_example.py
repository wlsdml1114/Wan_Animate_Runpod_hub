#!/usr/bin/env python3
"""
WanAnimate S3 Client 사용 예제
이 예제는 wananimate_s3_client.py를 사용하여 이미지와 비디오로부터 애니메이션을 생성하는 방법을 보여줍니다.
"""

import os
import sys
from wananimate_s3_client import WanAnimateS3Client

def main():
    """WanAnimate S3 클라이언트 사용 예제"""
    
    # ==================== 설정 ====================
    # 실제 값으로 변경하세요
    ENDPOINT_ID = "your-wananimate-endpoint-id"
    RUNPOD_API_KEY = "your-runpod-api-key"
    
    # S3 설정
    S3_ENDPOINT_URL = "https://s3api-eu-ro-1.runpod.io/"
    S3_ACCESS_KEY_ID = "your-s3-access-key"
    S3_SECRET_ACCESS_KEY = "your-s3-secret-key"
    S3_BUCKET_NAME = "your-bucket-name"
    S3_REGION = "eu-ro-1"
    
    # ==================== 클라이언트 초기화 ====================
    print("🚀 WanAnimate S3 클라이언트 초기화 중...")
    
    try:
        client = WanAnimateS3Client(
            runpod_endpoint_id=ENDPOINT_ID,
            runpod_api_key=RUNPOD_API_KEY,
            s3_endpoint_url=S3_ENDPOINT_URL,
            s3_access_key_id=S3_ACCESS_KEY_ID,
            s3_secret_access_key=S3_SECRET_ACCESS_KEY,
            s3_bucket_name=S3_BUCKET_NAME,
            s3_region=S3_REGION
        )
        print("✅ 클라이언트 초기화 완료!")
    except Exception as e:
        print(f"❌ 클라이언트 초기화 실패: {e}")
        return
    
    # ==================== 예제 1: 기본 애니메이션 생성 ====================
    print("\n" + "="*60)
    print("📹 예제 1: 기본 애니메이션 생성 (제어점 없음)")
    print("="*60)
    
    # 입력 파일 경로 (실제 파일 경로로 변경하세요)
    image_path = "./example_image.jpeg"
    video_path = "./example_video.mp4"
    
    # 파일 존재 확인
    if not os.path.exists(image_path):
        print(f"⚠️ 이미지 파일이 존재하지 않습니다: {image_path}")
        print("   예제 이미지 파일을 준비하거나 경로를 수정하세요.")
    else:
        result1 = client.create_animation_from_files(
            image_path=image_path,
            video_path=video_path if os.path.exists(video_path) else None,
            prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
            seed=12345,
            width=832,
            height=480,
            fps=16,
            cfg=1.0,
            steps=6
        )
        
        if result1.get('status') == 'COMPLETED':
            output_path = "./output_basic_animation.mp4"
            if client.save_video_result(result1, output_path):
                print(f"✅ 기본 애니메이션 생성 완료: {output_path}")
            else:
                print("❌ 결과 저장 실패")
        else:
            print(f"❌ 애니메이션 생성 실패: {result1.get('error')}")
    
    # ==================== 예제 2: 제어점을 사용한 애니메이션 생성 ====================
    print("\n" + "="*60)
    print("🎯 예제 2: 제어점을 사용한 애니메이션 생성")
    print("="*60)
    
    # 제어점 정의
    positive_points = [
        {"x": 483.34844284815, "y": 333.283583335728},
        {"x": 479.85856239437277, "y": 158.78956064686517}
    ]
    negative_points = [{"x": 0, "y": 0}]
    
    if os.path.exists(image_path):
        result2 = client.create_animation_with_control_points(
            image_path=image_path,
            video_path=video_path if os.path.exists(video_path) else None,
            prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
            seed=54321,
            width=832,
            height=480,
            fps=16,
            cfg=1.0,
            steps=6,
            positive_points=positive_points,
            negative_points=negative_points
        )
        
        if result2.get('status') == 'COMPLETED':
            output_path = "./output_controlled_animation.mp4"
            if client.save_video_result(result2, output_path):
                print(f"✅ 제어점 애니메이션 생성 완료: {output_path}")
            else:
                print("❌ 결과 저장 실패")
        else:
            print(f"❌ 애니메이션 생성 실패: {result2.get('error')}")
    else:
        print("⚠️ 이미지 파일이 없어 제어점 예제를 건너뜁니다.")
    
    # ==================== 예제 3: 배치 처리 ====================
    print("\n" + "="*60)
    print("📁 예제 3: 배치 처리 (여러 이미지 처리)")
    print("="*60)
    
    # 배치 처리용 폴더 경로
    image_folder = "./input_images"
    video_folder = "./input_videos"
    output_folder = "./output/batch_results"
    
    if os.path.isdir(image_folder):
        print(f"📂 이미지 폴더에서 배치 처리 시작: {image_folder}")
        
        batch_result = client.batch_process_animations(
            image_folder_path=image_folder,
            video_folder_path=video_folder if os.path.isdir(video_folder) else None,
            output_folder_path=output_folder,
            prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
            seed=11111,
            width=832,
            height=480,
            fps=16,
            cfg=1.0,
            steps=6
        )
        
        print(f"📊 배치 처리 결과:")
        print(f"   - 총 파일 수: {batch_result.get('total_files', 0)}")
        print(f"   - 성공: {batch_result.get('successful', 0)}")
        print(f"   - 실패: {batch_result.get('failed', 0)}")
        
        # 결과 상세 정보
        for result in batch_result.get('results', []):
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            print(f"   {status_emoji} {result['filename']}: {result['status']}")
            if result['status'] == 'failed':
                print(f"      오류: {result.get('error', 'Unknown error')}")
    else:
        print(f"⚠️ 이미지 폴더가 존재하지 않습니다: {image_folder}")
        print("   배치 처리를 위해 이미지 폴더를 준비하세요.")
    
    # ==================== 설정 가이드 ====================
    print("\n" + "="*60)
    print("⚙️ 설정 가이드")
    print("="*60)
    print("이 예제를 실행하기 전에 다음 설정을 확인하세요:")
    print()
    print("1. RunPod 설정:")
    print(f"   - ENDPOINT_ID: {ENDPOINT_ID}")
    print(f"   - RUNPOD_API_KEY: {RUNPOD_API_KEY}")
    print()
    print("2. S3 설정:")
    print(f"   - S3_ENDPOINT_URL: {S3_ENDPOINT_URL}")
    print(f"   - S3_ACCESS_KEY_ID: {S3_ACCESS_KEY_ID}")
    print(f"   - S3_SECRET_ACCESS_KEY: {S3_SECRET_ACCESS_KEY}")
    print(f"   - S3_BUCKET_NAME: {S3_BUCKET_NAME}")
    print(f"   - S3_REGION: {S3_REGION}")
    print()
    print("3. 입력 파일:")
    print(f"   - 이미지 파일: {image_path}")
    print(f"   - 비디오 파일: {video_path}")
    print(f"   - 이미지 폴더: {image_folder}")
    print(f"   - 비디오 폴더: {video_folder}")
    print()
    print("4. 필요한 패키지 설치:")
    print("   pip install boto3 requests")
    print()
    print("="*60)
    print("🎉 예제 실행 완료!")
    print("="*60)

if __name__ == "__main__":
    main()
