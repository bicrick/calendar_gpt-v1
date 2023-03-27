# AI Google Calendar Assistant

This repository contains an AI Google Calendar assistant that can help you schedule, modify, and delete events, and provide contextual information about your calendar using a chat model interface. Please note that this project is a work in progress and is by no means complete.

## Embeddings Framework

The assistant uses the text-embedding-ada-002 embeddings model from OpenAI to parse through your calendar and turn all of your events into embeddings that are stored in a Pinecone vector store. The `indexFunctions.py` file contains functions for the vector store and querying it to answer queries about the events and draw context between what the user is asking and the events on their calendar.

## Calendar Functions

To add, modify, and delete events, the assistant uses a number of functions that interact with the Google Calendar API. These functions are located in the `calendarFunctions.py` file. To modify the calendar using natural language, you will need to run the `agent.py` file and add your task to the `task` string before running the file.

## Configuration

To configure these files for your own use, you will need to add your own `credentials.json` file for the Google Calendar API, and generate an `authentication token.json` as well. Many of the functions require an `OPENAI_API_KEY` to be added to your environment variables. If you want to set up your own Pinecone vector store for your own events, you will also need to add an environment variable for your `PINECONE_API_KEY`.

# Setting Up Your Virtual Environment

Before you can run this project, you need to set up your environment. Here are the steps you should follow:

## 1. Install Python

You'll need to install Python on your machine. You can download Python from the official website at https://www.python.org/downloads/.

## 2. Create a Virtual Environment

It's best practice to create a virtual environment for your project. This will help ensure that your dependencies are isolated from other Python projects on your machine.

To create a virtual environment, open a terminal window and run the following command:

python3 -m venv env


This will create a new virtual environment in a directory named `env`.

## 3. Activate the Virtual Environment

To activate the virtual environment, run the following command in your terminal:

source env/bin/activate


This will activate the virtual environment and you should see `(env)` appear at the beginning of your terminal prompt.

## 4. Install the Dependencies

The project dependencies are listed in the `requirements.txt` file. To install them, run the following command:

pip install -r requirements.txt


This will install all the necessary packages and dependencies required to run the project.

