"""ML artifact and training data paths."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")

MODEL_FILE = os.path.join(MODEL_DIR, "model.pkl")
TRAIN_DATA_FILE = os.path.join(DATA_DIR, "Practice_4.csv")
