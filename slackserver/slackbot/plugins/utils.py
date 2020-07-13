import functools


def in_channel(allow_channel):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(message, *args, **kargs):
            channel_id = message.body['channel']
            channel_info = message.channel._client.channels[channel_id]
            channel = channel_info['name']
            if allow_channel not in (channel, channel_id):
                message.reply("Please post in #{}".format(allow_channel))
                return
            return func(message, *args, **kargs)
        return wrapper
    return decorator
