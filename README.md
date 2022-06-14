[![py-Discord.png](https://i.postimg.cc/xTNx6mbZ/py-Discord.png)](https://postimg.cc/TpGJwp0j)

[PyDiscordSentry][]
===================
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg?style=flat-square)](https://www.python.org/downloads/)


[md-pypi]: https://pypi.org/project/Markdown/
[pyversion-button]: https://img.shields.io/pypi/pyversions/Markdown.svg

A very simple Flask+Python class to send [Sentry's][] custom messages & exceptions
to your Discord channel.

This repo contains the necessary to download and deploy to heroku.

[PyDiscordSentry]: https://sentry.io/
[Sentry's]: https://sentry.io/

[Markdown]: https://daringfireball.net/projects/markdown/
[Features]: https://Python-Markdown.github.io#Features
[Available Extensions]: https://Python-Markdown.github.io/extensions

How to use?
-------------


```python
# Just like how you would use Sentry
sentry_sdk.init("https://<public_key>@<your_heroku_link>/<dsn>", 
                release="1.0.0", debug=True)
```
```python
import sentry_sdk

sentry_sdk.init("https://Foo@awesomeapp.herokuapp.com/1", 
                release="1.0.0", debug=True)
```

That's it!

Bonus note: 
When you deploy to heroku, you may provide the discord webhook url as an env variable.
Following is required env variables:

- `WEBHOOK_MAIN`: The main webhook url to send the messages to.
- `WEBHOOK_ERRORS`: Sometimes the class may not be able to cast the exception to a string, this is a fallback webhook to send the raw error to.
- `ICON_URL`: Embed icon url.
-------
Notes: 
1. The `Classes/SentryParser.py` will need to be updated to accept all types of events. Currently, It's very limited and I don't have much time to add more.
2. I'm not a Flask expert, but I'm sure you'd point out certain things that I'm missing on `app.py`
-------
Support
----
You may report bugs, ask for help, and discuss various other issues on the issues page.
