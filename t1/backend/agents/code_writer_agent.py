"""
Code Writer Agent for ZIEL-MAS
Writes complete code files, applications, and projects
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime
import httpx

from backend.agents.base_agent import BaseAgent


class CodeWriterAgent(BaseAgent):
    """
    Code Writer Agent - Writes complete, production-ready code
    Capabilities:
    - Single file generation
    - Multi-file projects
    - Full applications
    - Tests and documentation
    - Multiple languages/frameworks
    - Best practices enforcement
    """

    def __init__(self):
        super().__init__("Code Writer Agent", "code_writer")
        self.glm_api_key = os.getenv("GLM_API_KEY", "")
        self.glm_api_url = os.getenv("GLM_API_URL", "https://api.glm.ai/v1")

        # Supported languages and frameworks
        self.supported_languages = {
            "python": {
                "extensions": [".py"],
                "package_manager": "pip",
                "default_framework": "flask"
            },
            "javascript": {
                "extensions": [".js", ".jsx"],
                "package_manager": "npm",
                "default_framework": "express"
            },
            "typescript": {
                "extensions": [".ts", ".tsx"],
                "package_manager": "npm",
                "default_framework": "nextjs"
            },
            "java": {
                "extensions": [".java"],
                "package_manager": "maven",
                "default_framework": "spring"
            },
            "go": {
                "extensions": [".go"],
                "package_manager": "go",
                "default_framework": "gin"
            },
            "rust": {
                "extensions": [".rs"],
                "package_manager": "cargo",
                "default_framework": "actix"
            },
            "cpp": {
                "extensions": [".cpp", ".hpp"],
                "package_manager": "conan",
                "default_framework": "none"
            }
        }

        # Code templates
        self.code_templates = {
            "api": {
                "python": "flask_api_template",
                "typescript": "express_api_template",
                "go": "gin_api_template"
            },
            "webapp": {
                "typescript": "nextjs_template",
                "javascript": "react_template"
            },
            "cli": {
                "python": "click_template",
                "go": "cobra_template",
                "rust": "clap_template"
            },
            "library": {
                "python": "package_template",
                "typescript": "npm_package_template",
                "rust": "cargo_lib_template"
            }
        }

        logger.info("Code Writer Agent initialized with multi-language support")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a code writing action"""
        try:
            if action == "write_file":
                return await self._write_file(parameters)
            elif action == "write_project":
                return await self._write_project(parameters)
            elif action == "write_application":
                return await self._write_application(parameters)
            elif action == "write_tests":
                return await self._write_tests(parameters)
            elif action == "write_documentation":
                return await self._write_documentation(parameters)
            elif action == "refactor_code":
                return await self._refactor_code(parameters)
            elif action == "add_feature":
                return await self._add_feature(parameters)
            elif action == "fix_bug":
                return await self._fix_bug(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            logger.error(f"Code writing failed: {e}")
            return await self.handle_error(action, e)

    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a single code file
        Parameters:
        - description: What the file should do
        - language: Programming language
        - filename: Name of the file
        - framework: Framework to use (optional)
        - requirements: Additional requirements (optional)
        """
        description = params.get("description")
        language = params.get("language", "python")
        filename = params.get("filename", f"main.{self._get_extension(language)}")
        framework = params.get("framework")
        requirements = params.get("requirements", [])

        if not description:
            return self._create_response(
                status="failed",
                error="File description is required"
            )

        logger.info(f"Writing {filename} in {language}")

        try:
            # Generate code using GLM
            code_content = await self._generate_code(
                description=description,
                language=language,
                framework=framework,
                requirements=requirements,
                context=params.get("context", {})
            )

            # If output_path is provided, save the file
            output_path = params.get("output_path")
            file_path = None

            if output_path:
                file_path = await self._save_file(
                    content=code_content,
                    path=output_path,
                    filename=filename
                )

            return self._create_response(
                status="completed",
                output={
                    "code": code_content,
                    "filename": filename,
                    "language": language,
                    "file_path": file_path,
                    "lines": code_content.count('\n') + 1,
                    "size_bytes": len(code_content.encode()),
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"File writing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _write_project(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a multi-file project
        Parameters:
        - description: Project description
        - language: Main programming language
        - project_type: Type of project (api, webapp, cli, library)
        - files: List of files to create (optional)
        - framework: Framework to use
        """
        description = params.get("description")
        language = params.get("language", "python")
        project_type = params.get("project_type", "api")
        framework = params.get("framework")
        project_name = params.get("project_name", "my_project")

        if not description:
            return self._create_response(
                status="failed",
                error="Project description is required"
            )

        logger.info(f"Writing {project_type} project in {language}")

        try:
            # Generate project structure
            project_structure = await self._generate_project_structure(
                description=description,
                language=language,
                project_type=project_type,
                framework=framework,
                project_name=project_name,
                context=params.get("context", {})
            )

            # Write files if output path is provided
            output_path = params.get("output_path")
            created_files = []

            if output_path:
                for file_info in project_structure.get("files", []):
                    file_path = await self._save_file(
                        content=file_info["content"],
                        path=output_path,
                        filename=file_info["filename"],
                        subdirectory=file_info.get("subdirectory", "")
                    )
                    created_files.append(file_path)

            return self._create_response(
                status="completed",
                output={
                    "project_name": project_name,
                    "project_type": project_type,
                    "language": language,
                    "framework": framework,
                    "structure": project_structure,
                    "files_created": created_files,
                    "total_files": len(project_structure.get("files", [])),
                    "setup_commands": project_structure.get("setup_commands", []),
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Project writing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _write_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a complete application with all components
        """
        description = params.get("description")
        app_type = params.get("app_type", "web")
        language = params.get("language", "typescript")
        framework = params.get("framework")

        if not description:
            return self._create_response(
                status="failed",
                error="Application description is required"
            )

        logger.info(f"Writing {app_type} application")

        try:
            # Generate complete application
            application = await self._generate_application(
                description=description,
                app_type=app_type,
                language=language,
                framework=framework,
                context=params.get("context", {})
            )

            # Write files if output path provided
            output_path = params.get("output_path")
            created_files = []

            if output_path:
                for file_info in application.get("files", []):
                    file_path = await self._save_file(
                        content=file_info["content"],
                        path=output_path,
                        filename=file_info["filename"],
                        subdirectory=file_info.get("subdirectory", "")
                    )
                    created_files.append(file_path)

            return self._create_response(
                status="completed",
                output={
                    "app_name": application.get("app_name", "my_app"),
                    "app_type": app_type,
                    "language": language,
                    "framework": framework,
                    "application": application,
                    "files_created": created_files,
                    "run_commands": application.get("run_commands", []),
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Application writing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _write_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write tests for existing code"""
        code = params.get("code")
        code_path = params.get("code_path")
        language = params.get("language", "python")
        test_framework = params.get("test_framework")

        if not code and not code_path:
            return self._create_response(
                status="failed",
                error="Either code or code_path is required"
            )

        logger.info("Writing tests")

        try:
            # Read code from file if path provided
            if code_path:
                with open(code_path, 'r') as f:
                    code = f.read()

            # Generate tests
            tests = await self._generate_tests(
                code=code,
                language=language,
                test_framework=test_framework
            )

            return self._create_response(
                status="completed",
                output={
                    "tests": tests,
                    "language": language,
                    "test_framework": test_framework,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Test writing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _write_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write documentation for code"""
        code = params.get("code")
        code_path = params.get("code_path")
        doc_type = params.get("doc_type", "readme")

        logger.info("Writing documentation")

        try:
            # Read code from file if path provided
            if code_path:
                with open(code_path, 'r') as f:
                    code = f.read()

            # Generate documentation
            documentation = await self._generate_documentation(
                code=code,
                doc_type=doc_type
            )

            return self._create_response(
                status="completed",
                output={
                    "documentation": documentation,
                    "doc_type": doc_type,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Documentation writing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _refactor_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor existing code"""
        code = params.get("code")
        code_path = params.get("code_path")
        refactor_type = params.get("refactor_type", "improve")

        logger.info(f"Refactoring code: {refactor_type}")

        try:
            # Read code from file if path provided
            if code_path:
                with open(code_path, 'r') as f:
                    code = f.read()

            # Refactor code
            refactored = await self._refactor_code_internal(
                code=code,
                refactor_type=refactor_type
            )

            return self._create_response(
                status="completed",
                output={
                    "original_code": code,
                    "refactored_code": refactored,
                    "changes": self._diff_code(code, refactored),
                    "refactor_type": refactor_type,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _add_feature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a feature to existing code"""
        code = params.get("code")
        code_path = params.get("code_path")
        feature_description = params.get("feature_description")

        if not feature_description:
            return self._create_response(
                status="failed",
                error="Feature description is required"
            )

        logger.info(f"Adding feature: {feature_description}")

        try:
            # Read code from file if path provided
            if code_path:
                with open(code_path, 'r') as f:
                    code = f.read()

            # Add feature
            updated_code = await self._add_feature_internal(
                code=code,
                feature_description=feature_description
            )

            return self._create_response(
                status="completed",
                output={
                    "original_code": code,
                    "updated_code": updated_code,
                    "changes": self._diff_code(code, updated_code),
                    "feature_added": feature_description,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Feature addition failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _fix_bug(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fix a bug in code"""
        code = params.get("code")
        code_path = params.get("code_path")
        bug_description = params.get("bug_description")

        if not bug_description:
            return self._create_response(
                status="failed",
                error="Bug description is required"
            )

        logger.info(f"Fixing bug: {bug_description}")

        try:
            # Read code from file if path provided
            if code_path:
                with open(code_path, 'r') as f:
                    code = f.read()

            # Fix bug
            fixed_code = await self._fix_bug_internal(
                code=code,
                bug_description=bug_description
            )

            return self._create_response(
                status="completed",
                output={
                    "original_code": code,
                    "fixed_code": fixed_code,
                    "changes": self._diff_code(code, fixed_code),
                    "bug_fixed": bug_description,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Bug fixing failed: {e}")
            return self._create_response(
                status="failed",
                error=str(e)
            )

    async def _generate_code(
        self,
        description: str,
        language: str,
        framework: Optional[str],
        requirements: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Generate code using GLM API"""

        prompt = f"""Write complete, production-ready code for:

Description: {description}
Language: {language}
Framework: {framework or 'default for language'}
Requirements: {', '.join(requirements) if requirements else 'none'}
Context: {json.dumps(context, indent=2)}

Requirements for the code:
1. Must be complete and runnable
2. Follow best practices for {language}
3. Include proper error handling
4. Add comments for complex logic
5. Use type hints if applicable
6. Include input validation
7. Handle edge cases
8. Be production-ready

Return ONLY the code, no explanations or markdown."""

        try:
            code = await self._call_glm_api(prompt)
            return self._clean_code_response(code)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Code generation failed: {str(e)}")

    async def _generate_project_structure(
        self,
        description: str,
        language: str,
        project_type: str,
        framework: Optional[str],
        project_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete project structure"""

        prompt = f"""Design and generate a complete {project_type} project:

Description: {description}
Language: {language}
Project Name: {project_name}
Framework: {framework or 'default'}
Context: {json.dumps(context, indent=2)}

Create:
1. Project structure with all necessary files
2. Main application code
3. Configuration files
4. Dependencies
5. Documentation
6. Tests (basic structure)
7. Setup/run instructions

Return as JSON:
{{
    "files": [
        {{
            "filename": "name",
            "subdirectory": "path/if/any",
            "content": "complete file content"
        }}
    ],
    "setup_commands": ["command1", "command2"],
    "dependencies": ["package1", "package2"],
    "description": "project description"
}}"""

        try:
            response = await self._call_glm_api(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Project structure generation failed: {str(e)}")

    async def _generate_application(
        self,
        description: str,
        app_type: str,
        language: str,
        framework: Optional[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete application"""

        prompt = f"""Create a complete {app_type} application:

Description: {description}
Type: {app_type}
Language: {language}
Framework: {framework or 'default'}

Generate:
1. Complete source code
2. Configuration
3. Styling (if applicable)
4. Tests
5. Documentation
6. Deployment instructions

Return as JSON:
{{
    "app_name": "name",
    "files": [
        {{
            "filename": "name",
            "subdirectory": "path",
            "content": "code"
        }}
    ],
    "run_commands": ["cmd1", "cmd2"],
    "description": "app description"
}}"""

        try:
            response = await self._call_glm_api(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Application generation failed: {str(e)}")

    async def _generate_tests(
        self,
        code: str,
        language: str,
        test_framework: Optional[str]
    ) -> str:
        """Generate tests for code"""

        prompt = f"""Write comprehensive tests for this code:

Language: {language}
Test Framework: {test_framework or 'default'}
Code:
{code}

Generate tests that:
1. Cover all functions/methods
2. Test edge cases
3. Include positive and negative tests
4. Use proper assertions
5. Are well-organized

Return ONLY the test code."""

        try:
            return await self._call_glm_api(prompt)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Test generation failed: {str(e)}")

    async def _generate_documentation(
        self,
        code: str,
        doc_type: str
    ) -> str:
        """Generate documentation for code"""

        prompt = f"""Write {doc_type} documentation for this code:

Code:
{code}

Create:
1. Clear description
2. Usage examples
3. API documentation (if applicable)
4. Installation instructions
5. Configuration options

Return the documentation in markdown format."""

        try:
            return await self._call_glm_api(prompt)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Documentation generation failed: {str(e)}")

    async def _refactor_code_internal(
        self,
        code: str,
        refactor_type: str
    ) -> str:
        """Refactor code"""
        prompt = f"""Refactor this code to {refactor_type}:

Code:
{code}

Return ONLY the refactored code."""

        try:
            return await self._call_glm_api(prompt)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Code refactoring failed: {str(e)}")

    async def _add_feature_internal(
        self,
        code: str,
        feature_description: str
    ) -> str:
        """Add feature to code"""
        prompt = f"""Add this feature to the code:

Feature: {feature_description}
Code:
{code}

Return ONLY the updated code."""

        try:
            return await self._call_glm_api(prompt)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Feature addition failed: {str(e)}")

    async def _fix_bug_internal(
        self,
        code: str,
        bug_description: str
    ) -> str:
        """Fix bug in code"""
        prompt = f"""Fix this bug in the code:

Bug: {bug_description}
Code:
{code}

Return ONLY the fixed code."""

        try:
            return await self._call_glm_api(prompt)
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise Exception(f"Bug fixing failed: {str(e)}")

    async def _call_glm_api(self, prompt: str) -> str:
        """Call GLM API"""
        if not self.glm_api_key:
            raise Exception("GLM API key not configured")

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
                        "content": "You are an expert programmer. Write clean, production-ready code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.glm_api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    response_data = response.json()
                    return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    raise Exception(f"API error: {response.status_code}")

        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise

    def _clean_code_response(self, code: str) -> str:
        """Clean code response from API"""
        # Remove markdown code blocks
        if "```" in code:
            # Find the content between ```
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    # Remove language identifier if present
                    lines = part.split('\n')
                    if lines and lines[0].startswith(('python', 'javascript', 'typescript', 'java', 'go', 'rust')):
                        lines = lines[1:]
                    return '\n'.join(lines).strip()
        return code.strip()

    def _generate_mock_code(self, description: str, language: str) -> str:
        """Generate mock code for testing"""
        if language == "python":
            return f'''# Mock Python code for: {description}
def main():
    """Main function"""
    print("Implement: {description}")

if __name__ == "__main__":
    main()
'''
        elif language in ["javascript", "typescript"]:
            return f'''// Mock {language} code for: {description}
function main() {{
    console.log("Implement: {description}");
}}

main();
'''
        else:
            return f"# Mock {language} code for: {description}\n# Implement the functionality"

    def _generate_mock_project(self, name: str, language: str, project_type: str) -> Dict[str, Any]:
        """Generate mock project structure"""
        return {
            "files": [
                {
                    "filename": f"main.{self._get_extension(language)}",
                    "subdirectory": "",
                    "content": f"# Main file for {name}\n# Implement {project_type} functionality"
                },
                {
                    "filename": "README.md",
                    "subdirectory": "",
                    "content": f"# {name}\n\nDescription: {project_type} project in {language}\n\n## Setup\n\n## Usage\n\n## License"
                }
            ],
            "setup_commands": [
                f"Install dependencies for {language}"
            ],
            "dependencies": [],
            "description": f"{project_type} project in {language}"
        }

    def _generate_mock_application(self, app_type: str, language: str) -> Dict[str, Any]:
        """Generate mock application"""
        return {
            "app_name": f"mock_{app_type}_app",
            "files": [
                {
                    "filename": f"main.{self._get_extension(language)}",
                    "subdirectory": "src",
                    "content": f"# Main application file\n# Implement {app_type} functionality"
                }
            ],
            "run_commands": [
                f"Run the {app_type} application"
            ],
            "description": f"Mock {app_type} application in {language}"
        }

    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        lang_info = self.supported_languages.get(language, {})
        extensions = lang_info.get("extensions", [".txt"])
        return extensions[0] if extensions else ".txt"

    async def _save_file(
        self,
        content: str,
        path: str,
        filename: str,
        subdirectory: str = ""
    ) -> str:
        """Save file to disk"""
        try:
            full_path = Path(path)
            if subdirectory:
                full_path = full_path / subdirectory
                full_path.mkdir(parents=True, exist_ok=True)

            file_path = full_path / filename
            with open(file_path, 'w') as f:
                f.write(content)

            logger.info(f"Saved file: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return ""

    def _diff_code(self, original: str, updated: str) -> List[str]:
        """Simple diff between original and updated code"""
        original_lines = original.split('\n')
        updated_lines = updated.split('\n')
        changes = []

        for i, (orig, upd) in enumerate(zip(original_lines, updated_lines)):
            if orig != upd:
                changes.append(f"Line {i+1}: '{orig}' -> '{upd}'")

        if len(original_lines) != len(updated_lines):
            changes.append(f"Length changed: {len(original_lines)} -> {len(updated_lines)} lines")

        return changes
