from shinsa.utils.logger import get_logger


def test_logging():
    logger = get_logger("test_logging")
    logger.info("Logging test module initialized.")
    logger.debug("This is a debug message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")


def test_logger_instance():
    logger1 = get_logger("instance1")
    logger2 = get_logger("instance1")  # Should return the same instance
    logger3 = get_logger("instance2")

    assert logger1 is logger2, "Logger instances with the same name should be identical."
    assert logger1 is not logger3, "Logger instances with different names should not be identical."


if __name__ == "__main__":
    test_logging()
    test_logger_instance()
