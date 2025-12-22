import sqlite3
import os
import datetime
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = 'yaprosb_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    streak_days INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    amount INTEGER DEFAULT 0,
                    goal_reached BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sleep_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    hours REAL,
                    quality INTEGER CHECK(quality >= 1 AND quality <= 5),
                    goal_reached BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    steps INTEGER DEFAULT 0,
                    workout_minutes INTEGER DEFAULT 0,
                    goal_reached BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    mood TEXT,
                    emoji TEXT,
                    note TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    duration INTEGER,
                    session_type TEXT CHECK(session_type IN ('work', 'break')),
                    completed BOOLEAN DEFAULT 0,
                    actual_duration INTEGER,
                    task_description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    frequency TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS habit_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    habit_id INTEGER,
                    date DATE,
                    completed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (habit_id) REFERENCES habits (id),
                    UNIQUE(user_id, habit_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    deadline DATE,
                    progress INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement TEXT NOT NULL,
                    category TEXT,
                    date DATE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meditation_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    duration INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS breathing_practices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    duration INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    workout_type TEXT,
                    duration INTEGER,
                    calories INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sos_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    note TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
    
    def ensure_user_exists(self, user_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id)
                VALUES (?)
            ''', (user_id,))
            
            cursor.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?
            ''', (user_id,))
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user_row = cursor.fetchone()
            user_info = dict(user_row) if user_row else {}
            
            today = datetime.date.today().isoformat()
            
            cursor.execute('SELECT amount FROM water_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            water_row = cursor.fetchone()
            water_today = water_row['amount'] if water_row else 0
            
            cursor.execute('SELECT hours FROM sleep_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            sleep_row = cursor.fetchone()
            sleep_hours = sleep_row['hours'] if sleep_row else 0.0
            
            cursor.execute('SELECT steps FROM activity_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            activity_row = cursor.fetchone()
            steps_today = activity_row['steps'] if activity_row else 0
            
            cursor.execute('SELECT mood, emoji FROM mood_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            mood_row = cursor.fetchone()
            mood_today = mood_row['mood'] if mood_row else None
            emoji_today = mood_row['emoji'] if mood_row else None
            
            cursor.execute('''
                SELECT COUNT(*) as count, SUM(duration) as total_time 
                FROM pomodoro_sessions 
                WHERE user_id = ? AND date = ? AND completed = 1
            ''', (user_id, today))
            pomodoro_row = cursor.fetchone()
            pomodoro_today = pomodoro_row['count'] if pomodoro_row else 0
            
            cursor.execute('''
                SELECT COUNT(*) as total_count, SUM(duration) as total_time 
                FROM pomodoro_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            pomodoro_total_row = cursor.fetchone()
            pomodoro_count = pomodoro_total_row['total_count'] if pomodoro_total_row else 0
            
            return {
                'user_id': user_id,
                'created_at': user_info.get('created_at'),
                'last_active': user_info.get('last_active'),
                'streak_days': user_info.get('streak_days', 0),
                'water_today': water_today,
                'water_total': self._get_total_water(user_id),
                'sleep_hours': sleep_hours,
                'steps_today': steps_today,
                'mood_today': mood_today,
                'emoji_today': emoji_today,
                'pomodoro_today': pomodoro_today,
                'pomodoro_count': pomodoro_count,
            }
    
    def _get_total_water(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM water_tracking WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['total'] if result and result['total'] else 0
    
    def update_water_intake(self, user_id: int, date: str, amount: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT amount FROM water_tracking WHERE user_id = ? AND date = ?', (user_id, date))
            current_row = cursor.fetchone()
            
            if current_row:
                new_amount = current_row['amount'] + amount
                cursor.execute('''
                    UPDATE water_tracking 
                    SET amount = ?, goal_reached = ?
                    WHERE user_id = ? AND date = ?
                ''', (new_amount, 1 if new_amount >= 8 else 0, user_id, date))
            else:
                cursor.execute('''
                    INSERT INTO water_tracking (user_id, date, amount, goal_reached)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, date, amount, 1 if amount >= 8 else 0))
    
    def update_sleep_data(self, user_id: int, date: str, hours: float, quality: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sleep_tracking (user_id, date, hours, quality, goal_reached)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, date, hours, quality, 1 if hours >= 7 else 0))
    
    def update_activity_data(self, user_id: int, date: str, steps: int, workout_minutes: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO activity_tracking (user_id, date, steps, workout_minutes, goal_reached)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, date, steps, workout_minutes, 1 if steps >= 10000 else 0))
    
    def update_mood_data(self, user_id: int, date: str, mood: str, emoji: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO mood_tracking (user_id, date, mood, emoji)
                VALUES (?, ?, ?, ?)
            ''', (user_id, date, mood, emoji))
    
    def save_pomodoro_session(self, user_id: int, duration: int, session_type: str, completed: bool, 
                             task_description: str, date: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pomodoro_sessions (user_id, date, duration, session_type, completed, task_description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, date, duration, session_type, completed, task_description))
            return cursor.lastrowid
    
    def get_pomodoro_stats(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            today = datetime.date.today().isoformat()
            
            cursor.execute('''
                SELECT COUNT(*) as today_count, SUM(duration) as today_time
                FROM pomodoro_sessions 
                WHERE user_id = ? AND date = ? AND completed = 1
            ''', (user_id, today))
            today_result = cursor.fetchone()
            
            cursor.execute('''
                SELECT COUNT(*) as total_count, SUM(duration) as total_time
                FROM pomodoro_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            total_result = cursor.fetchone()
            
            return {
                'today_pomodoros': today_result['today_count'],
                'today_time': today_result['today_time'] or 0,
                'total_pomodoros': total_result['total_count'],
                'total_time': total_result['total_time'] or 0,
            }
    
    def create_habit(self, user_id: int, name: str, description: str, frequency: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO habits (user_id, name, description, frequency)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, description, frequency))
            return cursor.lastrowid
    
    def get_user_habits(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT h.*, 
                       (SELECT COUNT(*) FROM habit_completions hc WHERE hc.habit_id = h.id AND hc.completed = 1) as completion_count
                FROM habits h
                WHERE h.user_id = ?
            ''', (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_habit_status(self, user_id: int, habit_id: int, date: str, completed: bool) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO habit_completions (user_id, habit_id, date, completed)
                VALUES (?, ?, ?, ?)
            ''', (user_id, habit_id, date, completed))
    
    def get_habit_statistics(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT h.name, 
                       COUNT(hc.date) as total_attempts,
                       SUM(CASE WHEN hc.completed THEN 1 ELSE 0 END) as completed_count,
                       (SUM(CASE WHEN hc.completed THEN 1 ELSE 0 END) * 100.0 / COUNT(hc.date)) as success_rate
                FROM habits h
                LEFT JOIN habit_completions hc ON h.id = hc.habit_id
                WHERE h.user_id = ?
                GROUP BY h.id
            ''', (user_id,))
            habits = cursor.fetchall()
            
            return {
                'habits': [dict(habit) for habit in habits],
                'total_habits': len(habits),
            }
    
    def create_goal(self, user_id: int, name: str, description: str, deadline: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (user_id, name, description, deadline)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, description, deadline))
            return cursor.lastrowid
    
    def get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_goal_progress(self, user_id: int, goal_id: int, progress: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE goals SET progress = ? WHERE id = ? AND user_id = ?
            ''', (progress, goal_id, user_id))
    
    def get_goal_progress(self, user_id: int, goal_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT progress FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
            result = cursor.fetchone()
            return result['progress'] if result else 0
    
    def get_user_achievements(self, user_id: int, limit: int = 20) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement FROM achievements 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, limit))
            rows = cursor.fetchall()
            return [row['achievement'] for row in rows]
    
    def add_user_achievement(self, user_id: int, achievement: str, date: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievements (user_id, achievement, date)
                VALUES (?, ?, ?)
            ''', (user_id, achievement, date))
    
    def get_water_history(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, amount, goal_reached 
                FROM water_tracking 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_sleep_history(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, hours, quality, goal_reached 
                FROM sleep_tracking 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_activity_history(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, steps, workout_minutes, goal_reached 
                FROM activity_tracking 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_mood_history(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, mood, emoji, note 
                FROM mood_tracking 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_mood_statistics(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as days_count FROM mood_tracking WHERE user_id = ?', (user_id,))
            days_result = cursor.fetchone()
            
            cursor.execute('SELECT mood, COUNT(*) as count FROM mood_tracking WHERE user_id = ? GROUP BY mood ORDER BY count DESC LIMIT 3', (user_id,))
            mood_counts = cursor.fetchall()
            
            return {
                'days_with_mood': days_result['days_count'],
                'most_common_moods': [row['mood'] for row in mood_counts],
                'total_moods': len(mood_counts),
            }
    
    def get_pomodoro_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, duration, session_type, completed, task_description 
                FROM pomodoro_sessions 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            ''', (user_id, start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_comprehensive_user_data(self, user_id: int) -> Dict[str, Any]:
        basic_data = self.get_user_data(user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            today = datetime.date.today().isoformat()
            cursor.execute('''
                SELECT COUNT(*) as pomodoro_today, SUM(duration) as pomodoro_time
                FROM pomodoro_sessions 
                WHERE user_id = ? AND date = ? AND completed = 1
            ''', (user_id, today))
            pomodoro_result = cursor.fetchone()
            basic_data['pomodoro_today'] = pomodoro_result['pomodoro_today'] or 0
            basic_data['pomodoro_time'] = pomodoro_result['pomodoro_time'] or 0
            
            cursor.execute('''
                SELECT COUNT(*) as pomodoro_count, SUM(duration) as total_time
                FROM pomodoro_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            pomodoro_total = cursor.fetchone()
            basic_data['pomodoro_count'] = pomodoro_total['pomodoro_count'] or 0
            
            cursor.execute('''
                SELECT AVG(CASE 
                    WHEN mood = 'Отлично' THEN 5
                    WHEN mood = 'Хорошо' THEN 4
                    WHEN mood = 'Нормально' THEN 3
                    WHEN mood = 'Не очень' THEN 2
                    WHEN mood = 'Плохо' THEN 1
                    ELSE 3
                END) as avg_mood,
                COUNT(*) as mood_days
                FROM mood_tracking 
                WHERE user_id = ?
            ''', (user_id,))
            mood_result = cursor.fetchone()
            basic_data['avg_mood'] = round(mood_result['avg_mood'], 2) if mood_result['avg_mood'] else 0
            basic_data['mood_days'] = mood_result['mood_days'] or 0
        
        return basic_data
    
    def get_user_streaks(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date FROM water_tracking 
                WHERE user_id = ? AND goal_reached = 1
                ORDER BY date DESC
            ''', (user_id,))
            water_dates = [row['date'] for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT date FROM sleep_tracking 
                WHERE user_id = ? AND goal_reached = 1
                ORDER BY date DESC
            ''', (user_id,))
            sleep_dates = [row['date'] for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT date FROM activity_tracking 
                WHERE user_id = ? AND goal_reached = 1
                ORDER BY date DESC
            ''', (user_id,))
            activity_dates = [row['date'] for row in cursor.fetchall()]
            
            return {
                'water_streak': self._calculate_streak(water_dates),
                'sleep_streak': self._calculate_streak(sleep_dates),
                'activity_streak': self._calculate_streak(activity_dates),
            }
    
    def _calculate_streak(self, dates: List[str]) -> int:
        if not dates:
            return 0
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        streak = 0
        current_date = today
        
        for date_str in dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if date_obj == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif date_obj < current_date:
                break
        
        return streak
    
    def add_workout_session(self, user_id: int, date: str, workout_type: str, duration: int, calories: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workout_history (user_id, date, workout_type, duration, calories)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, date, workout_type, duration, calories))
    
    def get_workout_statistics(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            today = datetime.date.today().isoformat()
            
            cursor.execute('SELECT COUNT(*) as total_workouts, SUM(duration) as total_minutes FROM workout_history WHERE user_id = ?', (user_id,))
            total_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(DISTINCT date) as days_with_workout FROM workout_history WHERE user_id = ?', (user_id,))
            days_result = cursor.fetchone()
            
            return {
                'total_workouts': total_result['total_workouts'] or 0,
                'total_minutes': total_result['total_minutes'] or 0,
                'days_with_workout': days_result['days_with_workout'] or 0,
            }
    
    def record_sos_usage(self, user_id: int, date: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sos_usage (user_id, date) VALUES (?, ?)', (user_id, date))
    
    def get_mood_patterns(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT date, mood FROM mood_tracking WHERE user_id = ? ORDER BY date', (user_id,))
            rows = cursor.fetchall()
            
            mood_transitions = {}
            prev_mood = None
            
            for row in rows:
                current_mood = row['mood']
                if prev_mood and current_mood:
                    key = f"{prev_mood}→{current_mood}"
                    mood_transitions[key] = mood_transitions.get(key, 0) + 1
                prev_mood = current_mood
            
            return {
                'mood_transitions': mood_transitions,
                'total_records': len(rows),
            }
    
    def get_current_mood_data(self, user_id: int) -> Dict[str, Any]:
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT mood, emoji FROM mood_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            row = cursor.fetchone()
            if row:
                return {
                    'today_mood': row['mood'],
                    'today_emoji': row['emoji'],
                }
            return {'today_mood': 'Не отмечено', 'today_emoji': ''}
    
    def get_current_sleep_data(self, user_id: int) -> Dict[str, Any]:
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT hours, quality FROM sleep_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            row = cursor.fetchone()
            
            cursor.execute('''
                SELECT AVG(hours) as avg_hours, AVG(quality) as avg_quality 
                FROM sleep_tracking 
                WHERE user_id = ? AND date >= date(?, '-7 days')
            ''', (user_id, today))
            avg_row = cursor.fetchone()
            
            return {
                'today_hours': row['hours'] if row else 0.0,
                'today_quality': row['quality'] if row else 0,
                'avg_hours': avg_row['avg_hours'] or 0.0,
                'avg_quality': avg_row['avg_quality'] or 0.0,
            }
    
    def get_physical_health_overview(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as days_with_water, SUM(amount) as total_amount FROM water_tracking WHERE user_id = ?', (user_id,))
            water_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as days_with_sleep, AVG(hours) as avg_hours FROM sleep_tracking WHERE user_id = ?', (user_id,))
            sleep_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as days_with_activity, AVG(steps) as avg_steps, SUM(steps) as total_steps FROM activity_tracking WHERE user_id = ?', (user_id,))
            activity_result = cursor.fetchone()
            
            return {
                'water': {
                    'days_with_water': water_result['days_with_water'],
                    'total_amount': water_result['total_amount'] or 0,
                },
                'sleep': {
                    'days_with_sleep': sleep_result['days_with_sleep'],
                    'avg_hours': sleep_result['avg_hours'] or 0.0,
                },
                'activity': {
                    'days_with_activity': activity_result['days_with_activity'],
                    'avg_steps': int(activity_result['avg_steps'] or 0),
                    'total_steps': activity_result['total_steps'] or 0,
                },
            }
    
    def add_mood_note(self, user_id: int, date: str, note: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO mood_notes (user_id, date, note)
                VALUES (?, ?, ?)
            ''', (user_id, date, note))
    
    def get_meditation_statistics(self, user_id: int) -> Dict[str, Any]:
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(duration) as today_minutes FROM meditation_tracking WHERE user_id = ? AND date = ?', (user_id, today))
            today_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as total_sessions, SUM(duration) as total_minutes FROM meditation_tracking WHERE user_id = ?', (user_id,))
            total_result = cursor.fetchone()
            
            return {
                'today_minutes': today_result['today_minutes'] or 0,
                'total_sessions': total_result['total_sessions'] or 0,
                'total_minutes': total_result['total_minutes'] or 0,
            }
    
    def get_user_overview(self, user_id: int) -> Dict[str, Any]:
        basic_data = self.get_user_data(user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as days_with_goal, AVG(amount) as avg_amount
                FROM water_tracking 
                WHERE user_id = ? AND date >= date('now', '-7 days')
            ''', (user_id,))
            water_result = cursor.fetchone()
            
            cursor.execute('''
                SELECT AVG(hours) as avg_hours, AVG(quality) as avg_quality
                FROM sleep_tracking 
                WHERE user_id = ? AND date >= date('now', '-7 days')
            ''', (user_id,))
            sleep_result = cursor.fetchone()
            
            cursor.execute('''
                SELECT AVG(steps) as avg_steps, COUNT(*) as active_days
                FROM activity_tracking 
                WHERE user_id = ? AND date >= date('now', '-7 days')
            ''', (user_id,))
            activity_result = cursor.fetchone()
            
            cursor.execute('''
                SELECT mood, COUNT(*) as count 
                FROM mood_tracking 
                WHERE user_id = ? AND date >= date('now', '-7 days')
                GROUP BY mood
                ORDER BY count DESC
            ''', (user_id,))
            mood_history = [row['mood'] for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT COUNT(*) as days_with_pomodoro
                FROM (SELECT DISTINCT date FROM pomodoro_sessions WHERE user_id = ? AND date >= date('now', '-7 days'))
            ''', (user_id,))
            pomodoro_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as achievements_count FROM achievements WHERE user_id = ?', (user_id,))
            achievements_result = cursor.fetchone()
            
            return {
                'water': {
                    'today': basic_data['water_today'],
                    'total': basic_data['water_total'],
                    'days_with_goal': water_result['days_with_goal'] or 0,
                    'avg_amount': water_result['avg_amount'] or 0,
                },
                'sleep': {
                    'today_hours': basic_data['sleep_hours'],
                    'avg_hours': sleep_result['avg_hours'] or 0,
                    'avg_quality': sleep_result['avg_quality'] or 0,
                },
                'activity': {
                    'today_steps': basic_data['steps_today'],
                    'avg_steps': int(activity_result['avg_steps'] or 0),
                    'total_steps': self._get_total_steps(user_id),
                    'active_days': activity_result['active_days'] or 0,
                    'today_workout': 0,  
                },
                'mood': {
                    'today_mood': basic_data['mood_today'],
                    'today_emoji': basic_data['emoji_today'],
                    'days_with_mood': self._get_mood_days_count(user_id),
                    'mood_history': mood_history,
                },
                'pomodoro': {
                    'today_completed': basic_data['pomodoro_today'],
                    'total_completed': basic_data['pomodoro_count'],
                    'total_time': self._get_total_pomodoro_time(user_id),
                    'days_with_pomodoro': pomodoro_result['days_with_pomodoro'] or 0,
                },
                'streak_days': basic_data['streak_days'],
                'last_active': basic_data['last_active'],
                'achievements': self.get_user_achievements(user_id, 5),
            }
    
    def get_social_overview(self, user_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as total_pomodoros, SUM(duration) as total_duration FROM pomodoro_sessions WHERE user_id = ?', (user_id,))
            pomodoro_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as total_habits FROM habits WHERE user_id = ?', (user_id,))
            habits_result = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as total_goals, COUNT(CASE WHEN status = "completed" THEN 1 END) as completed_goals FROM goals WHERE user_id = ?', (user_id,))
            goals_result = cursor.fetchone()
            
            return {
                'pomodoro': {
                    'total_sessions': pomodoro_result['total_pomodoros'] or 0,
                    'total_duration': pomodoro_result['total_duration'] or 0,
                },
                'habits': {
                    'total_count': habits_result['total_habits'] or 0,
                },
                'goals': {
                    'total_count': goals_result['total_goals'] or 0,
                    'completed_count': goals_result['completed_goals'] or 0,
                },
            }
    
    def update_habit_info(self, user_id: int, habit_id: int, **kwargs) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['name', 'description', 'frequency']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if fields:
                query = f"UPDATE habits SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
                values.extend([habit_id, user_id])
                cursor.execute(query, values)
    
    def delete_user_habit(self, user_id: int, habit_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM habits WHERE id = ? AND user_id = ?', (habit_id, user_id))
            cursor.execute('DELETE FROM habit_completions WHERE habit_id = ? AND user_id = ?', (habit_id, user_id))
    
    def _get_total_steps(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(steps) as total FROM activity_tracking WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['total'] or 0
    
    def _get_mood_days_count(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM mood_tracking WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['count'] or 0
    
    def _get_total_pomodoro_time(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(duration) as total FROM pomodoro_sessions WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['total'] or 0

db = DatabaseManager()