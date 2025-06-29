import logging

def setup_logging(log_file: str = 'roof_calculator.log') -> None:
    """Configure logging for the roof calculator application.

    Sets up logging to both a file and the console.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file, mode='a')  # Use 'w' if you want a fresh log every run
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Log formatting
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info("Logging is set up.")
