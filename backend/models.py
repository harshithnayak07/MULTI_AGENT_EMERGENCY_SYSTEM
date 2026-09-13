from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class EmergencyRequest(BaseModel):
    user_input: str = Field(..., description="Emergency description from user")
    location: Optional[str] = Field(None, description="Optional location override")


class LocationRequest(BaseModel):
    user_input: str = Field(..., description="Text input to extract location from")


class LocationResponse(BaseModel):
    location: str = Field(..., description="Extracted location/city name")
    success: bool = Field(..., description="Whether location extraction was successful")


class HospitalRequest(BaseModel):
    city: str = Field(..., description="City name to find hospitals in")


class HospitalResponse(BaseModel):
    hospitals: List[str] = Field(..., description="List of hospital names and addresses")
    success: bool = Field(..., description="Whether hospital search was successful")


class WeatherResponse(BaseModel):
    temperature: float = Field(..., description="Current temperature in Celsius")
    location: Optional[str] = Field(None, description="Location for weather data")
    success: bool = Field(..., description="Whether weather retrieval was successful")


class VoiceRequest(BaseModel):
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data (optional)")


class VoiceResponse(BaseModel):
    text: str = Field(..., description="Transcribed text from voice input")
    success: bool = Field(..., description="Whether voice processing was successful")


class LLMAdviceRequest(BaseModel):
    emergency_text: str = Field(..., description="Emergency description")
    location: str = Field(..., description="Location of emergency")
    temperature: float = Field(..., description="Current temperature")


class LLMAdviceResponse(BaseModel):
    advice: str = Field(..., description="AI-generated medical advice")
    success: bool = Field(..., description="Whether advice generation was successful")


class EmergencyAnalysisResponse(BaseModel):
    location: str = Field(..., description="Detected location")
    hospitals: List[str] = Field(..., description="List of nearby hospitals")
    hospitals_detail: Optional[List[Dict[str, Any]]] = Field(
        None, description="Hospitals with name, address and coordinates"
    )
    coordinates: Optional[List[float]] = Field(
        None, description="[latitude, longitude] of the emergency location"
    )
    temperature: float = Field(..., description="Current temperature")
    advice: Optional[str] = Field(None, description="AI-generated advice")
    success: bool = Field(..., description="Whether analysis was successful")
    message: Optional[str] = Field(None, description="Additional information or error message")


class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type: status, update, error, complete")
    data: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of message")