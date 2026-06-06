# AI WhatsApp Lead Management System

AI-powered lead management platform built with FastAPI, PostgreSQL, React, and WhatsApp Cloud API.

## Features

* Receive WhatsApp messages
* Automatically create and manage leads
* Store complete conversation history
* Generate AI-powered conversation summaries
* Generate AI reply drafts
* Human approval before sending messages
* Send WhatsApp messages directly from the dashboard

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic

### Frontend

* React
* Vite
* Axios

### AI

* DeepSeek V4 Flash

### Messaging

* WhatsApp Cloud API

## Project Structure

```text
Backend
├── Models
├── Services
├── DTOs
├── APIs
└── Database

Frontend
├── Dashboard
├── Sidebar
├── Chat Window
└── Draft Box
```

## Workflow

```text
WhatsApp User
      ↓
Webhook
      ↓
Store Message
      ↓
Open Chat
      ↓
Generate Summary
      ↓
Generate AI Draft
      ↓
Review Draft
      ↓
Send Reply
```

## Core Modules

### User Management

Stores lead information such as:

* Name
* Phone Number
* Email
* Source

### Conversation Management

Stores:

* Incoming messages
* Outgoing messages
* Message timestamps
* Sender information

### AI Summarization

Maintains conversation summaries to reduce token usage and improve context management.

### AI Draft Generation

Creates suggested replies based on:

* Conversation summary
* Recent messages

### WhatsApp Integration

Handles:

* Incoming webhooks
* Outgoing messages
* Lead identification

## Getting Started

### Backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

## Future Enhancements

* Multi-channel support (Email, Instagram, Website Chat)
* Team assignment
* Analytics dashboard
* RAG knowledge base
* CRM integrations
* AI agents and workflow automation

## Status

🚀 MVP Completed

Current Version:

* Backend Complete
* WhatsApp Integration Complete
* AI Draft Generation Complete
* React Dashboard In Progress
