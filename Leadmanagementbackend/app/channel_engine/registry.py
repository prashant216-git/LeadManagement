from app.channel_engine.BaseChannelProvider import BaseChannelProvider


class ChannelProviderRegistry:

    _providers = {}

    @classmethod
    def register(cls, channel_code: str):

        def decorator(provider_cls):

            cls._providers[channel_code] = provider_cls

            print(
                f"Registered channel provider: {channel_code}"
            )

            return provider_cls

        return decorator

    @classmethod
    def get(cls, channel_code: str):

        provider = cls._providers.get(channel_code)

        if provider is None:
            raise ValueError(
                f"No provider registered for channel: {channel_code}"
            )

        return provider