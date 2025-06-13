![](https://github.com/ahlashkari/Benign-User-Profiler-BUP/blob/main/bccc.jpg)

# Benign User Profiler (BUP)

BUP is a tool for generating benign user traffic patterns for security research and testing. It simulates realistic user behavior across various protocols and applications.

# Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Traffic Models](#traffic-models)
- [Citation and Copyright 2024](#citation-and-copyright-2024)
- [Project Team members](#project-team-members)
- [Acknowledgement](#acknowledgement)

# Features

- **Multi-protocol support**: HTTP/HTTPS, SSH, FTP/SFTP, SMTP, IMAP, and command-line operations
- **Real Browser Support**: Interact with real Firefox browser for authentic traffic generation
- **YouTube support**: Visit YouTube, search for videos, watch content, and interact with playback controls
- **SoundCloud integration**: Browse and listen to music on SoundCloud
- **Google Search**: Perform Google searches and click on search results
- **Media download simulation**: Download images from various sources like Unsplash
- **Email capabilities**: Send and receive emails with attachments via Gmail and other providers
- **Application launching**: Open and interact with random applications on Windows and Linux
- **Office document integration**: Create and save documents using Microsoft Office (Windows) or LibreOffice (Linux) for email attachments
- **Network scanning**: Ping local network addresses to simulate network discovery
- **Scheduling**: Configure frequency and timing of activities with work hours restrictions and optional task randomization
- **Cross-platform**: Works on Linux and Windows with platform-specific implementations

# Installation

You must install the requirements in your system before you can begin installing or running anything. To do so, you can easily run this command:

```bash
pip3 install -r requirements.txt
```

You are now ready to install BenignUserProfiler. In order to do so, you should run this command, which will install the BenignUserProfiler package in your system:

```bash
python3 setup.py install
```

# Usage

## Standard Execution

To execute the program with simulated traffic, run this command:

```bash
benign-user-profiler
```

You can use `-h` to see different options of the program:

```bash
# Run with default config file
benign-user-profiler

# Run with a specific config file
benign-user-profiler --config /path/to/config.json

# Run with parallel execution
benign-user-profiler --parallel

# Run with work hours restrictions (9am-5pm by default)
benign-user-profiler --work-hours

# Run with custom work hours
benign-user-profiler --work-hours "10:00-18:00"

# Run with randomized task execution (shuffles task order regardless of start times)
benign-user-profiler --randomize
```

## Real Traffic Generation

For realistic traffic generation with actual browser interaction, use the included script:

```bash
# Run with real browser interaction
./run_real_traffic.sh

# Run in headless mode (no visible browser windows)
./run_real_traffic.sh --headless

# Run in simulation mode (no real browser interaction)
./run_real_traffic.sh --simulate
```

### Requirements for Real Traffic

Real traffic generation has the following dependencies:

#### Linux:
- Firefox browser
- xdotool (for keyboard/mouse simulation)
- LibreOffice (for document creation)

#### Windows:
- Firefox browser
- PowerShell (for application control)
- Microsoft Office (for document creation)

The `run_real_traffic.sh` script will check for these dependencies and warn you if any are missing.

## Configuration

The tool is configured via a JSON file (`config.json`). Here's a sample configuration:

```json
{
  "web_browsing": {
    "type": "HTTP",
    "randomize": true,
    "websites": [
      "https://www.wikipedia.org",
      "https://www.github.com",
      "https://www.reddit.com"
    ],
    "visit_sublinks": {
      "enabled": true,
      "depth": 2,
      "max_links": 4
    },
    "frequency": 2,
    "time_interval": [600, 1200],
    "start_time": "09:00",
    "start_time_format": "%H:%M",
    "work_hours": {
      "start": "09:00",
      "end": "17:00"
    }
  },
  "youtube_browsing": {
    "type": "HTTP",
    "website": "youtube",
    "youtube_searches": ["python programming", "cloud computing", "machine learning"],
    "youtube_min_watch": 60,
    "youtube_max_watch": 180,
    "frequency": 1,
    "time_interval": [1200, 3600],
    "start_time": "10:30",
    "start_time_format": "%H:%M"
  },
  "soundcloud_listening": {
    "type": "HTTP",
    "website": "soundcloud",
    "soundcloud_searches": ["electronic music", "ambient", "rock", "pop", "jazz"],
    "soundcloud_min_listen": 60,
    "soundcloud_max_listen": 300,
    "frequency": 1,
    "time_interval": [2400, 4800],
    "start_time": "14:30",
    "start_time_format": "%H:%M"
  },
  "random_apps": {
    "type": "CMD",
    "linux_apps": [
      "gnome-calculator",
      "gedit",
      "nautilus"
    ],
    "windows_apps": [
      "calc.exe",
      "notepad.exe",
      "explorer.exe"
    ],
    "min_apps_to_open": 2,
    "max_apps_to_open": 4,
    "app_use_time_min": 30,
    "app_use_time_max": 300,
    "frequency": 2,
    "time_interval": [1800, 3600]
  },
  "microsoft_office": {
    "type": "CMD",
    "windows_commands": [
      {
        "command": "start winword",
        "platform": "windows",
        "description": "Open Microsoft Word",
        "use_time": [120, 600]
      }
    ],
    "create_office_docs": true,
    "frequency": 1,
    "time_interval": [5400, 10800]
  }
}
```

See `config.json` for a complete example with all supported protocols.

### Task Scheduling and Randomization

By default, tasks are scheduled and executed based on their start times. You can enable task randomization in two ways:

1. Using the `--randomize` command-line flag: This will randomize all tasks regardless of their configured start times.
2. Setting `"randomize": true` in individual model configurations: This allows you to control which specific tasks/models should be randomized.

When randomization is enabled, tasks will be executed in a random order rather than strictly by their start times. This creates more realistic and less predictable traffic patterns.

This project has been successfully tested on Ubuntu 22.04. It should work on other versions of Ubuntu OS (or even Debian OS) as long as your system has the necessary python3 packages (you can see the required packages in the `requirements.txt` file).

# Architecture

![](./architecture.svg)

# Traffic Models

BUP supports the following traffic models:

## HTTP/HTTPS
- Real browser-based web browsing using Firefox
- Multi-site navigation with realistic scrolling and tab behavior
- YouTube integration for watching videos with playback control (play, pause, fullscreen)
- SoundCloud music browsing and listening
- Google search with result clicking
- Media downloading from sources like Unsplash
- Configurable sublink navigation with depth control
- Human-like behavior with realistic timing between actions
- Work hours restrictions for realistic usage patterns

## Email
- SMTP for sending emails
- IMAP for receiving emails
- Support for Gmail, Outlook, and other providers
- Attachment handling with generated Microsoft Office documents
- Automated email generation with realistic content

## Command Line
- Execute system commands
- Platform-specific command execution (Windows/Linux)
- Launch and interact with random applications
- Office document creation:
  - Microsoft Office (Word, Excel, PowerPoint) on Windows
  - LibreOffice (Writer, Calc, Impress) on Linux
- Lorem Ipsum content generation for documents
- Network scanning with ping
- Simulated keyboard input for realistic app interaction
- Application lifecycle management (opening, using, closing)

## SSH
- Connect to remote servers
- Execute commands
- Authentication with username/password

## FTP/SFTP
- File transfers
- Directory listing
- File uploading/downloading

# Citation and Copyright 2024

For citation in your works and also to understand BUP completely, you can find below the published paper:

"Toward Generating a New Cloud-Based Distributed Denial of Service (DDoS) Dataset and Cloud Intrusion Traffic Characterization", Shafi, MohammadMoein, Arash Habibi Lashkari, Vicente Rodriguez, and Ron Nevo.; Information 15, no. 4: 195. https://doi.org/10.3390/info15040195

```
@Article{info15040195,
AUTHOR = {Shafi, MohammadMoein and Lashkari, Arash Habibi and Rodriguez, Vicente and Nevo, Ron},
TITLE = {Toward Generating a New Cloud-Based Distributed Denial of Service (DDoS) Dataset and Cloud Intrusion Traffic Characterization},
JOURNAL = {Information},
VOLUME = {15},
YEAR = {2024},
NUMBER = {4},
ARTICLE-NUMBER = {195},
URL = {https://www.mdpi.com/2078-2489/15/4/195},
ISSN = {2078-2489},
DOI = {10.3390/info15040195}
}
```

# Project Team Members

* [**Arash Habibi Lashkari:**](http://ahlashkari.com/index.asp) Founder and supervisor

* [**Moein Shafi:**](https://github.com/moein-shafi) Graduate researcher and developer - York University

# Acknowledgement
This project has been made possible through funding from the Natural Sciences and Engineering Research Council of Canada — NSERC (#RGPIN-2020-04701) and Canada Research Chair (Tier II) - (#CRC-2021-00340) to Arash Habibi Lashkari.