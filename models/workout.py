from datetime import date, datetime, time

from database import cursor, db
from models.activity import Activity


class Workout:
    def __init__(
        self,
        workout_id,
        user_id,
        activity_type,
        duration,
        workout_date,
        workout_time=None,
        calories_burned=0,
        intensity=None,
    ):
        self.workout_id = workout_id
        self.user_id = user_id
        self.activity_type = activity_type
        self.duration = int(duration)
        self.workout_date = workout_date
        self.workout_time = workout_time
        self.calories_burned = int(calories_burned) if calories_burned is not None else 0
        self.intensity = intensity or "moderate"

    @staticmethod
    def _parse_date(value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    @staticmethod
    def _parse_time(value):
        if value in (None, ""):
            return None
        if isinstance(value, time):
            return value
        try:
            return datetime.strptime(str(value), "%H:%M:%S").time()
        except ValueError:
            return datetime.strptime(str(value), "%H:%M").time()

    @classmethod
    def _from_row(cls, row):
        if not row:
            return None
        (
            workout_id,
            user_id,
            activity_type,
            duration,
            workout_date,
            workout_time,
            calories_burned,
            intensity,
        ) = row
        return cls(
            workout_id=workout_id,
            user_id=user_id,
            activity_type=activity_type,
            duration=duration,
            workout_date=workout_date,
            workout_time=workout_time,
            calories_burned=calories_burned,
            intensity=intensity,
        )

    @staticmethod
    def calculate_calories_burned(duration, activity_type=None, calories_per_minute=None, intensity="moderate"):
        if duration is None or duration <= 0:
            return 0

        calories = calories_per_minute
        if calories is None and activity_type:
            activity = Activity.get_by_name(activity_type)
            if activity:
                calories = activity.calories_per_minute

        calories = calories or 0
        intensity_multipliers = {
            "low": 0.9,
            "light": 0.9,
            "moderate": 1.0,
            "medium": 1.0,
            "high": 1.1,
            "very-high": 1.2,
        }
        multiplier = intensity_multipliers.get((intensity or "").lower(), 1.0)
        return int(round(duration * calories * multiplier))

    @classmethod
    def log_workout(
        cls,
        user_id,
        activity_type,
        duration,
        workout_date=None,
        workout_time=None,
        intensity="moderate",
        calories_burned=None,
    ):
        duration = int(duration)
        if duration <= 0:
            raise ValueError("Duration must be greater than zero")

        workout_date = cls._parse_date(workout_date) or date.today()
        workout_time = cls._parse_time(workout_time)

        calories_burned = (
            int(calories_burned)
            if calories_burned is not None
            else cls.calculate_calories_burned(duration, activity_type, intensity=intensity)
        )

        sql = """
        INSERT INTO workout (user_id, activity_type, duration, workout_date, workout_time, calories_burned, intensity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (user_id, activity_type, duration, workout_date, workout_time, calories_burned, intensity),
        )
        db.commit()

        return cls(
            workout_id=cursor.lastrowid,
            user_id=user_id,
            activity_type=activity_type,
            duration=duration,
            workout_date=workout_date,
            workout_time=workout_time,
            calories_burned=calories_burned,
            intensity=intensity,
        )

    @classmethod
    def update_workout(cls, workout_id, user_id=None, **fields):
        allowed_fields = {
            "activity_type",
            "duration",
            "workout_date",
            "workout_time",
            "calories_burned",
            "intensity",
        }
        updates = {k: v for k, v in fields.items() if k in allowed_fields and v is not None}

        if not updates:
            raise ValueError("No valid fields provided for update")

        if "workout_date" in updates:
            updates["workout_date"] = cls._parse_date(updates["workout_date"])
        if "workout_time" in updates:
            updates["workout_time"] = cls._parse_time(updates["workout_time"])
        if "duration" in updates:
            updates["duration"] = int(updates["duration"])
        if "calories_burned" in updates:
            updates["calories_burned"] = int(updates["calories_burned"])

        set_clause = ", ".join([f"{field}=%s" for field in updates])
        params = list(updates.values())

        where_clause = "workout_id=%s"
        params.append(workout_id)
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"UPDATE workout SET {set_clause} WHERE {where_clause}"
        cursor.execute(sql, tuple(params))
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def delete_workout(cls, workout_id, user_id=None):
        params = [workout_id]
        where_clause = "workout_id=%s"
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"DELETE FROM workout WHERE {where_clause}"
        cursor.execute(sql, tuple(params))
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def get_workout_history(cls, user_id, start_date=None, end_date=None, limit=50):
        filters = ["user_id=%s"]
        params = [user_id]

        if start_date:
            filters.append("workout_date >= %s")
            params.append(cls._parse_date(start_date))
        if end_date:
            filters.append("workout_date <= %s")
            params.append(cls._parse_date(end_date))

        where_clause = " AND ".join(filters)

        sql = f"""
        SELECT workout_id, user_id, activity_type, duration, workout_date, workout_time, calories_burned, intensity
        FROM workout
        WHERE {where_clause}
        ORDER BY workout_date DESC, workout_time DESC
        """
        if limit:
            sql += " LIMIT %s"
            params.append(int(limit))

        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
        return [cls._from_row(row) for row in rows]

    @classmethod
    def get_daily_totals(cls, user_id, target_date=None):
        target_date = cls._parse_date(target_date) or date.today()
        sql = """
        SELECT COALESCE(SUM(duration), 0), COALESCE(SUM(calories_burned), 0)
        FROM workout
        WHERE user_id=%s AND workout_date=%s
        """
        cursor.execute(sql, (user_id, target_date))
        result = cursor.fetchone() or (0, 0)
        total_duration, total_calories = result
        return {
            "date": target_date,
            "total_duration": int(total_duration or 0),
            "total_calories": int(total_calories or 0),
        }

    @classmethod
    def get_range_totals(cls, user_id, start_date, end_date):
        start = cls._parse_date(start_date)
        end = cls._parse_date(end_date)
        sql = """
        SELECT COALESCE(SUM(duration), 0), COALESCE(SUM(calories_burned), 0)
        FROM workout
        WHERE user_id=%s AND workout_date BETWEEN %s AND %s
        """
        cursor.execute(sql, (user_id, start, end))
        result = cursor.fetchone() or (0, 0)
        total_duration, total_calories = result
        return {
            "start_date": start,
            "end_date": end,
            "total_duration": int(total_duration or 0),
            "total_calories": int(total_calories or 0),
        }

    def to_dict(self):
        return {
            "workout_id": self.workout_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "duration": self.duration,
            "workout_date": self.workout_date,
            "workout_time": self.workout_time,
            "calories_burned": self.calories_burned,
            "intensity": self.intensity,
        }
