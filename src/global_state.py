"""
Global State Management Module

This module provides centralized state tracking and logging functionality for the
flightAlertsSystem flight alert system. It maintains execution state across all pipeline
stages and provides structured logging capabilities.

The GLOBAL_STATE class serves as a singleton that tracks the progress of various
operations throughout the flight alert pipeline, from initial configuration loading
through final alert delivery. This enables better debugging, monitoring, and
ensures proper execution flow.

Key Features:
    - Pipeline stage tracking with boolean flags
    - Timestamp generation for unique execution identification
    - Centralized logging configuration and management
    - State reset functionality for multiple executions
    - Thread-safe singleton pattern for global access
    - Automatic state persistence and exception logging

Classes:
    GLOBAL_STATE: Central state management and logging coordinator

Module Variables:
    state: Singleton instance of GLOBAL_STATE for application-wide use
"""

import os
import json
import traceback
from datetime import datetime
from typing import Dict, Any

class GLOBAL_STATE:
    """
    Central state management and logging coordinator for the flight alert system.
    
    This class maintains execution state throughout the entire alert pipeline,
    tracking completion of major operations and providing centralized logging.
    Implemented as a singleton to ensure consistent state across all modules.
    
    The state tracking enables:
    - Pipeline progress monitoring and debugging
    - Conditional execution based on completion flags
    - Error recovery and retry logic
    - Performance monitoring and bottleneck identification
    
    State Flags Tracked:
        configInitialized: Configuration loaded and validated
        spreadSheetModInitialized: Google Sheets service initialized
        mileageModInitialized: Mileage conversion system ready
        flightsRetrieved: Flight data fetched from sources
        flightsAnalysed: Flight data processed and filtered
        availabilityObjectsRetrieved: Seat availability data obtained
        tripsFormatted: Trip objects created and formatted
        email_sent: Email alerts delivered successfully
        sheets_sent: Data written to Google Sheets
        whatsapp_msg_generated: WhatsApp messages prepared
        pdf_generated: PDF reports created
        
    Attributes:
        timestamp (str): Unique execution timestamp (YYYYMMDD_HHMM format)
        logger (logging.Logger): Configured logger instance for the system
        [Various boolean flags]: Pipeline stage completion indicators
    """
    
    def __init__(self):
        """
        Initialize the global state object.
        
        Creates an empty state object that requires load() to be called
        to set up timestamps, flags, and logging configuration.
        """
        self.log_buffer = []  # Store log messages for persistence
        self.state_file_path = None  # Will be set during load()
        pass

    def load(self):
        """
        Initialize all state flags and set up the execution timestamp and logger.
        
        This method prepares the global state for a new execution cycle by:
        - Generating a unique timestamp for this execution
        - Resetting all pipeline stage flags to False
        - Setting up the centralized logging system
        
        The timestamp format (YYYYMMDD_HHMM) provides unique identification
        for each execution run, useful for debugging and file naming.
        
        All boolean flags are initialized to False, representing the initial
        state where no pipeline operations have completed yet.
        
        Side Effects:
            - Sets timestamp attribute to current datetime string
            - Initializes all pipeline stage flags to False
            - Configures and assigns logger instance
            
        Note:
            Should be called once at the beginning of each alert execution cycle.
        """
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.mainModInitialized = False
        self.googleDriveModInitialized = False
        self.configInitialized = False
        self.cashModInitialized = False
        self.mileageModInitialized = False
        self.googleSheetsModInitialized = False
        self.openAIHandlerInitialized = False
        self.seatsAeroHandlerInitialized = False
        self.clickmassaHandlerInitialized = False
        self.flightsRetrieved = False
        self.flightsAnalysed = False
        self.flightsFormatted = False
        self.sentToGoogleSheets = False
        self.emailSent = False
        self.logger = self.setup_logger()
        
        # Set up state file path for persistence
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        self.state_file_path = os.path.join(logs_dir, f"execution_state_{self.timestamp}.json")
        
        # Save initial state
        self.save_state()

    def setup_logger(self):
        """
        Configure and return a centralized logger for the application.
        
        Sets up a standardized logging configuration that provides:
        - DEBUG level logging for detailed execution tracking
        - Console output via StreamHandler
        - Structured log format with timestamp, logger name, level, and message
        - Consistent formatting across all application modules
        - Log message buffering for state persistence
        
        The logger configuration ensures all modules can access the same
        logging infrastructure through the global state instance.
        
        Returns:
            logging.Logger: Configured logger instance ready for use
            
        Logger Configuration:
            - Name: "global_state" 
            - Level: DEBUG (captures all log messages)
            - Handler: StreamHandler (console output) + Custom buffer handler
            - Format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
        Note:
            This logger serves as the primary logging interface for the entire
            application, accessible via state.logger throughout the codebase.
        """
        import logging
        
        # Create custom handler to capture logs for persistence
        class BufferHandler(logging.Handler):
            def __init__(self, buffer):
                super().__init__()
                self.buffer = buffer
                
            def emit(self, record):
                log_entry = self.format(record)
                self.buffer.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.name
                })
        
        logger = logging.getLogger("global_state")
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to prevent duplicates
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Buffer handler for persistence
        buffer_handler = BufferHandler(self.log_buffer)
        buffer_handler.setFormatter(formatter)
        logger.addHandler(buffer_handler)
        
        return logger
    
    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get the current state as a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary containing all state flags, timestamp, and metadata
        """
        return {
            'timestamp': getattr(self, 'timestamp', None),
            'execution_time': datetime.now().isoformat(),
            'pipeline_flags': {
                'mainModInitialized': getattr(self, 'mainModInitialized', False),
                'configInitialized': getattr(self, 'configInitialized', False),
                'cashModInitialized': getattr(self, 'cashModInitialized', False),
                'mileageModInitialized': getattr(self, 'mileageModInitialized', False),
                'googleDriveModInitialized': getattr(self, 'googleDriveModInitialized', False),
                'googleSheetsModInitialized': getattr(self, 'googleSheetsModInitialized', False),
                'openAIHandlerInitialized': getattr(self, 'openAIHandlerInitialized', False),
                'seatsAeroHandlerInitialized': getattr(self, 'seatsAeroHandlerInitialized', False),
                'clickmassaHandlerInitialized': getattr(self, 'clickmassaHandlerInitialized', False),
                'flightsRetrieved': getattr(self, 'flightsRetrieved', False),
                'flightsAnalysed': getattr(self, 'flightsAnalysed', False),
                'flightsFormatted': getattr(self, 'flightsFormatted', False),
                'sentToGoogleSheets': getattr(self, 'sentToGoogleSheets', False),
                'emailSent': getattr(self, 'emailSent', False),
                
            },
            'logs': self.log_buffer[-50:] if self.log_buffer else []  # Keep last 50 log entries
        }
    
    def save_state(self, reason: str = "routine_save"):
        """
        Save the current global state and logs to a JSON file.
        
        This function persists the execution state including all pipeline flags,
        recent log messages, and metadata to enable debugging and recovery.
        Automatically called during state transitions and exceptions.
        
        Args:
            reason (str): Reason for saving state (e.g., "routine_save", "exception", "completion")
            
        Side Effects:
            - Creates/updates JSON file in logs/ directory
            - Captures current state snapshot with timestamp
            - Preserves recent log messages for debugging
            
        File Format:
            {
                "timestamp": "YYYYMMDD_HHMM",
                "execution_time": "ISO datetime",
                "save_reason": "reason string",
                "pipeline_flags": { ... },
                "logs": [ ... ]
            }
        """
        if not hasattr(self, 'state_file_path') or not self.state_file_path:
            return  # Not initialized yet
            
        try:
            state_data = self.get_state_dict()
            state_data['save_reason'] = reason
            
            with open(self.state_file_path, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
                
        except Exception as e:
            # Fallback: try to save to a basic file if main save fails
            try:
                fallback_path = f"logs/emergency_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(fallback_path, 'w') as f:
                    f.write(f"Save failed: {str(e)}\n")
                    f.write(f"State: {str(self.get_state_dict())}\n")
            except:
                pass  # If even fallback fails, continue silently
    
    def log_exception(self, exception: Exception, context: str = ""):
        """
        Log an exception with full context and automatically save state.
        
        This method captures detailed exception information including stack trace,
        current pipeline state, and context information for debugging purposes.
        Automatically triggers state persistence for post-mortem analysis.
        
        Args:
            exception (Exception): The exception that occurred
            context (str): Additional context about where/why the exception occurred
            
        Side Effects:
            - Logs exception details to console and buffer
            - Automatically saves current state with "exception" reason
            - Captures stack trace and execution context
            
        Usage:
            try:
                risky_operation()
            except Exception as e:
                state.log_exception(e, "During flight data retrieval")
                raise  # Re-raise if needed
        """
        error_details = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'context': context,
            'stack_trace': traceback.format_exc(),
            'current_state': self.get_state_dict()['pipeline_flags']
        }
        
        if hasattr(self, 'logger') and self.logger:
            self.logger.error(f"EXCEPTION in {context}: {type(exception).__name__}: {str(exception)}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
        
        # Save state immediately on exception
        self.save_state("exception")
        
        # Also save detailed exception info to separate file
        try:
            exception_file = f"logs/exception_{self.timestamp if hasattr(self, 'timestamp') else datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(exception_file, 'w') as f:
                json.dump(error_details, f, indent=2, default=str)
        except:
            pass  # Don't let exception logging cause more exceptions
    
    def update_flag(self, flag_name: str, value: bool = True):
        """
        Update a pipeline flag and automatically save state.
        
        This method provides a centralized way to update pipeline flags while
        ensuring state persistence. Automatically saves state after each update.
        
        Args:
            flag_name (str): Name of the flag to update
            value (bool): Value to set (default True)
            
        Raises:
            AttributeError: If flag_name doesn't exist
            
        Usage:
            >>> state.update_flag('configInitialized')
            >>> state.update_flag('flightsRetrieved', True)
        """
        if hasattr(self, flag_name):
            setattr(self, flag_name, value)
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"Pipeline flag updated: {flag_name} = {value}")
            self.save_state(f"flag_update_{flag_name}")
        else:
            raise AttributeError(f"Unknown pipeline flag: {flag_name}")
    
    def pipeline_context(self, stage_name: str):
        """
        Context manager for pipeline stages with automatic exception handling.
        
        This context manager automatically handles exceptions during pipeline stages,
        logs them appropriately, and saves state for debugging. Use this to wrap
        major pipeline operations for better error tracking.
        
        Args:
            stage_name (str): Name of the pipeline stage for logging
            
        Usage:
            with state.pipeline_context("flight_retrieval"):
                # Your pipeline code here
                fetch_flights()
                state.update_flag('flightsRetrieved')
        """
        return PipelineContext(self, stage_name)
    
    def reset(self):
        """
        Reset the global state for a new execution cycle.
        
        This method saves the current state before reinitializing, then clears
        all state flags and prepares for a fresh execution. The previous state
        is preserved in the logs directory for reference.
        
        Side Effects:
            - Saves current state before reset
            - Clears all pipeline stage flags
            - Removes timestamp and logger references
            - Resets object to uninitialized state
            
        Note:
            After calling reset(), load() must be called again to set up
            timestamps, flags, and logging for the next execution cycle.
            
        Usage:
            Used between execution cycles to ensure clean state:
            >>> state.reset()  # Save current state and clear
            >>> state.load()   # Initialize for new execution
        """
        # Save state before reset
        self.save_state("reset")
        self.__init__()


class PipelineContext:
    """
    Context manager for pipeline stages with automatic exception handling.
    
    This class provides automatic exception logging and state saving for
    pipeline operations, making it easier to debug issues and track progress.
    """
    
    def __init__(self, state_obj: GLOBAL_STATE, stage_name: str):
        self.state = state_obj
        self.stage_name = stage_name
        
    def __enter__(self):
        if hasattr(self.state, 'logger') and self.state.logger:
            self.state.logger.info(f"Starting pipeline stage: {self.stage_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Exception occurred
            self.state.log_exception(exc_val, f"Pipeline stage: {self.stage_name}")
            if hasattr(self.state, 'logger') and self.state.logger:
                self.state.logger.error(f"Pipeline stage failed: {self.stage_name}")
        else:
            # Stage completed successfully
            if hasattr(self.state, 'logger') and self.state.logger:
                self.state.logger.info(f"Pipeline stage completed: {self.stage_name}")
            self.state.save_state(f"stage_complete_{self.stage_name}")
        
        # Don't suppress exceptions
        return False



# Create a singleton global state instance for use throughout the application
state = GLOBAL_STATE()