#!/usr/bin/env python3

from . import config


def main():
    import uvicorn

    app_config = config.get_app_config()

    print("host:", app_config.HOST)
    print("port:", app_config.PORT)
    print("default template:", app_config.DEFAULT_TEMPLATE)
    if app_config.DISALLOW_ROBOTS:
        print("robots: Disallow")
    else:
        print("robots: Allow")

    uvicorn.run(
        "subconv.app:app",
        host=app_config.HOST,
        port=app_config.PORT,
        workers=4,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
