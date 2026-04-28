import math
from models import Volunteer, Task

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Distance in km between two GPS points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def skill_match(volunteer: Volunteer, task: Task) -> bool:
    return task.required_skill in volunteer.skills.split(",")

def score_volunteer(volunteer, task) -> float:
    if not skill_match(volunteer, task):
        return -1.0                    # disqualified
    dist = haversine(
        volunteer.latitude, volunteer.longitude,
        task.latitude,      task.longitude
    )
    proximity_score = max(0, 1 - dist / 50)   # 50 km max range
    return proximity_score

def find_best_match(task: Task, volunteers: list[Volunteer]):
    available = [v for v in volunteers if v.available]
    scored    = [(v, score_volunteer(v, task)) for v in available]
    scored    = [(v, s) for v, s in scored if s >= 0]
    if not scored:
        return None
    return max(scored, key=lambda x: x[1])[0]
