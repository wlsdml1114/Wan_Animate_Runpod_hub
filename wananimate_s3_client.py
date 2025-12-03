#!/usr/bin/env python3
"""
WanAnimate API client with S3 upload functionality
Complete client that uploads files using RunPod Network Volume S3 and calls wanAnimate API
"""

import os
import requests
import json
import boto3
from botocore.client import Config
import time
import base64
from typing import Optional, Dict, Any, List, Union
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WanAnimateS3Client:
    def __init__(
        self,
        runpod_endpoint_id: str,
        runpod_api_key: str,
        s3_endpoint_url: str,
        s3_access_key_id: str,
        s3_secret_access_key: str,
        s3_bucket_name: str,
        s3_region: str = 'eu-ro-1'
    ):
        """
        Initialize WanAnimate S3 client
        
        Args:
            runpod_endpoint_id: RunPod endpoint ID
            runpod_api_key: RunPod API key
            s3_endpoint_url: S3 endpoint URL
            s3_access_key_id: S3 access key ID
            s3_secret_access_key: S3 secret access key
            s3_bucket_name: S3 bucket name
            s3_region: S3 region
        """
        self.runpod_endpoint_id = runpod_endpoint_id
        self.runpod_api_key = runpod_api_key
        self.runpod_api_endpoint = f"https://api.runpod.ai/v2/{runpod_endpoint_id}/run"
        self.status_url = f"https://api.runpod.ai/v2/{runpod_endpoint_id}/status"
        
        # S3 configuration
        self.s3_endpoint_url = s3_endpoint_url
        self.s3_access_key_id = s3_access_key_id
        self.s3_secret_access_key = s3_secret_access_key
        self.s3_bucket_name = s3_bucket_name
        self.s3_region = s3_region
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint_url,
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_access_key,
            region_name=s3_region,
            config=Config(signature_version='s3v4')
        )
        
        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {runpod_api_key}',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"WanAnimateS3Client initialized - Endpoint: {runpod_endpoint_id}")
    
    def upload_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """
        Upload file to S3
        
        Args:
            file_path: Local path of file to upload
            s3_key: Key (path) to store in S3
        
        Returns:
            S3 path or None (on failure)
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
            
            logger.info(f"S3 upload started: {file_path} -> s3://{self.s3_bucket_name}/{s3_key}")
            
            self.s3_client.upload_file(file_path, self.s3_bucket_name, s3_key)
            
            s3_path = f"/runpod-volume/{s3_key}"
            logger.info(f"✅ S3 upload successful: {s3_path}")
            return s3_path
            
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return None
    
    def upload_multiple_files(self, file_paths: List[str], s3_keys: List[str]) -> Dict[str, Optional[str]]:
        """
        Upload multiple files to S3
        
        Args:
            file_paths: List of local paths of files to upload
            s3_keys: List of keys to store in S3
        
        Returns:
            Dictionary with filename as key and S3 path as value
        """
        results = {}
        
        for file_path, s3_key in zip(file_paths, s3_keys):
            filename = os.path.basename(file_path)
            s3_path = self.upload_to_s3(file_path, s3_key)
            results[filename] = s3_path
        
        return results
    
    def submit_job(self, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Submit job to RunPod
        
        Args:
            input_data: API input data
        
        Returns:
            Job ID or None (on failure)
        """
        payload = {"input": input_data}
        
        try:
            logger.info(f"Submitting job to RunPod: {self.runpod_api_endpoint}")
            logger.info(f"Input data: {json.dumps(input_data, indent=2, ensure_ascii=False)}")
            
            response = self.session.post(self.runpod_api_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            job_id = response_data.get('id')
            
            if job_id:
                logger.info(f"✅ Job submission successful! Job ID: {job_id}")
                return job_id
            else:
                logger.error(f"❌ Failed to receive Job ID: {response_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Job submission failed: {e}")
            return None
    
    def wait_for_completion(self, job_id: str, check_interval: int = 10, max_wait_time: int = 1800) -> Dict[str, Any]:
        """
        Wait for job completion
        
        Args:
            job_id: Job ID
            check_interval: Status check interval (seconds)
            max_wait_time: Maximum wait time (seconds)
        
        Returns:
            Job result dictionary
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                logger.info(f"⏱️ Checking job status... (Job ID: {job_id})")
                
                response = self.session.get(f"{self.status_url}/{job_id}", timeout=30)
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get('status')
                
                if status == 'COMPLETED':
                    logger.info("✅ Job completed!")
                    return {
                        'status': 'COMPLETED',
                        'output': status_data.get('output'),
                        'job_id': job_id
                    }
                elif status == 'FAILED':
                    logger.error("❌ Job failed.")
                    return {
                        'status': 'FAILED',
                        'error': status_data.get('error', 'Unknown error'),
                        'job_id': job_id
                    }
                elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                    logger.info(f"🏃 Job in progress... (status: {status})")
                    time.sleep(check_interval)
                else:
                    logger.warning(f"❓ Unknown status: {status}")
                    return {
                        'status': 'UNKNOWN',
                        'data': status_data,
                        'job_id': job_id
                    }
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error checking status: {e}")
                time.sleep(check_interval)
        
        logger.error(f"❌ Job wait timeout ({max_wait_time} seconds)")
        return {
            'status': 'TIMEOUT',
            'job_id': job_id
        }
    
    def save_video_result(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Save video file from job result
        
        Args:
            result: Job result dictionary
            output_path: File path to save
        
        Returns:
            Save success status
        """
        try:
            if result.get('status') != 'COMPLETED':
                logger.error(f"Job not completed: {result.get('status')}")
                return False
            
            output = result.get('output', {})
            video_b64 = output.get('video_base64') or output.get('video')
            
            if not video_b64:
                logger.error("No video data available")
                return False
            
            # Create directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Decode and save video
            decoded_video = base64.b64decode(video_b64)
            
            with open(output_path, 'wb') as f:
                f.write(decoded_video)
            
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Video saved successfully: {output_path} ({file_size / (1024*1024):.1f}MB)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Video save failed: {e}")
            return False
    
    def create_animation_from_files(
        self,
        image_path: str,
        video_path: Optional[str] = None,
        prompt: str = "A person walking in a natural way",
        negative_prompt: Optional[str] = None,
        seed: int = 12345,
        width: int = 832,
        height: int = 480,
        fps: int = 16,
        cfg: float = 1.0,
        steps: int = 6,
        points_store: Optional[str] = None,
        coordinates: Optional[str] = None,
        neg_coordinates: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create animation from local files (including S3 upload)
        
        Args:
            image_path: Image file path
            video_path: Reference video file path (optional)
            prompt: Animation description text
            negative_prompt: Negative prompt to avoid unwanted elements (optional)
            seed: Random seed for generation
            width: Output width
            height: Output height
            fps: Frame rate
            cfg: Classifier-free guidance scale
            steps: Number of denoising steps
            points_store: JSON string containing positive control points
            coordinates: JSON string containing coordinate points
            neg_coordinates: JSON string containing negative coordinate points
        
        Returns:
            Job result dictionary
        """
        # Check file existence
        if not os.path.exists(image_path):
            return {"error": f"Image file does not exist: {image_path}"}
        
        if video_path and not os.path.exists(video_path):
            return {"error": f"Video file does not exist: {video_path}"}
        
        # Upload files to S3
        timestamp = int(time.time())
        
        # Upload image
        image_s3_key = f"input/wananimate/{timestamp}_{os.path.basename(image_path)}"
        image_s3_path = self.upload_to_s3(image_path, image_s3_key)
        if not image_s3_path:
            return {"error": "Image S3 upload failed"}
        
        # Upload video (if provided)
        video_s3_path = None
        if video_path:
            video_s3_key = f"input/wananimate/{timestamp}_{os.path.basename(video_path)}"
            video_s3_path = self.upload_to_s3(video_path, video_s3_key)
            if not video_s3_path:
                return {"error": "Video S3 upload failed"}
        
        # Configure API input data
        input_data = {
            "prompt": prompt,
            "seed": seed,
            "width": width,
            "height": height,
            "fps": fps,
            "cfg": cfg,
            "steps": steps
        }
        
        # Set negative prompt (if provided)
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        
        # Set image input
        input_data["image_path"] = image_s3_path
        
        # Set video input (if provided)
        if video_s3_path:
            input_data["video_path"] = video_s3_path
        
        # Set control points (if provided)
        if points_store and coordinates and neg_coordinates:
            input_data["points_store"] = points_store
            input_data["coordinates"] = coordinates
            input_data["neg_coordinates"] = neg_coordinates
        
        # Submit job and wait
        job_id = self.submit_job(input_data)
        if not job_id:
            return {"error": "Job submission failed"}
        
        result = self.wait_for_completion(job_id)
        return result
    
    def create_animation_with_control_points(
        self,
        image_path: str,
        video_path: Optional[str] = None,
        prompt: str = "A person walking in a natural way",
        negative_prompt: Optional[str] = None,
        seed: int = 12345,
        width: int = 832,
        height: int = 480,
        fps: int = 16,
        cfg: float = 1.0,
        steps: int = 6,
        positive_points: Optional[List[Dict[str, float]]] = None,
        negative_points: Optional[List[Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        """
        Create animation with control points from local files
        
        Args:
            image_path: Image file path
            video_path: Reference video file path (optional)
            prompt: Animation description text
            negative_prompt: Negative prompt to avoid unwanted elements (optional)
            seed: Random seed for generation
            width: Output width
            height: Output height
            fps: Frame rate
            cfg: Classifier-free guidance scale
            steps: Number of denoising steps
            positive_points: List of positive control points [{"x": float, "y": float}]
            negative_points: List of negative control points [{"x": float, "y": float}]
        
        Returns:
            Job result dictionary
        """
        # Prepare control points
        points_store = None
        coordinates = None
        neg_coordinates = None
        
        if positive_points and negative_points:
            points_store = json.dumps({
                "positive": positive_points,
                "negative": negative_points
            })
            coordinates = json.dumps(positive_points)
            neg_coordinates = json.dumps(negative_points)
        
        return self.create_animation_from_files(
            image_path=image_path,
            video_path=video_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            width=width,
            height=height,
            fps=fps,
            cfg=cfg,
            steps=steps,
            points_store=points_store,
            coordinates=coordinates,
            neg_coordinates=neg_coordinates
        )
    
    def batch_process_animations(
        self,
        image_folder_path: str,
        video_folder_path: Optional[str] = None,
        output_folder_path: str = "output/wananimate_batch",
        valid_image_extensions: tuple = ('.jpg', '.jpeg', '.png', '.bmp'),
        valid_video_extensions: tuple = ('.mp4', '.avi', '.mov', '.mkv'),
        prompt: str = "A person walking in a natural way",
        negative_prompt: Optional[str] = None,
        seed: int = 12345,
        width: int = 832,
        height: int = 480,
        fps: int = 16,
        cfg: float = 1.0,
        steps: int = 6
    ) -> Dict[str, Any]:
        """
        Batch process animations from folder
        
        Args:
            image_folder_path: Folder path containing image files
            video_folder_path: Folder path containing video files (optional)
            output_folder_path: Folder path to save results
            valid_image_extensions: Image file extensions to process
            valid_video_extensions: Video file extensions to process
            prompt: Animation description text
            negative_prompt: Negative prompt to avoid unwanted elements (optional)
            seed: Random seed for generation
            width: Output width
            height: Output height
            fps: Frame rate
            cfg: Classifier-free guidance scale
            steps: Number of denoising steps
        
        Returns:
            Batch processing result dictionary
        """
        # Check paths
        if not os.path.isdir(image_folder_path):
            return {"error": f"Image folder does not exist: {image_folder_path}"}
        
        if video_folder_path and not os.path.isdir(video_folder_path):
            return {"error": f"Video folder does not exist: {video_folder_path}"}
        
        # Create output folder
        os.makedirs(output_folder_path, exist_ok=True)
        
        # Get image file list
        image_files = [
            f for f in os.listdir(image_folder_path)
            if f.lower().endswith(valid_image_extensions)
        ]
        
        if not image_files:
            return {"error": f"No image files to process: {image_folder_path}"}
        
        # Get video file list (if video folder provided)
        video_files = []
        if video_folder_path:
            video_files = [
                f for f in os.listdir(video_folder_path)
                if f.lower().endswith(valid_video_extensions)
            ]
        
        logger.info(f"Batch processing started: {len(image_files)} images, {len(video_files)} videos")
        
        results = {
            "total_files": len(image_files),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        # Process each image file
        for i, image_filename in enumerate(image_files):
            logger.info(f"\n==================== Processing started: {image_filename} ====================")
            
            image_path = os.path.join(image_folder_path, image_filename)
            
            # Find corresponding video file (if video folder provided)
            video_path = None
            if video_files:
                # Try to find video with same base name
                base_name = os.path.splitext(image_filename)[0]
                for video_filename in video_files:
                    if os.path.splitext(video_filename)[0] == base_name:
                        video_path = os.path.join(video_folder_path, video_filename)
                        break
                
                # If no matching video found, use first video
                if not video_path and video_files:
                    video_path = os.path.join(video_folder_path, video_files[0])
            
            # Create animation
            result = self.create_animation_from_files(
                image_path=image_path,
                video_path=video_path,
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed + i,  # Different seed for each file
                width=width,
                height=height,
                fps=fps,
                cfg=cfg,
                steps=steps
            )
            
            if result.get('status') == 'COMPLETED':
                # Save result file
                base_filename = os.path.splitext(image_filename)[0]
                output_filename = os.path.join(output_folder_path, f"animation_{base_filename}.mp4")
                
                if self.save_video_result(result, output_filename):
                    logger.info(f"✅ [{image_filename}] Processing completed")
                    results["successful"] += 1
                    results["results"].append({
                        "filename": image_filename,
                        "status": "success",
                        "output_file": output_filename,
                        "job_id": result.get('job_id')
                    })
                else:
                    logger.error(f"[{image_filename}] Result save failed")
                    results["failed"] += 1
                    results["results"].append({
                        "filename": image_filename,
                        "status": "failed",
                        "error": "Result save failed",
                        "job_id": result.get('job_id')
                    })
            else:
                logger.error(f"[{image_filename}] Job failed: {result.get('error', 'Unknown error')}")
                results["failed"] += 1
                results["results"].append({
                    "filename": image_filename,
                    "status": "failed",
                    "error": result.get('error', 'Unknown error'),
                    "job_id": result.get('job_id')
                })
            
            logger.info(f"==================== Processing completed: {image_filename} ====================")
        
        logger.info(f"\n🎉 Batch processing completed: {results['successful']}/{results['total_files']} successful")
        return results


def main():
    """Usage example"""
    
    # Configuration (change to actual values)
    ENDPOINT_ID = "your-endpoint-id"
    RUNPOD_API_KEY = "your-runpod-api-key"
    
    # S3 configuration
    S3_ENDPOINT_URL = "https://s3api-eu-ro-1.runpod.io/"
    S3_ACCESS_KEY_ID = "your-s3-access-key"
    S3_SECRET_ACCESS_KEY = "your-s3-secret-key"
    S3_BUCKET_NAME = "your-bucket-name"
    S3_REGION = "eu-ro-1"
    
    # Initialize client
    client = WanAnimateS3Client(
        runpod_endpoint_id=ENDPOINT_ID,
        runpod_api_key=RUNPOD_API_KEY,
        s3_endpoint_url=S3_ENDPOINT_URL,
        s3_access_key_id=S3_ACCESS_KEY_ID,
        s3_secret_access_key=S3_SECRET_ACCESS_KEY,
        s3_bucket_name=S3_BUCKET_NAME,
        s3_region=S3_REGION
    )
    
    print("=== WanAnimate S3 Client Usage Example ===\n")
    
    # Example 1: Basic animation without control points
    print("1. Basic animation without control points")
    result1 = client.create_animation_from_files(
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
    
    if result1.get('status') == 'COMPLETED':
        client.save_video_result(result1, "./output_basic_animation.mp4")
    else:
        print(f"Error: {result1.get('error')}")
    
    print("\n" + "-"*50 + "\n")
    
    # Example 2: Animation with control points
    print("2. Animation with control points")
    positive_points = [
        {"x": 483.34844284815, "y": 333.283583335728},
        {"x": 479.85856239437277, "y": 158.78956064686517}
    ]
    negative_points = [{"x": 0, "y": 0}]
    
    result2 = client.create_animation_with_control_points(
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
    
    if result2.get('status') == 'COMPLETED':
        client.save_video_result(result2, "./output_controlled_animation.mp4")
    else:
        print(f"Error: {result2.get('error')}")
    
    print("\n" + "-"*50 + "\n")
    
    # # Example 3: Batch processing
    # print("3. Batch processing")
    # batch_result = client.batch_process_animations(
    #     image_folder_path="./input_images",
    #     video_folder_path="./input_videos",
    #     output_folder_path="./output/batch_results",
    #     prompt="A person walking in a natural way, soft 3D render style, night time, moonlight",
    #     seed=12345,
    #     width=832,
    #     height=480,
    #     fps=16,
    #     cfg=1.0,
    #     steps=6
    # )
    
    # print(f"Batch processing result: {batch_result}")
    
    # print("\n=== All examples completed ===")


if __name__ == "__main__":
    main()
