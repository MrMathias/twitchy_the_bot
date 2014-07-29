twitchy_the_top_bot
===============

A reddit bot that get the most viewed twitch streams of a game

#Setup

* Open config.py and add the reddit username and password of the bot, as well as the twitch-game and the number of streams you want to display

* Copy the CSS from css.css to your subreddit's stylesheet to have the thumbnail images displayed. This can be editted as needed for your own subreddit's stylesheet. - The CSS might be bad, I have no idea what I am doing.

* In your sidebar, add these two markers where you want the stream to display:

---
    [](#TwitchStartMarker)

    [](#TwitchEndMarker)
---

#Running 

The script only runs once, then exits. You need to run it on a cron job/schedule however often you want it to run. The recommended time is every 10 minutes. 

Alternatively, you can add a while loop and a time.sleep(600) so it will run continually, but only loop every 10 minutes.

#Contact 

If you have any issues with this bot, you can message me on reddit at /u/captainhatdog, if you have questions about the CSS you will likely have more luck asking the org. creator /u/andygmb.
