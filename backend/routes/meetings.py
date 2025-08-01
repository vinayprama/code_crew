from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MeetingRequest(BaseModel):
    user_id: str
    project_name: str
    requested_time: str
    team_member_email: str

@router.post("/api/schedule_meeting")
def schedule_meeting(data: MeetingRequest):
    # For demo, just return a fake meeting URL
    meeting_time = data.requested_time or "some time"
    return {
        "message": f"✅ (Demo) Meeting scheduled with {data.team_member_email} at {meeting_time}.",
        "join_url": "https://teams.microsoft.com/l/meetup-join/fake-demo-meeting-url"
    }