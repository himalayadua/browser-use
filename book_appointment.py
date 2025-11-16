"""
General-purpose appointment booking automation script.

This script uses browser-use with NVIDIA NIM to automate the process of
booking appointments on websites. It's designed to be flexible and work
with various appointment booking systems.

Usage:
    python book_appointment.py --url <booking_url> --data appointment_data.json
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Import browser-use components
from browser_use import Agent, Browser, Tools
from browser_use.agent.views import ActionResult

# Import our NVIDIA NIM LLM
from llm_nvidia_nim import ChatNvidiaNIM

load_dotenv()


class AppointmentData(BaseModel):
    """Data structure for appointment information."""
    
    # Personal Information
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    
    # Appointment Details
    appointment_type: str | None = Field(None, description="Type of appointment (e.g., 'Oil Change', 'Inspection')")
    preferred_date: str | None = Field(None, description="Preferred date (YYYY-MM-DD format)")
    preferred_time: str | None = Field(None, description="Preferred time (HH:MM format)")
    
    # Vehicle Information (if applicable)
    vehicle_make: str | None = Field(None, description="Vehicle make (e.g., 'Toyota')")
    vehicle_model: str | None = Field(None, description="Vehicle model (e.g., 'Camry')")
    vehicle_year: str | None = Field(None, description="Vehicle year")
    vehicle_vin: str | None = Field(None, description="Vehicle VIN number")
    license_plate: str | None = Field(None, description="License plate number")
    
    # Additional Information
    notes: str | None = Field(None, description="Additional notes or special requests")
    address: str | None = Field(None, description="Address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    zip_code: str | None = Field(None, description="ZIP code")


class AppointmentResult(BaseModel):
    """Result of the appointment booking."""
    
    success: bool = Field(..., description="Whether the appointment was successfully booked")
    confirmation_number: str | None = Field(None, description="Appointment confirmation number")
    appointment_date: str | None = Field(None, description="Confirmed appointment date")
    appointment_time: str | None = Field(None, description="Confirmed appointment time")
    message: str = Field(..., description="Summary message about the booking")


async def book_appointment(
    booking_url: str,
    appointment_data: AppointmentData,
    max_steps: int = 50,
    headless: bool = False,
    use_vision: bool = True,
) -> AppointmentResult:
    """
    Book an appointment using browser automation.
    
    Args:
        booking_url: URL of the appointment booking page
        appointment_data: Appointment information
        max_steps: Maximum number of steps for the agent
        headless: Whether to run browser in headless mode
        use_vision: Whether to use vision capabilities
        
    Returns:
        AppointmentResult with booking details
    """
    
    # Initialize NVIDIA NIM LLM
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable is required")
    
    llm = ChatNvidiaNIM(
        api_key=api_key,
        model="qwen/qwen3-next-80b-a3b-instruct",
        temperature=0.6,
        top_p=0.7,
        max_completion_tokens=4096,
    )
    
    # Initialize browser
    browser = Browser(
        headless=headless,
        disable_security=False,
    )
    
    # Initialize tools
    tools = Tools()
    
    # Create the task prompt
    task = f"""
    Your goal is to book an appointment on the website at {booking_url}.
    
    **Appointment Information:**
    {json.dumps(appointment_data.model_dump(exclude_none=True), indent=2)}
    
    **Instructions:**
    1. Navigate to {booking_url}
    2. Look for the appointment booking form or button to start booking
    3. Fill out ALL required fields with the provided information
    4. If a field is not provided in the data but is required, make a reasonable choice or skip if optional
    5. Select the appointment type, date, and time as close as possible to the preferences
    6. If the exact preferred date/time is not available, choose the closest available option
    7. Complete any additional steps (vehicle information, contact details, etc.)
    8. Review the information before submitting
    9. Submit the appointment booking
    10. Capture the confirmation number and appointment details
    
    **Important Guidelines:**
    - Work through the form step by step, filling one section at a time
    - If you encounter dropdowns, select the most appropriate option
    - If you encounter date/time pickers, use the provided preferences
    - Handle any pop-ups or modals that appear
    - If login is required and credentials are not provided, try to proceed as a guest
    - Take screenshots at key steps for verification
    - After submission, extract the confirmation number and appointment details
    
    **Field Mapping Tips:**
    - "First Name" / "Given Name" → use first_name
    - "Last Name" / "Family Name" / "Surname" → use last_name
    - "Email" / "Email Address" → use email
    - "Phone" / "Phone Number" / "Mobile" → use phone
    - "Make" / "Manufacturer" → use vehicle_make
    - "Model" → use vehicle_model
    - "Year" → use vehicle_year
    - "VIN" / "VIN Number" → use vehicle_vin
    - "License Plate" / "Plate Number" → use license_plate
    
    **Success Criteria:**
    - You must reach a confirmation page or receive a confirmation message
    - Extract the confirmation number if available
    - Note the final appointment date and time
    - Mark the task as successful only if you see confirmation
    """
    
    # Create agent with structured output
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        tools=tools,
        use_vision=use_vision,
        output_model_schema=AppointmentResult,
    )
    
    # Run the agent
    try:
        history = await agent.run(max_steps=max_steps)
        
        # Get structured output
        if history.structured_output:
            return history.structured_output
        else:
            # Fallback if structured output is not available
            final_result = history.final_result()
            return AppointmentResult(
                success=history.is_successful() or False,
                message=final_result or "Appointment booking completed but no confirmation details captured",
            )
    
    except Exception as e:
        return AppointmentResult(
            success=False,
            message=f"Error during appointment booking: {str(e)}",
        )
    
    finally:
        # Clean up
        await agent.close()


async def main():
    """Main entry point for the script."""
    
    parser = argparse.ArgumentParser(
        description="Book an appointment using browser automation with NVIDIA NIM"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the appointment booking page",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to JSON file containing appointment data",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum number of steps for the agent (default: 50)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="Disable vision capabilities",
    )
    
    args = parser.parse_args()
    
    # Load appointment data
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Data file not found at {args.data}")
        return
    
    with open(data_path) as f:
        data_dict = json.load(f)
    
    appointment_data = AppointmentData(**data_dict)
    
    print("=" * 60)
    print("Appointment Booking Automation")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Name: {appointment_data.first_name} {appointment_data.last_name}")
    print(f"Email: {appointment_data.email}")
    print(f"Phone: {appointment_data.phone}")
    if appointment_data.appointment_type:
        print(f"Type: {appointment_data.appointment_type}")
    if appointment_data.preferred_date:
        print(f"Preferred Date: {appointment_data.preferred_date}")
    if appointment_data.preferred_time:
        print(f"Preferred Time: {appointment_data.preferred_time}")
    print("=" * 60)
    print()
    
    # Book the appointment
    result = await book_appointment(
        booking_url=args.url,
        appointment_data=appointment_data,
        max_steps=args.max_steps,
        headless=args.headless,
        use_vision=not args.no_vision,
    )
    
    # Display results
    print()
    print("=" * 60)
    print("Booking Result")
    print("=" * 60)
    print(f"Success: {result.success}")
    if result.confirmation_number:
        print(f"Confirmation Number: {result.confirmation_number}")
    if result.appointment_date:
        print(f"Appointment Date: {result.appointment_date}")
    if result.appointment_time:
        print(f"Appointment Time: {result.appointment_time}")
    print(f"Message: {result.message}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
