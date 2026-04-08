from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key, None)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class QueuePolicy[K]:
    capacity: int
    _order: list[K]

    def get_key_to_evict(self) -> K | None:
        if len(self._order) <= self.capacity:
            return None
        return self._order[0]

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class DictionaryPolicy[K]:
    capacity: int
    _key_counter: dict[K, int]
    _last_key: K | None

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        minimal_frequency = None
        for key, frequency in self._key_counter.items():
            if key == self._last_key:
                continue
            if minimal_frequency is None or frequency < minimal_frequency:
                key_to_evict = key
                minimal_frequency = frequency

        return key_to_evict

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0


@dataclass
class FIFOPolicy(QueuePolicy[K]):
    capacity: int
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        if key in self._order:
            return
        self._order.append(key)


@dataclass
class LRUPolicy(QueuePolicy[K]):
    capacity: int
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)


@dataclass
class LFUPolicy(DictionaryPolicy[K]):
    capacity: int
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _last_key: K | None

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._key_counter = {}
        self._last_key = None

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 0
            self._last_key = key
        self._key_counter[key] += 1


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)

        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict:
            self.storage.remove(key_to_evict)
            self.policy.remove_key(key_to_evict)

    def get(self, key: K) -> V | None:
        if not self.storage.exists(key):
            return None
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        is_available = self.storage.exists(key)
        if is_available:
            self.policy.register_access(key)
        return is_available

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func

    def __get__(self, instance: HasCache[Any, V] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]

        func_key: str = str(instance) + self._func.__name__

        value = instance.cache.get(func_key)
        if value is not None:
            return value

        call_result = self._func(instance)
        instance.cache.set(func_key, call_result)
        return call_result
