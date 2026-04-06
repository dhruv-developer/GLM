"""
Reasoning Engine for ZIEL-MAS
Implements chain-of-thought reasoning before task execution
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from loguru import logger
from pydantic import BaseModel, Field

from backend.models.task import TaskGraph, TaskNode, TaskStatus
from backend.services.database import DatabaseService
from backend.services.cache import RedisService


class ReasoningStep(BaseModel):
    """A single reasoning step"""
    step_number: int
    step_type: str  # "analysis", "planning", "validation", "refinement"
    thought: str
    reasoning: str
    alternatives: List[str] = Field(default_factory=list)
    decision: str
    decision_obj: Optional[Dict[str, Any]] = None  # Store structured decision data
    confidence: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReasoningChain(BaseModel):
    """A chain of reasoning steps"""
    task_id: str
    intent: str
    steps: List[ReasoningStep] = Field(default_factory=list)
    final_plan: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=0.0)
    estimated_duration: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReasoningEngine:
    """
    Reasoning Engine - Implements chain-of-thought reasoning
    Before executing any task, the system:
    1. Analyzes the intent deeply
    2. Plans the approach
    3. Considers alternatives
    4. Validates the plan
    5. Refines if needed
    6. Only then executes
    """

    def __init__(
        self,
        db_service: DatabaseService,
        redis_service: RedisService,
        glm_api_key: str,
        glm_api_url: str
    ):
        self.db = db_service
        self.redis = redis_service
        self.glm_api_key = glm_api_key
        self.glm_api_url = glm_api_url

    async def reason_about_task(
        self,
        intent: str,
        task_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningChain:
        """
        Perform complete reasoning chain for a task
        """
        logger.info(f"Starting reasoning chain for task {task_id}")

        reasoning_chain = ReasoningChain(
            task_id=task_id,
            intent=intent
        )

        start_time = time.time()

        try:
            # Step 1: Deep Analysis
            analysis_step = await self._analyze_intent(intent, context)
            reasoning_chain.steps.append(analysis_step)

            # Step 2: Approach Planning
            planning_step = await self._plan_approach(intent, analysis_step, context)
            reasoning_chain.steps.append(planning_step)

            # Step 3: Alternative Consideration
            alternatives_step = await self._consider_alternatives(intent, planning_step, context)
            reasoning_chain.steps.append(alternatives_step)

            # Step 4: Plan Validation
            validation_step = await self._validate_plan(intent, planning_step, context)
            reasoning_chain.steps.append(validation_step)

            # Step 5: Refinement (if needed)
            if validation_step.confidence < 0.7:
                refinement_step = await self._refine_plan(intent, planning_step, validation_step, context)
                reasoning_chain.steps.append(refinement_step)
                reasoning_chain.final_plan = refinement_step.decision_obj
            else:
                reasoning_chain.final_plan = planning_step.decision_obj

            # Calculate overall confidence
            reasoning_chain.confidence_score = sum(
                step.confidence for step in reasoning_chain.steps
            ) / len(reasoning_chain.steps)

            # Estimate duration
            reasoning_chain.estimated_duration = await self._estimate_execution_time(reasoning_chain)

            # Store reasoning chain
            await self._store_reasoning_chain(reasoning_chain)

            execution_time = time.time() - start_time
            logger.info(f"Reasoning completed for {task_id} in {execution_time:.2f}s")

            return reasoning_chain

        except Exception as e:
            logger.error(f"Reasoning failed for {task_id}: {e}")
            # Create fallback reasoning
            fallback_step = ReasoningStep(
                step_number=1,
                step_type="fallback",
                thought=f"Reasoning failed, using direct execution",
                reasoning=str(e),
                decision="execute_directly",
                confidence=0.5
            )
            reasoning_chain.steps.append(fallback_step)
            reasoning_chain.confidence_score = 0.5
            return reasoning_chain

    async def _analyze_intent(
        self,
        intent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        """
        Step 1: Deep analysis of the user's intent
        """
        logger.info("Step 1: Analyzing intent")

        prompt = f"""Analyze this user intent deeply:

Intent: "{intent}"

Context: {json.dumps(context, indent=2) if context else "None"}

Provide a detailed analysis covering:
1. What does the user actually want to achieve?
2. What is the core problem or need?
3. What are the explicit requirements?
4. What are the implicit requirements?
5. What is the complexity level (simple, moderate, complex)?
6. What are the potential challenges?
7. What information is missing or ambiguous?

Format your response as JSON:
{{
    "understanding": "deep understanding of intent",
    "core_problem": "the core problem",
    "explicit_requirements": ["req1", "req2"],
    "implicit_requirements": ["req1", "req2"],
    "complexity": "simple|moderate|complex",
    "challenges": ["challenge1", "challenge2"],
    "missing_info": ["info1", "info2"],
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_glm_api(prompt)

            return ReasoningStep(
                step_number=1,
                step_type="analysis",
                thought="Deep analysis of user intent",
                reasoning=response.get("understanding", ""),
                alternatives=[
                    f"Complexity: {response.get('complexity', 'unknown')}",
                    f"Challenges: {len(response.get('challenges', []))} identified"
                ],
                decision=json.dumps(response),
                confidence=response.get("confidence", 0.7)
            )
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return ReasoningStep(
                step_number=1,
                step_type="analysis",
                thought="Basic intent analysis",
                reasoning=intent,
                decision="proceed_with_execution",
                confidence=0.6
            )

    async def _plan_approach(
        self,
        intent: str,
        analysis_step: ReasoningStep,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        """
        Step 2: Plan the approach for execution
        """
        logger.info("Step 2: Planning approach")

        analysis = json.loads(analysis_step.decision) if analysis_step.decision else {}

        prompt = f"""Based on this analysis, plan the execution approach:

Intent: "{intent}"

Analysis:
{json.dumps(analysis, indent=2)}

Create a detailed execution plan:
1. What agents should be involved?
2. What is the optimal sequence of operations?
3. What data needs to be collected?
4. What are the key milestones?
5. What could go wrong at each step?
6. How do we measure success?

Format your response as JSON:
{{
    "agents_needed": ["agent1", "agent2"],
    "execution_sequence": ["step1", "step2", "step3"],
    "data_requirements": ["data1", "data2"],
    "milestones": ["milestone1", "milestone2"],
    "risk_factors": ["risk1", "risk2"],
    "success_criteria": ["criteria1", "criteria2"],
    "estimated_steps": 5,
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_glm_api(prompt)

            return ReasoningStep(
                step_number=2,
                step_type="planning",
                thought="Detailed execution planning",
                reasoning=f"Plan involving {len(response.get('agents_needed', []))} agents",
                alternatives=[
                    f"Steps: {response.get('estimated_steps', 'unknown')}",
                    f"Agents: {', '.join(response.get('agents_needed', [])[:3])}"
                ],
                decision=json.dumps(response),
                confidence=response.get("confidence", 0.7),
                decision_obj=response
            )
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return ReasoningStep(
                step_number=2,
                step_type="planning",
                thought="Basic execution plan",
                reasoning="Standard execution approach",
                decision="standard_execution",
                confidence=0.6,
                decision_obj={"agents_needed": ["controller"], "execution_sequence": ["execute"]}
            )

    async def _consider_alternatives(
        self,
        intent: str,
        planning_step: ReasoningStep,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        """
        Step 3: Consider alternative approaches
        """
        logger.info("Step 3: Considering alternatives")

        plan = json.loads(planning_step.decision) if planning_step.decision else {}

        prompt = f"""Think of alternative approaches to this plan:

Intent: "{intent}"

Current Plan:
{json.dumps(plan, indent=2)}

Consider:
1. What are 2-3 alternative approaches?
2. What are the pros and cons of each?
3. Which approach is optimal and why?
4. What could make an alternative approach better?

Format your response as JSON:
{{
    "alternatives": [
        {{
            "name": "Alternative 1",
            "description": "Description",
            "pros": ["pro1", "pro2"],
            "cons": ["con1", "con2"],
            "suitability": "low|medium|high"
        }}
    ],
    "recommended": "name of recommended approach",
    "reasoning": "why this approach is best",
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_glm_api(prompt)

            alternatives = response.get("alternatives", [])
            alt_descriptions = [alt.get("name", "Unknown") for alt in alternatives]

            return ReasoningStep(
                step_number=3,
                step_type="alternatives",
                thought=f"Evaluated {len(alternatives)} alternative approaches",
                reasoning=response.get("reasoning", ""),
                alternatives=alt_descriptions,
                decision=response.get("recommended", "current_plan"),
                confidence=response.get("confidence", 0.7)
            )
        except Exception as e:
            logger.error(f"Alternative consideration failed: {e}")
            return ReasoningStep(
                step_number=3,
                step_type="alternatives",
                thought="Considered current plan",
                reasoning="Proceeding with planned approach",
                decision=["current_plan"],
                confidence=0.6
            )

    async def _validate_plan(
        self,
        intent: str,
        planning_step: ReasoningStep,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        """
        Step 4: Validate the plan
        """
        logger.info("Step 4: Validating plan")

        plan = planning_step.decision_obj if hasattr(planning_step, 'decision_obj') else {}

        prompt = f"""Validate this execution plan:

Intent: "{intent}"

Plan:
{json.dumps(plan, indent=2)}

Validate:
1. Is this plan feasible?
2. Are all required agents available?
3. Are the data requirements realistic?
4. What are the potential failure points?
5. Is the timeline reasonable?
6. What improvements would you suggest?

Format your response as JSON:
{{
    "feasibility": "high|medium|low",
    "agents_available": true|false,
    "data_requirements_realistic": true|false,
    "failure_points": ["point1", "point2"],
    "timeline_reasonable": true|false,
    "suggested_improvements": ["improvement1", "improvement2"],
    "overall_confidence": 0.0-1.0,
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_glm_api(prompt)

            return ReasoningStep(
                step_number=4,
                step_type="validation",
                thought=f"Plan validation: {response.get('feasibility', 'unknown')} feasibility",
                reasoning=f"Failure points: {len(response.get('failure_points', []))}",
                alternatives=response.get("suggested_improvements", []),
                decision="valid" if response.get("feasibility") == "high" else "needs_refinement",
                confidence=response.get("overall_confidence", 0.7)
            )
        except Exception as e:
            logger.error(f"Plan validation failed: {e}")
            return ReasoningStep(
                step_number=4,
                step_type="validation",
                thought="Basic validation",
                reasoning="Plan appears valid",
                decision="valid",
                confidence=0.6
            )

    async def _refine_plan(
        self,
        intent: str,
        planning_step: ReasoningStep,
        validation_step: ReasoningStep,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningStep:
        """
        Step 5: Refine the plan based on validation
        """
        logger.info("Step 5: Refining plan")

        plan = planning_step.decision_obj if hasattr(planning_step, 'decision_obj') else {}
        validation = json.loads(validation_step.decision) if validation_step.decision else {}

        prompt = f"""Refine this execution plan based on validation feedback:

Intent: "{intent}"

Original Plan:
{json.dumps(plan, indent=2)}

Validation Feedback:
{json.dumps(validation, indent=2)}

Create a refined plan that addresses the validation concerns:
1. How do we address the failure points?
2. How do we incorporate the suggested improvements?
3. What is the refined execution sequence?
4. What additional safeguards are needed?

Format your response as JSON:
{{
    "refined_plan": {{
        "agents_needed": ["agent1", "agent2"],
        "execution_sequence": ["step1", "step2"],
        "data_requirements": ["data1", "data2"],
        "safeguards": ["safeguard1", "safeguard2"],
        "improvements_applied": ["improvement1", "improvement2"]
    }},
    "refinement_summary": "summary of changes",
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._call_glm_api(prompt)

            refined_plan = response.get("refined_plan", {})

            return ReasoningStep(
                step_number=5,
                step_type="refinement",
                thought=response.get("refinement_summary", "Plan refined"),
                reasoning=f"Applied {len(refined_plan.get('improvements_applied', []))} improvements",
                alternatives=refined_plan.get("safeguards", []),
                decision=json.dumps(refined_plan),
                confidence=response.get("confidence", 0.7),
                decision_obj=refined_plan
            )
        except Exception as e:
            logger.error(f"Plan refinement failed: {e}")
            return planning_step  # Return original plan if refinement fails

    async def _estimate_execution_time(self, reasoning_chain: ReasoningChain) -> int:
        """Estimate execution time based on reasoning"""
        try:
            plan = reasoning_chain.final_plan
            if isinstance(plan, dict):
                steps = len(plan.get("execution_sequence", []))
                agents = len(plan.get("agents_needed", []))
                complexity = reasoning_chain.steps[0].decision if reasoning_chain.steps else {}

                base_time = 30  # 30 seconds base
                step_multiplier = steps * 10
                agent_multiplier = agents * 5

                return base_time + step_multiplier + agent_multiplier
        except:
            pass
        return 60  # Default 1 minute

    async def _call_glm_api(self, prompt: str) -> Dict[str, Any]:
        """Call GLM API for reasoning"""
        import httpx

        if not self.glm_api_key:
            logger.warning("GLM API key not configured, using mock response")
            return {"confidence": 0.7}

        try:
            headers = {
                "Authorization": f"Bearer {self.glm_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a reasoning AI. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.glm_api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    response_data = response.json()
                    content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                    # Try to parse JSON from response
                    try:
                        # Extract JSON from markdown code blocks if present
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()

                        return json.loads(content)
                    except:
                        logger.warning("Failed to parse JSON from GLM response")
                        return {"confidence": 0.6, "raw_response": content}
                else:
                    logger.error(f"GLM API error: {response.status_code}")
                    return {"confidence": 0.5}

        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            return {"confidence": 0.5}

    async def _store_reasoning_chain(self, chain: ReasoningChain):
        """Store reasoning chain in Redis"""
        try:
            await self.redis.client.set(
                f"reasoning:{chain.task_id}",
                json.dumps(chain.dict(), default=str),
                ex=3600  # Expire after 1 hour
            )
            logger.info(f"Stored reasoning chain for {chain.task_id}")
        except Exception as e:
            logger.error(f"Failed to store reasoning chain: {e}")

    async def get_reasoning_chain(self, task_id: str) -> Optional[ReasoningChain]:
        """Retrieve reasoning chain for a task"""
        try:
            data = await self.redis.client.get(f"reasoning:{task_id}")
            if data:
                chain_dict = json.loads(data)
                return ReasoningChain(**chain_dict)
        except Exception as e:
            logger.error(f"Failed to retrieve reasoning chain: {e}")
        return None
