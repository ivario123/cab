# CAB
is a simple canvas discord integration.

It sends a message to the webhook defined in the auth.cfg file detailing the link and assignment info for the next assignemnt
in the course specified from start.


# Minimum requierments

## Modify auth.cfg
---
### api_key
In auth.cfg you need to specify your api key, this can be generated in canvas by going to

```https://<your institution canvas url>/profile/settings```

Remember to copy the key right away since it will never be fully visible again after closing the dialog.
### discord_webhook
You also need to specify the discord_webhook url for the discord channel.

This can be generated by opening the text channel that you want to send a message to and adding a webhook in the integrations tab.

## starting the app
---

To start the app you need to run the dependencies script

```bash
$ chmod +x dependencies.bas
$ python3 cab.py course_id
```
where course_id should be the course id of the course you want to monitor


# Contributing
All contributions need to be MIT licensed. 

Contributions to the number of languages supported would be greatly appriciated. 
Aswell as contributions towards a more rigourus implementation would also be appriciated.