"""Pure protocol logic shared by training, analysis exports and tests."""
from dataclasses import dataclass


@dataclass
class Detector:
    train_threshold: float = .99
    test_threshold: float = .95
    consecutive: int = 3
    mem_streak: int = 0
    gen_streak: int = 0
    memorization_time: int | None = None
    generalization_time: int | None = None
    relapsed: bool = False

    def observe(self, step, train_acc, test_acc):
        self.mem_streak = self.mem_streak + 1 if train_acc >= self.train_threshold else 0
        self.gen_streak = self.gen_streak + 1 if (train_acc >= self.train_threshold and test_acc >= self.test_threshold) else 0
        if self.memorization_time is None and self.mem_streak >= self.consecutive:
            self.memorization_time = step
        if self.generalization_time is None and self.gen_streak >= self.consecutive:
            self.generalization_time = step
        if self.generalization_time is not None and test_acc < self.test_threshold:
            self.relapsed = True

    def delayed(self, ratio=3., min_gap=200):
        m, t = self.memorization_time, self.generalization_time
        return bool(m is not None and t is not None and m > 0 and t >= ratio*m and t-m >= min_gap)


def allocate_budget(budget, k):
    if k not in (1, 2, 4) or budget <= 0 or budget % k:
        raise ValueError('Budget must be positive and divisible by k=1,2,4.')
    return [budget // k] * k


def success_probability(f, k):
    if not 0 <= f <= 1 or k <= 0:
        raise ValueError('Invalid probability or number of runs.')
    return 1-(1-f)**k
