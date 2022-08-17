# format and stylesheet

def OFFButtonStyle():
    return"""
    QPushButton{
        background-color: #ff0000;
        border-style: outset;
        border-width: 2px;
        border-radius: 5px;
        border-color: black;
        font: 12px;
        padding: 6px;
        min-width: 6em;
    }
    """

def ONButtonStyle():
    return"""
    QPushButton{
        background-color: #00ff00;
        border-style: outset;
        border-width: 2px;
        border-radius: 5px;
        border-color: black;
        font: 12px;
        padding: 6px;
        min-width: 6em;
    }
    """
def TopRightFrame():
    return"""
    QFrame{
        font: 4pt Times;
        background-color: white;
        border-style: outset;
        border-width: 2px;
        border-radius: 5px;
        border-color: black;
    }
    """

def botLeftFrame():
    return"""
    QFrame{
        font: 4pt Times;
        background-color: white;
        border-style: outset;
        border-width: 2px;
        border-radius: 5px;
        border-color: black;
    }
    """