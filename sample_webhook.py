from Classes import SentryParser as Sn
from discord_webhook import DiscordWebhook, DiscordEmbed

import os

# Your Heroku Environment Variables here
webhook_url = os.environ.get('WEBHOOK_MAIN', "")
icon_url = os.environ.get('ICON_URL', "")
errors_hook = os.environ.get('WEBHOOK_ERRORS', "")


def error_handler(error_title, error_body):
    webhook = DiscordWebhook(url=errors_hook)
    embed = DiscordEmbed(title=error_title, description=error_body, color='03b2f8')
    embed.set_author(name='PyDiscordSentry', url='https://sentry.io/',
                     icon_url=icon_url)
    webhook.add_embed(embed)
    webhook.execute()


def prepare_webhook(sentry_trace: Sn.SentryTrace):
    webhook = DiscordWebhook(url=webhook_url)

    nl = '\n'

    level = "Unknown"
    if sentry_trace.level is not None:
        level = sentry_trace.level if sentry_trace.level is not None else "Unknown"
        level = level[0].upper() + level[1:]
    if sentry_trace.message is not None:
        trace_body = "Message Event Received"
        title = f"Message Event (Level: {level})"
    else:
        trace_body = f"New Exception"
        title = f"Exception Event (Level: {level})"

    embed = DiscordEmbed(title=title, description=trace_body, color='03b2f8')
    embed.set_author(name='PyDiscordSentry', url='https://sentry.io/',
                     icon_url=icon_url)

    # Is it a message event? Add it
    if sentry_trace.message is not None:
        embed.add_embed_field(name='Message', value=f'```{sentry_trace.message}```', inline=False)

    if sentry_trace.exception is not None:
        for values in sentry_trace.exception.values:
            frames = values.stacktrace.frames if len(values.stacktrace.frames) > 0 else []
            list_of_frames = []
            for frame in frames:
                list_of_frames.append(frame)

            # Frames
            i = 0
            for frames in list_of_frames.__reversed__():
                i += 1
                # Exception String
                exception_string = f"""```Frame: {frames.filename} of {i}\nModule: {values.module}\nType: {values.type}
Value: {values.value}\nFile Name: {frames.filename}\nAbsolute Path: {frames.abs_path}\nFunction: {frames.function}\n
Module: {frames.module}\nLine Number: {frames.lineno}```"""
                embed.add_embed_field(name='Exception', value=exception_string, inline=False)

                if len(frames.pre_context) > 0:
                    pre_context_string = f"""```{f'{nl}__'.join(frames.pre_context)}__```"""
                    embed.add_embed_field(name='Pre Context', value=pre_context_string, inline=False)

                # Exception Context
                context_line_string = f"""```>>> {frames.context_line}```"""
                embed.add_embed_field(name='Context Line', value=context_line_string, inline=False)

                if len(frames.post_context) > 0:
                    post_context_string = f"""```{f'{nl}'.join(frames.post_context)}```"""
                    embed.add_embed_field(name='Post Context', value=post_context_string, inline=False)

                # Vars
                if frames.vars:
                    vars_string_list = []
                    for key in frames.vars:
                        vars_string_list.append(f'{key.var_identifier}: {key.var_value}\n')

                    vars_string = f"""```{f'{nl}'.join(vars_string_list)}```"""
                    embed.add_embed_field(name='Vars', value=vars_string, inline=False)

                    embed.add_embed_field(name='In App?', value=f"`{frames.in_app}`", inline=False)

    # Contexts
    if sentry_trace.contexts is not None:
        contexts_string = f"""```{sentry_trace.contexts.__repr__()}```"""
        embed.add_embed_field(name='Contexts', value=contexts_string, inline=False)

    # Installed Modules
    if sentry_trace.modules is not None:
        modules = []
        for module in sentry_trace.modules:
            modules.append(f"{module.name}: {module.version}")
        installed_packages_string = f"""```{f'{nl}'.join(modules)}```"""
        embed.add_embed_field(name='Installed Packages', value=installed_packages_string, inline=False)

    # Extras
    extras = []
    if sentry_trace.extra is not None:
        for extra in sentry_trace.extra:
            extras.append(extra.__repr__())
        extras_string = f"""```{f'{nl}'.join(extras)}```"""
        embed.add_embed_field(name='Extra', value=extras_string, inline=False)

        embed.add_embed_field(name='Release', value=f"`{sentry_trace.release}`", inline=False)
        embed.add_embed_field(name='Environment', value=f"`{sentry_trace.environment}`", inline=False)
        embed.add_embed_field(name='Platform', value=f"`{sentry_trace.platform}`", inline=False)

    # Packages
    packages = []
    if sentry_trace.sdk.packages is not None:
        for package in sentry_trace.sdk.packages:
            packages.append(f"{package.name}: {package.version}")
        sdk_packages_string = f"""{f'{nl}'.join(packages)}"""
        sdk_string = f"""```SDK Name: {sentry_trace.sdk.name}\nSDK Version: {sentry_trace.sdk.version}\nSDK Package: {sdk_packages_string} 
\nSDK Integrations: {f' - '.join(sentry_trace.sdk.integrations)}
        ```"""
        embed.add_embed_field(name='SDK', value=sdk_string, inline=False)

    # Additional Fields
    if sentry_trace.event_id and sentry_trace.timestamp:
        additional_data_string = f"""```\nEvent ID: {sentry_trace.event_id}\nEvent Timestamp: {sentry_trace.timestamp}
```"""
        embed.add_embed_field(name='Additional Data', value=additional_data_string, inline=False)

    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code == 200:
        print("Successfully sent message to Discord")
    else:
        print("Error sending message to Discord")
