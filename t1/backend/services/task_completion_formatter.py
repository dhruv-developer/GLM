"""
Task Completion Formatter for ZIEL-MAS
Formats task results in user-friendly text format
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

class TaskCompletionFormatter:
    """Formats task execution results into user-friendly text"""
    
    def __init__(self):
        self.emoji_map = {
            "completed": "✅",
            "failed": "❌", 
            "cancelled": "⏹️",
            "running": "🔄",
            "pending": "⏳"
        }
        
        self.task_type_emojis = {
            "web_search": "🔍",
            "code_generation": "💻",
            "communication": "📧",
            "scheduling": "⏰",
            "web_automation": "🤖",
            "data_processing": "📊",
            "api_call": "🔌",
            "booking": "📅",
            "general": "🎯"
        }

    def format_completion_summary(self, execution_data: Dict[str, Any]) -> str:
        """Format a comprehensive task completion summary"""
        
        execution_id = execution_data.get("execution_id", "Unknown")
        status = execution_data.get("status", "unknown")
        intent = execution_data.get("intent", "No intent provided")
        result = execution_data.get("result", {})
        error = execution_data.get("error", "")
        progress = execution_data.get("progress", 0.0)
        completed_tasks = execution_data.get("completed_tasks", 0)
        total_tasks = execution_data.get("total_tasks", 0)
        logs = execution_data.get("logs", [])
        
        # Start building the summary
        summary_lines = []
        
        # Header
        summary_lines.append("🎯 " + "=" * 60)
        summary_lines.append("🎯   ZIEL-MAS TASK COMPLETION SUMMARY")
        summary_lines.append("🎯 " + "=" * 60)
        summary_lines.append("")
        
        # Task Overview
        summary_lines.append("📋 TASK OVERVIEW")
        summary_lines.append("-" * 30)
        summary_lines.append(f"🆔 Task ID: {execution_id[:8]}...")
        summary_lines.append(f"📝 Intent: {intent}")
        summary_lines.append(f"📊 Status: {self.emoji_map.get(status, '❓')} {status.title()}")
        summary_lines.append(f"⏱️  Progress: {int(progress * 100)}% ({completed_tasks}/{total_tasks} tasks)")
        summary_lines.append("")
        
        # Status-specific content
        if status == "completed":
            summary_lines.extend(self._format_completed_section(result, total_tasks))
        elif status == "failed":
            summary_lines.extend(self._format_failed_section(error, logs))
        elif status == "cancelled":
            summary_lines.extend(self._format_cancelled_section(logs))
        else:
            summary_lines.extend(self._format_in_progress_section(progress, completed_tasks, total_tasks))
        
        # Execution Timeline
        if logs:
            summary_lines.append("")
            summary_lines.append("📅 EXECUTION TIMELINE")
            summary_lines.append("-" * 30)
            summary_lines.extend(self._format_timeline(logs))
        
        # Footer
        summary_lines.append("")
        summary_lines.append("🎯 " + "=" * 60)
        summary_lines.append(f"🎯   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append("🎯 " + "=" * 60)
        
        return "\n".join(summary_lines)

    def _format_completed_section(self, result: Dict[str, Any], total_tasks: int) -> List[str]:
        """Format completed task section"""
        lines = []
        
        lines.append("🎉 TASK COMPLETED SUCCESSFULLY!")
        lines.append("")
        
        # Results summary
        if result:
            lines.append("📊 RESULTS SUMMARY")
            lines.append("-" * 20)
            
            # Handle different result types
            if "code" in result:
                lines.extend(self._format_code_result(result))
            elif "results" in result:
                lines.extend(self._format_search_result(result))
            elif "files" in result:
                lines.extend(self._format_project_result(result))
            elif "output" in result:
                lines.extend(self._format_general_result(result))
            else:
                lines.append("📦 Task completed successfully")
                lines.append(f"📋 Result type: {type(result).__name__}")
        
        lines.append(f"✨ Total tasks processed: {total_tasks}")
        
        return lines

    def _format_failed_section(self, error: str, logs: List[Dict[str, Any]]) -> List[str]:
        """Format failed task section"""
        lines = []
        
        lines.append("❌ TASK FAILED")
        lines.append("")
        
        if error:
            lines.append("🚨 ERROR DETAILS")
            lines.append("-" * 20)
            lines.append(f"❌ {error}")
            lines.append("")
        
        # Find the error log
        error_logs = [log for log in logs if log.get("level") == "ERROR"]
        if error_logs:
            lines.append("📋 ERROR LOGS")
            lines.append("-" * 15)
            for log in error_logs[-3:]:  # Show last 3 error logs
                timestamp = log.get("timestamp", "")
                message = log.get("message", "")
                lines.append(f"⏰ {timestamp}")
                lines.append(f"❌ {message}")
                lines.append("")
        
        # Suggestions
        lines.append("💡 SUGGESTIONS")
        lines.append("-" * 15)
        lines.append("🔧 Check if all required services are running")
        lines.append("🔧 Verify API keys are configured")
        lines.append("🔧 Check network connectivity")
        lines.append("🔧 Review task parameters")
        
        return lines

    def _format_cancelled_section(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Format cancelled task section"""
        lines = []
        
        lines.append("⏹️ TASK CANCELLED")
        lines.append("")
        lines.append("📋 The task was cancelled by user or system.")
        lines.append("")
        
        # Show cancellation reason if available
        cancel_logs = [log for log in logs if "cancel" in log.get("message", "").lower()]
        if cancel_logs:
            lines.append("📋 CANCELLATION DETAILS")
            lines.append("-" * 25)
            for log in cancel_logs[-1:]:
                lines.append(f"📝 {log.get('message', 'No cancellation reason')}")
        
        return lines

    def _format_in_progress_section(self, progress: float, completed: int, total: int) -> List[str]:
        """Format in-progress task section"""
        lines = []
        
        lines.append("🔄 TASK IN PROGRESS")
        lines.append("")
        
        # Progress bar
        progress_bars = int(progress * 20)
        bars = "█" * progress_bars + "░" * (20 - progress_bars)
        lines.append(f"📊 Progress: [{bars}] {int(progress * 100)}%")
        lines.append(f"📋 Tasks completed: {completed}/{total}")
        lines.append("")
        lines.append("⏳ Task is still running...")
        lines.append("💡 Check back later for final results")
        
        return lines

    def _format_code_result(self, result: Dict[str, Any]) -> List[str]:
        """Format code generation result"""
        lines = []
        
        code = result.get("code", "")
        language = result.get("language", "unknown")
        filename = result.get("filename", "generated_code")
        lines_count = result.get("lines", 0)
        
        lines.append("💻 CODE GENERATED")
        lines.append("-" * 20)
        lines.append(f"📁 Filename: {filename}")
        lines.append(f"🔤 Language: {language}")
        lines.append(f"📏 Lines: {lines_count}")
        
        if code:
            # Show first few lines of code
            code_lines = code.split('\n')
            preview_lines = code_lines[:5]
            lines.append("")
            lines.append("📄 CODE PREVIEW:")
            lines.append("-" * 15)
            for i, line in enumerate(preview_lines, 1):
                lines.append(f"   {i:2d}: {line}")
            
            if len(code_lines) > 5:
                lines.append("   ...")
                lines.append(f"   ({len(code_lines) - 5} more lines)")
        
        return lines

    def _format_search_result(self, result: Dict[str, Any]) -> List[str]:
        """Format web search result"""
        lines = []
        
        search_results = result.get("results", [])
        query = result.get("query", "unknown query")
        
        lines.append("🔍 SEARCH RESULTS")
        lines.append("-" * 20)
        lines.append(f"🔍 Query: {query}")
        lines.append(f"📊 Results found: {len(search_results)}")
        
        if search_results:
            lines.append("")
            lines.append("📋 TOP RESULTS:")
            lines.append("-" * 15)
            for i, item in enumerate(search_results[:3], 1):
                title = item.get("title", "No title")
                url = item.get("url", "No URL")
                snippet = item.get("snippet", "No description")[:100]
                
                lines.append(f"{i}. 📄 {title}")
                lines.append(f"   🔗 {url}")
                lines.append(f"   📝 {snippet}...")
                lines.append("")
        
        return lines

    def _format_project_result(self, result: Dict[str, Any]) -> List[str]:
        """Format project generation result"""
        lines = []
        
        files = result.get("files", [])
        project_name = result.get("project_name", "New Project")
        project_type = result.get("project_type", "unknown")
        
        lines.append("📁 PROJECT GENERATED")
        lines.append("-" * 25)
        lines.append(f"📂 Project: {project_name}")
        lines.append(f"🔤 Type: {project_type}")
        lines.append(f"📄 Files created: {len(files)}")
        
        if files:
            lines.append("")
            lines.append("📋 PROJECT STRUCTURE:")
            lines.append("-" * 20)
            for file_info in files[:5]:  # Show first 5 files
                filename = file_info.get("filename", "unknown")
                subdirectory = file_info.get("subdirectory", "")
                if subdirectory:
                    lines.append(f"📁 {subdirectory}/{filename}")
                else:
                    lines.append(f"📄 {filename}")
            
            if len(files) > 5:
                lines.append(f"... and {len(files) - 5} more files")
        
        return lines

    def _format_general_result(self, result: Dict[str, Any]) -> List[str]:
        """Format general task result"""
        lines = []
        
        lines.append("📦 TASK RESULT")
        lines.append("-" * 20)
        
        # Try to extract meaningful information
        if isinstance(result, dict):
            for key, value in result.items():
                if key not in ["execution_id", "timestamp"]:
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    lines.append(f"📋 {key.title()}: {value}")
        else:
            lines.append(f"📋 Result: {str(result)[:200]}...")
        
        return lines

    def _format_timeline(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Format execution timeline"""
        lines = []
        
        # Show key events from logs
        key_events = []
        for log in logs:
            level = log.get("level", "INFO")
            message = log.get("message", "")
            timestamp = log.get("timestamp", "")
            
            if any(keyword in message.lower() for keyword in ["started", "completed", "failed", "created", "executed"]):
                key_events.append((timestamp, level, message))
        
        # Sort by timestamp and show last 10 events
        key_events.sort(key=lambda x: x[0])
        key_events = key_events[-10:]
        
        for timestamp, level, message in key_events:
            emoji = {"INFO": "ℹ️", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
            # Format timestamp to be more readable
            if timestamp:
                try:
                    # Handle if timestamp is already a datetime object
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = timestamp
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    if isinstance(timestamp, str):
                        time_str = timestamp[:8]
                    else:
                        time_str = "???:??"
            else:
                time_str = "???:??"
            
            lines.append(f"{emoji} {time_str} - {message}")
        
        return lines

    def format_quick_summary(self, execution_data: Dict[str, Any]) -> str:
        """Format a quick one-line summary"""
        
        status = execution_data.get("status", "unknown")
        intent = execution_data.get("intent", "No intent")
        execution_id = execution_data.get("execution_id", "Unknown")
        
        emoji = self.emoji_map.get(status, "❓")
        
        # Truncate intent if too long
        if len(intent) > 50:
            intent = intent[:47] + "..."
        
        return f"{emoji} Task {execution_id[:8]}... ({status}): {intent}"

    def format_error_message(self, error: str, execution_id: str = "Unknown") -> str:
        """Format a user-friendly error message"""
        
        lines = []
        lines.append("❌ " + "=" * 50)
        lines.append("❌ TASK EXECUTION ERROR")
        lines.append("❌ " + "=" * 50)
        lines.append("")
        lines.append(f"🆔 Task ID: {execution_id[:8]}...")
        lines.append(f"❌ Error: {error}")
        lines.append("")
        lines.append("💡 What you can do:")
        lines.append("   🔧 Check if the backend server is running")
        lines.append("   🔧 Verify your internet connection")
        lines.append("   🔧 Check if API keys are configured")
        lines.append("   🔧 Try running the task again")
        lines.append("")
        lines.append("❌ " + "=" * 50)
        
        return "\n".join(lines)
