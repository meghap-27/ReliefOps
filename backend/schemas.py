from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str

# Add this section below
class VolunteerCreate(BaseModel):
    name: str
    email: str
    # Add any other fields your volunteer registration needs
