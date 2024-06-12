import matplotlib.pyplot as plt
import pandas as pd

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

# Define the Patient agent
class PatientAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.status = "waiting"
        self.waiting_time = random.randint(12, 24)
        self.color = (255, 255, 255)  # White
        self.is_emergency = random.random() < 0.1  # 10% chance of being an emergency case

        if self.is_emergency:
            self.status = "emergency"
            self.color = (255, 0, 0)  # Red

    def step(self):
        if self.status == "waiting":
            self.move()
            if self.model.registration_desks.count_empty() > 0:
                self.status = "registering"
                self.model.registration_desks.add_patient(self)
                if self in self.model.waiting_room:
                    self.model.waiting_room.remove(self)
        elif self.status == "registering":
            self.waiting_time -= 1
            if self.waiting_time <= 0:
                self.status = random.choices(
                    ["registered_green", "registered_yellow"],
                    weights=[0.7, 0.3]
                )[0]
                if self.status == "registered_green":
                    self.color = (0, 255, 0)  # Green
                else:
                    self.color = (255, 255, 0)  # Yellow
        elif self.status == "emergency":
            if self not in self.model.emergency_room:
                self.model.emergency_room.add(self)
                self.model.emergency_count += 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

# Define the Registration Desk agent
class RegistrationDesk:
    def __init__(self, model, capacity):
        self.model = model
        self.capacity = capacity
        self.patients = []

    def count_empty(self):
        return self.capacity - len(self.patients)

    def add_patient(self, patient):
        if self.count_empty() > 0:
            self.patients.append(patient)
            return True
        return False

    def step(self):
        for patient in self.patients[:]:
            if patient.status in ["registered_green", "registered_yellow"]:
                self.patients.remove(patient)
                if patient.status == "registered_green":
                    self.model.green_count += 1
                else:
                    self.model.yellow_count += 1

# Define the Hospital model
class HospitalModel(Model):
    def __init__(self, N, width, height, desk_capacity):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.registration_desks = RegistrationDesk(self, desk_capacity)
        self.waiting_room = set()
        self.emergency_room = set()
        self.green_count = 0
        self.yellow_count = 0
        self.emergency_count = 0

        self.datacollector = DataCollector(
            {
                "Waiting": lambda m: sum([1 for a in m.schedule.agents if a.status == "waiting"]),
                "Registering": lambda m: sum([1 for a in m.schedule.agents if a.status == "registering"]),
                "Registered_Green": lambda m: m.green_count,
                "Registered_Yellow": lambda m: m.yellow_count,
                "Emergency": lambda m: m.emergency_count,
            }
        )

        # Create agents
        for i in range(self.num_agents):
            patient = PatientAgent(i, self)
            self.grid.place_agent(patient, (random.randrange(self.grid.width), random.randrange(self.grid.height)))
            self.schedule.add(patient)
            if patient.status == "emergency":
                self.emergency_room.add(patient)
                self.emergency_count += 1
            else:
                self.waiting_room.add(patient)

    def step(self):
        self.schedule.step()
        self.registration_desks.step()
        self.datacollector.collect(self)

# Run the model
model = HospitalModel(120, 20, 20, 3)  # 120 patients per day
for i in range(240):
    model.step()

# Collect results
results = model.datacollector.get_model_vars_dataframe()
print(results)

# Save the results as a table image
def save_dataframe_as_image(df, path):
    fig, ax = plt.subplots(figsize=(10, 6))  # Set the size of the table
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    plt.savefig(path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

save_dataframe_as_image(results, 'hospital_simulation_results.png')
