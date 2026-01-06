import uuid
import time
import threading
from flask import Flask, jsonify, Blueprint, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flasgger import Swagger

from data import generate_hybrid_fleet
from optimizer import optimize_induction

# =====================================================
# App Initialization
# =====================================================
app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Hybrid Fleet Optimization API",
    "uiversion": 3
}

Swagger(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

fleet_api = Blueprint("fleet_api", __name__, url_prefix="/api/v1")

# =====================================================
# In-Memory Stores (Replace with DB / Redis later)
# =====================================================
FLEET_LIST = generate_hybrid_fleet(n_trainsets=25, n_bays=12)
FLEET_DICT = {ts.train_id: ts for ts in FLEET_LIST}
OPTIMIZATION_JOBS = {}

# =====================================================
# Utility Helpers
# =====================================================
def api_response(success=True, data=None, error=None, meta=None, status=200):
    return jsonify({
        "success": success,
        "data": data,
        "error": error,
        "meta": meta or {
            "timestamp": time.time(),
            "api_version": "v1"
        }
    }), status


# =====================================================
# Health Check
# =====================================================
@fleet_api.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service is running
    """
    return api_response(data={
        "service": "Hybrid Fleet Optimizer",
        "status": "UP"
    })


# =====================================================
# Fleet Status API
# =====================================================
@fleet_api.route("/fleet", methods=["GET"])
def get_fleet():
    """
    Get real-time fleet status
    ---
    responses:
      200:
        description: Fleet data
    """
    try:
        fleet_data = []
        for ts in FLEET_LIST:
            fleet_data.append({
                "train_id": ts.train_id,
                "train_name": ts.train_name,
                "status": "ON_TIME" if ts.avg_delay_min < 5 else "DELAYED",
                "telemetry": {
                    "scheduled_departure": ts.scheduled_departure.isoformat(),
                    "actual_departure": ts.actual_departure.isoformat(),
                    "current_mileage": ts.current_mileage,
                    "route_distance_km": ts.route_distance_km
                },
                "maintenance": {
                    "open_job_cards": ts.job_cards_open,
                    "branding_hours_left": ts.branding_hours_left
                },
                "stabling_bay": ts.stabling_bay,
                "shunt_cost": ts.shunt_cost_to_bays
            })

        return api_response(data=fleet_data)

    except Exception as e:
        return api_response(success=False, error=str(e), status=500)


# =====================================================
# Optimization Worker (Async Simulation)
# =====================================================
def run_optimization_job(job_id, params):
    try:
        socketio.emit("job_update", {"job_id": job_id, "status": "RUNNING"})

        weights = {
            "service_ready": 5.0,
            "branding": 2.0,
            "mileage_balance": 1.0,
            "shunt_cost": -1.0,
            "ibl_penalty": -10.0,
            "standby_preference": 0.5,
        }

        df, objective_value, explainability = optimize_induction(
            FLEET_DICT,
            n_service_slots=params["n_service_slots"],
            ibl_capacity=params["ibl_capacity"],
            n_bays=params["n_bays"],
            weights=weights,
            explain=True
        )

        OPTIMIZATION_JOBS[job_id]["status"] = "COMPLETED"
        OPTIMIZATION_JOBS[job_id]["result"] = {
            "objective_value": objective_value,
            "assignments": df.to_dict(orient="records"),
            "explainability": explainability
        }

        socketio.emit("job_update", {
            "job_id": job_id,
            "status": "COMPLETED"
        })

    except Exception as e:
        OPTIMIZATION_JOBS[job_id]["status"] = "FAILED"
        OPTIMIZATION_JOBS[job_id]["error"] = str(e)

        socketio.emit("job_update", {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(e)
        })


# =====================================================
# Trigger Optimization
# =====================================================
@fleet_api.route("/optimize", methods=["POST"])
def trigger_optimization():
    """
    Trigger optimization job
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            n_service_slots:
              type: integer
            ibl_capacity:
              type: integer
            n_bays:
              type: integer
    responses:
      202:
        description: Optimization started
    """
    try:
        payload = request.get_json(force=True)

        job_id = str(uuid.uuid4())
        OPTIMIZATION_JOBS[job_id] = {
            "status": "PENDING",
            "created_at": time.time(),
            "result": None
        }

        params = {
            "n_service_slots": payload.get("n_service_slots", 12),
            "ibl_capacity": payload.get("ibl_capacity", 4),
            "n_bays": payload.get("n_bays", 12)
        }

        thread = threading.Thread(
            target=run_optimization_job,
            args=(job_id, params)
        )
        thread.start()

        return api_response(
            data={"job_id": job_id},
            meta={"message": "Optimization job started"},
            status=202
        )

    except Exception as e:
        return api_response(success=False, error=str(e), status=500)


# =====================================================
# Optimization Job Status
# =====================================================
@fleet_api.route("/optimize/status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    job = OPTIMIZATION_JOBS.get(job_id)
    if not job:
        return api_response(success=False, error="Job not found", status=404)

    return api_response(data=job)


# =====================================================
# WebSocket Events
# =====================================================
@socketio.on("connect")
def ws_connect():
    emit("connected", {"message": "WebSocket connected"})


# =====================================================
# Register Blueprint
# =====================================================
app.register_blueprint(fleet_api)

# =====================================================
# Main
# =====================================================
if __name__ == "__main__":
    print("🚆 Hybrid Fleet Optimization API running on port 8000")
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
