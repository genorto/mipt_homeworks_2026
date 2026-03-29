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
    _order: list[K] = field()

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
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        minimal_frequency = max(self._key_counter.values())
        for key, frequency in self._key_counter.items():
            if frequency <= minimal_frequency:
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
    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)


@dataclass
class LRUPolicy(QueuePolicy[K]):
    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)


@dataclass
class LFUPolicy(DictionaryPolicy[K]):
    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 0
        self._key_counter[key] += 1


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)

        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict is None:
            return

        self.storage.remove(key_to_evict)
        self.policy.remove_key(key_to_evict)

    def get(self, key: K) -> V | None:
        if self.storage.exists(key):
            self.policy.register_access(key)
            return self.storage.get(key)
        return None

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
    def __init__(self, func: Callable[[Any], V]) -> None:
        self.func = func
        self.attr = func.__name__

    def __get__(self, instance: HasCache[Any, V], owner: type) -> V:
        value = instance.cache.get(self.attr)
        if value is not None:
            return value

        call_result = self.func(instance)
        instance.cache.set(self.attr, call_result)
        return call_result
