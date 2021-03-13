register_channels = {
    809859067324792842: 819626948404838401,
}
data_channels = {
    809859067324792842: 819970629717327923,
}


def registerPageID(guild_id):
    return register_channels[guild_id]


def dataPageID(guild_id):
    return data_channels[guild_id]
