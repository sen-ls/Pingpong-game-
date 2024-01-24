
import cProfile

test_game = False

if test_game:
    # Run Nikolas' test server and client
    from Game.Server_test import test_server
    from Game.Test_Client import test_client
    import threading

    server_thread = threading.Thread(target=test_server)
    server_thread.daemon = True
    server_thread.start()
    test_client()
else:
    # from Lobby.PongLobbyClient import main
    from Lobby.Gui.entry_window import main

    # Run the GUI with lobby logic
    #cProfile.run("main()")
    main()
