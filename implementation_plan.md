# PlayerScoutAlert Implementation Plan

This document outlines the steps to build and deploy the eFootball Player Scout Alert system. 

## Overview
The goal is to scrape `https://pesdb.net/efootball/?all=1&sort=time_added`, find the most recently added player, compare it to the last known player, and if it's different, send a Telegram message and update our records. This will be automated using GitHub Actions.

## Step 1: Project Setup
1. Create a folder named `PlayerScoutAlert` and initialize a git repository.
2. Create the following file structure:
   - `scraper.py`: The Python script that does the scraping and messaging.
   - `requirements.txt`: Python dependencies (`requests`, `beautifulsoup4`).
   - `last_player.txt`: A simple text file to store the most recently seen player's ID or Name (acts as our memory).
   - `.github/workflows/alert.yml`: The GitHub Actions workflow file.

## Step 2: Telegram Bot Setup
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the instructions to create a bot.
3. Copy the **HTTP API Token** provided by BotFather.
4. Start a chat with your new bot and send a random message like "hello".
5. Find your Chat ID (you can use bots like `@userinfobot` to get your ID).

## Step 3: Python Scraper (`scraper.py`)
The script will perform the following actions:
1. Fetch the URL: `https://pesdb.net/efootball/?all=1&sort=time_added`
2. Parse the HTML to extract the first player in the table (the newest addition).
3. Read `last_player.txt` to see who the last recorded player was.
4. If the new player is different from the one in `last_player.txt`:
   - Send a message to Telegram using the Bot Token and Chat ID.
   - Update `last_player.txt` with the new player's name/ID.
5. If it's the same, do nothing.

## Step 4: GitHub Actions Workflow (`alert.yml`)
The workflow will automate the scraper:
1. Trigger the workflow on a schedule (e.g., every 6 hours using `cron: '0 */6 * * *'`) and manually (`workflow_dispatch`).
2. Check out the repository code.
3. Set up Python and install dependencies from `requirements.txt`.
4. Run `scraper.py` passing the Telegram secrets via environment variables.
5. Check if `last_player.txt` was modified.
6. If modified, commit the changes to `last_player.txt` and push them back to the repository so the state is saved for the next run.

## Step 5: Deployment
1. Push the local git repository to a new repository on GitHub.
2. Go to the GitHub repository **Settings > Secrets and variables > Actions**.
3. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: The token from BotFather.
   - `TELEGRAM_CHAT_ID`: Your Telegram Chat ID.
4. Enable workflow read and write permissions (Settings > Actions > General > Workflow permissions -> "Read and write permissions") so the bot can commit the updated `last_player.txt`.
5. The action will run automatically based on the schedule, and you will receive a Telegram message whenever the page updates with a new player!
