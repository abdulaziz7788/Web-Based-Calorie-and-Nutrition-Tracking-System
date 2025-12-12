from database import cursor, db


class Activity:
    def __init__(self, activity_id, activity_name, activity_category, calories_per_minute, description=None):
        self.activity_id = activity_id
        self.activity_name = activity_name
        self.activity_category = activity_category
        self.calories_per_minute = float(calories_per_minute)
        self.description = description or ""

    @classmethod
    def _from_row(cls, row):
        if not row:
            return None
        activity_id, name, category, calories_per_minute, description = row
        return cls(
            activity_id=activity_id,
            activity_name=name,
            activity_category=category,
            calories_per_minute=calories_per_minute,
            description=description,
        )

    @classmethod
    def get_activity_details(cls, activity_id):
        sql = """
        SELECT activity_id, activity_name, activity_category, calories_per_minute, description
        FROM activity
        WHERE activity_id = %s
        """
        cursor.execute(sql, (activity_id,))
        return cls._from_row(cursor.fetchone())

    @classmethod
    def get_activity_list(cls, category=None):
        if category:
            sql = """
            SELECT activity_id, activity_name, activity_category, calories_per_minute, description
            FROM activity
            WHERE activity_category = %s
            ORDER BY activity_name
            """
            cursor.execute(sql, (category,))
        else:
            sql = """
            SELECT activity_id, activity_name, activity_category, calories_per_minute, description
            FROM activity
            ORDER BY activity_name
            """
            cursor.execute(sql)

        rows = cursor.fetchall() or []
        return [cls._from_row(row) for row in rows]

    @classmethod
    def search_activity(cls, keyword):
        like_query = f"%{keyword}%"
        sql = """
        SELECT activity_id, activity_name, activity_category, calories_per_minute, description
        FROM activity
        WHERE activity_name LIKE %s OR description LIKE %s
        ORDER BY activity_name
        """
        cursor.execute(sql, (like_query, like_query))
        rows = cursor.fetchall() or []
        return [cls._from_row(row) for row in rows]

    @classmethod
    def get_by_name(cls, activity_name):
        sql = """
        SELECT activity_id, activity_name, activity_category, calories_per_minute, description
        FROM activity
        WHERE LOWER(activity_name) = LOWER(%s)
        LIMIT 1
        """
        cursor.execute(sql, (activity_name,))
        return cls._from_row(cursor.fetchone())

    @classmethod
    def add_new_activity(cls, activity_name, activity_category, calories_per_minute, description=None):
        sql = """
        INSERT INTO activity (activity_name, activity_category, calories_per_minute, description)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (activity_name, activity_category, calories_per_minute, description))
        db.commit()
        return cls(
            activity_id=cursor.lastrowid,
            activity_name=activity_name,
            activity_category=activity_category,
            calories_per_minute=calories_per_minute,
            description=description or "",
        )

    @classmethod
    def get_categories(cls):
        sql = "SELECT DISTINCT activity_category FROM activity ORDER BY activity_category"
        cursor.execute(sql)
        rows = cursor.fetchall() or []
        return [row[0] for row in rows if row and row[0] is not None]

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "activity_name": self.activity_name,
            "activity_category": self.activity_category,
            "calories_per_minute": self.calories_per_minute,
            "description": self.description,
        }
