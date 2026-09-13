from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from starlette.concurrency import run_in_threadpool
import sys
import os
import asyncio

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.location_agent import extract_location
from agents.hospital_agent import find_hospitals, find_hospitals_with_coordinates
from agents.weather_agent import get_weather
from agents.coordinator_agent import coordinate_agents
from agents.voice_agent import listen_emergency
from agents.llm_advice_agent import generate_llm_advice
from backend.models import (
    EmergencyRequest, LocationRequest, LocationResponse,
    HospitalRequest, HospitalResponse, WeatherResponse,
    VoiceRequest, VoiceResponse, LLMAdviceRequest, LLMAdviceResponse,
    EmergencyAnalysisResponse
)
from backend.websocket_manager import manager

app = FastAPI(title="Multi-Agent Emergency System API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# City coordinates for mapping
CITY_COORDINATES = {
    "Delhi": [28.6139, 77.2090],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Mumbai": [19.0760, 72.8777],
    "Vijayawada": [16.5062, 80.6480]
}


@app.get("/")
async def read_root():
    """Root endpoint - serve the frontend"""
    return FileResponse("frontend/index.html")


@app.post("/api/emergency/analyze", response_model=EmergencyAnalysisResponse)
async def analyze_emergency(request: EmergencyRequest):
    """
    Main endpoint to analyze emergency situation using all agents.
    """
    try:
        # Use location override if provided, otherwise extract from input
        if request.location:
            location = request.location
        else:
            location = extract_location(request.user_input)
        
        # Get hospitals and weather
        hospitals_detail = find_hospitals_with_coordinates(
            location, CITY_COORDINATES.get(location)
        )
        hospitals = [h["address"] for h in hospitals_detail]
        temperature = get_weather()
        
        # Generate AI advice
        advice = generate_llm_advice(request.user_input, location, temperature if temperature else 0)
        
        return EmergencyAnalysisResponse(
            location=location,
            hospitals=hospitals,
            hospitals_detail=hospitals_detail,
            coordinates=CITY_COORDINATES.get(location),
            temperature=temperature if temperature else 0,
            advice=advice,
            success=True
        )
    except Exception as e:
        return EmergencyAnalysisResponse(
            location="Unknown",
            hospitals=[],
            hospitals_detail=[],
            coordinates=None,
            temperature=0,
            advice=None,
            success=False,
            message=f"Analysis failed: {str(e)}"
        )


@app.post("/api/location/extract", response_model=LocationResponse)
async def extract_location_endpoint(request: LocationRequest):
    """Extract location from user input"""
    try:
        location = extract_location(request.user_input)
        return LocationResponse(location=location, success=True)
    except Exception as e:
        return LocationResponse(location="Unknown", success=False)


@app.post("/api/hospitals/find", response_model=HospitalResponse)
async def find_hospitals_endpoint(request: HospitalRequest):
    """Find hospitals in a given city"""
    try:
        hospitals = find_hospitals(request.city)
        return HospitalResponse(hospitals=hospitals, success=True)
    except Exception as e:
        return HospitalResponse(hospitals=[], success=False)


@app.get("/api/weather/current", response_model=WeatherResponse)
async def get_weather_endpoint(latitude: float = 17.385, longitude: float = 78.4867):
    """Get current weather for given coordinates"""
    try:
        temperature = get_weather(latitude, longitude)
        if temperature is not None:
            return WeatherResponse(
                temperature=temperature,
                location=f"{latitude}, {longitude}",
                success=True
            )
        else:
            return WeatherResponse(temperature=0, success=False)
    except Exception as e:
        return WeatherResponse(temperature=0, success=False)


@app.post("/api/voice/process", response_model=VoiceResponse)
async def process_voice_endpoint(request: VoiceRequest):
    """Process voice input (backend fallback)"""
    try:
        text = listen_emergency()
        return VoiceResponse(text=text, success=True)
    except Exception as e:
        return VoiceResponse(text="Voice processing failed", success=False)


@app.post("/api/llm/advice", response_model=LLMAdviceResponse)
async def get_llm_advice_endpoint(request: LLMAdviceRequest):
    """Get AI-generated medical advice"""
    try:
        advice = generate_llm_advice(
            request.emergency_text,
            request.location,
            request.temperature
        )
        return LLMAdviceResponse(advice=advice, success=True)
    except Exception as e:
        return LLMAdviceResponse(
            advice="AI advice unavailable. Call emergency services.",
            success=False
        )


@app.get("/api/coordinates/{city}")
async def get_city_coordinates(city: str):
    """Get coordinates for a supported city"""
    if city in CITY_COORDINATES:
        return {"city": city, "coordinates": CITY_COORDINATES[city]}
    else:
        raise HTTPException(status_code=404, detail="City not found")


async def _stream_llm_advice(websocket: WebSocket, emergency_text: str,
                             location: str, temperature: float) -> str:
    """
    Run LLM advice generation in a worker thread and stream chunks to the
    WebSocket in real-time. The sync agent uses the `requests` library, so it
    must be offloaded to a thread; chunks are marshalled onto the event loop
    thread-safely through an asyncio.Queue.
    """
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def stream_callback(chunk: str) -> None:
        # Called from the worker thread; schedule chunk on the event loop.
        loop.call_soon_threadsafe(queue.put_nowait, chunk)

    async def pump_chunks() -> None:
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            if chunk:
                await manager.send_stream_chunk(websocket, chunk)

    pump_task = asyncio.create_task(pump_chunks())
    try:
        advice = await run_in_threadpool(
            generate_llm_advice, emergency_text, location, temperature, stream_callback
        )
    finally:
        await queue.put(None)
        await pump_task

    return advice


@app.websocket("/ws/real-time")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time emergency analysis with streaming updates.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "emergency_analysis":
                user_input = data.get("user_input", "")
                location_override = data.get("location")
                
                # Send status update
                await manager.send_status_update(websocket, "processing", 
                    {"message": "Starting emergency analysis"})
                
                # Extract location
                await manager.send_agent_update(websocket, "location_agent", "processing")
                if location_override:
                    location = location_override
                else:
                    location = extract_location(user_input)
                await manager.send_agent_update(websocket, "location_agent", "complete", 
                    {"location": location})
                
                # Find hospitals
                await manager.send_agent_update(websocket, "hospital_agent", "processing")
                hospitals_detail = find_hospitals_with_coordinates(
                    location, CITY_COORDINATES.get(location)
                )
                hospitals = [h["address"] for h in hospitals_detail]
                await manager.send_agent_update(websocket, "hospital_agent", "complete",
                    {"hospital_count": len(hospitals)})
                
                # Get weather
                await manager.send_agent_update(websocket, "weather_agent", "processing")
                temperature = get_weather()
                await manager.send_agent_update(websocket, "weather_agent", "complete",
                    {"temperature": temperature})
                
                # Stream LLM advice
                await manager.send_agent_update(websocket, "llm_agent", "processing")

                advice = await _stream_llm_advice(
                    websocket, user_input, location, temperature if temperature else 0
                )
                
                # Send final stream chunk
                await manager.send_stream_chunk(websocket, "", is_final=True)
                await manager.send_agent_update(websocket, "llm_agent", "complete")
                
                # Send complete message with all results
                result = {
                    "location": location,
                    "hospitals": hospitals,
                    "hospitals_detail": hospitals_detail,
                    "coordinates": CITY_COORDINATES.get(location),
                    "temperature": temperature if temperature else 0,
                    "advice": advice,
                }
                await manager.send_complete(websocket, result)
                
            elif data.get("type") == "ping":
                await manager.send_personal_message(websocket, {"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_error(websocket, str(e))
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "connections": manager.get_connection_count(),
        "service": "Multi-Agent Emergency System"
    }


# Mount static files for frontend (must be last to avoid conflicts with API routes)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)