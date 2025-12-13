from database import cursor
from datetime import datetime, timedelta

class Progress:

    @staticmethod
    def get_weekly_daily_summary(user_id, week_start):
        week_end = week_start + timedelta(days=6)

        sql = """
        SELECT
            summary_date,
            total_calories_consumed,
            total_calories_burned,
            net_calories,
            total_protein,
            total_carb,
            total_fat
        FROM daily_summary
        WHERE user_id = %s
        AND summary_date BETWEEN %s AND %s
        ORDER BY summary_date
        """

        cursor.execute(sql, (user_id, week_start, week_end))
        return cursor.fetchall()

    @staticmethod
    def get_weekly_water(user_id, week_start):
        week_end = week_start + timedelta(days=6)

        sql = """
        SELECT 
            DATE(logged_at),
            SUM(amount)
        FROM water_intake
        WHERE user_id = %s
        AND logged_at BETWEEN %s AND %s
        GROUP BY DATE(logged_at)
        """

        cursor.execute(sql, (user_id, week_start, week_end))
        return dict(cursor.fetchall())

    @staticmethod
    def get_weekly_sleep(user_id, week_start):
        week_end = week_start + timedelta(days=6)

        sql = """
        SELECT 
            sleep_date,
            hours
        FROM sleep_log
        WHERE user_id = %s
        AND sleep_date BETWEEN %s AND %s
        """

        cursor.execute(sql, (user_id, week_start, week_end))
        return dict(cursor.fetchall())

    @staticmethod
    def get_weekly_summary_boxes(user_id, week_start):
        week_end = week_start + timedelta(days=6)

        cursor.execute("""
            SELECT SUM(amount)
            FROM water_intake
            WHERE user_id=%s
            AND logged_at BETWEEN %s AND %s
        """, (user_id, week_start, week_end))
        total_water = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT AVG(hours)
            FROM sleep_log
            WHERE user_id=%s
            AND sleep_date BETWEEN %s AND %s
        """, (user_id, week_start, week_end))
        avg_sleep = cursor.fetchone()[0] or 0

        cursor.execute("SELECT current_weight FROM user WHERE user_id=%s", (user_id,))
        weight = cursor.fetchone()[0]

        return {
            "total_water_l": round(total_water / 1000, 2),
            "avg_sleep": round(avg_sleep, 2),
            "weight_change": 0.0,
            "current_weight": weight
        }

    @staticmethod
    def get_weekly_macros(user_id, week_start):
        week_end = week_start + timedelta(days=6)

        sql = """
        SELECT 
            SUM(total_protein),
            SUM(total_carb),
            SUM(total_fat)
        FROM daily_summary
        WHERE user_id=%s
        AND summary_date BETWEEN %s AND %s
        """

        cursor.execute(sql, (user_id, week_start, week_end))
        result = cursor.fetchone()

        return {
            "protein": result[0] or 0,
            "carbs": result[1] or 0,
            "fat": result[2] or 0,
            "sugar": 0,
            "fiber": 0
        }
