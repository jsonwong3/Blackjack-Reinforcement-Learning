import BlackjackDriver as BJD
import BlackjackHelperDriver as BJHD

if (__name__ == "__main__"):
    isRunning = True

    
    while(isRunning):
        program = input('Select program:\n' + 
                        '1) Blackjack\n' + 
                        '2) Blackjack Helper\n' + 
                        '3) Exit Program\n')
        if program == '1':
            print('\nStarting BlackJack Game')
            p = BJD.BlackjackDriver()
        elif program == '2':
            print('\nStarting Blackjack Helper')
            p = BJHD.BlackjackHelperDriver()
        elif program == '3':
            print('\nExiting Program')
            exit()
        else:
            pass
