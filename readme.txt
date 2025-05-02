# Voice Assistant Documentation

## Overview
This is a Python-based voice assistant that provides voice interaction capabilities with features including reminders, notes, and basic commands. The assistant uses speech recognition for input and text-to-speech for output.

## Key Features

### 1. Voice Interaction
- Wake word detection ("hey assistant" by default)
- Speech recognition for commands
- Text-to-speech responses
- Customizable voice settings

### 2. Reminder System
- Set reminders using natural language
- Flexible time formats (both relative and absolute)
- Background checking for due reminders
- List all upcoming reminders
- Automatic reminder notifications

### 3. Note Taking
- Voice-to-text note creation
- Timestamp for each note
- View all saved notes
- Chronological organization

### 4. Data Management
- Persistent storage using JSON
- Automatic data saving
- Error handling and recovery
- User preferences storage

## Requirements
- Python 3.x
- Required packages:
  - speech_recognition
  - pyttsx3
  - dateparser
  - threading
  - json
  - datetime
  - os

## Installation
1. Install required Python packages:
```bash
pip install speech_recognition pyttsx3 dateparser
