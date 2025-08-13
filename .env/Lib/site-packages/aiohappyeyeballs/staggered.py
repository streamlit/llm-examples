import sys

if sys.version_info > (3, 11):
    # https://github.com/python/cpython/issues/124639#issuecomment-2378129834
    from ._staggered import staggered_race
else:
    from asyncio.staggered import staggered_race

__all__ = ["staggered_race"]
