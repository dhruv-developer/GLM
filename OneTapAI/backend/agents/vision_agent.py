"""
Vision Agent for ZIEL-MAS
Provides image and video analysis capabilities using GLM Vision API
"""

import httpx
import base64
import os
import tempfile
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
from pathlib import Path

from backend.agents.base_agent import BaseAgent


class VisionAgent(BaseAgent):
    """
    Vision Agent - Analyzes images and videos using GLM Vision API
    Supports:
    - Image analysis (UI screenshots, technical diagrams, data visualization)
    - OCR (text extraction from screenshots)
    - Error diagnosis from screenshots
    - Video understanding
    """

    def __init__(self):
        super().__init__("Vision Agent", "vision")
        self.zai_api_key = os.getenv("ZAI_API_KEY", "")
        self.zai_api_url = os.getenv("ZAI_API_URL", "https://open.bigmodel.cn/api/paas/v4")

        # Supported analysis types
        self.analysis_types = {
            "ui_to_artifact": "Convert UI screenshots to code/prompts/specs",
            "extract_text": "OCR - Extract text from screenshots",
            "diagnose_error": "Analyze error screenshots and propose fixes",
            "understand_technical_diagram": "Interpret technical diagrams",
            "analyze_data_visualization": "Read charts and dashboards",
            "ui_diff_check": "Compare two UI screenshots",
            "general_analysis": "General-purpose image understanding"
        }

        logger.info("Vision Agent initialized with GLM-4.6V capabilities")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a vision analysis action"""
        try:
            if action == "analyze_image":
                return await self._analyze_image(parameters)
            elif action == "analyze_video":
                return await self._analyze_video(parameters)
            elif action == "extract_text":
                return await self._extract_text(parameters)
            elif action == "diagnose_error":
                return await self._diagnose_error(parameters)
            elif action == "ui_to_code":
                return await self._ui_to_code(parameters)
            elif action == "understand_diagram":
                return await self._understand_diagram(parameters)
            elif action == "analyze_chart":
                return await self._analyze_chart(parameters)
            elif action == "compare_ui":
                return await self._compare_ui(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return await self.handle_error(action, e)

    async def _analyze_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """General image analysis using GLM Vision API"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")
        prompt = params.get("prompt", "Describe this image in detail")
        analysis_type = params.get("analysis_type", "general")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info(f"Analyzing image with type: {analysis_type}")
        start_time = datetime.now()

        try:
            # Prepare image data
            if image_path:
                image_data = await self._load_image(image_path)
                if not image_data:
                    return self._create_response(
                        status="failed",
                        error=f"Failed to load image from path: {image_path}"
                    )
            else:
                image_data = image_base64

            # Call GLM Vision API
            result = await self._call_glm_vision_api(
                image_data=image_data,
                prompt=prompt,
                analysis_type=analysis_type
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"Image analysis completed in {execution_time:.2f}s")

            return self._create_response(
                status="completed",
                output={
                    "analysis_type": analysis_type,
                    "prompt": prompt,
                    "result": result,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "image_analyzed": True
                }
            )

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _analyze_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Video analysis using GLM Vision API"""
        video_path = params.get("video_path")
        video_base64 = params.get("video_base64")
        prompt = params.get("prompt", "Describe this video in detail")

        if not video_path and not video_base64:
            return self._create_response(
                status="failed",
                error="Either video_path or video_base64 is required"
            )

        logger.info("Analyzing video")
        start_time = datetime.now()

        try:
            # Prepare video data (video files are larger, need special handling)
            if video_path:
                video_data = await self._load_video(video_path)
                if not video_data:
                    return self._create_response(
                        status="failed",
                        error=f"Failed to load video from path: {video_path}"
                    )
            else:
                video_data = video_base64

            # Check file size (GLM Vision API has limits)
            video_size = len(video_data) if isinstance(video_data, str) else len(video_data.encode())
            if video_size > 8 * 1024 * 1024:  # 8MB limit
                return self._create_response(
                    status="failed",
                    error="Video file exceeds 8MB limit"
                )

            # Call GLM Vision API for video
            result = await self._call_glm_vision_api(
                image_data=video_data,
                prompt=prompt,
                analysis_type="video"
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"Video analysis completed in {execution_time:.2f}s")

            return self._create_response(
                status="completed",
                output={
                    "analysis_type": "video",
                    "prompt": prompt,
                    "result": result,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "video_analyzed": True
                }
            )

        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _extract_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OCR - Extract text from image"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info("Extracting text from image")

        # Enhanced prompt for OCR
        ocr_prompt = """Extract all text from this image accurately.
        Preserve the structure and formatting as much as possible.
        If there are multiple sections, organize them clearly.
        If this is code, preserve the exact syntax and indentation.
        If this is a document, extract headers, paragraphs, and lists properly."""

        return await self._analyze_image({
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt": ocr_prompt,
            "analysis_type": "extract_text"
        })

    async def _diagnose_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose error from screenshot"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")
        context = params.get("context", "")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info("Diagnosing error from screenshot")

        # Enhanced prompt for error diagnosis
        error_prompt = f"""Analyze this error screenshot and provide:
        1. Error type and identification
        2. Root cause analysis
        3. Specific, actionable fix steps
        4. Code examples if applicable
        5. Prevention strategies

        Context: {context}

        Be specific and practical in your recommendations."""

        return await self._analyze_image({
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt": error_prompt,
            "analysis_type": "diagnose_error"
        })

    async def _ui_to_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UI screenshot to code"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")
        framework = params.get("framework", "React")
        language = params.get("language", "TypeScript")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info(f"Converting UI to {framework} code")

        # Enhanced prompt for UI to code
        ui_prompt = f"""Convert this UI design into production-ready {framework} code using {language}.

        Requirements:
        1. Use modern best practices and patterns
        2. Make it responsive and accessible
        3. Include proper styling (CSS/Tailwind)
        4. Add necessary props and interfaces
        5. Include comments for complex logic
        6. Provide usage examples

        Return:
        - Complete component code
        - Styling code
        - Usage instructions
        - Dependencies needed"""

        return await self._analyze_image({
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt": ui_prompt,
            "analysis_type": "ui_to_artifact"
        })

    async def _understand_diagram(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Understand technical diagrams"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")
        diagram_type = params.get("diagram_type", "unknown")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info(f"Understanding {diagram_type} diagram")

        # Enhanced prompt for diagram understanding
        diagram_prompt = f"""Analyze this technical diagram ({diagram_type}) and provide:
        1. Diagram type and purpose
        2. Key components and their relationships
        3. Flow and interactions
        4. Insights and patterns
        5. Potential improvements or issues
        6. Implementation recommendations if applicable

        Be thorough and specific in your analysis."""

        return await self._analyze_image({
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt": diagram_prompt,
            "analysis_type": "understand_technical_diagram"
        })

    async def _analyze_chart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data visualization/charts"""
        image_path = params.get("image_path")
        image_base64 = params.get("image_base64")

        if not image_path and not image_base64:
            return self._create_response(
                status="failed",
                error="Either image_path or image_base64 is required"
            )

        logger.info("Analyzing data visualization")

        # Enhanced prompt for chart analysis
        chart_prompt = """Analyze this data visualization and provide:
        1. Chart type and structure
        2. Key data points and trends
        3. Insights and patterns
        4. Anomalies or outliers
        5. Data-driven recommendations
        6. Alternative visualization suggestions

        Extract specific values when possible and provide actionable insights."""

        return await self._analyze_image({
            "image_path": image_path,
            "image_base64": image_base64,
            "prompt": chart_prompt,
            "analysis_type": "analyze_data_visualization"
        })

    async def _compare_ui(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two UI screenshots"""
        image1_path = params.get("image1_path")
        image1_base64 = params.get("image1_base64")
        image2_path = params.get("image2_path")
        image2_base64 = params.get("image2_base64")

        if not image1_path and not image1_base64:
            return self._create_response(
                status="failed",
                error="image1_path or image1_base64 is required"
            )

        if not image2_path and not image2_base64:
            return self._create_response(
                status="failed",
                error="image2_path or image2_base64 is required"
            )

        logger.info("Comparing UI screenshots")

        # For UI comparison, we need to analyze both images
        # This is a simplified version - in production you'd want more sophisticated comparison
        result1 = await self._analyze_image({
            "image_path": image1_path,
            "image_base64": image1_base64,
            "prompt": "Describe this UI in detail, noting all visible elements, layout, styling, colors, and interactions.",
            "analysis_type": "ui_diff_check"
        })

        result2 = await self._analyze_image({
            "image_path": image2_path,
            "image_base64": image2_base64,
            "prompt": "Describe this UI in detail, noting all visible elements, layout, styling, colors, and interactions.",
            "analysis_type": "ui_diff_check"
        })

        if result1.get("status") == "completed" and result2.get("status") == "completed":
            return self._create_response(
                status="completed",
                output={
                    "analysis_type": "ui_diff_check",
                    "ui1_analysis": result1.get("output", {}),
                    "ui2_analysis": result2.get("output", {}),
                    "comparison": "Manual comparison of the two analyses above",
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            return self._create_response(
                status="failed",
                error="Failed to analyze one or both UI screenshots"
            )

    async def _load_image(self, image_path: str) -> Optional[str]:
        """Load image from file and convert to base64"""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image file not found: {image_path}")
                return None

            # Read image file
            with open(path, "rb") as image_file:
                image_data = image_file.read()

            # Determine content type
            if image_path.endswith(('.png', '.PNG')):
                content_type = "image/png"
            elif image_path.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                content_type = "image/jpeg"
            elif image_path.endswith(('.gif', '.GIF')):
                content_type = "image/gif"
            elif image_path.endswith(('.webp', '.WEBP')):
                content_type = "image/webp"
            else:
                content_type = "image/png"  # Default

            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{content_type};base64,{base64_data}"

        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None

    async def _load_video(self, video_path: str) -> Optional[str]:
        """Load video from file and convert to base64"""
        try:
            path = Path(video_path)
            if not path.exists():
                logger.error(f"Video file not found: {video_path}")
                return None

            # Read video file
            with open(path, "rb") as video_file:
                video_data = video_file.read()

            # Determine content type
            if video_path.endswith(('.mp4', '.MP4')):
                content_type = "video/mp4"
            elif video_path.endswith(('.mov', '.MOV')):
                content_type = "video/quicktime"
            elif video_path.endswith(('.webm', '.WEBM')):
                content_type = "video/webm"
            else:
                content_type = "video/mp4"  # Default

            # Convert to base64
            base64_data = base64.b64encode(video_data).decode('utf-8')
            return f"data:{content_type};base64,{base64_data}"

        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            return None

    async def _call_glm_vision_api(
        self,
        image_data: str,
        prompt: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Call GLM Vision API for image analysis"""

        if not self.zai_api_key:
            # Return mock result if no API key configured
            logger.warning("ZAI_API_KEY not configured, returning mock result")
            return {
                "mock": True,
                "analysis": "This is a mock result. Configure ZAI_API_KEY to use real GLM Vision API.",
                "prompt": prompt,
                "analysis_type": analysis_type
            }

        try:
            headers = {
                "Authorization": f"Bearer {self.zai_api_key}",
                "Content-Type": "application/json"
            }

            # Prepare payload for GLM Vision API
            payload = {
                "model": "glm-4v",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.zai_api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    response_data = response.json()
                    content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                    return {
                        "success": True,
                        "analysis": content,
                        "model": "glm-4v",
                        "usage": response_data.get("usage", {})
                    }
                else:
                    logger.error(f"GLM Vision API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "details": response.text
                    }

        except httpx.TimeoutException:
            logger.error("GLM Vision API timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"GLM Vision API call failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
