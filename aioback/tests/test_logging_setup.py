import pytest

from core.logging.setup import Log, RequestLogger, configure_logging, get_logger, log_call


class TestLogFacade:
    def test_setup_does_not_raise(self):
        Log.setup(debug=False, env="testing")

    def test_setup_idempotent(self):
        Log.setup(debug=True, env="development")
        Log.setup(debug=True, env="development")  # second call is no-op

    def test_get_returns_logger(self):
        log = Log.get("TestService", user_id=1)
        assert log is not None

    def test_debug_does_not_raise(self):
        Log.debug("debug message")

    def test_info_does_not_raise(self):
        Log.info("info message")

    def test_warning_does_not_raise(self):
        Log.warning("warning message")

    def test_error_does_not_raise(self):
        Log.error("error message")

    def test_critical_does_not_raise(self):
        Log.critical("critical message")

    def test_exception_does_not_raise(self):
        try:
            raise ValueError("test")
        except ValueError:
            Log.exception("caught exception")

    def test_trace_returns_callable(self):
        decorator = Log.trace(level="DEBUG")
        assert callable(decorator)

    def test_request_returns_request_logger(self):
        rl = Log.request("GET", "/test")
        assert isinstance(rl, RequestLogger)

    def test_catch_returns_context_manager(self):
        ctx = Log.catch("some message")
        assert ctx is not None


class TestConfigureFunctions:
    def test_configure_logging_does_not_raise(self):
        configure_logging(debug=False, env="testing")

    def test_get_logger_returns_logger(self):
        log = get_logger("TestModule", key="value")
        assert log is not None


class TestRequestLogger:
    async def test_context_manager_success(self):
        async with Log.request("POST", "/users", request_id="abc") as log:
            assert log is not None

    async def test_context_manager_with_exception(self):
        with pytest.raises(ValueError):
            async with Log.request("DELETE", "/users/1"):
                raise ValueError("test error")


class TestLogCall:
    async def test_async_function_traced(self):
        @log_call(level="DEBUG")
        async def my_func(x):
            return x * 2

        result = await my_func(5)
        assert result == 10

    async def test_async_function_with_log_args(self):
        @log_call(level="DEBUG", log_args=True, log_result=True)
        async def my_func(self_arg, x):
            return x + 1

        result = await my_func(None, 3)
        assert result == 4

    def test_sync_function_traced(self):
        @log_call(level="DEBUG")
        def my_sync(x):
            return x + 1

        result = my_sync(10)
        assert result == 11

    def test_sync_function_with_log_args(self):
        @log_call(level="DEBUG", log_args=True, log_result=True)
        def my_sync(self_arg, x):
            return x * 3

        result = my_sync(None, 4)
        assert result == 12

    async def test_async_exception_is_reraised(self):
        @log_call(catch=True)
        async def failing():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await failing()

    def test_sync_exception_is_reraised(self):
        @log_call(catch=True)
        def failing(self_arg):
            raise ValueError("oops")

        with pytest.raises(ValueError):
            failing(None)
