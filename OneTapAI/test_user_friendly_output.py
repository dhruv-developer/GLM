#!/usr/bin/env python3
"""
Test script to demonstrate user-friendly task completion output
"""

import asyncio
import json
from backend.services.task_completion_formatter import TaskCompletionFormatter

def test_completed_task():
    """Test formatting a completed task"""
    formatter = TaskCompletionFormatter()
    
    # Sample completed task data
    task_data = {
        "execution_id": "2a1b365e-4014-4588-9933-74896e3544ad",
        "status": "completed",
        "intent": "Create a Python web scraper to extract product prices from Amazon",
        "progress": 1.0,
        "completed_tasks": 3,
        "total_tasks": 3,
        "result": {
            "code": """import requests
from bs4 import BeautifulSoup
import json

def scrape_amazon_prices(url):
    '''Scrape product prices from Amazon'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract price
    price_element = soup.find('span', class_='a-price-whole')
    if price_element:
        price = price_element.text.strip()
        return {'price': price, 'currency': '$'}
    
    return None

if __name__ == "__main__":
    url = "https://www.amazon.com/dp/B08N5WRWNW"
    result = scrape_amazon_prices(url)
    print(json.dumps(result, indent=2))""",
            "language": "python",
            "filename": "amazon_scraper.py",
            "lines": 25
        },
        "logs": [
            {
                "log_id": "log1",
                "execution_id": "2a1b365e-4014-4588-9933-74896e3544ad",
                "level": "INFO",
                "message": "Task execution started",
                "timestamp": "2026-04-05T00:45:00.000Z"
            },
            {
                "log_id": "log2",
                "execution_id": "2a1b365e-4014-4588-9933-74896e3544ad",
                "level": "INFO",
                "message": "Code generation completed successfully",
                "timestamp": "2026-04-05T00:45:15.000Z"
            },
            {
                "log_id": "log3",
                "execution_id": "2a1b365e-4014-4588-9933-74896e3544ad",
                "level": "INFO",
                "message": "Task execution completed",
                "timestamp": "2026-04-05T00:45:30.000Z"
            }
        ]
    }
    
    print("🎯 COMPLETED TASK EXAMPLE")
    print("=" * 60)
    print()
    
    # Format full summary
    summary = formatter.format_completion_summary(task_data)
    print(summary)
    
    print("\n" + "=" * 60)
    print("📝 QUICK SUMMARY")
    print("=" * 60)
    print()
    quick = formatter.format_quick_summary(task_data)
    print(quick)

def test_failed_task():
    """Test formatting a failed task"""
    formatter = TaskCompletionFormatter()
    
    # Sample failed task data
    task_data = {
        "execution_id": "3c2d476f-5125-5699-0044-85997f4655be",
        "status": "failed",
        "intent": "Send email to john@example.com with project update",
        "progress": 0.3,
        "completed_tasks": 1,
        "total_tasks": 3,
        "error": "SMTP authentication failed: Invalid username or password",
        "logs": [
            {
                "log_id": "log1",
                "execution_id": "3c2d476f-5125-5699-0044-85997f4655be",
                "level": "INFO",
                "message": "Task execution started",
                "timestamp": "2026-04-05T01:15:00.000Z"
            },
            {
                "log_id": "log2",
                "execution_id": "3c2d476f-5125-5699-0044-85997f4655be",
                "level": "ERROR",
                "message": "SMTP connection failed: Invalid credentials",
                "timestamp": "2026-04-05T01:15:10.000Z"
            },
            {
                "log_id": "log3",
                "execution_id": "3c2d476f-5125-5699-0044-85997f4655be",
                "level": "ERROR",
                "message": "Task execution failed: SMTP authentication failed",
                "timestamp": "2026-04-05T01:15:12.000Z"
            }
        ]
    }
    
    print("\n🚨 FAILED TASK EXAMPLE")
    print("=" * 60)
    print()
    
    # Format full summary
    summary = formatter.format_completion_summary(task_data)
    print(summary)
    
    print("\n" + "=" * 60)
    print("📝 QUICK SUMMARY")
    print("=" * 60)
    print()
    quick = formatter.format_quick_summary(task_data)
    print(quick)

def test_search_task():
    """Test formatting a web search task"""
    formatter = TaskCompletionFormatter()
    
    # Sample search task data
    task_data = {
        "execution_id": "4d3e587g-6236-6700-1155-96018g5766cf",
        "status": "completed",
        "intent": "Search for Python async programming best practices",
        "progress": 1.0,
        "completed_tasks": 2,
        "total_tasks": 2,
        "result": {
            "query": "Python async programming best practices",
            "results": [
                {
                    "title": "Python Async Await Best Practices",
                    "url": "https://realpython.com/async-io-python/",
                    "snippet": "Learn how to use async/await in Python effectively with these best practices and examples.",
                    "source": "duckduckgo"
                },
                {
                    "title": "Asyncio in Python - Complete Guide",
                    "url": "https://docs.python.org/3/library/asyncio.html",
                    "snippet": "Official Python documentation for asyncio, including best practices and examples.",
                    "source": "duckduckgo"
                },
                {
                    "title": "Common Async Programming Mistakes",
                    "url": "https://medium.com/python-features/async-mistakes",
                    "snippet": "Avoid these common mistakes when writing async code in Python for better performance.",
                    "source": "duckduckgo"
                }
            ]
        },
        "logs": [
            {
                "log_id": "log1",
                "execution_id": "4d3e587g-6236-6700-1155-96018g5766cf",
                "level": "INFO",
                "message": "Web search started for: Python async programming best practices",
                "timestamp": "2026-04-05T02:30:00.000Z"
            },
            {
                "log_id": "log2",
                "execution_id": "4d3e587g-6236-6700-1155-96018g5766cf",
                "level": "INFO",
                "message": "Found 15 search results",
                "timestamp": "2026-04-05T02:30:05.000Z"
            },
            {
                "log_id": "log3",
                "execution_id": "4d3e587g-6236-6700-1155-96018g5766cf",
                "level": "INFO",
                "message": "Web search completed successfully",
                "timestamp": "2026-04-05T02:30:08.000Z"
            }
        ]
    }
    
    print("\n🔍 SEARCH TASK EXAMPLE")
    print("=" * 60)
    print()
    
    # Format full summary
    summary = formatter.format_completion_summary(task_data)
    print(summary)
    
    print("\n" + "=" * 60)
    print("📝 QUICK SUMMARY")
    print("=" * 60)
    print()
    quick = formatter.format_quick_summary(task_data)
    print(quick)

def test_in_progress_task():
    """Test formatting an in-progress task"""
    formatter = TaskCompletionFormatter()
    
    # Sample in-progress task data
    task_data = {
        "execution_id": "5e4f698h-7347-7811-2266-07129h6877dg",
        "status": "running",
        "intent": "Generate a complete React dashboard application",
        "progress": 0.6,
        "completed_tasks": 3,
        "total_tasks": 5,
        "logs": [
            {
                "log_id": "log1",
                "execution_id": "5e4f698h-7347-7811-2266-07129h6877dg",
                "level": "INFO",
                "message": "Task execution started",
                "timestamp": "2026-04-05T03:00:00.000Z"
            },
            {
                "log_id": "log2",
                "execution_id": "5e4f698h-7347-7811-2266-07129h6877dg",
                "level": "INFO",
                "message": "Component structure generated",
                "timestamp": "2026-04-05T03:02:00.000Z"
            },
            {
                "log_id": "log3",
                "execution_id": "5e4f698h-7347-7811-2266-07129h6877dg",
                "level": "INFO",
                "message": "Main dashboard component created",
                "timestamp": "2026-04-05T03:05:00.000Z"
            }
        ]
    }
    
    print("\n🔄 IN-PROGRESS TASK EXAMPLE")
    print("=" * 60)
    print()
    
    # Format full summary
    summary = formatter.format_completion_summary(task_data)
    print(summary)
    
    print("\n" + "=" * 60)
    print("📝 QUICK SUMMARY")
    print("=" * 60)
    print()
    quick = formatter.format_quick_summary(task_data)
    print(quick)

def main():
    """Run all examples"""
    print("🎯 ZIEL-MAS USER-FRIENDLY OUTPUT DEMONSTRATION")
    print("=" * 60)
    print("This script shows how task results are formatted in a user-friendly way")
    print()
    
    # Test different task types
    test_completed_task()
    test_failed_task()
    test_search_task()
    test_in_progress_task()
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print()
    print("💡 Key Features:")
    print("   ✅ Clear, readable summaries with emojis")
    print("   ✅ Task-specific formatting (code, search, etc.)")
    print("   ✅ Progress indicators and status updates")
    print("   ✅ Error messages with helpful suggestions")
    print("   ✅ Execution timeline with key events")
    print("   ✅ Quick one-line summaries for notifications")
    print()
    print("🚀 This makes ZIEL-MAS results much more user-friendly!")

if __name__ == "__main__":
    main()
