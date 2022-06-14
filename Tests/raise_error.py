import sentry_sdk

sentry_sdk.init("https://Foo@awesomeapp.herokuapp.com/1", release="1.0.0", debug=True)


# Raise an error
def raise_error():
    raise EOFError()


sentry_sdk.capture_message("This is a test")
raise Exception("This is a test")
