import pulp
import pandas as pd
import numpy as np
from typing import Dict
from data import Trainset
import shap

class InductionOptimizer:
    def __init__(self, fleet: Dict[str, Trainset], n_bays: int, n_service_slots: int, ibl_capacity: int):
        self.fleet = fleet
        self.n_bays = n_bays
        self.n_service_slots = n_service_slots
        self.ibl_capacity = ibl_capacity

        self.trainset_ids = list(fleet.keys())
        self.bays = [f"Bay_{i}" for i in range(1, n_bays + 1)]
        self.service_slots = [f"Service_{i}" for i in range(1, n_service_slots + 1)]
        self.problem = pulp.LpProblem("Fleet_Induction_Optimization", pulp.LpMaximize)

        # Decision Variables
        self.x = pulp.LpVariable.dicts(
            "assign_service",
            [(i, j) for i in self.trainset_ids for j in self.service_slots],
            cat="Binary"
        )
        self.y = pulp.LpVariable.dicts(
            "assign_bay",
            [(i, k) for i in self.trainset_ids for k in self.bays],
            cat="Binary"
        )
        self.z = pulp.LpVariable.dicts(
            "assign_ibl",
            [(i) for i in self.trainset_ids],
            cat="Binary"
        )

    # ---------------- Constraints ---------------- #
    def add_constraints(self):
        for i in self.trainset_ids:
            self.problem += (
                pulp.lpSum([self.x[(i, j)] for j in self.service_slots]) +
                pulp.lpSum([self.y[(i, k)] for k in self.bays]) +
                self.z[i] <= 1
            )
        for j in self.service_slots:
            self.problem += pulp.lpSum([self.x[(i, j)] for i in self.trainset_ids]) <= 1
        for k in self.bays:
            self.problem += pulp.lpSum([self.y[(i, k)] for i in self.trainset_ids]) <= 1
        self.problem += pulp.lpSum([self.z[i] for i in self.trainset_ids]) <= self.ibl_capacity

    # ---------------- Objective ---------------- #
    def set_objective(self, weights: Dict[str, float]):
        avg_mileage = np.mean([ts.current_mileage for ts in self.fleet.values()])

        objective = pulp.lpSum([
            # Service readiness
            weights.get("service_ready", 0.0) * (1 if ts.status=="On Time" else 0) * self.x[(i,j)] +
            # Branding exposure
            weights.get("branding", 0.0) * ts.branding_hours_left * self.x[(i,j)] +
            # Mileage balance
            weights.get("mileage_balance",0.0) * (1/(abs(ts.current_mileage - avg_mileage)+1)) * self.x[(i,j)] +
            # Shunt cost
            weights.get("shunt_cost",0.0) * (-min(ts.shunt_cost_to_bays.values())) * self.x[(i,j)]
            for i, ts in self.fleet.items() for j in self.service_slots
        ])
        # IBL penalty
        objective += pulp.lpSum([weights.get("ibl_penalty",0.0)*self.z[i] for i in self.trainset_ids])
        self.problem.setObjective(objective)

    # ---------------- Solve ---------------- #
    def solve(self) -> tuple[pd.DataFrame, float]:
        self.problem.solve(pulp.PULP_CBC_CMD(msg=False))
        if pulp.LpStatus[self.problem.status] != "Optimal":
            return pd.DataFrame(), 0.0

        solution = []
        for i in self.trainset_ids:
            assignment = {"train_id": i, "assignment": "Standby", "location": None}
            for j in self.service_slots:
                if self.x[(i,j)].varValue==1.0:
                    assignment.update({"assignment":"Service","location":j})
            for k in self.bays:
                if self.y[(i,k)].varValue==1.0:
                    assignment.update({"assignment":"Maintenance","location":k})
            if self.z[i].varValue==1.0:
                assignment.update({"assignment":"IBL","location":"IBL"})
            solution.append(assignment)
        return pd.DataFrame(solution), pulp.value(self.problem.objective)

    # ---------------- SHAP Explainability ---------------- #
    def explain_solution(self, weights: Dict[str,float]):
        fleet_df = pd.DataFrame([{
            "service_ready": 1 if ts.status=="On Time" else 0,
            "branding": ts.branding_hours_left,
            "mileage": ts.current_mileage,
            "shunt_cost": min(ts.shunt_cost_to_bays.values())
        } for ts in self.fleet.values()], index=self.fleet.keys())

        def objective_predict(X):
            scores = []
            avg_mileage = fleet_df["mileage"].mean()
            for idx,row in X.iterrows():
                score = (weights.get("service_ready",0.0)*row["service_ready"] +
                         weights.get("branding",0.0)*row["branding"] +
                         weights.get("mileage_balance",0.0)*(1/(abs(row["mileage"]-avg_mileage)+1)) +
                         weights.get("shunt_cost",0.0)*(-row["shunt_cost"]))
                scores.append(score)
            return np.array(scores)

        explainer = shap.Explainer(objective_predict, fleet_df)
        shap_values = explainer(fleet_df)
        return shap_values


# ---------------- Helper ---------------- #
def optimize_induction(fleet: Dict[str,Trainset], n_service_slots:int, ibl_capacity:int, n_bays:int, weights:Dict[str,float]):
    optimizer = InductionOptimizer(fleet, n_bays, n_service_slots, ibl_capacity)
    optimizer.add_constraints()
    optimizer.set_objective(weights)
    return optimizer.solve()
