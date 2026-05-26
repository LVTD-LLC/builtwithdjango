# Built with Django

A list of projects and apps built with Django.

[This site](https://builtwithdjango.com) is meant to showcase the awesome work the Django community is doing. I wanted to create a place for people to have their work recognized, especially if it is open source (proprietary projects definitely welcome though!), and stand as examples for those who are new to the language.

## Submitting a project

You can submit your project here -> https://builtwithdjango.com/projects/new/

## Contributing

If you have any ideas, please open up an issue, and I'll try to implement it when I can.

## Observability

Production Sentry is enabled when `SENTRY_DSN` is set and `SENTRY_ENABLED` is true. `SENTRY_ENABLED` defaults to true only when `ENV=prod`. The default config captures all errors, warning-and-above logs, sampled traces, trace-lifecycle profiles, application metrics, and AI spans for Pydantic AI.

For a free-plan project, keep the defaults in `.env.example` unless volume requires tuning. The most useful knobs are `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILE_SESSION_SAMPLE_RATE`, `SENTRY_LOG_LEVEL`, and `SENTRY_INCLUDE_AI_PROMPTS`. Prompts and local variables are disabled by default to avoid accidentally sending submitted project content or secrets to Sentry.
