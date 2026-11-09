from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.progress import (
    Progress as RichProgress,
)


class Progress(RichProgress):
    def __enter__(self):
        for task_id in self.task_ids:
            self.remove_task(task_id)
        return super().__enter__()


progress = Progress(
    TextColumn('{task.description}'),
    BarColumn(bar_width=None),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
)
