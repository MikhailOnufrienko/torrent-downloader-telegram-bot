from datetime import timedelta


class ScheduledTasks:
    watchdog_tasks = {
        "watchdog": {
            "task": "app.tasks.tasks.watch_for_downloads_task",
            "schedule": timedelta(seconds=60),
        },
    }
