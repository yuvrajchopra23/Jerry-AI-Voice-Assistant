from core.assistant import run
import threading

if __name__ == "__main__":

    #Start jerry in background thread
    jerry_thread = threading.Thread(target=run, daemon=True)
    jerry_thread.start()

    #Run widget on main thread (required for pyqt5)
    from widget.jerry_widget import run_widget 
    run_widget()