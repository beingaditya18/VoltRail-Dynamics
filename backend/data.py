import pandas as pd
import random
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timedelta

@dataclass
class Trainset:
    train_id: str
    train_name: str
    day: str
    date: str
    scheduled_departure: str
    scheduled_arrival: str
    actual_departure: str
    actual_arrival: str
    status: str
    route_distance_km: float
    avg_delay_min: float
    fitness_rolling_valid: int
    fitness_signalling_valid: int
    fitness_telecom_valid: int
    job_cards_open: int
    branding_hours_left: float
    current_mileage: int
    cleaning_slots_needed: int
    stabling_bay: int
    shunt_cost_to_bays: Dict[int, float]

def generate_hybrid_fleet(n_trainsets: int = 25, n_bays: int = 12, seed: int = 42) -> List[Trainset]:
    random.seed(seed)
    train_names = [
        "Shatabdi Express", "Rajdhani Express", "Duronto Express",
        "Garib Rath", "Tejas Express", "Vande Bharat", "Sampark Kranti",
        "Intercity Express", "Jan Shatabdi", "Humsafar Express"
    ]
    
    fleet = []
    today = datetime.now()
    
    for i in range(n_trainsets):
        tid = f"R{i+1:03d}"
        name = random.choice(train_names)
        
        dep_time = today + timedelta(hours=random.randint(1, 72))
        arr_time = dep_time + timedelta(hours=random.randint(2, 20))
        delay = random.choice([0, 5, 10, 20, 30, 60])
        actual_dep = dep_time + timedelta(minutes=delay)
        actual_arr = arr_time + timedelta(minutes=delay)
        status = "On Time" if delay == 0 else "Delayed"
        
        route_km = random.uniform(100, 2000)
        avg_delay = random.uniform(0, 120)
        
        fitness_rolling_valid = random.randint(-2, 10)
        fitness_signalling_valid = random.randint(-1, 10)
        fitness_telecom_valid = random.randint(-1, 10)
        job_cards_open = random.choices([0, 1, 2], weights=[0.6,0.3,0.1])[0]
        branding_hours_left = random.choice([0,12,24,36,48])
        current_mileage = int(route_km * random.uniform(500,1500))
        cleaning_slots_needed = random.choices([0,1,2,3], weights=[0.5,0.3,0.15,0.05])[0]
        stabling_bay = random.randint(1, n_bays)
        shunt_cost_to_bays = {b: abs(b - stabling_bay) + random.random()*0.5 for b in range(1, n_bays+1)}
        
        fleet.append(Trainset(
            train_id=tid,
            train_name=name,
            day=dep_time.strftime("%A"),
            date=dep_time.strftime("%Y-%m-%d"),
            scheduled_departure=dep_time.strftime("%H:%M"),
            scheduled_arrival=arr_time.strftime("%H:%M"),
            actual_departure=actual_dep.strftime("%H:%M"),
            actual_arrival=actual_arr.strftime("%H:%M"),
            status=status,
            route_distance_km=route_km,
            avg_delay_min=avg_delay,
            fitness_rolling_valid=fitness_rolling_valid,
            fitness_signalling_valid=fitness_signalling_valid,
            fitness_telecom_valid=fitness_telecom_valid,
            job_cards_open=job_cards_open,
            branding_hours_left=branding_hours_left,
            current_mileage=current_mileage,
            cleaning_slots_needed=cleaning_slots_needed,
            stabling_bay=stabling_bay,
            shunt_cost_to_bays=shunt_cost_to_bays
        ))
    
    return fleet
