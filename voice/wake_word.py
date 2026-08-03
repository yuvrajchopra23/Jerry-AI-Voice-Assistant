import keyboard



def wait_for_wake():
    print("Waiting for wake word...")
    keyboard.wait('ctrl+space')
    print("Jerry Activated!!")