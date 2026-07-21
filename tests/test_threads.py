from core.threads import ThreadManager


def test_run_map_applies_function():
    tm = ThreadManager(max_workers=4)
    assert sorted(tm.run_map(lambda x: x * 2, [1, 2, 3])) == [2, 4, 6]


def test_run_batch_simple_yields_results():
    tm = ThreadManager(max_workers=4)
    out = sorted(tm.run_batch_simple(lambda x: x + 1, [1, 2, 3]))
    assert out == [2, 3, 4]


def test_run_batch_runs_callables():
    tm = ThreadManager(max_workers=2)
    tasks = [
        (lambda a, b: a + b, [1, 2], {}),
        (lambda a, b: a * b, [2, 3], {}),
    ]
    results = tm.run_batch(tasks)
    assert sorted(results) == [3, 6]


def test_run_map_preserves_string_mapping():
    tm = ThreadManager(max_workers=1)
    assert tm.run_map(str, [1, 2]) == ["1", "2"]
