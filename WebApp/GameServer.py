# GameServer.py

# The game server is going to be stateless.  The client will maintain
# the puzzle state.  We're asked to provide a new initial puzzle state,
# or to manipulate a given puzzle state to then be returned to the client.
# I believe "restful" is another term used for this approach.  Note that
# my first inclination suggests that the best way to develop this application
# is as operating completely and exclusively on the client side.  Having each
# puzzle manipulation move require a round-trip query to the server could
# potentially, under heavy network conditions, provide a bad user experience.
# I'm willing to bet, however, that in most circumstances it will be reasonable,
# so to go as far as giving it all a try.

if __name__ == '__main__':
    pass