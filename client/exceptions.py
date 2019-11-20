''' Exception classes for macro module '''


class ConsentRequiredException(Exception):
    ''' Raised when consent is required '''


class AuthenticationFailureException(Exception):
    ''' Raised when authentication is failed '''


class AccountBannedException(Exception):
    ''' Raised when account ban is detected '''


class NoSessionException(Exception):
    ''' Raised when no session exists '''


class RateLimitedException(Exception):
    ''' Raised when the login rate is limited '''


class BadUsernameException(Exception):
    ''' Raised when summoner name is not available '''


class AccountChangeNeededException(Exception):
    ''' Raised when account needs to be changed '''


class LogoutNeededException(Exception):
    ''' Raised when account needs to be logout '''


class LootRetrieveException(Exception):
    ''' Raised when there is an error when retriving loot '''


class BuggedLobbyException(Exception):
    ''' Raised when the lobby is bugged '''
