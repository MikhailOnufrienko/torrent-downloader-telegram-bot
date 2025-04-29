from datetime import timedelta


class ScheduledTasks:
    watchdog_tasks = {
        "watchdog": {
            "task": "app.tasks.tasks.watch_for_downloads",
            "schedule": timedelta(minutes=1),
        },
    }
