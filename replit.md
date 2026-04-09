# Star Collector

A mobile-first web application that helps users track progress toward personal goals through a gamified "star collection" system.

## Project Overview

Users set a target number of stars, track daily progress, reach milestones (25%, 50%, 75%), and earn rewards (e.g., "Movie Night", "Ice Cream").

## Architecture

- **Type**: Pure static single-page application — no build system, no dependencies
- **Frontend**: Single HTML file (`StarCollector.html` / `index.html`) with embedded Tailwind CSS (CDN), Vanilla JS, and Material Symbols icons
- **Storage**: `localStorage` for client-side persistence (stars, goal, milestones, check-in history)
- **Fonts**: Google Fonts (Plus Jakarta Sans, Be Vietnam Pro)

## Project Structure

```
.
├── index.html              # Main app (copy of StarCollector.html for web serving)
├── StarCollector.html      # Original source file
├── pages/
│   └── picturebook/
│       └── CHANGELOG.md    # Chinese development log / feature spec
└── replit.md               # This file
```

## Running the App

The app is served via Python's built-in HTTP server:

```
python3 -m http.server 5000 --bind 0.0.0.0
```

- Workflow: "Start application" on port 5000
- Deployment: Static site, public directory is `.`

## Key Features

- **Star tracking**: Tap to add a star toward a user-defined goal
- **Milestones**: Visual celebrations at 25%, 50%, and 75% progress
- **Calendar**: Daily check-in tracking and day streak counter
- **Rewards**: Preset or custom reward selection for goal completion
- **Month summary**: Stars earned this month displayed on home screen
