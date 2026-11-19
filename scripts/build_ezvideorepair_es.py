"""Publish maintained Spanish page sources to their established public URLs."""
from build_pages import build as build_pages


def build():
    return build_pages(spanish_only=True)


if __name__ == '__main__':
    print(f'Built {len(build())} Spanish pages')
