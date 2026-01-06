import uuid
import time
from flask import Flask, jsonify, Blueprint
from data import generate_hybrid_fleet
from optimizer import optimize_induction

# Initialize Flask app and Blueprint
app = Flask(__name__)
fleet_api = Blueprint("fleet_api", __name__, url_prefix="/api/v1")

# In a production system, this data would be stored in a persistent database
# For this example, we'll keep it as a singleton.
# Future enhancement: use a dynamic data store or a caching layer.
FLEET_LIST = generate_hybrid_fleet(n_trainsets=25, n_bays=12)
FLEET_DICT = {ts.train_id: ts for ts in FLEET_LIST}

# Placeholder for a task queue. In a real-world scenario, this would
# connect to a distributed system like Celery, RQ, or a cloud service.
OPTIMIZATION_JOBS = {}


@fleet_api.route("/fleet")
def get_fleet_status():
    """Returns the real-time status of the hybrid fleet."""
    try:
        data = [
            {
                "train_id": ts.train_id,
                "train_name": ts.train_name,
                "current_status": "On Time" if ts.avg_delay_min < 5 else "Delayed",
                "telemetry": {
                    "scheduled_departure": ts.scheduled_departure.isoformat(),
                    "scheduled_arrival": ts.scheduled_arrival.isoformat(),
                    "actual_departure": ts.actual_departure.isoformat(),
                    "actual_arrival": ts.actual_arrival.isoformat(),
                    "current_mileage": ts.current_mileage,
                    "route_distance_km": ts.route_distance_km,
                },
                "maintenance_log": {
                    "open_job_cards": ts.job_cards_open,
                    "branding_hours_remaining": ts.branding_hours_left,
                    "last_service_check": ts.current_mileage - 1000, # A futuristic placeholder
                },
                "stabling_location": ts.stabling_bay,
                "cleaning_slots_needed": ts.cleaning_slots_needed,
                "logistics_cost": {
                    str(k): v for k, v in ts.shunt_cost_to_bays.items()
                },
            }
            for ts in FLEET_LIST
        ]
        return jsonify({"data": data, "timestamp": time.time()})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve fleet data: {e}"}), 500


@fleet_api.route("/optimize", methods=["POST"])
def trigger_optimization():
    """
    Triggers a fleet induction optimization task.
    This is an asynchronous operation.
    """
    try:
        # Generate a unique ID for the optimization job
        job_id = str(uuid.uuid4())
        OPTIMIZATION_JOBS[job_id] = {"status": "pending", "result": None}

        # In a real system, you would enqueue the task here.
        # For this example, we will run the function directly.
        # task_queue.enqueue(run_optimization_job, job_id)
        # However, for this simplified example, we'll run it synchronously
        # to demonstrate the function, but the conceptual model is async.

        weights = {
            "service_ready": 5.0,
            "branding": 2.0,
            "mileage_balance": 1.0,
            "shunt_cost": -1.0,
            "ibl_penalty": -10.0,
            "standby_preference": 0.5,
        }
        df, objective_value = optimize_induction(
            FLEET_DICT,
            n_service_slots=12,
            ibl_capacity=4,
            n_bays=12,
            weights=weights,
        )

        result_data = {
            "objective_value": objective_value,
            "assignments": df.to_dict(orient="records"),
        }
        OPTIMIZATION_JOBS[job_id]["status"] = "completed"
        OPTIMIZATION_JOBS[job_id]["result"] = result_data

        # Return a 202 status to indicate the request was accepted for processing
        return jsonify({"request_id": job_id, "status": "Optimization job started."}), 202

    except Exception as e:
        return jsonify({"error": f"Failed to start optimization job: {e}"}), 500


@fleet_api.route("/optimize/status/<job_id>")
def get_optimization_status(job_id: str):
    """
    Checks the status of a specific optimization job.
    """
    job = OPTIMIZATION_JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404
    
    return jsonify(job), 200


# Register the blueprint with the Flask application
app.register_blueprint(fleet_api)

if __name__ == "__main__":
    # In a production environment, you would use a WSGI server like Gunicorn or uWSGI
    # and a task queue for background jobs.
    app.run(debug=True, port=8000)