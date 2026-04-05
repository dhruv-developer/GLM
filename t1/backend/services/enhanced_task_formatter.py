"""
Enhanced Task Completion Formatter - Beautiful User-Friendly Display
Creates impressive, professional summaries that look like premium AI results
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

class EnhancedTaskFormatter:
    """Enhanced formatter for creating beautiful, user-friendly task summaries"""
    
    def __init__(self):
        self.success_templates = [
            "🎉 Task completed successfully with exceptional results!",
            "✨ Your request has been processed with outstanding accuracy!",
            "🚀 Mission accomplished! Here are your comprehensive results:",
            "⭐ Excellent! Your task has been completed with precision:",
            "🎯 Perfect execution! Here's what we achieved for you:"
        ]
        
        self.result_headers = {
            "web_search": "🔍 Search Results",
            "code_generation": "💻 Generated Code", 
            "communication": "📧 Communication Results",
            "general": "📋 Task Results"
        }

    def format_enhanced_summary(self, execution_data: Dict[str, Any]) -> str:
        """Create an enhanced, user-friendly summary"""
        
        status = execution_data.get("status", "unknown")
        intent = execution_data.get("intent", "No intent provided")
        execution_id = execution_data.get("execution_id", "Unknown")
        
        # Choose a success template
        if status == "completed":
            header = "🎉 Task Completed Successfully!"
            subheader = "Here are your comprehensive results:"
        elif status == "failed":
            header = "❌ Task Execution Failed"
            subheader = "We encountered some issues:"
        else:
            header = "⏳ Task in Progress"
            subheader = "Your task is being processed..."
        
        lines = [
            "=" * 60,
            f"{header}",
            "=" * 60,
            "",
            f"📝 **Original Request:** {intent}",
            f"🆔 **Task ID:** {execution_id[:8]}...",
            f"⏰ **Status:** {status.title()}",
            "",
            f"{subheader}",
            ""
        ]
        
        # Add results if available
        result = execution_data.get("result", {})
        if result and "tasks" in result:
            lines.extend(self._format_enhanced_results(result["tasks"]))
        
        # Add execution summary
        lines.extend(self._format_execution_summary(execution_data))
        
        # Add next steps
        if status == "completed":
            lines.extend(self._format_next_steps(execution_data))
        
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def _format_enhanced_results(self, tasks: Dict[str, Any]) -> List[str]:
        """Format task results in an enhanced, user-friendly way"""
        lines = []
        
        # Group results by agent type
        agent_results = {}
        for task_id, task_info in tasks.items():
            agent = task_info.get("agent", "unknown")
            if agent not in agent_results:
                agent_results[agent] = []
            agent_results[agent].append(task_info)
        
        # Display each agent's results beautifully
        for agent, results in agent_results.items():
            header = self.result_headers.get(agent, f"📋 {agent.title()} Results")
            lines.append(f"{header}")
            lines.append("-" * len(header))
            
            for result in results:
                output = result.get("output", {})
                
                if agent == "web_search":
                    lines.extend(self._format_search_results_enhanced(output))
                elif agent == "code_writer":
                    lines.extend(self._format_code_results_enhanced(output))
                elif agent == "controller":
                    lines.extend(self._format_controller_results_enhanced(output))
                else:
                    lines.extend(self._format_general_results_enhanced(output))
            
            lines.append("")
        
        return lines

    def _format_search_results_enhanced(self, output: Dict[str, Any]) -> List[str]:
        """Format search results with enhanced display"""
        lines = []
        
        results = output.get("results", [])
        result_count = output.get("result_count", 0)
        query = output.get("query", "")
        source = output.get("source", "")
        execution_time = output.get("execution_time", 0)
        
        if result_count > 0:
            lines.append(f"🔍 **Search Query:** {query}")
            lines.append(f"📊 **Results Found:** {result_count} sources")
            lines.append(f"⚡ **Search Time:** {execution_time:.2f} seconds")
            lines.append(f"🌐 **Source:** {source.replace('_', ' ').title()}")
            lines.append("")
            
            lines.append("**🌟 Top Results:**")
            for i, result in enumerate(results[:5], 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                snippet = result.get("snippet", "")
                
                lines.append(f"{i}. **{title}**")
                lines.append(f"   🔗 {url}")
                if snippet:
                    lines.append(f"   📝 {snippet}")
                lines.append("")
        else:
            lines.append("🔍 **Search Query:** {query}")
            lines.append("❌ No results found. Try refining your search terms.")
        
        return lines

    def _format_code_results_enhanced(self, output: Dict[str, Any]) -> List[str]:
        """Format code generation results with enhanced display"""
        lines = []
        
        code = output.get("code", "")
        language = output.get("language", "python")
        description = output.get("description", "")
        
        if code:
            lines.append(f"💻 **Generated Code:** {language.title()}")
            lines.append(f"📝 **Description:** {description}")
            lines.append("")
            lines.append("**🚀 Generated Solution:**")
            lines.append("```" + language)
            lines.append(code)
            lines.append("```")
            lines.append("")
            lines.append(f"📏 **Code Length:** {len(code)} characters")
            lines.append(f"💾 **Ready to download:** Yes")
        else:
            lines.append("❌ No code was generated.")
        
        return lines

    def _format_controller_results_enhanced(self, output: Dict[str, Any]) -> List[str]:
        """Format controller results with enhanced display"""
        lines = []
        
        action = output.get("action", "")
        message = output.get("message", "")
        parameters = output.get("parameters", {})
        
        if action:
            lines.append(f"🎯 **Action:** {action.replace('_', ' ').title()}")
            lines.append(f"📝 **Message:** {message}")
            
            if parameters:
                lines.append("")
                lines.append("**🔧 Parameters Processed:**")
                for key, value in parameters.items():
                    lines.append(f"   • {key.title()}: {value}")
        else:
            lines.append("❌ No controller action was performed.")
        
        return lines

    def _format_general_results_enhanced(self, output: Dict[str, Any]) -> List[str]:
        """Format general results with enhanced display"""
        lines = []
        
        if output:
            lines.append("📋 **Task Results:**")
            for key, value in output.items():
                if key != "timestamp":
                    lines.append(f"   • {key.title()}: {value}")
        else:
            lines.append("❌ No results available.")
        
        return lines

    def _format_execution_summary(self, execution_data: Dict[str, Any]) -> List[str]:
        """Format execution summary with enhanced display"""
        lines = []
        
        lines.append("📊 **Execution Summary:**")
        lines.append("-" * 20)
        
        completed = execution_data.get("completed_tasks", 0)
        total = execution_data.get("total_tasks", 0)
        progress = execution_data.get("progress", 0)
        
        lines.append(f"✅ **Tasks Completed:** {completed}/{total}")
        lines.append(f"📈 **Progress:** {int(progress * 100)}%")
        
        if completed == total and total > 0:
            lines.append("🎉 **Status:** All tasks completed successfully!")
        elif completed > 0:
            lines.append(f"⏳ **Status:** {completed} of {total} tasks completed")
        else:
            lines.append("⏳ **Status:** Task processing in progress...")
        
        return lines

    def _format_next_steps(self, execution_data: Dict[str, Any]) -> List[str]:
        """Format next steps with enhanced display"""
        lines = []
        
        lines.append("🎯 **Next Steps:**")
        lines.append("-" * 15)
        
        # Check what actions are available
        has_code = execution_data.get("generated_code")
        has_download = execution_data.get("download_filename")
        has_results = execution_data.get("result", {}).get("tasks")
        
        if has_code:
            lines.append("📥 **Download Code:** Use the download button to save your generated code")
        
        if has_results:
            lines.append("🔍 **Review Results:** Check the detailed results above")
            lines.append("💾 **Save Progress:** Your results are saved for future reference")
        
        lines.append("🔄 **Create New Task:** Start another task when ready")
        lines.append("📧 **Share Results:** Share your success with others!")
        
        return lines

    def format_quick_summary_enhanced(self, execution_data: Dict[str, Any]) -> str:
        """Format a quick, impressive one-line summary"""
        
        status = execution_data.get("status", "unknown")
        intent = execution_data.get("intent", "No intent")
        completed = execution_data.get("completed_tasks", 0)
        total = execution_data.get("total_tasks", 0)
        
        if status == "completed" and completed == total:
            return f"✅ Successfully completed: {intent[:50]}{'...' if len(intent) > 50 else ''}"
        elif status == "failed":
            return f"❌ Task failed: {intent[:50]}{'...' if len(intent) > 50 else ''}"
        else:
            return f"⏳ Processing: {intent[:50]}{'...' if len(intent) > 50 else ''}"
