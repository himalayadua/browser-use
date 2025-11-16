# General-Purpose Appointment Booking Automation

This project provides a flexible, AI-powered appointment booking automation system using browser-use and NVIDIA NIM.

## Features

- **General Purpose**: Works with various appointment booking websites
- **NVIDIA NIM Integration**: Uses NVIDIA's powerful LLM API for intelligent browser control
- **Vision Support**: Can analyze screenshots to understand page layout
- **Structured Output**: Returns appointment confirmation details in a structured format
- **Flexible Data Model**: Supports various types of appointments (service, medical, etc.)
- **Error Handling**: Gracefully handles booking failures and provides detailed feedback

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your NVIDIA API key:

```bash
cp .env.example .env
```

Edit `.env` and add your NVIDIA NIM API key:
```
NVIDIA_API_KEY=nvapi-your-api-key-here
```

Get your API key from: https://build.nvidia.com/

### 3. Prepare Appointment Data

Create a JSON file with your appointment information (see `example_data.json`):

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-123-4567",
  "appointment_type": "Oil Change",
  "preferred_date": "2025-02-15",
  "preferred_time": "10:00",
  "vehicle_make": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_year": "2020"
}
```

## Usage

### Basic Usage

```bash
python book_appointment.py \
  --url "https://example.com/book-appointment" \
  --data example_data.json
```

### Advanced Options

```bash
python book_appointment.py \
  --url "https://example.com/book-appointment" \
  --data my_appointment.json \
  --max-steps 100 \
  --headless \
  --no-vision
```

**Options:**
- `--url`: URL of the appointment booking page (required)
- `--data`: Path to JSON file with appointment data (required)
- `--max-steps`: Maximum number of steps for the agent (default: 50)
- `--headless`: Run browser in headless mode
- `--no-vision`: Disable vision capabilities (faster but less accurate)

## Data Model

### Required Fields
- `first_name`: First name
- `last_name`: Last name
- `email`: Email address
- `phone`: Phone number

### Optional Fields
- `appointment_type`: Type of appointment
- `preferred_date`: Preferred date (YYYY-MM-DD)
- `preferred_time`: Preferred time (HH:MM)
- `vehicle_make`: Vehicle manufacturer
- `vehicle_model`: Vehicle model
- `vehicle_year`: Vehicle year
- `vehicle_vin`: Vehicle VIN number
- `license_plate`: License plate
- `notes`: Additional notes
- `address`: Street address
- `city`: City
- `state`: State
- `zip_code`: ZIP code

## How It Works

1. **Initialize**: Sets up NVIDIA NIM LLM and browser session
2. **Navigate**: Opens the booking URL
3. **Analyze**: Uses vision to understand the page layout
4. **Fill Form**: Intelligently fills out the booking form
5. **Submit**: Submits the appointment request
6. **Confirm**: Captures confirmation details
7. **Return**: Returns structured result with booking information

## NVIDIA NIM Integration

This project uses NVIDIA NIM's OpenAI-compatible API. The `ChatNvidiaNIM` class wraps the NVIDIA API and provides:

- **Model**: `qwen/qwen3-next-80b-a3b-instruct` (default, can be changed)
- **Streaming**: Supports streaming responses
- **Structured Output**: Can return Pydantic models
- **Vision**: Supports image analysis for screenshot understanding

### Available NVIDIA NIM Models

You can use different models by modifying the `model` parameter:

```python
llm = ChatNvidiaNIM(
    api_key="nvapi-xxx",
    model="meta/llama-3.1-405b-instruct",  # or other models
)
```

Popular models:
- `qwen/qwen3-next-80b-a3b-instruct` (default)
- `meta/llama-3.1-405b-instruct`
- `nvidia/llama-3.1-nemotron-70b-instruct`
- `mistralai/mixtral-8x7b-instruct-v0.1`

## Examples

### Example 1: Car Service Appointment

```bash
python book_appointment.py \
  --url "https://dealership.com/schedule-service" \
  --data car_service.json
```

### Example 2: Medical Appointment

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "555-987-6543",
  "appointment_type": "Annual Checkup",
  "preferred_date": "2025-03-01",
  "preferred_time": "14:00",
  "notes": "First visit"
}
```

### Example 3: General Appointment

```json
{
  "first_name": "Bob",
  "last_name": "Johnson",
  "email": "bob@example.com",
  "phone": "555-456-7890",
  "appointment_type": "Consultation",
  "preferred_date": "2025-02-20",
  "preferred_time": "09:00"
}
```

## Troubleshooting

### Issue: "NVIDIA_API_KEY environment variable is required"
**Solution**: Make sure you've created a `.env` file with your NVIDIA API key.

### Issue: Agent fails to find booking form
**Solution**: 
- Try running without `--headless` to see what the agent sees
- Increase `--max-steps` to give the agent more time
- Check if the website requires login (provide credentials in data)

### Issue: Wrong fields are filled
**Solution**:
- Enable vision with `--no-vision` flag removed
- Provide more specific field names in your data
- Check the website's field labels match expected names

### Issue: Booking not confirmed
**Solution**:
- Check if the website requires additional verification (email, SMS)
- Verify all required fields are provided in your data
- Review the agent's actions to see where it stopped

## Advanced Usage

### Custom LLM Configuration

You can customize the NVIDIA NIM LLM settings in `book_appointment.py`:

```python
llm = ChatNvidiaNIM(
    api_key=api_key,
    model="qwen/qwen3-next-80b-a3b-instruct",
    temperature=0.6,  # Lower = more deterministic
    top_p=0.7,        # Nucleus sampling
    max_completion_tokens=4096,
)
```

### Custom Tools

You can add custom tools to handle specific website features:

```python
tools = Tools()

@tools.action("Handle specific popup")
async def handle_popup(browser_session):
    # Custom logic here
    return ActionResult(extracted_content="Popup handled")

agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
    tools=tools,
)
```

## License

This project is provided as-is for educational and automation purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser-use documentation: https://docs.browser-use.com
3. Check NVIDIA NIM documentation: https://build.nvidia.com/
