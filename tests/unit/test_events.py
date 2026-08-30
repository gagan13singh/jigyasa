"""Unit tests for the event system."""

from physengine.core.events import (
    CollisionDetected,
    EventBus,
    SimulationStarted,
    SimulationStopped,
    StepCompleted,
)


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(SimulationStarted, handler)
        bus.emit(SimulationStarted(duration=10.0))

        assert len(received) == 1
        assert isinstance(received[0], SimulationStarted)
        assert received[0].duration == 10.0

    def test_multiple_handlers(self):
        bus = EventBus()
        count = {"a": 0, "b": 0}

        bus.subscribe(StepCompleted, lambda e: count.__setitem__("a", count["a"] + 1))
        bus.subscribe(StepCompleted, lambda e: count.__setitem__("b", count["b"] + 1))

        bus.emit(StepCompleted(step_number=1, dt=0.01))

        assert count["a"] == 1
        assert count["b"] == 1

    def test_type_specific_dispatch(self):
        bus = EventBus()
        received_types = []

        bus.subscribe(SimulationStarted, lambda e: received_types.append("start"))
        bus.subscribe(SimulationStopped, lambda e: received_types.append("stop"))

        bus.emit(SimulationStarted(duration=5.0))

        assert received_types == ["start"]

    def test_consume_event(self):
        bus = EventBus()
        received = []

        def handler1(event):
            received.append("first")
            event.consume()

        def handler2(event):
            received.append("second")

        bus.subscribe(StepCompleted, handler1)
        bus.subscribe(StepCompleted, handler2)

        bus.emit(StepCompleted())

        assert received == ["first"]

    def test_unsubscribe(self):
        bus = EventBus()
        count = [0]

        def handler(event):
            count[0] += 1

        bus.subscribe(StepCompleted, handler)
        bus.emit(StepCompleted())
        assert count[0] == 1

        bus.unsubscribe(StepCompleted, handler)
        bus.emit(StepCompleted())
        assert count[0] == 1

    def test_global_handler(self):
        bus = EventBus()
        received = []

        bus.subscribe_all(lambda e: received.append(type(e).__name__))

        bus.emit(SimulationStarted())
        bus.emit(StepCompleted())

        assert len(received) == 2

    def test_clear(self):
        bus = EventBus()
        bus.subscribe(StepCompleted, lambda e: None)
        bus.subscribe_all(lambda e: None)

        assert bus.handler_count == 2
        bus.clear()
        assert bus.handler_count == 0

    def test_collision_event(self):
        bus = EventBus()
        collisions = []

        bus.subscribe(CollisionDetected, lambda e: collisions.append(e))
        bus.emit(CollisionDetected(entity_a="ball", entity_b="wall"))

        assert len(collisions) == 1
        assert collisions[0].entity_a == "ball"
