#!/bin/bash
python -m spacy download en_core_web_sm
python services/train_resume_classifier.py
uvicorn main:app --host 0.0.0.0 --port $PORT