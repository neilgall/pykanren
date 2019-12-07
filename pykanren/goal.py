from typing import Callable, Iterator

Goal = Callable[["State"], Iterator["State"]]
