from datetime import date, datetime, time, timedelta

from database import cursor, db


class Sleep:
    def __init__(
        self,
        sleep_log_id,
        user_id,
        sleep_date,
        bedtime,
        wake_time,
        hours_slept=None,
        sleep_quality=None,
        notes=None,
    ):
        self.sleep_log_id = sleep_log_id
        self.user_id = user_id
        self.sleep_date = sleep_date
        self.bedtime = bedtime
        self.wake_time = wake_time
        self.hours_slept = float(hours_slept) if hours_slept is not None else None
        self.sleep_quality = sleep_quality
        self.notes = notes or ""

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
        sleep_log_id, user_id, sleep_date, bedtime, wake_time, hours_slept, sleep_quality, notes = row
        return cls(
            sleep_log_id=sleep_log_id,
            user_id=user_id,
            sleep_date=sleep_date,
            bedtime=bedtime,
            wake_time=wake_time,
            hours_slept=hours_slept,
            sleep_quality=sleep_quality,
            notes=notes,
        )

    @staticmethod
    def calculate_hours_slept(bedtime, wake_time):
        bed_time_obj = Sleep._parse_time(bedtime)
        wake_time_obj = Sleep._parse_time(wake_time)
        if not bed_time_obj or not wake_time_obj:
            return None

        today = date.today()
        bed_dt = datetime.combine(today, bed_time_obj)
        wake_dt = datetime.combine(today, wake_time_obj)

        if wake_dt <= bed_dt:
            wake_dt += timedelta(days=1)

        hours = (wake_dt - bed_dt).total_seconds() / 3600
        return round(hours, 2)

    @classmethod
    def log_sleep(
        cls,
        user_id,
        sleep_date=None,
        bedtime=None,
        wake_time=None,
        sleep_quality=None,
        notes=None,
        hours_slept=None,
    ):
        sleep_date = cls._parse_date(sleep_date) or date.today()
        bedtime = cls._parse_time(bedtime)
        wake_time = cls._parse_time(wake_time)

        calculated_hours = cls.calculate_hours_slept(bedtime, wake_time)
        hours_value = hours_slept if hours_slept is not None else calculated_hours

        sql = """
        INSERT INTO sleep_log (user_id, sleep_date, bedtime, wake_time, hours_slept, sleep_quality, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (user_id, sleep_date, bedtime, wake_time, hours_value, sleep_quality, notes),
        )
        db.commit()

        return cls(
            sleep_log_id=cursor.lastrowid,
            user_id=user_id,
            sleep_date=sleep_date,
            bedtime=bedtime,
            wake_time=wake_time,
            hours_slept=hours_value,
            sleep_quality=sleep_quality,
            notes=notes,
        )

    @classmethod
    def update_sleep_log(cls, sleep_log_id, user_id=None, **fields):
        allowed_fields = {
            "sleep_date",
            "bedtime",
            "wake_time",
            "hours_slept",
            "sleep_quality",
            "notes",
        }
        updates = {k: v for k, v in fields.items() if k in allowed_fields and v is not None}
        if not updates:
            raise ValueError("No valid fields provided for update")

        if "sleep_date" in updates:
            updates["sleep_date"] = cls._parse_date(updates["sleep_date"])
        if "bedtime" in updates:
            updates["bedtime"] = cls._parse_time(updates["bedtime"])
        if "wake_time" in updates:
            updates["wake_time"] = cls._parse_time(updates["wake_time"])

        if "hours_slept" not in updates and "bedtime" in updates and "wake_time" in updates:
            updates["hours_slept"] = cls.calculate_hours_slept(updates["bedtime"], updates["wake_time"])

        set_clause = ", ".join([f"{field}=%s" for field in updates])
        params = list(updates.values())

        where_clause = "sleep_log_id=%s"
        params.append(sleep_log_id)
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"UPDATE sleep_log SET {set_clause} WHERE {where_clause}"
        cursor.execute(sql, tuple(params))
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def delete_sleep_log(cls, sleep_log_id, user_id=None):
        params = [sleep_log_id]
        where_clause = "sleep_log_id=%s"
        if user_id:
            where_clause += " AND user_id=%s"
            params.append(user_id)

        sql = f"DELETE FROM sleep_log WHERE {where_clause}"
        cursor.execute(sql, tuple(params))
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def get_sleep_history(cls, user_id, start_date=None, end_date=None, limit=30):
        filters = ["user_id=%s"]
        params = [user_id]

        if start_date:
            filters.append("sleep_date >= %s")
            params.append(cls._parse_date(start_date))
        if end_date:
            filters.append("sleep_date <= %s")
            params.append(cls._parse_date(end_date))

        where_clause = " AND ".join(filters)
        sql = f"""
        SELECT sleep_log_id, user_id, sleep_date, bedtime, wake_time, hours_slept, sleep_quality, notes
        FROM sleep_log
        WHERE {where_clause}
        ORDER BY sleep_date DESC, bedtime DESC
        """
        if limit:
            sql += " LIMIT %s"
            params.append(int(limit))

        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
        return [cls._from_row(row) for row in rows]

    @classmethod
    def get_latest_sleep(cls, user_id):
        sql = """
        SELECT sleep_id, user_id, hours, sleep_date
        FROM sleep_log
        WHERE user_id=%s
        ORDER BY sleep_date DESC
        LIMIT 1
        """
        cursor.execute(sql, (user_id,))
        return cls._from_row(cursor.fetchone())

    @classmethod
    def get_average_sleep(cls, user_id, days=7):
        days = int(days) if days else 7
        start_date = date.today() - timedelta(days=days - 1)

        sql = """
        SELECT AVG(hours_slept)
        FROM sleep_log
        WHERE user_id = %s AND sleep_date >= %s
        """
        cursor.execute(sql, (user_id, start_date))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] is not None else None

    def to_dict(self):
        return {
            "sleep_log_id": self.sleep_log_id,
            "user_id": self.user_id,
            "sleep_date": self.sleep_date,
            "bedtime": self.bedtime,
            "wake_time": self.wake_time,
            "hours_slept": self.hours_slept,
            "sleep_quality": self.sleep_quality,
            "notes": self.notes,
        }
