import sentry_sdk

sentry_sdk.init("https://Foo@pydiscordsentry.herokuapp.com/1", release="1.0.0", debug=True)


# Raise an error
def raise_error():
    raise EOFError()


raise Exception("This is a test")
#sentry_sdk.capture_message("This is a test")
