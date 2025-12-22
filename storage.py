import datetime
from typing import Dict, Any, List, Optional
from database import db

def ensure_user(user_id: int) -> None:
    db.ensure_user_exists(user_id)

def get_user_data(user_id: int) -> Dict[str, Any]:
    return db.get_user_data(user_id)

def update_water(user_id: int, amount: int) -> None:
    today = datetime.date.today().isoformat()
    db.update_water_intake(user_id, today, amount)

def update_sleep(user_id: int, hours: float, quality: int) -> None:
    today = datetime.date.today().isoformat()
    db.update_sleep_data(user_id, today, hours, quality)

def update_steps(user_id: int, steps: int, workout_minutes: int) -> None:
    today = datetime.date.today().isoformat()
    db.update_activity_data(user_id, today, steps, workout_minutes)

def set_mood(user_id: int, mood: str, emoji: str) -> None:
    today = datetime.date.today().isoformat()
    db.update_mood_data(user_id, today, mood, emoji)

def add_pomodoro_session(user_id: int, duration: int, session_type: str, completed: bool, task_description: str) -> int:
    today = datetime.date.today().isoformat()
    return db.save_pomodoro_session(user_id, duration, session_type, completed, task_description, today)

def get_pomodoro_stats(user_id: int) -> Dict[str, Any]:
    return db.get_pomodoro_stats(user_id)

def add_habit(user_id: int, name: str, description: str, frequency: str) -> int:
    return db.create_habit(user_id, name, description, frequency)

def get_habits(user_id: int) -> List[Dict[str, Any]]:
    return db.get_user_habits(user_id)

def update_habit_completion(user_id: int, habit_id: int, completed: bool) -> None:
    today = datetime.date.today().isoformat()
    db.update_habit_status(user_id, habit_id, today, completed)

def get_habit_streaks(user_id: int) -> Dict[str, Any]:
    return db.get_habit_statistics(user_id)

def save_goal(user_id: int, name: str, description: str, deadline: str) -> int:
    return db.create_goal(user_id, name, description, deadline)

def get_goals(user_id: int) -> List[Dict[str, Any]]:
    return db.get_user_goals(user_id)

def update_goal_progress(user_id: int, goal_id: int, progress: int) -> None:
    db.update_goal_progress(user_id, goal_id, progress)

def get_achievements(user_id: int, limit: int = 20) -> List[str]:
    return db.get_user_achievements(user_id, limit)

def add_achievement(user_id: int, achievement: str) -> None:
    today = datetime.date.today().isoformat()
    db.add_user_achievement(user_id, achievement, today)

def get_water_history(user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    return db.get_water_history(user_id, days)

def get_sleep_history(user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    return db.get_sleep_history(user_id, days)

def get_activity_history(user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    return db.get_activity_history(user_id, days)

def get_mood_history(user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    return db.get_mood_history(user_id, days)

def get_mood_stats(user_id: int) -> Dict[str, Any]:
    return db.get_mood_statistics(user_id)

def get_pomodoro_history(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
    return db.get_pomodoro_history(user_id, days)

def get_all_user_data(user_id: int) -> Dict[str, Any]:
    return db.get_comprehensive_user_data(user_id)

def get_streak_data(user_id: int) -> Dict[str, Any]:
    return db.get_user_streaks(user_id)

def add_workout(user_id: int, workout_type: str, duration: int, calories: int) -> None:
    today = datetime.date.today().isoformat()
    db.add_workout_session(user_id, today, workout_type, duration, calories)

def get_workout_data(user_id: int) -> Dict[str, Any]:
    return db.get_workout_statistics(user_id)

def add_sos_usage(user_id: int) -> None:
    today = datetime.date.today().isoformat()
    db.record_sos_usage(user_id, today)

def get_mood_patterns(user_id: int) -> Dict[str, Any]:
    return db.get_mood_patterns(user_id)

def get_mood_data(user_id: int) -> Dict[str, Any]:
    return db.get_current_mood_data(user_id)

def get_sleep_data(user_id: int) -> Dict[str, Any]:
    return db.get_current_sleep_data(user_id)

def get_physical_overview(user_id: int) -> Dict[str, Any]:
    return db.get_physical_health_overview(user_id)

def add_mood_note(user_id: int, note: str) -> None:
    today = datetime.date.today().isoformat()
    db.add_mood_note(user_id, today, note)

def get_meditation_data(user_id: int) -> Dict[str, Any]:
    return db.get_meditation_statistics(user_id)

def get_social_overview(user_id: int) -> Dict[str, Any]:
    return db.get_social_overview(user_id)

def get_goal_progress(user_id: int, goal_id: int) -> int:
    return db.get_goal_progress(user_id, goal_id)

def update_habit(user_id: int, habit_id: int, **kwargs) -> None:
    db.update_habit_info(user_id, habit_id, **kwargs)

def delete_habit(user_id: int, habit_id: int) -> None:
    db.delete_user_habit(user_id, habit_id)

def save_pomodoro_session(user_id: int, duration: int, session_type: str, completed: bool, task_description: str, date: str) -> int:
    return db.save_pomodoro_session(user_id, duration, session_type, completed, task_description, date)