from flask import Blueprint, request, jsonify
from water_intake import WaterIntake

water_api = Blueprint("water_api", __name__)

@water_api.post("/water")
def add_water():
    data = request.json
    w = WaterIntake(
        waterIntakeID=None,
        userID=data["user_id"],
        amount=data["amount"],
        unit=data["unit"],
        loggedAt=None
    )
    w.addIntake()
    return jsonify({"message": "Water logged"}), 201


@water_api.get("/water/history/<int:user_id>")
def water_history(user_id):
    history = WaterIntake.getIntakeHistory(user_id)
    return jsonify([
        {
            "water_id": h.waterIntakeID,
            "user_id": h.userID,
            "amount": h.amount,
            "unit": h.unit,
            "logged_at": str(h.loggedAt)
        } 
        for h in history
    ])


@water_api.get("/water/total/<int:user_id>")
def daily_water_total(user_id):
    date_str = request.args.get("date")
    total = WaterIntake.getDailyTotal(userID=user_id, date_str=date_str)
    return jsonify({"total_amount": total})
