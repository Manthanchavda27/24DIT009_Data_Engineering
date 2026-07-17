from generate_data import *
from profile_data import profile
from validate_data import validate
from database import store

print("Generating data...")
print("--------------------")

profile()

print("--------------------")

validate()

print("--------------------")

store()

print("--------------------")

print("Project Completed Successfully.")