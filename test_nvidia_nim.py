"""
Test script to verify NVIDIA NIM integration with browser-use.

This script tests the ChatNvidiaNIM class to ensure it works correctly
with the browser-use framework.
"""

import asyncio
import os

from dotenv import load_dotenv

from llm_nvidia_nim import ChatNvidiaNIM
from browser_use.llm.messages import SystemMessage, UserMessage

load_dotenv()


async def test_basic_completion():
    """Test basic text completion."""
    print("=" * 60)
    print("Test 1: Basic Text Completion")
    print("=" * 60)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Error: NVIDIA_API_KEY not set in environment")
        return
    
    llm = ChatNvidiaNIM(
        api_key=api_key,
        model="qwen/qwen3-next-80b-a3b-instruct",
        temperature=0.6,
    )
    
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is 2+2? Answer in one sentence."),
    ]
    
    try:
        result = await llm.ainvoke(messages)
        print(f"Response: {result.completion}")
        print(f"Tokens - Prompt: {result.usage.prompt_tokens if result.usage else 'N/A'}, "
              f"Completion: {result.usage.completion_tokens if result.usage else 'N/A'}")
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print()


async def test_structured_output():
    """Test structured output with Pydantic model."""
    print("=" * 60)
    print("Test 2: Structured Output")
    print("=" * 60)
    
    from pydantic import BaseModel, Field
    
    class Person(BaseModel):
        name: str = Field(..., description="Person's name")
        age: int = Field(..., description="Person's age")
        occupation: str = Field(..., description="Person's occupation")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Error: NVIDIA_API_KEY not set in environment")
        return
    
    llm = ChatNvidiaNIM(
        api_key=api_key,
        model="qwen/qwen3-next-80b-a3b-instruct",
        temperature=0.6,
    )
    
    messages = [
        SystemMessage(content="Extract person information from the text."),
        UserMessage(content="John Smith is a 35-year-old software engineer."),
    ]
    
    try:
        result = await llm.ainvoke(messages, output_format=Person)
        person = result.completion
        print(f"Name: {person.name}")
        print(f"Age: {person.age}")
        print(f"Occupation: {person.occupation}")
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print()


async def test_browser_task():
    """Test with a simple browser task."""
    print("=" * 60)
    print("Test 3: Browser Task Simulation")
    print("=" * 60)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Error: NVIDIA_API_KEY not set in environment")
        return
    
    llm = ChatNvidiaNIM(
        api_key=api_key,
        model="qwen/qwen3-next-80b-a3b-instruct",
        temperature=0.6,
    )
    
    messages = [
        SystemMessage(content="""You are a browser automation agent. 
Given a task, you should describe the steps needed to complete it."""),
        UserMessage(content="""Task: Book an appointment for an oil change.
Website has a form with fields: Name, Email, Phone, Date, Time, Service Type.

Describe the steps you would take."""),
    ]
    
    try:
        result = await llm.ainvoke(messages)
        print("Agent's response:")
        print(result.completion)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    print()


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NVIDIA NIM Integration Tests")
    print("=" * 60 + "\n")
    
    await test_basic_completion()
    await test_structured_output()
    await test_browser_task()
    
    print("=" * 60)
    print("All tests completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
