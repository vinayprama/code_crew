
# from datetime import datetime, timedelta
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from dateutil import parser as date_parser
# from utils.teams import create_teams_meeting

# router = APIRouter()

# class MeetingRequest(BaseModel):
#     user_id: str
#     project_name: str
#     requested_time: str
#     team_member_email: str

# @router.post("/api/schedule_meeting")
# def schedule_meeting(data: MeetingRequest):
#     print("DEBUG MeetingRequest received:", data)
#     # If requested_time is empty or "now", schedule for 1 hour from now
#     if not data.requested_time or data.requested_time.lower() == "now":
#         parsed_time = datetime.now() + timedelta(hours=1)
#     else:
#         try:
#             parsed_time = date_parser.parse(data.requested_time, fuzzy=True)
#         except Exception as e:
#             print("ERROR parsing date:", e)
#             raise HTTPException(status_code=422, detail="Invalid datetime format.")

#     start_iso = parsed_time.isoformat()
#     end_iso = (parsed_time + timedelta(hours=1)).isoformat()

#     try:
#         join_url = create_teams_meeting(
#             subject=f"Meeting for {data.project_name}",
#             start_time=start_iso,
#             end_time=end_iso,
#             attendees=[data.team_member_email]
#         )
#         print("DEBUG join_url:", join_url)
#     except Exception as e:
#         print("ERROR in create_teams_meeting:", e)
#         raise HTTPException(status_code=500, detail=f"Could not create Teams meeting: {e}")

#     return {
#         "message": f"✅ Meeting scheduled with {data.team_member_email} at {parsed_time.strftime('%Y-%m-%d %I:%M %p')}.",
#         "join_url": join_url
#     }

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