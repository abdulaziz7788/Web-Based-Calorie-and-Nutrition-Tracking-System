from datetime import date, datetime

from database import cursor, db


class Goal:
    def __init__(
        self,
        goal_id,
        user_id,
        goal_type,
        target_weight=None,
        daily_calorie_target=None,
        start_date=None,
        target_date=None,
        status="active",
    ):
        self.goal_id = goal_id
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_weight = float(target_weight) if target_weight is not None else None
        self.daily_calorie_target = int(daily_calorie_target) if daily_calorie_target is not None else None
        self.start_date = start_date
        self.target_date = target_date
        self.status = status or "active"

    @staticmethod
    def _parse_date(value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    @classmethod
    def _from_row(cls, row):
        if not row:
            return None

        goal_id, user_id, goal_type, target_weight, daily_calorie_target, start_date, target_date, status = row
        return cls(
            goal_id=goal_id,
            user_id=user_id,
            goal_type=goal_type,
            target_weight=target_weight,
            daily_calorie_target=daily_calorie_target,
            start_date=start_date,
            target_date=target_date,
            status=status,
        )

    @classmethod
    def create_goal(
        cls,
        user_id,
        goal_type,
        target_weight=None,
        daily_calorie_target=None,
        start_date=None,
        target_date=None,
        status="active",
    ):
        start_date = cls._parse_date(start_date) or date.today()
        target_date = cls._parse_date(target_date)

        sql = """
        INSERT INTO goal (user_id, goal_type, target_weight, daily_calorie_target, start_date, target_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                user_id,
                goal_type,
                target_weight,
                daily_calorie_target,
                start_date,
                target_date,
                status,
            ),
        )
        db.commit()

        return cls(
            goal_id=cursor.lastrowid,
            user_id=user_id,
            goal_type=goal_type,
            target_weight=target_weight,
            daily_calorie_target=daily_calorie_target,
            start_date=start_date,
            target_date=target_date,
            status=status,
        )

    @classmethod
    def update_goal(cls, goal_id, user_id=None, **fields):
        allowed_fields = {
            "goal_type",
            "target_weight",
            "daily_calorie_target",
            "start_date",
            "target_date",
            "status",
        }
        updates = {k: v for k, v in fields.items() if k in allowed_fields and v is not None}
        if not updates:
            raise ValueError("No valid fields provided for update")

        if "start_date" in updates:
            updates["start_date"] = cls._parse_date(updates["start_date"])
        if "target_date" in updates:
            updates["target_date"] = cls._parse_date(updates["target_date"])

        set_clause = ", ".join([f"{field}=%s" for field in updates])
        params = list(updates.values())

        where_clause = "goal_id=%s"
        params.append(goal_id)
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"UPDATE goal SET {set_clause} WHERE {where_clause}"
        cursor.execute(sql, tuple(params))
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def get_goal_by_id(cls, goal_id, user_id=None):
        params = [goal_id]
        where_clause = "goal_id=%s"
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"""
        SELECT goal_id, user_id, goal_type, target_weight, daily_calorie_target, start_date, target_date, status
        FROM goal
        WHERE {where_clause}
        """
        cursor.execute(sql, tuple(params))
        return cls._from_row(cursor.fetchone())

    @classmethod
    def get_goals_for_user(cls, user_id, status=None):
        params = [user_id]
        where_clause = "user_id=%s"
        if status:
            where_clause += " AND status=%s"
            params.append(status)

        sql = f"""
        SELECT goal_id, user_id, goal_type, target_weight, daily_calorie_target, start_date, target_date, status
        FROM goal
        WHERE {where_clause}
        ORDER BY start_date DESC
        """
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
        return [cls._from_row(row) for row in rows]

    @classmethod
    def get_active_goal(cls, user_id):
        sql = """
        SELECT goal_id, user_id, goal_type, target_weight, daily_calorie_target, start_date, target_date, status
        FROM goal
        WHERE user_id=%s AND status='active'
        ORDER BY start_date DESC
        LIMIT 1
        """
        cursor.execute(sql, (user_id,))
        return cls._from_row(cursor.fetchone())

    def calculate_progress(self, current_weight=None, average_daily_calories=None):
        today = date.today()
        timeline_completion = None
        days_remaining = None

        if self.start_date and self.target_date:
            total_days = (self.target_date - self.start_date).days
            elapsed_days = (today - self.start_date).days
            if total_days > 0:
                timeline_completion = max(0.0, min(1.0, elapsed_days / total_days))
            days_remaining = (self.target_date - today).days

        weight_gap = None
        if self.target_weight is not None and current_weight is not None:
            weight_gap = round(current_weight - self.target_weight, 2)

        calorie_gap = None
        if self.daily_calorie_target is not None and average_daily_calories is not None:
            calorie_gap = int(average_daily_calories - self.daily_calorie_target)

        return {
            "timeline_completion": timeline_completion,
            "days_remaining": days_remaining,
            "weight_gap": weight_gap,
            "calorie_gap": calorie_gap,
        }

    def check_progress(self, current_weight=None, average_daily_calories=None):
        progress = self.calculate_progress(current_weight, average_daily_calories)

        if progress["timeline_completion"] is not None and progress["timeline_completion"] >= 1:
            if progress["weight_gap"] is not None and progress["weight_gap"] <= 0:
                return "completed"
            return "overdue"

        if progress["calorie_gap"] is not None and progress["calorie_gap"] > 0:
            return "at_risk"

        return "on_track"

    def to_dict(self):
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "goal_type": self.goal_type,
            "target_weight": self.target_weight,
            "daily_calorie_target": self.daily_calorie_target,
            "start_date": self.start_date,
            "target_date": self.target_date,
            "status": self.status,
        }
