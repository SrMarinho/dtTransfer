from abc import ABC, abstractmethod


class Process(ABC):
    @abstractmethod
    def run(self):
        ...


def strip_date_filter(query: str) -> str:
    lines = [
        l for l in query.splitlines()
        if 'REPLACE_START_DATE' not in l and 'REPLACE_END_DATE' not in l
    ]
    return '\n'.join(lines).strip()
