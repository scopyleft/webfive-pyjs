"""Synchronization primitives"""

__all__ = ['Lock', 'EventWaiter', 'Condition', 'Semaphore']

import collections
import time

from . import events
from . import futures
from . import tasks


class Lock:
    """The class implementing primitive lock objects.

    A primitive lock is a synchronization primitive that is not owned by
    a particular coroutine when locked. A primitive lock is in one of two
    states, "locked" or "unlocked".
    It is created in the unlocked state. It has two basic methods,
    acquire() and release(). When the state is unlocked, acquire() changes
    the state to locked and returns immediately. When the state is locked,
    acquire() blocks until a call to release() in another coroutine changes
    it to unlocked, then the acquire() call resets it to locked and returns.
    The release() method should only be called in the locked state; it changes
    the state to unlocked and returns immediately. If an attempt is made
    to release an unlocked lock, a RuntimeError will be raised.

    When more than one coroutine is blocked in acquire() waiting for the state
    to turn to unlocked, only one coroutine proceeds when a release() call
    resets the state to unlocked; first coroutine which is blocked in acquire()
    is being processed.

    acquire() method is a coroutine and should be called with "yield from"

    Locks also support the context manager protocol. (yield from lock) should
    be used as context manager expression.

    Usage:

        lock = Lock()
        ...
        yield from lock
        try:
            ...
        finally:
            lock.release()

    Context manager usage:

        lock = Lock()
        ...
        with (yield from lock):
             ...

    Lock object could be tested for locking state:

        if not lock.locked():
           yield from lock
        else:
           # lock is acquired
           ...

    """

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._locked = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        return '<{} [{}]>'.format(
            res[1:-1], 'locked' if self._locked else 'unlocked')

    def locked(self):
        """Return true if lock is acquired."""
        return self._locked

    @tasks.coroutine
    def acquire(self, timeout=None):
        """Acquire a lock.

        Acquire method blocks until the lock is unlocked, then set it to
        locked and return True.

        When invoked with the floating-point timeout argument set, blocks for
        at most the number of seconds specified by timeout and as long as
        the lock cannot be acquired.

        The return value is True if the lock is acquired successfully,
        False if not (for example if the timeout expired).
        """
        if not self._waiters and not self._locked:
            self._locked = True
            return True

        fut = futures.Future(loop=self._loop, timeout=timeout)

        self._waiters.append(fut)
        try:
            yield from fut
        except futures.CancelledError:
            self._waiters.remove(fut)
            return False
        else:
            f = self._waiters.popleft()
            assert f is fut

        self._locked = True
        return True

    def release(self):
        """Release a lock.

        When the lock is locked, reset it to unlocked, and return.
        If any other coroutines are blocked waiting for the lock to become
        unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError is raised.

        There is no return value.
        """
        if self._locked:
            self._locked = False
            if self._waiters:
                self._waiters[0].set_result(True)
        else:
            raise RuntimeError('Lock is not acquired.')

    def __enter__(self):
        if not self._locked:
            raise RuntimeError(
                '"yield from" should be used as context manager expression')
        return True

    def __exit__(self, *args):
        self.release()

    def __iter__(self):
        yield from self.acquire()
        return self


class EventWaiter:
    """A EventWaiter implementation, our equivalent to threading.Event

    Class implementing event objects. An event manages a flag that can be set
    to true with the set() method and reset to false with the clear() method.
    The wait() method blocks until the flag is true. The flag is initially
    false.
    """

    def __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._value = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        return '<{} [{}]>'.format(res[1:-1], 'set' if self._value else 'unset')

    def is_set(self):
        """Return true if and only if the internal flag is true."""
        return self._value

    def set(self):
        """Set the internal flag to true. All coroutines waiting for it to
        become true are awakened. Coroutine that call wait() once the flag is
        true will not block at all.
        """
        if not self._value:
            self._value = True

            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(True)

    def clear(self):
        """Reset the internal flag to false. Subsequently, coroutines calling
        wait() will block until set() is called to set the internal flag
        to true again."""
        self._value = False

    @tasks.coroutine
    def wait(self, timeout=None):
        """Block until the internal flag is true. If the internal flag
        is true on entry, return immediately. Otherwise, block until another
        coroutine calls set() to set the flag to true, or until the optional
        timeout occurs.

        When the timeout argument is present and not None, it should be
        a floating point number specifying a timeout for the operation in
        seconds (or fractions thereof).

        This method returns true if and only if the internal flag has been
        set to true, either before the wait call or after the wait starts,
        so it will always return True except if a timeout is given and
        the operation times out.

        wait() method is a coroutine.
        """
        if self._value:
            return True

        fut = futures.Future(loop=self._loop, timeout=timeout)

        self._waiters.append(fut)
        try:
            yield from fut
        except futures.CancelledError:
            self._waiters.remove(fut)
            return False
        else:
            f = self._waiters.popleft()
            assert f is fut

        return True


class Condition(Lock):
    """A Condition implementation.

    This class implements condition variable objects. A condition variable
    allows one or more coroutines to wait until they are notified by another
    coroutine.
    """

    def __init__(self, *, loop=None):
        super().__init__(loop=loop)

        self._condition_waiters = collections.deque()

    @tasks.coroutine
    def wait(self, timeout=None):
        """Wait until notified or until a timeout occurs. If the calling
        coroutine has not acquired the lock when this method is called,
        a RuntimeError is raised.

        This method releases the underlying lock, and then blocks until it is
        awakened by a notify() or notify_all() call for the same condition
        variable in another coroutine, or until the optional timeout occurs.
        Once awakened or timed out, it re-acquires the lock and returns.

        When the timeout argument is present and not None, it should be
        a floating point number specifying a timeout for the operation
        in seconds (or fractions thereof).

        The return value is True unless a given timeout expired, in which
        case it is False.
        """
        if not self._locked:
            raise RuntimeError('cannot wait on un-acquired lock')

        self.release()

        fut = futures.Future(loop=self._loop, timeout=timeout)

        self._condition_waiters.append(fut)
        try:
            yield from fut
        except futures.CancelledError:
            self._condition_waiters.remove(fut)
            return False
        else:
            f = self._condition_waiters.popleft()
            assert fut is f
        finally:
            yield from self.acquire()

        return True

    @tasks.coroutine
    def wait_for(self, predicate, timeout=None):
        """Wait until a condition evaluates to True. predicate should be a
        callable which result will be interpreted as a boolean value. A timeout
        may be provided giving the maximum time to wait.
        """
        endtime = None
        waittime = timeout
        result = predicate()

        while not result:
            if waittime is not None:
                if endtime is None:
                    endtime = time.monotonic() + waittime
                else:
                    waittime = endtime - time.monotonic()
                    if waittime <= 0:
                        break

            yield from self.wait(waittime)
            result = predicate()

        return result

    def notify(self, n=1):
        """By default, wake up one coroutine waiting on this condition, if any.
        If the calling coroutine has not acquired the lock when this method
        is called, a RuntimeError is raised.

        This method wakes up at most n of the coroutines waiting for the
        condition variable; it is a no-op if no coroutines are waiting.

        Note: an awakened coroutine does not actually return from its
        wait() call until it can reacquire the lock. Since notify() does
        not release the lock, its caller should.
        """
        if not self._locked:
            raise RuntimeError('cannot notify on un-acquired lock')

        idx = 0
        for fut in self._condition_waiters:
            if idx >= n:
                break

            if not fut.done():
                idx += 1
                fut.set_result(False)

    def notify_all(self):
        """Wake up all threads waiting on this condition. This method acts
        like notify(), but wakes up all waiting threads instead of one. If the
        calling thread has not acquired the lock when this method is called,
        a RuntimeError is raised.
        """
        self.notify(len(self._condition_waiters))


class Semaphore:
    """A Semaphore implementation.

    A semaphore manages an internal counter which is decremented by each
    acquire() call and incremented by each release() call. The counter
    can never go below zero; when acquire() finds that it is zero, it blocks,
    waiting until some other thread calls release().

    Semaphores also support the context manager protocol.

    The first optional argument gives the initial value for the internal
    counter; it defaults to 1. If the value given is less than 0,
    ValueError is raised.

    The second optional argument determins can semophore be released more than
    initial internal counter value; it defaults to False. If the value given
    is True and number of release() is more than number of successfull
    acquire() calls ValueError is raised.
    """

    def __init__(self, value=1, bound=False, *, loop=None):
        if value < 0:
            raise ValueError("Semaphore initial value must be > 0")
        self._value = value
        self._bound = bound
        self._bound_value = value
        self._waiters = collections.deque()
        self._locked = False
        if loop is not None:
            self._loop = loop
        else:
            self._loop = events.get_event_loop()

    def __repr__(self):
        res = super().__repr__()
        return '<{} [{}]>'.format(
            res[1:-1],
            'locked' if self._locked else 'unlocked,value:{}'.format(
                self._value))

    def locked(self):
        """Returns True if semaphore can not be acquired immediately."""
        return self._locked

    @tasks.coroutine
    def acquire(self, timeout=None):
        """Acquire a semaphore. acquire() method is a coroutine.

        When invoked without arguments: if the internal counter is larger
        than zero on entry, decrement it by one and return immediately.
        If it is zero on entry, block, waiting until some other coroutine has
        called release() to make it larger than zero.

        When invoked with a timeout other than None, it will block for at
        most timeout seconds. If acquire does not complete successfully in
        that interval, return false. Return true otherwise.
        """
        if not self._waiters and self._value > 0:
            self._value -= 1
            if self._value == 0:
                self._locked = True
            return True

        fut = futures.Future(loop=self._loop, timeout=timeout)

        self._waiters.append(fut)
        try:
            yield from fut
        except futures.CancelledError:
            self._waiters.remove(fut)
            return False
        else:
            f = self._waiters.popleft()
            assert f is fut

        self._value -= 1
        if self._value == 0:
            self._locked = True
        return True

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.
        When it was zero on entry and another coroutine is waiting for it to
        become larger than zero again, wake up that coroutine.

        If Semaphore is create with "bound" paramter equals true, then
        release() method checks to make sure its current value doesn't exceed
        its initial value. If it does, ValueError is raised.
        """
        if self._bound and self._value >= self._bound_value:
            raise ValueError('Semaphore released too many times')

        self._value += 1
        self._locked = False

        for waiter in self._waiters:
            if not waiter.done():
                waiter.set_result(True)
                break

    def __enter__(self):
        return True

    def __exit__(self, *args):
        self.release()

    def __iter__(self):
        yield from self.acquire()
        return self
