"""
Logger configuration for the Plan Recommendation Engine API
"""

import logging

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Set up and configure a logger for the application
    
    Args:
        name: Logger name (defaults to module name)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured to avoid duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger

# Create a default logger for the module
logger = setup_logger(__name__)
